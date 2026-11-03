{
  lib,
  appimageTools,
  fetchurl,
  runCommand,
  unzip,
  sources,
}: let
  pname = "display-pilot-2";
  inherit (sources) version;

  # BenQ ships the AppImage inside a zip archive.
  archive = fetchurl {
    inherit (sources) url hash;
    name = "display-pilot-2-${version}.zip";
  };

  src = runCommand "display-pilot-2-${version}.AppImage" {nativeBuildInputs = [unzip];} ''
    unzip -p ${archive} '*.AppImage' > "$out"
    chmod +x "$out"
  '';

  contents = appimageTools.extract {inherit pname version src;};
in
  appimageTools.wrapType2 {
    inherit pname version src;

    # Volume control runs amixer. The bundled libgcrypt links libgpg-error,
    # which the AppImage leaves out.
    extraPkgs = pkgs: [
      pkgs.alsa-utils
      pkgs.libgpg-error
    ];

    # BenQ supports only X11, so run through XWayland even when the session
    # exports QT_QPA_PLATFORM=wayland.
    profile = ''
      export QT_QPA_PLATFORM=xcb
    '';

    extraInstallCommands = ''
      install -Dm444 ${contents}/com.benq.DisplayPilot2.desktop \
        "$out/share/applications/com.benq.DisplayPilot2.desktop"
      substituteInPlace "$out/share/applications/com.benq.DisplayPilot2.desktop" \
        --replace-fail 'Exec=Display_Pilot_2' 'Exec=${pname}' \
        --replace-fail 'Icon=dp2_svg' 'Icon=${pname}'
      install -Dm444 ${contents}/dp2_svg.svg \
        "$out/share/icons/hicolor/scalable/apps/${pname}.svg"
    '';

    meta = {
      description = "BenQ monitor control for RD series displays over DDC/CI";
      longDescription = ''
        Needs read-write access to /dev/i2c-*. On NixOS, set
        hardware.i2c.enable and add the user to the i2c group.
      '';
      homepage = "https://www.benq.com/en-us/monitor/software/display-pilot-2.html";
      license = lib.licenses.unfree;
      sourceProvenance = [lib.sourceTypes.binaryNativeCode];
      platforms = ["x86_64-linux"];
      mainProgram = pname;
    };
  }
