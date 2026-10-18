{lib, ...}: {
  perSystem = {
    pkgs,
    system,
    ...
  }: {
    packages = lib.optionalAttrs pkgs.stdenv.hostPlatform.isLinux (let
      sources = builtins.fromJSON (builtins.readFile ./sources.json);
      zen-browser-unwrapped = pkgs.callPackage ./_unwrapped.nix {
        inherit (sources.${system}) hash url;
        inherit (sources) version firefoxVersion;
      };
    in {
      zen-browser = pkgs.callPackage ./_package.nix {inherit zen-browser-unwrapped;};
    });
  };
}
