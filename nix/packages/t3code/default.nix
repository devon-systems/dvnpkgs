{inputs, ...}: {
  perSystem = {
    pkgs,
    system,
    ...
  }: let
    # Forked from numtide/llm-agents.nix at a6f1327436d9ca78ead8fe53341ef18f4b91cfb7.
    agents = inputs.llm-agents.packages.${system};
    unwrapped = pkgs.callPackage ./_unwrapped.nix {
      formatelf = pkgs.callPackage ./_formatelf.nix {};
      versionCheckHomeHook = pkgs.callPackage ./_version-check-home.nix {};
    };
    t3code = pkgs.callPackage ./_package.nix {
      t3code-unwrapped = unwrapped;
      inherit (agents) codex claude-code cursor-agent grok opencode;
    };
  in {
    packages = {
      inherit t3code;
      t3code-desktop = t3code.desktop;
    };
  };
}
