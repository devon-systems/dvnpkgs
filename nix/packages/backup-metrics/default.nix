{lib, ...}: {
  perSystem = {pkgs, ...}: {
    checks.backup-metrics =
      pkgs.runCommand "backup-metrics-tests" {
        nativeBuildInputs = [(pkgs.python3.withPackages (python: [python.pyyaml]))];
      } ''
        cp ${./.}/*.py .
        python3 test-backup-metrics.py
        touch "$out"
      '';
    checks.backup-metrics-quality =
      pkgs.runCommand "backup-metrics-quality" {
        nativeBuildInputs = [pkgs.ruff pkgs.ty];
      } ''
        cp ${./backup-metrics.py} backup-metrics.py
        ruff format --isolated --check --target-version py313 backup-metrics.py
        ruff check --isolated --target-version py313 --select E4,E7,E9,F,I,UP,B backup-metrics.py
        ty check --python-version 3.13 backup-metrics.py
        touch "$out"
      '';
    packages = lib.optionalAttrs pkgs.stdenv.hostPlatform.isLinux {
      backup-metrics = pkgs.writeShellApplication {
        name = "backup-metrics";
        runtimeInputs = [pkgs.python3 pkgs.systemd pkgs.coreutils];
        text = ''exec python3 ${./backup-metrics.py} "$@"'';
      };
    };
  };
}
