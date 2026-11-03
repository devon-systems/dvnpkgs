{lib, ...}: {
  perSystem = {
    pkgs,
    system,
    ...
  }: {
    packages = lib.optionalAttrs (system == "x86_64-linux") {
      display-pilot-2 = pkgs.callPackage ./_package.nix {
        sources = builtins.fromJSON (builtins.readFile ./sources.json);
      };
    };
  };
}
