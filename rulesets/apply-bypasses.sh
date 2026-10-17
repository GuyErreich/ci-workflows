#!/usr/bin/env bash
# Prepared gh api commands. Default: print only. Does not apply rulesets.
# Replace SEMVER_APP_ID in the JSON files first.
set -euo pipefail

root="$(cd "$(dirname "$0")" && pwd)"
repo="${GITHUB_REPOSITORY:-GuyErreich/ci-workflows}"

releases_cmd=(gh api --method PUT "repos/${repo}/rulesets/25303595" --input "${root}/releases-always-bypass.json")
main_cmd=(gh api --method PUT "repos/${repo}/rulesets/25303593" --input "${root}/main-always-bypass.json")

echo "Prepared commands (not run):"
printf '  %q ' "${releases_cmd[@]}"; echo
printf '  %q ' "${main_cmd[@]}"; echo

if [ "${1:-}" != "--i-understand-this-mutates-github" ]; then
  echo "Refusing to apply. Pass --i-understand-this-mutates-github only when Guy is applying these bypasses."
  exit 0
fi

if grep -q 'SEMVER_APP_ID' "${root}/releases-always-bypass.json" "${root}/main-always-bypass.json"; then
  echo "SEMVER_APP_ID placeholder still present; not applying."
  exit 1
fi

"${releases_cmd[@]}"
"${main_cmd[@]}"
