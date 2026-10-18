#!/usr/bin/env python3
"""Evidence: classic ASC bump vs title-mapped bump for cursor/ merges."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from semver_release import bump_version, group_messages, title_to_asc_branch  # noqa: E402


def _asc_version():
    src = os.environ.get("ASC_SRC", "")
    if src:
        sys.path.insert(0, src)
    from auto_semver.core.semver.version import Version  # type: ignore

    return Version


def show(label: str, branch: str, title: str, current: str = "0.1.2") -> None:
    """Print one dry-run row."""
    Version = _asc_version()
    classic = Version.detect_bump_type(branch)
    classic_ver = Version.parse(current)
    classic_ver.bump(branch_name=branch)
    mapped_branch, mapped_label = title_to_asc_branch(title)
    new_ver, applied, _ = bump_version(current, title)
    groups = group_messages([title])
    section = groups[0][0] if groups else "(none)"
    print(f"## {label}")
    print(f"  branch: {branch}")
    print(f"  title:  {title}")
    print(f"  ASC classic detect_bump_type({branch!r}) = {classic}")
    print(f"  ASC Version.bump({branch!r})           = {current} -> {classic_ver}")
    print(f"  title map → {mapped_branch} ({mapped_label})")
    print(f"  applied (title→ASC prefix)             = {current} -> {new_ver} ({applied})")
    print(f"  changelog group                        = {section}")
    print()


def main() -> int:
    """Run the cursor/ merge cases requested in review."""
    print("Pinned ASC Version.detect_bump_type / Version.bump")
    print("source: Action-Semver-Control src/auto_semver/core/semver/version.py")
    print("unknown prefixes default to patch (line 223 / 233).")
    print()
    show(
        "cursor/ + feat title (desired: minor)",
        "cursor/add-widget-5359",
        "feat: add reusable widget",
    )
    show(
        "cursor/ + fix title (desired: patch)",
        "cursor/fix-checkout-5359",
        "fix: persist-credentials on checkout",
    )
    show(
        "cursor/ + ci title (desired: patch)",
        "cursor/add-auto-semver-5359",
        "ci: add auto-semver release flow",
    )
    show(
        "feature/ control (ASC minor without mapping)",
        "feature/add-widget",
        "feat: add reusable widget",
    )
    show(
        "cursor/ + BREAKING CHANGE (desired: major)",
        "cursor/break-api-5359",
        "BREAKING CHANGE: drop legacy endpoint",
    )
    show(
        "cursor/ + breaking: (desired: major)",
        "cursor/breaking-auth-5359",
        "breaking: rotate token format",
    )
    show(
        "cursor/ + major: (desired: major)",
        "cursor/major-bump-5359",
        "major: require node 22",
    )
    show(
        "cursor/ + feat! (desired: major)",
        "cursor/feat-bang-5359",
        "feat!: rename widget API",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
