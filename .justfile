_default:
    @just --list

# Update selected inputs, or every input when none are specified
[group('flake')]
update *inputs:
    nix flake update {{ inputs }} --commit-lock-file

[group('flake')]
update-nixpkgs: (update "nixpkgs")

[group('packages')]
update-zen:
    nix run .#update-zen

[group('packages')]
[positional-arguments]
update-vicinae-extension extension:
    nix develop -c python scripts/update-vicinae-extension.py "$1"

[group('checks')]
fmt:
    nix fmt

[group('checks')]
check:
    nix flake check

# Build one exported package on the current system
[group('packages')]
[positional-arguments]
build package:
    nix build --print-out-paths ".#$1"

# Build every package exported for the current system
[group('packages')]
build-all:
    #!/usr/bin/env bash
    set -euo pipefail
    system=$(nix eval --impure --raw --expr builtins.currentSystem)
    nix eval --json ".#packages.$system" --apply builtins.attrNames |
        jq -r '.[]' |
        while IFS= read -r package; do
            nix build --no-link --print-out-paths ".#packages.$system.$package"
        done
