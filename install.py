#!/usr/bin/env python3
"""Cross-platform installer for agent-skills.

Discovers skills under <repo>/skills/*/SKILL.md and installs them into
~/.claude/skills/ via symlink (POSIX), directory junction (Windows fallback),
or file copy (--copy or last-resort fallback). Optionally installs per-skill
Python deps from requirements.txt.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
SKILLS_DIR = REPO_ROOT / "skills"
DEFAULT_TARGET = Path.home() / ".claude" / "skills"


@dataclass
class Skill:
    name: str
    path: Path
    description: str

    @property
    def requirements(self) -> Path | None:
        req = self.path / "requirements.txt"
        return req if req.is_file() else None


def discover_skills() -> list[Skill]:
    skills: list[Skill] = []
    if not SKILLS_DIR.is_dir():
        return skills
    for entry in sorted(SKILLS_DIR.iterdir()):
        skill_md = entry / "SKILL.md"
        if not (entry.is_dir() and skill_md.is_file()):
            continue
        skills.append(Skill(name=entry.name, path=entry, description=parse_description(skill_md)))
    return skills


def parse_description(skill_md: Path) -> str:
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        return ""
    fm = m.group(1)
    desc_match = re.search(r"^description:\s*(.+?)(?:\n[a-zA-Z_]+:|\Z)", fm, re.DOTALL | re.MULTILINE)
    if not desc_match:
        return ""
    desc = " ".join(desc_match.group(1).split())
    sentence = re.split(r"(?<=[.!?])\s+", desc, maxsplit=1)[0]
    return sentence.strip()


def find_skill(name: str, skills: list[Skill]) -> Skill:
    for s in skills:
        if s.name == name:
            return s
    available = ", ".join(s.name for s in skills) or "(none)"
    sys.exit(f"error: skill '{name}' not found. available: {available}")


def is_link_or_junction(path: Path) -> bool:
    if path.is_symlink():
        return True
    if os.name == "nt" and path.exists():
        try:
            attrs = path.lstat().st_file_attributes  # type: ignore[attr-defined]
        except (AttributeError, OSError):
            return False
        FILE_ATTRIBUTE_REPARSE_POINT = 0x0400
        return bool(attrs & FILE_ATTRIBUTE_REPARSE_POINT)
    return False


def link_target(path: Path) -> Path | None:
    if path.is_symlink():
        try:
            return Path(os.readlink(path)).resolve()
        except OSError:
            return None
    if os.name == "nt" and is_link_or_junction(path):
        try:
            return path.resolve()
        except OSError:
            return None
    return None


def prompt_yes_no(msg: str, default_yes: bool = True) -> bool:
    suffix = "[Y/n]" if default_yes else "[y/N]"
    try:
        ans = input(f"{msg} {suffix} ").strip().lower()
    except EOFError:
        return default_yes
    if not ans:
        return default_yes
    return ans in ("y", "yes")


def remove_target(path: Path) -> None:
    if is_link_or_junction(path):
        try:
            path.unlink()
            return
        except (OSError, IsADirectoryError):
            # Windows junction sometimes needs rmdir
            if os.name == "nt":
                subprocess.run(["cmd", "/c", "rmdir", str(path)], check=True)
                return
            raise
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def create_link(src: Path, dst: Path, force_copy: bool) -> str:
    """Create symlink/junction/copy from dst -> src. Returns method used."""
    src = src.resolve()
    if force_copy:
        shutil.copytree(src, dst)
        return "copy"

    if os.name == "posix":
        os.symlink(src, dst, target_is_directory=True)
        return "symlink"

    # Windows
    try:
        os.symlink(src, dst, target_is_directory=True)
        return "symlink"
    except OSError as e:
        if getattr(e, "winerror", None) != 1314:
            # Unknown error — fall through to junction attempt anyway
            pass
    try:
        result = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(dst), str(src)],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return "junction"
        print(f"  junction failed: {result.stderr.strip()}", file=sys.stderr)
    except OSError as e:
        print(f"  junction failed: {e}", file=sys.stderr)

    print("  falling back to copy (re-run installer to update)", file=sys.stderr)
    shutil.copytree(src, dst)
    return "copy"


def install_skill(skill: Skill, target_dir: Path, *, copy: bool, force: bool, no_deps: bool) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)
    dst = target_dir / skill.name
    src = skill.path.resolve()

    if dst.exists() or dst.is_symlink():
        existing = link_target(dst)
        if existing == src and not copy:
            print(f"= {skill.name} already installed -> {src}")
        else:
            label = "link" if is_link_or_junction(dst) else "directory"
            if not force:
                if not prompt_yes_no(
                    f"  {dst} exists ({label}). overwrite?", default_yes=False
                ):
                    print(f"- skipped {skill.name}")
                    return
            remove_target(dst)
            method = create_link(src, dst, copy)
            print(f"+ {skill.name} ({method}) -> {dst}")
    else:
        method = create_link(src, dst, copy)
        print(f"+ {skill.name} ({method}) -> {dst}")

    if not no_deps and skill.requirements:
        maybe_install_deps(skill)


def maybe_install_deps(skill: Skill) -> None:
    req = skill.requirements
    assert req is not None
    contents = req.read_text(encoding="utf-8").strip()
    print(f"  skill '{skill.name}' declares deps:")
    for line in contents.splitlines():
        print(f"    {line}")
    if not prompt_yes_no(f"  install via 'pip install --user -r {req.name}'?"):
        print(f"  skipped. run manually: {sys.executable} -m pip install --user -r {req}")
        return
    cmd = [sys.executable, "-m", "pip", "install", "--user", "-r", str(req)]
    print(f"  $ {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"  pip install failed (exit {result.returncode})", file=sys.stderr)


def uninstall_skill(name: str, target_dir: Path, *, force: bool) -> None:
    dst = target_dir / name
    if not (dst.exists() or dst.is_symlink()):
        print(f"= {name} not installed at {dst}")
        return
    if is_link_or_junction(dst):
        dst_resolved = link_target(dst)
        try:
            dst.unlink()
        except (OSError, IsADirectoryError):
            if os.name == "nt":
                subprocess.run(["cmd", "/c", "rmdir", str(dst)], check=True)
            else:
                raise
        print(f"- removed link {dst} (was -> {dst_resolved})")
        return
    # Real directory (copy install). Confirm before recursive delete.
    if not force and not prompt_yes_no(
        f"  {dst} is a real directory (copy install). delete recursively?",
        default_yes=False,
    ):
        print(f"- skipped {name}")
        return
    shutil.rmtree(dst)
    print(f"- removed directory {dst}")


def cmd_list(skills: list[Skill]) -> None:
    if not skills:
        print("(no skills found under skills/)")
        return
    for s in skills:
        desc = s.description or "(no description)"
        print(f"  {s.name} — {desc}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="install",
        description="Install agent-skills into ~/.claude/skills/.",
    )
    p.add_argument("--list", action="store_true", help="list available skills and exit")
    p.add_argument("--all", action="store_true", help="install every skill")
    p.add_argument(
        "--skill",
        action="append",
        default=[],
        metavar="NAME",
        help="install one skill by name (repeatable)",
    )
    p.add_argument(
        "--uninstall",
        action="append",
        default=[],
        metavar="NAME",
        help="remove a skill from target dir; pass 'all' to remove every discovered skill",
    )
    p.add_argument("--copy", action="store_true", help="copy files instead of linking")
    p.add_argument("--no-deps", action="store_true", help="skip Python dep prompts")
    p.add_argument("--force", action="store_true", help="overwrite existing entries without prompt")
    p.add_argument(
        "--target",
        type=Path,
        default=DEFAULT_TARGET,
        help=f"target directory (default: {DEFAULT_TARGET})",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    skills = discover_skills()

    if args.list:
        cmd_list(skills)
        return 0

    target = args.target.expanduser()

    if args.uninstall:
        names = args.uninstall
        if "all" in names:
            names = [s.name for s in skills]
        for name in names:
            uninstall_skill(name, target, force=args.force)
        return 0

    if not args.all and not args.skill:
        cmd_list(skills)
        print()
        print("nothing to install. pass --all, --skill <name>, or --list.")
        return 1

    if args.all:
        selected = skills
    else:
        selected = [find_skill(n, skills) for n in args.skill]

    print(f"target: {target}")
    for skill in selected:
        install_skill(
            skill,
            target,
            copy=args.copy,
            force=args.force,
            no_deps=args.no_deps,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
