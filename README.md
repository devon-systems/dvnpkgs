# dvnpkgs

My Nix packages and pinned upstream exports.

## Packages

| Export                     | Source                                                        | `x86_64-linux` | `aarch64-darwin` |
| -------------------------- | ------------------------------------------------------------- | -------------- | ---------------- |
| `tg`                       | Re-export from `aly.codes/tg`                                 | Yes            | Yes              |
| `tgmcp`                    | Re-export from `aly.codes/tg`                                 | Yes            | Yes              |
| `crush`                    | Personal [crush](https://github.com/charmbracelet/crush) fork | Yes            | Yes              |
| `t3code`                   | Forked T3 Code source build with bundled coding agents        | Yes            | Yes              |
| `t3code-desktop`           | T3 Code desktop with Linux OAuth callback support             | Yes            | Yes              |
| `sway`                     | Sway with wlroots patches                                     | Yes            | No               |
| `tmux`                     | Personal tmux configuration                                   | Yes            | Yes              |
| `vicinae-extensions-pdsls` | PDSls integration for Vicinae                                 | Yes            | Yes              |
| `vicinae-extensions-herdr` | Herdr integration for Vicinae                                 | Yes            | Yes              |
| `zen-browser`              | Patched Zen release binaries                                  | Yes            | No               |
| `display-pilot-2`          | BenQ Display Pilot 2 AppImage (unfree)                        | Yes            | No               |
| `freepilot`                | Rust monitor controls with a GPUI app and CLI                 | Yes            | No               |
| `update-zen`               | Python release updater built with uv2nix                      | Yes            | Yes              |
| `generate-host-readmes`    | Host documentation from NixOS and macOS hardware reports      | Yes            | Yes              |

The cluster helpers are also exported:

- `check-k8s` validates a cluster repository from its working directory. Pass
  `--kubernetes-version <major.minor.patch>` for the cluster's Kubernetes version.
  It supports Linux and macOS.
- `backup-metrics` publishes systemd Restic job results. It supports Linux.
- `btrfs-metrics` publishes existing Btrfs scrub results and device errors.
  It supports Linux.

The reporters accept `--directory` for their output location. Deployment
repositories own service definitions, timers, job selection, and metric paths.
Helper regression tests and reporter lint and type checks run in this repository.

The Herdr extension uses macOS tools to launch and focus terminals. Those
actions may fail on Linux. Install the Herdr CLI separately.

## Display Pilot 2

Display Pilot 2 controls BenQ RD series monitors over DDC/CI. It needs
read-write access to `/dev/i2c-*`. On NixOS, load `i2c-dev`, add your user to
the `i2c` group, and allow unfree packages:

```nix
hardware.i2c.enable = true;
users.users.<name>.extraGroups = ["i2c"];
nixpkgs.config.allowUnfree = true;
```

Log out and back in after changing groups. Check access with `ls -l /dev/i2c-*`.

[Freepilot](https://github.com/alyraffauf/freepilot) is a free alternative with
a GPUI desktop app, tray picture-mode controls, and CLI subcommands. It uses
`ddcutil` with the same I²C permissions and opens the GUI when run without a
subcommand. The `freepilot` export includes its desktop entry and runtime
dependencies. Its upstream flake also provides NixOS and Home Manager modules.

BenQ supports GNOME on X11. The wrapper sets `QT_QPA_PLATFORM=xcb`, so Wayland
sessions need XWayland. DDC/CI controls should work on any desktop, but
resolution scaling uses the desktop's display API and may fail outside GNOME. On
other desktops, install `gnome-control-center` separately to use the settings
shortcut.

The in-app updater cannot replace files in the Nix store. Update through this
flake instead.

## Use a package

Add the flake input:

```nix
inputs.dvnpkgs.url = "github:devon-systems/dvnpkgs";
```

Then select a package for the current system:

```nix
home.packages = [
  inputs.dvnpkgs.packages.${pkgs.stdenv.hostPlatform.system}.tg
];
```

## Development

Enter the pinned development shell with `nix develop`, or run `direnv allow` to
load it automatically. Package definitions live in `nix/packages/<name>/`.

Build one package or every package supported on your system:

```sh
just build tg
just build-all
```

Before committing, run:

```sh
nix fmt
nix flake check
```

CI builds every exported package on its supported systems. Pull requests build
packages and checks whose derivations change. Changes to the flake or CI logic
run every build.

## Update dependencies

Update a flake input and commit the new lockfile:

```sh
just update tg
```

Preview and apply a Zen update:

```sh
nix run .#update-zen -- --check
just update-zen
```

Preview and apply a Vicinae extension update:

```sh
nix develop -c python scripts/update-vicinae-extension.py pdsls --check
just update-vicinae-extension pdsls
```

Use `herdr` instead of `pdsls` for the Herdr extension.

Preview and apply a Display Pilot 2 update:

```sh
nix develop -c python scripts/update-display-pilot-2.py --check
just update-display-pilot-2
```

Daily workflows open update PRs for Zen, Display Pilot 2, and both extensions.
Auto-merge waits for CI to pass.

## Credits

Zen's packaging comes from
[`youwen5/zen-browser-flake` at `458cd16`](https://github.com/youwen5/zen-browser-flake/tree/458cd16116c362a5e92d5db6bdc3599e4e8b1f4a).
License notices are in [LICENSE](nix/packages/zen-browser/LICENSE) and
[LICENSE.nixpkgs](nix/packages/zen-browser/LICENSE.nixpkgs).
