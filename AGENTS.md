# Work in dvnpkgs

This repository contains Nix packages and pinned upstream exports. Keep host
and service configuration in the repositories that deploy them.

## Add or change a package

Put each package in `nix/packages/<name>/default.nix` as a flake-parts module
that declares `perSystem.packages`. `flake.nix` loads Nix files under `nix/`
through import-tree. Prefix helper Nix filenames with `_` to exclude them.

Export packages for `x86_64-linux` and `aarch64-darwin` where supported.
Keep package export names stable.

## Check changes

Run `nix fmt` and `nix flake check` before committing. Build changed packages
on their supported platforms. Use `just build-all` to build every export for
the current system. CI builds on native Linux and Apple Silicon runners.

## Update dependencies

Keep package edits separate from dependency upgrades when possible. Update
flake inputs with `just update <input>` and commit `flake.lock`.
Keep the repository's nixpkgs pin independent of consumers.

Use scoped Conventional Commits, such as `feat(tg): export the MCP server` or
`fix(sway): update the wlroots patch`.
