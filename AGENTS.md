# Work in dvnpkgs

This repository contains Nix packages and pinned upstream exports. Keep host and service configuration in their deployment repositories.

## Change packages

Define each package in `nix/packages/<name>/default.nix` as a flake-parts module with `perSystem.packages`. `flake.nix` loads `nix/` through import-tree. Prefix helper Nix files with `_` to exclude them.

Export for `x86_64-linux` and `aarch64-darwin` where supported. Keep export names stable.

## Validate changes

Before committing, run `nix fmt` and `nix flake check`. Build changed packages on every supported platform. Use `just build-all` for every export on the current system. CI covers both platforms.

## Update dependencies

Keep package edits separate from dependency upgrades when possible. Run `just update <input>` and commit `flake.lock`. Keep this repository's nixpkgs pin independent of consumers.

Use scoped Conventional Commits, such as `feat(tg): export the MCP server` or `fix(sway): update the wlroots patch`.
