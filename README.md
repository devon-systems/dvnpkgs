# dvnpkgs

Personal Nix packages and pinned upstream flakes.

## Packages

| Export          | Source                                                        | Linux x86-64 | Apple Silicon |
| --------------- | ------------------------------------------------------------- | ------------ | ------------- |
| `tg`            | Re-export from `aly.codes/tg`                                 | Yes          | Yes           |
| `tgmcp`         | Re-export from `aly.codes/tg`                                 | Yes          | Yes           |
| `crush`         | Personal [crush](https://github.com/charmbracelet/crush) fork | Yes          | Yes           |
| `sway`          | Sway with the wlroots patches                                 | Yes          | No            |
| `tmux`          | Personal tmux config                                          | Yes          | Yes           |
| `vicinae-pdsls` | PDSls extension for Vicinae                                   | Yes          | Yes           |
| `zen-browser`   | Patched Zen release binaries                                  | Yes          | No            |
| `update-zen`    | Python release updater built with uv2nix                      | Yes          | Yes           |

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

CI builds every exported package on native Linux and Apple Silicon runners.

## Update

Update a flake input and commit the new lockfile:

```sh
just update tg
```

Preview a Zen release update with `nix run .#update-zen -- --check`.
Apply it with `just update-zen`.

## Credits

Zen's packaging comes from
[`youwen5/zen-browser-flake` at `458cd16`](https://github.com/youwen5/zen-browser-flake/tree/458cd16116c362a5e92d5db6bdc3599e4e8b1f4a).
License notices are in [LICENSE](nix/packages/zen-browser/LICENSE) and
[LICENSE.nixpkgs](nix/packages/zen-browser/LICENSE.nixpkgs).
