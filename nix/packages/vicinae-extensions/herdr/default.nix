_: {
  perSystem = {pkgs, ...}: {
    packages.vicinae-extensions-herdr = pkgs.callPackage ../_build-extension.nix {
      name = "herdr";
      sources = builtins.fromJSON (builtins.readFile ./sources.json);
    };
  };
}
