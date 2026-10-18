{inputs, ...}: {
  perSystem = {system, ...}: {
    packages = {
      tg = inputs.tg.packages.${system}.default;
      tgmcp = inputs.tg.packages.${system}.tgmcp;
    };
  };
}
