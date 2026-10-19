# dvnpkgs

Personal Nix packages and pinned upstream flakes.

## Packages

| Export                     | Source                                                        | `x86_64-linux` | `aarch64-darwin` |
| -------------------------- | ------------------------------------------------------------- | -------------- | ---------------- |
| `tg`                       | Re-export from `aly.codes/tg`                                 | Yes            | Yes              |
| `tgmcp`                    | Re-export from `aly.codes/tg`                                 | Yes            | Yes              |
| `crush`                    | Personal [crush](https://github.com/charmbracelet/crush) fork | Yes            | Yes              |
| `sway`                     | Sway with the wlroots patches                                 | Yes            | No               |
| `tmux`                     | Personal tmux config                                          | Yes            | Yes              |
| `vicinae-extensions-pdsls` | PDSls integration for Vicinae                                 | Yes            | Yes              |
| `vicinae-extensions-herdr` | Herdr integration for Vicinae                                 | Yes            | Yes              |
| `zen-browser`              | Patched Zen release binaries                                  | Yes            | No               |
| `update-zen`               | Python release updater built with uv2nix                      | Yes            | Yes              |

Herdr's extension uses macOS tools to launch and focus terminals. Those actions
may fail on Linux. Install the Herdr CLI separately.

## Use

Add the flake to your configuration:

```nix
inputs.dvnpkgs.url = "github:devon-systems/dvnpkgs";
```

Select a package by name:

```nix
home.packages = [
	inputs.dvnpkgs.packages.${pkgs.stdenv.hostPlatform.system}.tg
];
```

## Develop

Enter the development shell and build a package:

```sh
nix develop
just build tg
```

Build all packages for your system:

```sh
just build-all
```

Format and check:

```sh
nix fmt
nix flake check
```

CI builds each exported package for its supported systems: `x86_64-linux` and
`aarch64-darwin`. Pull requests build packages and checks whose Nix derivations
change. Changes to `flake.nix`, `flake.lock`, or CI logic run every build, as do
pushes to `master`. Formatting and flake evaluation run on every pull request.

## Update

Update a flake input and commit the new lockfile:

```sh
just update tg
```

Preview a Zen release update with `nix run .#update-zen -- --check`.
Apply it with `just update-zen`.

Preview a Vicinae extension update with
`nix develop -c python scripts/update-vicinae-extension.py pdsls --check`.
Apply it with `just update-vicinae-extension pdsls`. Use `herdr` to update the
Herdr extension.

Daily workflows open signed bot PRs for Zen and the Vicinae extensions.
Each PR shows the old and new pins, an upstream link, and quoted release notes
when available. Auto-merge waits for the required `CI` check.

The extension updater tracks each extension's directory in the Raycast
repository. It skips unrelated commits and updates both source and npm
dependency hashes. Each extension has its own pins and update PR.

## Credits

Zen's packaging comes from
[`youwen5/zen-browser-flake` at `458cd16`](https://github.com/youwen5/zen-browser-flake/tree/458cd16116c362a5e92d5db6bdc3599e4e8b1f4a).
License notices are in [LICENSE](nix/packages/zen-browser/LICENSE) and
[LICENSE.nixpkgs](nix/packages/zen-browser/LICENSE.nixpkgs).
