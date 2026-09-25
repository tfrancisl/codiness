let
  inputs = import ./.tack;
in
{
  inherit (inputs)
    nixpkgs
    pyproject-nix
    uv2nix
    pyproject-build-systems
    cpython
    ;
}
