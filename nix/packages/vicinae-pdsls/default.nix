_: {
  perSystem = {pkgs, ...}: let
    sources = builtins.fromJSON (builtins.readFile ./sources.json);
  in {
    packages.vicinae-pdsls = pkgs.buildNpmPackage {
      name = "pdsls";
      src =
        pkgs.fetchFromGitHub {
          owner = "raycast";
          repo = "extensions";
          inherit (sources) rev hash;
          sparseCheckout = ["/extensions/pdsls"];
        }
        + "/extensions/pdsls";

      inherit (sources) npmDepsHash;
      dontNpmInstall = true;

      buildPhase = ''
        runHook preBuild
        npm run build -- -o "$out"
        runHook postBuild
      '';

      dontInstall = true;
    };
  };
}
