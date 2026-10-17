#!/usr/bin/env bash
# Build a merged-PR JSON event from the push SHA (title via jq, not run:).
set -euo pipefail

out="${EVENT_OUT:?EVENT_OUT is required}"
repo="${GITHUB_REPOSITORY:?}"
sha="${GITHUB_SHA:?}"
github_output="${GITHUB_OUTPUT:-/dev/null}"

# SHA is a revision, not a path — do not pass it after --.
subject="$(git log -1 --format=%s "$sha")"
case "$subject" in
  "chore: finalize semver lock"*|"chore: release "*)
    echo "skip=true" >> "$github_output"
    echo "Release/finalize commit — skipping to avoid a second bump"
    exit 0
    ;;
esac

pr_json="$(gh api "repos/${repo}/commits/${sha}/pulls" \
  -H "Accept: application/vnd.github.groot-preview+json")"

selected="$(printf '%s\n' "$pr_json" | jq -c '
  map(select(.merged_at != null and .base.ref == "main")) | .[0] // empty
')"

if [ -z "$selected" ]; then
  echo "skip=true" >> "$github_output"
  echo "No merged PR targeting main for this commit — skipping"
  exit 0
fi

printf '%s\n' "$selected" | jq --arg repo "$repo" --arg sha "$sha" '{
  repository: {full_name: $repo},
  pull_request: {
    merged: true,
    title: .title,
    body: (.body // ""),
    labels: [.labels[]? | {name: .name}],
    head: {ref: .head.ref, sha: .head.sha},
    base: {ref: .base.ref, sha: .base.sha},
    merge_commit_sha: (.merge_commit_sha // $sha)
  }
}' > "$out"

echo "skip=false" >> "$github_output"
