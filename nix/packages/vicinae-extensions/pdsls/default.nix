_: {
  perSystem = {pkgs, ...}: {
    packages.vicinae-extensions-pdsls = pkgs.callPackage ../_build-extension.nix {
      name = "pdsls";
      sources = builtins.fromJSON (builtins.readFile ./sources.json);
    };
  };
}
