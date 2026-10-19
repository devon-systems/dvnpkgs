#!/usr/bin/env bash
set -euo pipefail

sources=nix/packages/zen-browser/sources.json
cp "$sources" "$RUNNER_TEMP/zen-before.json"
nix run .#update-zen
version=$(jq -r .version "$sources")

gh release view "$version" --repo zen-browser/desktop --json body,url \
  >"$RUNNER_TEMP/zen-release.json"
jq -n --slurpfile before "$RUNNER_TEMP/zen-before.json" --slurpfile after "$sources" \
  --slurpfile release "$RUNNER_TEMP/zen-release.json" '
  $before[0] as $before | $after[0] as $after |
  {
    package: "zen-browser",
    changes: [
      {name: "Zen", before: $before.version, after: $after.version},
      {name: "Firefox", before: $before.firefoxVersion, after: $after.firefoxVersion},
      {name: "x86_64-linux SHA-256", before: $before["x86_64-linux"].hash, after: $after["x86_64-linux"].hash}
    ],
    upstream: $release[0].url,
    notes: ($release[0].body // "")
  }
' >"$RUNNER_TEMP/update-pr.json"
