{
  inputs,
  lib,
  ...
}: {
  perSystem = {
    config,
    pkgs,
    ...
  }: let
    workspace = inputs.uv2nix.lib.workspace.loadWorkspace {workspaceRoot = ./.;};
    pythonSet =
      (pkgs.callPackage inputs.pyproject-nix.build.packages {python = pkgs.python3;}).overrideScope
      (lib.composeManyExtensions [
        inputs.pyproject-build-systems.overlays.wheel
        (workspace.mkPyprojectOverlay {sourcePreference = "wheel";})
      ]);
  in {
    packages.update-zen = pythonSet.mkVirtualEnv "update-zen" workspace.deps.default;

    apps.update-zen = {
      type = "app";
      program = "${config.packages.update-zen}/bin/update-zen";
    };

    checks.update-zen = pkgs.runCommand "update-zen-check" {nativeBuildInputs = [pkgs.ty];} ''
      ty check --project ${./.} --python ${config.packages.update-zen}/bin/python
      touch "$out"
    '';
  };
}
