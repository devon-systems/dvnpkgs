{lib, ...}: {
  perSystem = {pkgs, ...}: {
    packages = lib.optionalAttrs pkgs.stdenv.hostPlatform.isLinux (let
      patchedWlroots = pkgs.wlroots_0_20.overrideAttrs (previousAttrs: {
        patches =
          (previousAttrs.patches or [])
          ++ [
            (pkgs.fetchpatch {
              url = "https://github.com/to-json/wlroots-patch/commit/100b64c21b042324299c42da3a3e0a357f5ef464.patch";
              hash = "sha256-NZ2uZWS0BdL8Xrq4K4vIAeoWR2YE98DFL2nPrVMMQf8=";
            })
          ];
      });

      patchedSwayUnwrapped = pkgs.sway-unwrapped.override {
        wlroots_0_20 = patchedWlroots;
      };
    in {
      sway = pkgs.sway.override {
        sway-unwrapped = patchedSwayUnwrapped;
      };
    });
  };
}
