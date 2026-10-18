{inputs, ...}: {
  perSystem = {system, ...}: {
    packages.crush = inputs.llm-agents.packages.${system}.crush.overrideAttrs (_: {
      version = "0.96.2-symlinked-skills";
      src = inputs.crush-fork;
      vendorHash = "sha256-kGvyIpS+ZrwfOl0j1Wj/tnMEiCB6zdll0vql+35jSg4=";
      ldflags = [
        "-s"
        "-w"
        "-X=github.com/charmbracelet/crush/internal/version.Version=0.96.2-symlinked-skills"
      ];
    });
  };
}
