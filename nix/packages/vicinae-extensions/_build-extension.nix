{
  buildNpmPackage,
  fetchFromGitHub,
  name,
  sources,
}:
buildNpmPackage {
  inherit name;
  src =
    fetchFromGitHub {
      owner = "raycast";
      repo = "extensions";
      inherit (sources) rev hash;
      sparseCheckout = ["/extensions/${name}"];
    }
    + "/extensions/${name}";

  inherit (sources) npmDepsHash;
  dontNpmInstall = true;

  buildPhase = ''
    runHook preBuild
    npm run build -- -o "$out"
    runHook postBuild
  '';

  dontInstall = true;
}
