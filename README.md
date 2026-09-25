# codiness

Experiments in assessing code with [Laya](https://pypi.org/project/laya/), a fast decision model
that answers yes/no, score and multiple-choice questions in a single forward pass. A
[marimo](https://marimo.io) notebook asks it about a snippet's inputs, outputs, side effects,
purity, complexity and robustness, then scores the answers against hand-written labels.

## Layout

| Path | What it is |
| --- | --- |
| `notebook.py` | The marimo notebook: ask questions about one snippet, run an eval, browse saved runs |
| `examples/`, `labels.json` | Small hand-written snippets in many languages, and the expected answer to every question |
| `corpus/` | Real code from nixpkgs and CPython: `manifest.toml` lists the slices, `labels.json` labels them |
| `corpus.nix` | Builds `corpus/snippets/` from the pinned sources (nothing third-party is committed) |
| `results/` | One JSONL file per eval run (not committed) |
| `.tack/` | Pinned inputs, managed with [tack](https://github.com/manic-systems/tack), including the CPython source |
| `pyproject.toml`, `uv.lock` | Python dependencies, built from wheels by uv2nix |
| `overrides-wheel.nix` | Fixes the native libraries that the CUDA wheels expect |
| `default.nix`, `inputs.nix`, `outputs.nix`, `shell.nix` | Nix entry points; no flakes |

`src/hello_world` is left over from the uv2nix template.

## Running the notebook

You need Nix. Laya downloads its model checkpoints from Hugging Face on first use.

```sh
nix-shell        # or `direnv allow`; the first build is large (torch and CUDA wheels)
nix-build -A packages.x86_64-linux.corpus -o corpus/snippets   # optional: real-code examples
marimo edit notebook.py
```

Inference uses the GPU when torch can see one, and the CPU otherwise. On NixOS the shell exposes
the driver library for you.

In the notebook:

1. Pick an example and a model. The answers appear with a bar and confidence for each question.
2. Press **Run eval** to score the selected models on every labelled example. The results are
   written to `results/eval-<time>.jsonl` and summarised in tables.
3. Choose earlier runs under **Saved eval runs** to compare them; the selected run's label and
   track record are shown beside each answer in step 1.

Run `tack update` in the shell to move the pins. If the nixpkgs or CPython slices shift, the corpus
build fails its hash check and the line ranges in `corpus/manifest.toml` need updating.
