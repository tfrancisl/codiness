let
  inputs = import ./inputs.nix;
  system = builtins.currentSystem;
  pkgs = inputs.nixpkgs.legacyPackages.${system};
  outputs = import ./outputs.nix inputs;
in
outputs.devShells.${system}.default.overrideAttrs (old: {
  nativeBuildInputs = (old.nativeBuildInputs or [ ]) ++ [
    pkgs.tack
    pkgs.treefmt
    pkgs.nixfmt
    pkgs.taplo
  ];
  TACK_DIR = "./.tack"; # inputs.nix here is not tack's, so point it at .tack
})
