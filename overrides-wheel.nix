{ pkgs }:
final: prev:
let
  inherit (pkgs) lib;
  addDeps = name: extra: attrs: {
    ${name} = prev.${name}.overrideAttrs (
      old:
      {
        buildInputs = (old.buildInputs or [ ]) ++ extra;
        # nvidia wheels keep their libraries under site-packages/nvidia/*/lib,
        # which autoPatchelfHook does not search by default
        preFixup =
          (old.preFixup or "")
          + lib.concatMapStrings (dep: ''
            for d in ${dep}/${final.python.sitePackages}/nvidia/*/lib; do
              addAutoPatchelfSearchPath "$d"
            done
          '') (lib.filter (dep: dep ? pname && lib.hasPrefix "nvidia-" dep.pname) extra);
      }
      // attrs
    );
  };
in

# Wheels are automatically patched using autoPatchelfHook.
#
# For manylinux wheels the appropriate packages are added
# as described in https://peps.python.org/pep-0599/ and various other PEPs.
#
# Some packages provide binary libraries as a part of their binary wheels,
# others expect libraries to be provided by the system.

# laya overrides
addDeps "nvidia-cufile" [ pkgs.rdma-core ] { }
// addDeps "nvidia-cusparse" [ final.nvidia-nvjitlink ] { }
// addDeps "nvidia-cufft" [ final.nvidia-nvjitlink ] { }
// addDeps "nvidia-cusolver" [
  final.nvidia-cublas
  final.nvidia-cusparse
  final.nvidia-nvjitlink
] { }
//
  addDeps "nvidia-cudnn-cu13"
    [
      final.nvidia-cublas
      final.nvidia-cuda-nvrtc
    ]
    {
      # libcudnn dlopens its sibling engine libraries by name at runtime, so
      # they must stay findable via $ORIGIN once autoPatchelf rewrites the RPATH
      autoPatchelfFlags = [ "--preserve-origin" ];
      postFixup = ''
        for f in $out/${final.python.sitePackages}/nvidia/cudnn/lib/*.so*; do
          patchelf --add-rpath '$ORIGIN' "$f"
        done
      '';
    }
//
  addDeps "nvidia-nvshmem-cu13"
    [
      pkgs.rdma-core
      pkgs.ucx
      pkgs.libfabric
    ]
    {
      # optional bootstrap plugins that need MPI/PMIx/OpenSHMEM
      autoPatchelfIgnoreMissingDeps = [
        "libmpi.so.40"
        "liboshmem.so.40"
        "libpmix.so.2"
      ];
    }
// addDeps "marimo" [
  pkgs.libsecret
  pkgs.glib
] { }
//
  addDeps "torch"
    (map (name: final.${name}) [
      "cuda-bindings"
      "nvidia-cublas"
      "nvidia-cuda-cupti"
      "nvidia-cuda-nvrtc"
      "nvidia-cuda-runtime"
      "nvidia-cudnn-cu13"
      "nvidia-cufft"
      "nvidia-cufile"
      "nvidia-curand"
      "nvidia-cusolver"
      "nvidia-cusparse"
      "nvidia-cusparselt-cu13"
      "nvidia-nccl-cu13"
      "nvidia-nvjitlink"
      "nvidia-nvshmem-cu13"
      "nvidia-nvtx"
    ])
    {
      # provided by the host driver at runtime
      autoPatchelfIgnoreMissingDeps = [ "libcuda.so.1" ];
    }
