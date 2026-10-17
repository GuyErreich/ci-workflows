#!/usr/bin/env bash
# GET each live ruleset, add the semver app always-bypass if missing, print the
# PUT body. Does not apply unless --i-understand-this-mutates-github is passed
# AND SEMVER_APP_ID is a numeric App id (placeholder is refused).
set -euo pipefail

root="$(cd "$(dirname "$0")" && pwd)"
repo="${GITHUB_REPOSITORY:-GuyErreich/ci-workflows}"
app_id="${SEMVER_APP_ID:-SEMVER_APP_ID}"
fragment="${root}/bypass-actor.json"
apply=false
if [ "${1:-}" = "--i-understand-this-mutates-github" ]; then
  apply=true
fi

if [ ! -f "$fragment" ]; then
  echo "missing ${fragment}" >&2
  exit 1
fi

if [ "$apply" = true ]; then
  if [ "$app_id" = "SEMVER_APP_ID" ] || ! [[ "$app_id" =~ ^[0-9]+$ ]]; then
    echo "SEMVER_APP_ID is missing or not numeric; refusing to apply." >&2
    exit 1
  fi
fi

merge_actor() {
  local ruleset_id="$1"
  local live merged
  live="$(gh api "repos/${repo}/rulesets/${ruleset_id}")"
  merged="$(printf '%s\n' "$live" | jq --arg app_id "$app_id" --slurpfile frag "$fragment" '
    ($frag[0] | .actor_id = (if $app_id == "SEMVER_APP_ID" then .actor_id else ($app_id | tonumber) end)) as $actor
    | (.bypass_actors // []) as $existing
    | (any($existing[]?;
        (.actor_type == $actor.actor_type)
        and (.bypass_mode == $actor.bypass_mode)
        and ((.actor_id | tostring) == ($actor.actor_id | tostring))
      )) as $present
    | {
        name, target, enforcement, conditions, rules,
        bypass_actors: (if $present then $existing else ($existing + [$actor]) end),
        _skipped: $present
      }
  ')"
  printf '%s\n' "$merged"
}

put_ruleset() {
  local ruleset_id="$1"
  local body="$2"
  local payload
  payload="$(printf '%s\n' "$body" | jq 'del(._skipped)')"
  printf '%s\n' "$payload" | gh api --method PUT "repos/${repo}/rulesets/${ruleset_id}" --input -
}

for spec in "25303595:Releases" "25303593:Standard Flow (main)"; do
  id="${spec%%:*}"
  name="${spec#*:}"
  echo "=== GET ${name} (${id}) + merge bypass ==="
  body="$(merge_actor "$id")"
  skipped="$(printf '%s\n' "$body" | jq -r '._skipped')"
  if [ "$skipped" = "true" ]; then
    echo "bypass already present — skip"
  else
    echo "would PUT:"
    printf '%s\n' "$body" | jq 'del(._skipped)'
  fi
  if [ "$apply" = true ] && [ "$skipped" != "true" ]; then
    put_ruleset "$id" "$body"
    echo "applied ${name}"
  fi
done

if [ "$apply" != true ]; then
  echo "Print-only. Pass --i-understand-this-mutates-github and a numeric SEMVER_APP_ID to apply."
fi
