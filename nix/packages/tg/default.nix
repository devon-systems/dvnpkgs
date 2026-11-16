{inputs, ...}: {
  perSystem = {
    pkgs,
    system,
    ...
  }: let
    # tg requires Go 1.27.4 before it is available in our nixpkgs pin.
    go =
      if pkgs.lib.versionAtLeast pkgs.go_1_27.version "1.27.4"
      then pkgs.go_1_27
      else
        pkgs.go_1_27.overrideAttrs {
          version = "1.27.4";
          src = pkgs.fetchurl {
            url = "https://go.dev/dl/go1.27.4.src.tar.gz";
            hash = "sha256-c8+4VxrsDAEXdofbhxY9Rqog6XeWcncokaoXZU2aYJk=";
          };
        };
    tg = inputs.tg.packages.${system}.default.override {
      buildGoModule = pkgs.buildGoModule.override {inherit go;};
    };
  in {
    packages = {
      inherit tg;
      tgmcp = inputs.tg.packages.${system}.tgmcp.override {inherit tg;};
    };
  };
}
