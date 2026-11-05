{
  inputs,
  lib,
  ...
}: {
  perSystem = {system, ...}: {
    # freepilot talks to monitors through /dev/i2c-*, so it is Linux only.
    packages = lib.optionalAttrs (system == "x86_64-linux") {
      inherit (inputs.freepilot.packages.${system}) freepilot;
    };
  };
}
