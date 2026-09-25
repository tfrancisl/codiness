# Slices the snippets listed in corpus/manifest.toml out of pinned sources.
{ pkgs, sources }:
let
  inherit (pkgs) lib;
  manifest = builtins.fromTOML (builtins.readFile ./corpus/manifest.toml);

  extension = path: lib.last (lib.splitString "." path);

  extract =
    s:
    let
      src = "${sources.${s.pin}}/${s.path}";
      out = ''"$out/${s.id}.${extension s.path}"'';
      slice =
        if s ? lines then
          "sed -n '${toString (lib.head s.lines)},${toString (lib.last s.lines)}p'"
        else
          "cat";
      dedent = lib.optionalString (s ? dedent) " | sed 's/^ \\{${toString s.dedent}\\}//'";
    in
    ''
      ${slice} ${src}${dedent} > ${out}
    ''
    + lib.optionalString (s ? sha256) ''
      echo "${s.sha256}  "${out} | sha256sum --check --quiet
    '';
in
pkgs.runCommand "corpus" { } ''
  mkdir -p $out
  ${lib.concatMapStrings extract manifest.snippet}
''
