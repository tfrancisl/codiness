{ pkgs, greeting ? "hello" }:
pkgs.writeShellScriptBin "greet" ''
  echo "${greeting}, $1"
''
