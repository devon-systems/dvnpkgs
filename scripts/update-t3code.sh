#!/usr/bin/env bash
set -euo pipefail

# nix-update uses nixpkgs' Nix, which needs the source tree materialized by
# Determinate Nix before reading its shared flake cache.
export NIX_CONFIG="${NIX_CONFIG:-}"$'\n''lazy-trees = false'

package=nix/packages/t3code/_unwrapped.nix
before=$(nix eval --raw .#t3code.version)
tag=$(gh release view --repo pingdotgg/t3code --json tagName --jq .tagName)
[[ $tag =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]
after=${tag#v}

if [[ $before != "$after" ]]; then
  nix-update --flake --version "$after" --override-filename "$package" \
    --subpackage resourceMonitor --subpackage hyprlandSnapShot --subpackage kdeSnapShot \
    t3code.unwrapped
  test "$(nix eval --raw .#t3code.version)" = "$after"
fi

jq -n --arg before "$before" --arg after "$after" '{
  package: "t3code",
  changes: [{name: "T3 Code", before: $before, after: $after}],
  upstream: "https://github.com/pingdotgg/t3code/compare/v\($before)...v\($after)"
}' >"$RUNNER_TEMP/update-pr.json"
