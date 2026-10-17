#!/usr/bin/env python3
"""Direct-main bump using Action-Semver-Control's Version.bump at the pinned SHA.

ASC classic mode only inspects branch prefixes (version.py detect_bump_type).
Unknown prefixes such as cursor/ default to patch. This repo maps the PR title
type onto a prefix ASC understands (feat→feature/, fix→fix/, breaking→breaking/)
so Version.bump implements feat=minor and fix=patch.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys
from pathlib import Path

_TYPE_RE = re.compile(r"^(?P<type>[A-Za-z]+)(?:\([^)]*\))?(?P<bang>!)?:")

# Title type → prefix that ASC Version.detect_bump_type understands.
_TITLE_TO_ASC_BRANCH = {
    "breaking": "breaking/from-title",
    "major": "major/from-title",
    "feat": "feature/from-title",
    "feature": "feature/from-title",
    "add": "feature/from-title",
    "enhance": "feature/from-title",
    "fix": "fix/from-title",
    "bug": "fix/from-title",
    "hotfix": "fix/from-title",
    "patch": "fix/from-title",
}

_PATCH_TYPES = {
    "refactor",
    "style",
    "format",
    "lint",
    "chore",
    "ci",
    "build",
    "devops",
    "dep",
    "deps",
    "test",
    "tests",
    "testing",
    "doc",
    "docs",
    "documentation",
    "readme",
}


def _load_version_class():
    """Import Version from the pinned Action-Semver-Control checkout."""
    src = os.environ.get("ASC_SRC", "")
    if src:
        sys.path.insert(0, src)
    from auto_semver.core.semver.version import Version  # type: ignore

    return Version


def parse_title_type(title: str) -> tuple[str, bool] | None:
    """Return (type, breaking-bang) from a conventional PR title."""
    match = _TYPE_RE.match(title.strip())
    if not match:
        return None
    return match.group("type"), bool(match.group("bang"))


def title_to_asc_branch(title: str) -> tuple[str, str]:
    """Map a PR title to (asc_branch, bump_label) for Version.bump."""
    parsed = parse_title_type(title)
    if parsed is None:
        return "fix/from-title", "patch"
    typ, bang = parsed
    if bang or typ in {"breaking", "major"}:
        return "breaking/from-title", "major"
    if typ in _TITLE_TO_ASC_BRANCH:
        branch = _TITLE_TO_ASC_BRANCH[typ]
        label = "minor" if branch.startswith("feature/") else "patch"
        return branch, label
    if typ in _PATCH_TYPES:
        return "fix/from-title", "patch"
    return "fix/from-title", "patch"


def _group_patterns() -> list[tuple[str, list[re.Pattern[str]]]]:
    """Readable Backpin-style sections; union of types is the pr-title list."""
    specs: list[tuple[str, list[str]]] = [
        (
            "Breaking Changes",
            [
                r"^(BREAKING CHANGE|breaking)(\([^)]*\))?:",
                r"^major(\([^)]*\))?:",
                r"^feat.*!:",
                r"^fix.*!:",
            ],
        ),
        (
            "Features & Enhancements",
            [
                r"^feat(\([^)]*\))?:",
                r"^feature(\([^)]*\))?:",
                r"^add(\([^)]*\))?:",
                r"^enhance(\([^)]*\))?:",
            ],
        ),
        (
            "Refactoring & Code Quality",
            [
                r"^refactor(\([^)]*\))?:",
                r"^style(\([^)]*\))?:",
                r"^format(\([^)]*\))?:",
                r"^lint(\([^)]*\))?:",
            ],
        ),
        (
            "Infrastructure & Tooling",
            [
                r"^chore(\([^)]*\))?:",
                r"^ci(\([^)]*\))?:",
                r"^build(\([^)]*\))?:",
                r"^devops(\([^)]*\))?:",
                r"^deps?(\([^)]*\))?:",
            ],
        ),
        (
            "Bug Fixes & Resolutions",
            [
                r"^fix(\([^)]*\))?:",
                r"^bug(\([^)]*\))?:",
                r"^hotfix(\([^)]*\))?:",
                r"^patch(\([^)]*\))?:",
            ],
        ),
        (
            "Testing",
            [
                r"^test(\([^)]*\))?:",
                r"^tests?(\([^)]*\))?:",
                r"^testing(\([^)]*\))?:",
            ],
        ),
        (
            "Documentation",
            [
                r"^docs?(\([^)]*\))?:",
                r"^documentation(\([^)]*\))?:",
                r"^readme(\([^)]*\))?:",
            ],
        ),
    ]
    return [(title, [re.compile(p) for p in pats]) for title, pats in specs]


def group_messages(messages: list[str]) -> list[tuple[str, list[str]]]:
    """Group conventional titles. Unmatched are dropped (no Other Changes)."""
    grouped: dict[str, list[str]] = {}
    order: list[str] = []
    for section, patterns in _group_patterns():
        order.append(section)
        grouped[section] = []
    for message in messages:
        header = message.split("\n", 1)[0].strip()
        for section, patterns in _group_patterns():
            if any(p.match(header) for p in patterns):
                body = header.split(":", 1)[1].strip() if ":" in header else header
                grouped[section].append(body or header)
                break
    return [(section, grouped[section]) for section in order if grouped[section]]


def render_changelog(version: str, groups: list[tuple[str, list[str]]]) -> str:
    """Render one changelog section (Backpin-style headings)."""
    date = datetime.date.today().strftime("%d-%m-%Y")
    lines = [f"## [{version}] - {date}", ""]
    for title, items in groups:
        lines.append(f"### {title}")
        for item in items:
            lines.append(f"- {item}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def bump_version(current: str, title: str) -> tuple[str, str, str]:
    """Return (new_version, bump_label, asc_branch) via ASC Version.bump."""
    Version = _load_version_class()
    version = Version.parse(current)
    branch, label = title_to_asc_branch(title)
    version.bump(branch_name=branch)
    return str(version), label, branch


def main() -> int:
    """CLI: dry-run or write version.txt + CHANGELOG.md."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--title", default="")
    parser.add_argument("--branch", default="")
    parser.add_argument("--event-json", default=os.environ.get("EVENT_OUT", ""))
    args = parser.parse_args()

    title = args.title
    branch = args.branch
    if args.event_json:
        payload = json.loads(Path(args.event_json).read_text(encoding="utf-8"))
        pr = payload.get("pull_request", {})
        title = title or str(pr.get("title", ""))
        branch = branch or str(pr.get("head", {}).get("ref", ""))

    current = Path("version.txt").read_text(encoding="utf-8").strip()
    Version = _load_version_class()
    classic = Version.detect_bump_type(branch) if branch else "(no branch)"
    new_version, label, asc_branch = bump_version(current, title)

    print(f"branch={branch or '(none)'}")
    print(f"title={title or '(none)'}")
    print(f"asc_classic_on_branch={classic}")
    print(f"title_mapped_asc_branch={asc_branch}")
    print(f"applied_bump={label}")
    print(f"version={current} -> {new_version}")

    if args.dry_run:
        return 0

    messages = [title] if title else []
    section = render_changelog(new_version, group_messages(messages))
    notes_out = os.environ.get("RELEASE_NOTES_OUT")
    if notes_out:
        Path(notes_out).write_text(section, encoding="utf-8")
    changelog = Path("CHANGELOG.md")
    existing = changelog.read_text(encoding="utf-8") if changelog.exists() else (
        "# Changelog\nAll notable changes to this project will be documented in this file.\n"
    )
    if "\n## [" in existing:
        pre, sep, post = existing.partition("\n## [")
        changelog.write_text(pre.rstrip() + "\n\n" + section + "\n" + sep.lstrip("\n") + post, encoding="utf-8")
    else:
        changelog.write_text(existing.rstrip() + "\n\n" + section, encoding="utf-8")
    Path("version.txt").write_text(new_version + "\n", encoding="utf-8")

    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as handle:
            handle.write(f"version={new_version}\n")
            handle.write(f"bump={label}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
