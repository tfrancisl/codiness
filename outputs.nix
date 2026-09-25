{
  nixpkgs,
  pyproject-nix,
  uv2nix,
  pyproject-build-systems,
  cpython,
  ...
}:
let
  inherit (nixpkgs) lib;
  forAllSystems = lib.genAttrs lib.systems.flakeExposed;

  workspace = uv2nix.lib.workspace.loadWorkspace { workspaceRoot = ./.; };

  overlay = workspace.mkPyprojectOverlay {
    sourcePreference = "wheel";
  };

  editableOverlay = workspace.mkEditablePyprojectOverlay {
    root = "$REPO_ROOT";
  };

  pythonSets = forAllSystems (
    system:
    let
      pkgs = nixpkgs.legacyPackages.${system};
    in
    (pkgs.callPackage pyproject-nix.build.packages {
      python = pkgs.python3;
    }).overrideScope
      (
        lib.composeManyExtensions [
          pyproject-build-systems.overlays.wheel
          overlay
          (import ./overrides-wheel.nix { inherit pkgs; })
        ]
      )
  );
in
{
  devShells = forAllSystems (
    system:
    let
      pkgs = nixpkgs.legacyPackages.${system};
      pythonSet = pythonSets.${system}.overrideScope editableOverlay;
      virtualenv = pythonSet.mkVirtualEnv "codiness-dev-env" workspace.deps.all;
    in
    {
      default = pkgs.mkShell {
        packages = [
          virtualenv
          pkgs.uv
        ];
        env = {
          UV_NO_SYNC = "1";
          UV_PYTHON = pythonSet.python.interpreter;
          UV_PYTHON_DOWNLOADS = "never";
        };
        shellHook = ''
          unset PYTHONPATH
          export REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
          # NixOS keeps libcuda.so.1 here, where torch and triton's JIT (which
          # calls /sbin/ldconfig) do not look
          if [ -d /run/opengl-driver/lib ]; then
            export LD_LIBRARY_PATH=/run/opengl-driver/lib''${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}
            export TRITON_LIBCUDA_PATH=/run/opengl-driver/lib
          fi
        '';
      };
    }
  );

  packages = forAllSystems (system: {
    default = pythonSets.${system}.mkVirtualEnv "codiness-env" workspace.deps.default;
    corpus = nixpkgs.legacyPackages.${system}.callPackage ./corpus.nix {
      sources = { inherit nixpkgs cpython; };
    };
  });
}
