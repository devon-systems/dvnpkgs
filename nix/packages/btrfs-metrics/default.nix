{lib, ...}: {
  perSystem = {pkgs, ...}: {
    checks.btrfs-metrics-quality =
      pkgs.runCommand "btrfs-metrics-quality" {
        nativeBuildInputs = [pkgs.ruff pkgs.ty];
      } ''
        cp ${./btrfs-metrics.py} btrfs-metrics.py
        ruff format --isolated --check --target-version py313 btrfs-metrics.py
        ruff check --isolated --target-version py313 --select E4,E7,E9,F,I,UP,B btrfs-metrics.py
        ty check --python-version 3.13 btrfs-metrics.py
        touch "$out"
      '';
    packages = lib.optionalAttrs pkgs.stdenv.hostPlatform.isLinux {
      btrfs-metrics = pkgs.writeShellApplication {
        name = "btrfs-metrics";
        runtimeInputs = [pkgs.python3];
        text = ''exec python3 ${./btrfs-metrics.py} "$@"'';
      };
    };
  };
}
