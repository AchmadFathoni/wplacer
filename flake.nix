{
  description = "WPlacer";
  inputs = {
    nixpkgs.url = "git+file:///home/toni/Documents/source/nixpkgs";
    flake-utils.url = "github:numtide/flake-utils";
  };
  outputs = {
    nixpkgs,
    flake-utils,
    ...
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = import nixpkgs {
        inherit system;
      };
      buildInputs = [
        pkgs.brave
      ];
    in {
      devShells.default = pkgs.mkShell {
        inherit buildInputs;
        shellHook = ''
          export LD_LIBRARY_PATH=${pkgs.lib.makeLibraryPath [pkgs.libuuid]}:$LD_LIBRARY_PATH;
        '';
      };
    });
}
