_: {
  perSystem = {pkgs, ...}: {
    checks.check-k8s =
      pkgs.runCommand "check-k8s-tests" {
        nativeBuildInputs = [(pkgs.python3.withPackages (python: [python.pyyaml]))];
      } ''
        cp ${./.}/*.py .
        cp ${./gotk-components.yaml} gotk-components.yaml
        python3 test-k8s-bundle.py
        touch "$out"
      '';
    packages = {
      check-k8s = pkgs.writeShellApplication {
        name = "check-k8s";
        runtimeInputs = [(pkgs.python3.withPackages (python: [python.pyyaml])) pkgs.kustomize pkgs.kubernetes-helm pkgs.kubeconform];
        text = ''exec python3 ${./check-k8s.py} "$@"'';
      };
    };
  };
}
