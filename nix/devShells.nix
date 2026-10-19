_: {
  perSystem = {pkgs, ...}: {
    devShells.default = pkgs.mkShell {
      packages = [
        pkgs.gh
        pkgs.git
        pkgs.jq
        pkgs.just
        pkgs.nixd
        pkgs.nix-prefetch-git
        pkgs.prefetch-npm-deps
        pkgs.python3
        pkgs.ruff
        pkgs.ty
        pkgs.uv
      ];
      env = {
        UV_PYTHON = pkgs.python3.interpreter;
        UV_PYTHON_DOWNLOADS = "never";
      };
    };
  };
}
