import marimo

__generated_with = "0.25.0"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import laya

    return laya, mo


@app.cell
def _(laya, mo):
    mo.md(f"""
    # Laya code assessment

    Ask [Laya](https://pypi.org/project/laya/) {laya.__version__} yes/no, score and
    multiple-choice questions about a snippet, then score its answers against the
    hand-written labels. See the README for how the pieces fit together.
    """)
    return


@app.cell
def _(laya):
    router = laya.Router()
    return (router,)


@app.cell
def _(mo):
    _sources = {
        "examples": mo.notebook_dir() / "examples",
        "corpus": mo.notebook_dir() / "corpus" / "snippets",  # built from pinned sources, see corpus.nix
    }
    examples = {}
    example_source = {}
    for _source, _dir in _sources.items():
        if _dir.is_dir():
            for _path in sorted(_dir.iterdir()):
                if _path.is_file():
                    examples[_path.name] = _path.read_text()
                    example_source[_path.name] = _source

    _choices = {
        name if example_source[name] == "examples" else f"{name} (corpus)": name for name in examples
    }
    example_picker = mo.ui.dropdown(
        options=_choices,
        value=next(iter(_choices)),
        label="Example",
    )
    model_picker = mo.ui.dropdown(
        options=["auto", "english", "typed-decisions", "multilingual"],
        value="english",
        label="Model",
    )
    mo.hstack([example_picker, model_picker], justify="start")
    return example_picker, examples, model_picker


@app.cell
def _(mo):
    rescan = mo.ui.button(label="Rescan results")
    return (rescan,)


@app.cell
def _(mo, rescan):
    rescan.value  # re-run when the button is pressed

    _results = mo.notebook_dir() / "results"
    run_files = {p.stem.removeprefix("eval-"): p for p in sorted(_results.glob("eval-*.jsonl"))}

    saved_runs = mo.ui.multiselect(
        options=list(reversed(run_files)),
        value=list(run_files)[-1:],
        label="Saved runs",
    )
    mo.vstack([
        mo.md("## Saved eval runs (overlaid on the answers below)"),
        mo.hstack([saved_runs, rescan], justify="start", align="end"),
    ])
    return run_files, saved_runs


@app.cell
def _(json, run_files, saved_runs):
    saved_run_rows = {
        run_id: [json.loads(line) for line in run_files[run_id].read_text().splitlines()]
        for run_id in saved_runs.value
    }
    return (saved_run_rows,)


@app.cell
def _(
    example_picker,
    labels,
    make_run_meta,
    model_picker,
    question_stats,
    questions,
    saved_run_rows,
):
    # The most recent selected saved run that has the chosen model, for the display above
    overlay = None
    for _run_id in sorted(saved_run_rows, reverse=True):
        _rows = [r for r in saved_run_rows[_run_id] if r["model"] == model_picker.value]
        if _rows:
            _now = make_run_meta(questions, labels)
            overlay = {
                "run_id": _run_id,
                "rows": {r["question"]: r for r in _rows if r["example"] == example_picker.value},
                "stats": question_stats(_rows, labels, questions),
                "stale": (_rows[0]["questions_sha"], _rows[0]["labels_sha"])
                != (_now["questions_sha"], _now["labels_sha"]),
            }
            break
    return (overlay,)


@app.cell
def _():
    language_by_suffix = {
        ".py": "Python",
        ".sh": "Bash",
        ".rs": "Rust",
        ".c": "C",
        ".cpp": "C++",
        ".java": "Java",
        ".kt": "Kotlin",
        ".js": "JavaScript",
        ".cs": "C#",
        ".swift": "Swift",
        ".hs": "Haskell",
        ".zig": "Zig",
        ".jl": "Julia",
        ".nix": "Nix",
        ".ml": "OCaml",
        ".go": "Go",
        ".rb": "Ruby",
        ".ts": "TypeScript",
    }
    _fence_tags = {"Bash": "bash", "C#": "csharp", "C++": "cpp"}


    def with_language(name, code):
        """Give the model the language up front.

        Guessing the language from a snippet is unreliable for these checkpoints,
        and it is known from the file name anyway, so state it instead of asking.
        """
        language = language_by_suffix.get("." + name.rsplit(".", 1)[-1])
        if language is None:
            return code
        tag = _fence_tags.get(language, language.lower())
        return f"Programming language: {language}\n\n```{tag}\n{code}\n```"

    return (with_language,)


@app.cell
def _():
    def _yes_no(text):
        return {"type": "noul", "instructions": text}


    question_groups = {
        "Inputs": {
            "input_source": {
                "type": "choice",
                "instructions": "Where does this code get its main input?",
                "criteria": {
                    "arguments": "values passed in as function or command-line arguments",
                    "file": "reads a file from disk",
                    "network": "fetches data over the network",
                    "stdin": "reads standard input",
                    "database": "queries a database",
                    "environment": "reads environment variables",
                    "none": "takes no input",
                },
            },
            "untrusted_input": _yes_no(
                "Does this code handle input that could come from an untrusted source?"
            ),
            "validates_input": _yes_no("Does this code validate or sanitize its input?"),
        },
        "Outputs": {
            "output_channel": {
                "type": "choice",
                "instructions": "Where does this code deliver its main result?",
                "criteria": {
                    "return_value": "returns a value to the caller",
                    "stdout": "prints to standard output",
                    "file": "writes a file",
                    "database": "writes to a database",
                    "mutates_argument": "modifies one of its arguments in place",
                    "none": "produces no result",
                },
            },
            "returns_value": _yes_no("Does this code return a value?"),
            "structured_output": _yes_no(
                "Is the result structured data, such as a dict, list or record, rather than a single scalar or text?"
            ),
        },
        "Side effects": {
            "writes_files": _yes_no("Does this code write, create or delete files or directories?"),
            "network": _yes_no("Does this code make network requests?"),
            "subprocess": _yes_no("Does this code run external programs or shell commands?"),
            "database": _yes_no("Does this code read or write a database?"),
            "global_state": _yes_no("Does this code modify global or module-level state?"),
            "mutates_arguments": _yes_no("Does this code modify its arguments in place?"),
            "logs_or_prints": _yes_no("Does this code print, log or write to the console?"),
            "reads_environment": _yes_no("Does this code read environment variables or the system clock?"),
            "destructive": _yes_no("Can this code permanently destroy or delete data?"),
        },
        "Complexity": {
            "algorithmic_complexity": {
                "type": "choice",
                "instructions": "How does the running time grow with the size of the data it processes?",
                "criteria": {
                    "constant": "takes the same time whatever the input size",
                    "logarithmic": "time grows with the logarithm of the input size, as in binary search or a heap operation",
                    "linear": "time grows in proportion to the input size",
                    "linearithmic": "time grows like n log n, as in efficient sorting",
                    "quadratic_or_worse": "nested passes over the input, or worse",
                    "io_bound": "dominated by files, network, databases or other processes rather than computation",
                },
            },
            "has_loops": _yes_no(
                "Does this code contain an explicit loop or comprehension (for, while, repeat, list comprehension)?"
            ),
            "recursion": _yes_no("Does any function in this code call itself?"),
            "nesting_depth": {
                "type": "score",
                "instructions": "How deeply nested are the branches, loops and try blocks?",
                "criteria": ["flat", "one level", "two levels", "three or more levels"],
            },
            "readability": {
                "type": "score",
                "instructions": "How easy is this code to read and follow?",
                "criteria": [
                    "immediately clear",
                    "clear with some effort",
                    "hard to follow",
                    "very hard to follow",
                ],
            },
        },
        "Robustness": {
            "crashes_on_bad_input": _yes_no(
                "Can empty, missing or malformed input make this code raise an unhandled error or abort?"
            ),
            "swallows_errors": _yes_no("Does this code catch errors and ignore them or carry on silently?"),
            "builds_from_input": _yes_no(
                "Does this code build a shell command, SQL query or file path from input without sanitizing it?"
            ),
        },
        "Context": {
            "code_role": {
                "type": "choice",
                "instructions": "What role does this code play?",
                "criteria": {
                    "pure_logic": "computes a result from its inputs without touching the outside world",
                    "io_glue": "moves data between files, the network, databases or other processes",
                    "entry_point": "the top-level program, command or request handler that is run directly",
                    "stateful_component": "keeps state across calls in objects, modules or globals",
                    "maintenance_task": "cleans up, backs up or deletes resources",
                    "configuration": "declares configuration or build definitions",
                },
            },
            "dependency_level": {
                "type": "choice",
                "instructions": "How much does this code depend on libraries outside the language's standard library?",
                "criteria": {
                    "stdlib_only": "uses only the language's standard library",
                    "common_libraries": "uses widely available third-party libraries",
                    "heavy_framework": "depends on a large framework, such as a web or machine learning framework",
                },
            },
        },
        "Assessment": {
            "purity": {
                "type": "score",
                "instructions": "How side-effectful is this code?",
                "criteria": [
                    "pure function",
                    "minor (reads, logging)",
                    "moderate (writes local state)",
                    "major (external systems, destructive)",
                ],
            },
            "risk_if_buggy": {
                "type": "score",
                "instructions": "How bad would it be if this code had a bug?",
                "criteria": ["harmless", "annoying", "serious", "catastrophic"],
            },
            "test_difficulty": {
                "type": "score",
                "instructions": "How hard is this code to unit test?",
                "criteria": ["trivial", "needs fixtures", "needs mocks", "needs real infrastructure"],
            },
            "deterministic": _yes_no("Does this code always give the same result for the same inputs?"),
            "idempotent": _yes_no("Is it safe to run this code twice with the same inputs?"),
        },
    }

    questions = {
        key: question
        for group in question_groups.values()
        for key, question in group.items()
    }
    return question_groups, questions


@app.cell
def _(example_picker, examples, mo):
    _editor_languages = {
        ".py": "python",
        ".sh": "shell",
        ".rs": "rust",
        ".c": "c",
        ".cpp": "cpp",
        ".java": "java",
        ".kt": "kotlin",
        ".js": "javascript",
        ".cs": "csharp",
        ".swift": "swift",
        ".hs": "haskell",
        ".zig": "zig",
        ".jl": "julia",
        ".nix": "nix",
        ".ml": "ocaml",
        ".go": "go",
        ".rb": "ruby",
        ".ts": "typescript",
    }
    _suffix = "." + example_picker.value.rsplit(".", 1)[-1]

    message = mo.ui.code_editor(
        value=examples[example_picker.value],
        language=_editor_languages.get(_suffix, "python"),
        label="Code",
        min_height=200,
    )
    message
    return (message,)


@app.cell
def _(example_picker, message, model_picker, questions, router, with_language):
    result = router.predict(
        with_language(example_picker.value, message.value),
        questions,
        model=None if model_picker.value == "auto" else model_picker.value,
    )
    return (result,)


@app.cell
def _(mo, model_picker, overlay, question_groups, result):
    import html

    _CSS = """
    <style>
    .lm { font-size: 0.9rem; }
    .lm-route { opacity: 0.7; margin-bottom: 0.5rem; }
    .lm h3 { margin: 1.2rem 0 0.2rem; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.06em; opacity: 0.65; }
    .lm h3 .lm-flag { text-transform: none; letter-spacing: 0; margin-left: 0.5rem; color: #d97706; opacity: 1; }
    .lm-row { display: grid; grid-template-columns: minmax(0, 1.3fr) minmax(0, 1fr); gap: 0.2rem 1rem; align-items: center;
              padding: 0.4rem 0; border-bottom: 1px solid color-mix(in srgb, currentColor 10%, transparent); }
    .lm.has-eval .lm-row { grid-template-columns: minmax(0, 1.2fr) minmax(0, 1fr) minmax(0, 1.1fr); }
    .lm-q code { display: block; font-size: 0.72rem; opacity: 0.55; background: none; padding: 0; }
    .lm-line { display: flex; align-items: center; gap: 0.6rem; }
    .lm-meter { flex: 1; min-width: 4rem; height: 0.5rem; border-radius: 0.25rem; overflow: hidden;
                background: color-mix(in srgb, currentColor 12%, transparent); }
    .lm-fill { height: 100%; background: #3b82f6; }
    .lm-fill.lm-unsure { background: #f59e0b; }
    .lm-val { min-width: 10rem; white-space: nowrap; font-variant-numeric: tabular-nums; }
    .lm-chips { font-size: 0.72rem; opacity: 0.6; margin-top: 0.15rem; }
    .lm-chips span { margin-right: 0.6rem; }
    .lm-eval { font-size: 0.85rem; }
    .lm-ok { color: #16a34a; font-weight: 600; }
    .lm-miss { color: #dc2626; font-weight: 600; }
    .lm-note { opacity: 0.7; margin-bottom: 0.5rem; }
    .lm-note .lm-flag { color: #d97706; }
    @media (max-width: 640px) { .lm-row, .lm.has-eval .lm-row { grid-template-columns: 1fr; } .lm-val { min-width: 0; } }
    </style>
    """


    def _pct(x):
        return f"{x * 100:.0f}%"


    def _line(frac, text, unsure):
        fill = "lm-fill lm-unsure" if unsure else "lm-fill"
        return (
            f'<div class="lm-line"><div class="lm-meter"><div class="{fill}" '
            f'style="width:{frac * 100:.1f}%"></div></div>'
            f'<div class="lm-val">{html.escape(text)}</div></div>'
        )


    def _expected(question, truth):
        if question["type"] == "noul":
            return "yes" if truth else "no"
        if question["type"] == "score":
            return question["criteria"][truth]
        return str(truth)


    def _eval_cell(key, question):
        """What the loaded eval says about this question: the label, the verdict, and its track record."""
        row = overlay["rows"].get(key)
        if row is None:
            return '<div class="lm-eval"></div>'
        mark = '<span class="lm-ok">&#10003;</span>' if row["hit"] else '<span class="lm-miss">&#10007;</span>'
        stat = overlay["stats"].get(key)
        bits = []
        if stat:
            bits.append(f"hit {_pct(stat['hit rate'])} vs {_pct(stat['baseline'])} baseline")
            if stat["AUC"] is not None:
                bits.append(f"AUC {stat['AUC']:.2f}")
            if stat["Spearman"] is not None:
                bits.append(f"&rho; {stat['Spearman']:.2f}")
            if stat["yes labels"] is not None:
                bits.append(f"{stat['yes labels']} of {stat['n']} yes")
        return (
            f'<div class="lm-eval"><div>{mark} expected <b>{html.escape(_expected(question, row["truth"]))}</b></div>'
            f'<div class="lm-chips">{" &middot; ".join(bits)}</div></div>'
        )


    def _row(key, question, body):
        extra = _eval_cell(key, question) if overlay else ""
        return (
            f'<div class="lm-row"><div class="lm-q">{html.escape(question["instructions"])}'
            f"<code>{key}</code></div><div>{body}</div>{extra}</div>"
        )


    def _render(key, question, answer):
        kind = answer["type"]
        if kind == "noul":
            p = answer["noul"]
            unsure = 0.35 < p < 0.65
            verdict = ("yes" if p >= 0.5 else "no") + f" · {_pct(p)}" + (" · unsure" if unsure else "")
            return _row(key, question, _line(p, verdict, unsure))
        if kind == "score":
            top = len(answer["legend"]) - 1
            score = answer["score"]
            label = answer["legend"][str(min(max(round(score), 0), top))]
            return _row(key, question, _line(score / top, f"{label} · {score:.1f}/{top}", False))
        ranked = sorted(answer["probabilities"].items(), key=lambda kv: -kv[1])
        (best, p), runners_up = ranked[0], ranked[1:3]
        chips = "".join(f"<span>{html.escape(k)} {_pct(v)}</span>" for k, v in runners_up)
        body = _line(p, f"{best} · {_pct(p)}", p < 0.5) + f'<div class="lm-chips">{chips}</div>'
        return _row(key, question, body)


    def _section(title, group):
        rows = "".join(_render(k, q, result["answers"][k]) for k, q in group.items())
        flagged = [k for k in group if result["answers"][k]["type"] == "noul" and result["answers"][k]["noul"] >= 0.5]
        flag = f'<span class="lm-flag">{len(flagged)} of {len(group)} flagged</span>' if title == "Side effects" else ""
        return f"<h3>{html.escape(title)}{flag}</h3>{rows}"


    _routing = result["routing"]
    _header = f'<div class="lm-route">Model <b>{_routing["model"]}</b> · {html.escape(_routing["reason"])}</div>'
    if overlay:
        _stale = ' <span class="lm-flag">(this run used different questions or labels)</span>' if overlay["stale"] else ""
        _header += (
            f'<div class="lm-note">Eval overlay: run <b>{overlay["run_id"]}</b>, model <b>{html.escape(model_picker.value)}</b>'
            f"{_stale}</div>"
        )
    _body = "".join(_section(title, group) for title, group in question_groups.items())
    _classes = "lm has-eval" if overlay else "lm"

    mo.vstack([
        mo.Html(f'{_CSS}<div class="{_classes}">{_header}{_body}</div>'),
        mo.accordion({"Raw result": mo.json(result)}),
    ])
    return


@app.cell
def _(examples, mo, questions):
    import json

    _all_labels = {}
    for _file in (mo.notebook_dir() / "labels.json", mo.notebook_dir() / "corpus" / "labels.json"):
        if _file.exists():
            _all_labels.update(json.loads(_file.read_text()))

    # Labels for snippets that are not available, such as an unbuilt corpus, are set aside
    labels = {name: truth for name, truth in _all_labels.items() if name in examples}

    _unlabelled = sorted(set(examples) - set(labels))
    _unavailable = sorted(set(_all_labels) - set(examples))
    _missing_keys = sorted(
        f"{name}:{key}" for name, truth in labels.items() for key in questions if key not in truth
    )
    _problems = [
        f"{title}: {', '.join(items)}"
        for title, items in [
            ("examples without labels", _unlabelled),
            ("labels missing a question", _missing_keys),
        ]
        if items
    ]
    _summary = f"{len(labels)} labelled examples, {len(questions)} questions each"
    if _unavailable:
        _summary += (
            f". {len(_unavailable)} labelled snippets are unavailable; build them with "
            "`nix-build -A packages.x86_64-linux.corpus -o corpus/snippets`"
        )
    mo.callout(mo.md("\n\n".join(_problems)), kind="warn") if _problems else mo.md(_summary)
    return json, labels


@app.cell
def _(json, laya, mo, with_language):
    import datetime
    import hashlib
    import subprocess
    import time

    def score_answer(question, answer, truth):
        """Score one answer against its label as (hit, loss).

        A hit is the right choice, the right side of 0.5 for a noul, or a score
        within one level of the label. The loss is 0 for a perfect answer and grows
        to about 1 for a confidently wrong one.
        """
        kind = question["type"]
        if kind == "choice":
            return answer["choice"] == truth, 1.0 - answer["probabilities"].get(truth, 0.0)
        if kind == "noul":
            p = answer["noul"]
            return (p >= 0.5) == truth, (p - float(truth)) ** 2
        error = abs(answer["score"] - truth)
        return error <= 1.0, error / (len(question["criteria"]) - 1)


    def baseline_hit_rate(question, truths):
        """Hit rate of a model that always gives the single best constant answer."""
        if question["type"] == "score":
            levels = range(len(question["criteria"]))
            return max(sum(abs(t - c) <= 1 for t in truths) for c in levels) / len(truths)
        return max(truths.count(t) for t in set(truths)) / len(truths)


    def describe_answer(question, answer):
        """A compact, human-readable form of a raw answer."""
        kind = question["type"]
        if kind == "choice":
            return answer["choice"]
        if kind == "noul":
            return f"{answer['noul']:.2f}"
        return f"{answer['score']:.1f}"


    def make_run_meta(questions, labels):
        """Facts that tie a set of eval rows to the code, questions and labels that made them."""

        def _sha(obj):
            return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()[:12]

        try:
            git_rev = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, check=True
            ).stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            git_rev = None
        return {
            "run_id": datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
            "laya_version": laya.__version__,
            "git_rev": git_rev,
            "questions_sha": _sha(questions),
            "labels_sha": _sha(labels),
            "framing": "language-fence",
        }


    def answer_value(question, answer):
        """The model's raw number for an answer: p(yes), the score, or p(chosen option)."""
        kind = question["type"]
        if kind == "noul":
            return answer["noul"]
        if kind == "score":
            return answer["score"]
        return answer["probabilities"][answer["choice"]]


    def collect_eval_rows(router, examples, labels, questions, models, run_meta=None, on_step=lambda: None):
        """Run every labelled example through each model and score every answer.

        Models are the outer loop so the router only has to swap checkpoints once
        per model. Returns one plain, JSON-serializable dict per (model, example,
        question), each carrying `run_meta` and the time the example took to predict.
        """
        rows = []
        for model in models:
            for name, truth in labels.items():
                started = time.perf_counter()
                result = router.predict(with_language(name, examples[name]), questions, model=model)
                predict_ms = (time.perf_counter() - started) * 1000
                device = str(getattr(router._agents.get(model), "device", "unknown"))
                for key, question in questions.items():
                    answer = result["answers"][key]
                    hit, loss = score_answer(question, answer, truth[key])
                    rows.append({
                        **(run_meta or {}),
                        "model": model,
                        "device": device,
                        "example": name,
                        "question": key,
                        "type": question["type"],
                        "predicted": describe_answer(question, answer),
                        "value": answer_value(question, answer),
                        "confidence": answer.get("confidence"),
                        "truth": truth[key],
                        "hit": hit,
                        "loss": loss,
                        "predict_ms": round(predict_ms, 1),
                    })
                on_step()
        return rows


    def write_jsonl(rows, path):
        """Write one JSON object per line."""
        path.write_text("".join(json.dumps(row) + "\n" for row in rows))


    def _ranks(values):
        """Average ranks (0-based), with ties sharing their mean rank."""
        order = sorted(range(len(values)), key=values.__getitem__)
        ranks = [0.0] * len(values)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
                j += 1
            for k in range(i, j + 1):
                ranks[order[k]] = (i + j) / 2
            i = j + 1
        return ranks


    def spearman(a, b):
        """Spearman rank correlation, or None if either side is constant."""
        ra, rb = _ranks(a), _ranks(b)
        ma, mb = sum(ra) / len(ra), sum(rb) / len(rb)
        cov = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
        var_a = sum((x - ma) ** 2 for x in ra)
        var_b = sum((y - mb) ** 2 for y in rb)
        return cov / (var_a * var_b) ** 0.5 if var_a and var_b else None


    def auc(scores, positives):
        """Chance that a random positive outscores a random negative."""
        ranks = _ranks(scores)
        positive_ranks = [r for r, p in zip(ranks, positives) if p]
        n_pos, n_neg = len(positive_ranks), len(ranks) - len(positive_ranks)
        if not n_pos or not n_neg:
            return None
        return (sum(positive_ranks) - n_pos * (n_pos - 1) / 2) / (n_pos * n_neg)


    # yes/no questions whose "yes" makes code less pure
    purity_effects = [
        "writes_files", "network", "subprocess", "database", "global_state",
        "mutates_arguments", "logs_or_prints", "reads_environment", "destructive",
    ]


    def purity_table(by_series, labels):
        """How well each series ranks examples by impurity, against the labelled purity level.

        Compares the direct purity score with the mean of the side-effect answers and
        "not deterministic", each weighted equally. AUC is the chance an impure example scores higher than a pure one.
        """
        table = []
        for series, rows in by_series.items():
            values = {}
            for r in rows:
                values.setdefault(r["example"], {})[r["question"]] = r["value"]
            needed = ["purity", "deterministic", *purity_effects]
            names = [n for n in labels if all(q in values.get(n, {}) for q in needed)]
            if len(names) < 3:
                continue
            truth = [labels[n]["purity"] for n in names]
            signals = {
                "direct purity score": [values[n]["purity"] for n in names],
                "mean of side-effect answers": [
                    (sum(values[n][q] for q in purity_effects) + 1 - values[n]["deterministic"])
                    / (len(purity_effects) + 1)
                    for n in names
                ],
            }
            for signal, scores in signals.items():
                rho, area = spearman(scores, truth), auc(scores, [t > 0 for t in truth])
                table.append({
                    "series": series,
                    "signal": signal,
                    "examples": len(names),
                    "spearman": None if rho is None else round(rho, 2),
                    "AUC (impure vs pure)": None if area is None else round(area, 2),
                    "mean abs error": (
                        round(sum(abs(s - t) for s, t in zip(scores, truth)) / len(truth), 2)
                        if signal == "direct purity score"
                        else None
                    ),
                })
        return table


    def hit_rate(rows):
        return sum(r["hit"] for r in rows) / len(rows) if rows else None


    def question_stats(rows, labels, questions):
        """Metrics per question for one series' rows.

        Hit rate against its baseline, mean loss, and, for yes/no questions, the AUC
        and number of yes labels, or for scores the Spearman correlation with the labels.
        """
        stats = {}
        for key, question in questions.items():
            rs = [r for r in rows if r["question"] == key]
            if not rs:
                continue
            truths = [t[key] for t in labels.values() if key in t]
            baseline = baseline_hit_rate(question, truths) if truths else None
            hit = hit_rate(rs)
            area = rho = yes_labels = None
            if question["type"] == "noul":
                yes_labels = sum(bool(r["truth"]) for r in rs)
                area = auc([r["value"] for r in rs], [bool(r["truth"]) for r in rs])
            elif question["type"] == "score":
                rho = spearman([r["value"] for r in rs], [r["truth"] for r in rs])
            stats[key] = {
                "type": question["type"],
                "n": len(rs),
                "hit rate": hit,
                "baseline": baseline,
                "lift": None if baseline is None else hit - baseline,
                "AUC": area,
                "Spearman": rho,
                "mean loss": sum(r["loss"] for r in rs) / len(rs),
                "yes labels": yes_labels,
            }
        return stats


    def _round(value, digits=2):
        return None if value is None else round(value, digits)


    def eval_tables(rows, labels, questions):
        """Aggregate scored rows into report tables.

        Each row needs a `series` (what to compare, e.g. a model or a model and run).
        """
        series = list(dict.fromkeys(r["series"] for r in rows))
        by_series = {s: [r for r in rows if r["series"] == s] for s in series}
        stats = {s: question_stats(rs, labels, questions) for s, rs in by_series.items()}

        by_question = [
            {
                "question": key,
                "type": st["type"],
                "series": s,
                "n": st["n"],
                "hit rate": st["hit rate"],
                "baseline": st["baseline"],
                "lift": st["lift"],
                "AUC": _round(st["AUC"]),
                "Spearman": _round(st["Spearman"]),
                "mean loss": _round(st["mean loss"], 3),
                "yes labels": st["yes labels"],
            }
            for key in questions
            for s in series
            if (st := stats[s].get(key))
        ]

        by_example = []
        for name, truth in labels.items():
            row = {"example": name, "purity label": truth["purity"]}
            for s, rs in by_series.items():
                mine = [r for r in rs if r["example"] == name]
                row[s] = hit_rate(mine)
                row[f"{s} loss"] = _round(sum(r["loss"] for r in mine) / len(mine), 3) if mine else None
                row[f"{s} misses"] = sum(not r["hit"] for r in mine) if mine else None
            by_example.append(row)

        misses = sorted((r for r in rows if not r["hit"]), key=lambda r: -r["loss"])
        misses = [
            {
                "series": r["series"],
                **{k: r[k] for k in ("example", "question", "predicted", "truth")},
                "value": _round(r["value"]),
                "confidence": _round(r.get("confidence")),
                "loss": round(r["loss"], 3),
            }
            for r in misses
        ]

        edges = [0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0001]
        calibration = []
        for s, rs in by_series.items():
            yes_no = [r for r in rs if r["type"] == "noul"]
            for lo, hi in zip(edges, edges[1:]):
                bucket = [r for r in yes_no if lo <= r["value"] < hi]
                if bucket:
                    mean_p = sum(r["value"] for r in bucket) / len(bucket)
                    actual = sum(bool(r["truth"]) for r in bucket) / len(bucket)
                    calibration.append({
                        "series": s,
                        "p(yes) range": f"{lo:.1f}-{min(hi, 1):.1f}",
                        "n": len(bucket),
                        "mean p(yes)": mean_p,
                        "actual yes": actual,
                        "gap": mean_p - actual,
                    })

        coverage = []
        for s, rs in by_series.items():
            scored = [r for r in rs if r.get("confidence") is not None]
            for floor in (0, 0.5, 0.7, 0.85, 0.95):
                kept = [r for r in scored if r["confidence"] >= floor]
                if kept:
                    coverage.append({
                        "series": s,
                        "confidence at least": floor,
                        "n": len(kept),
                        "coverage": len(kept) / len(scored),
                        "hit rate": hit_rate(kept),
                        "mean loss": _round(sum(r["loss"] for r in kept) / len(kept), 3),
                    })

        summary = []
        for s, rs in by_series.items():
            per_question = stats[s].values()
            lifts = [st["lift"] for st in per_question if st["lift"] is not None]
            baselines = [st["baseline"] for st in per_question if st["baseline"] is not None]
            areas = [st["AUC"] for st in per_question if st["AUC"] is not None]
            bins = [c for c in calibration if c["series"] == s]
            seen = sum(c["n"] for c in bins)
            summary.append({
                "series": s,
                "examples": len({r["example"] for r in rs}),
                "hit rate": hit_rate(rs),
                "baseline": sum(baselines) / len(baselines) if baselines else None,
                "beats baseline": f"{sum(lift > 0 for lift in lifts)} of {len(lifts)} questions",
                "mean AUC": _round(sum(areas) / len(areas)) if areas else None,
                "calibration error": sum(c["n"] * abs(c["gap"]) for c in bins) / seen if seen else None,
                "mean loss": round(sum(r["loss"] for r in rs) / len(rs), 3),
                "ms/example": round(sum(r.get("predict_ms") or 0 for r in rs) / len(rs)),
            })

        return {
            "series": series,
            "summary": summary,
            "purity": purity_table(by_series, labels),
            "by_question": by_question,
            "by_example": by_example,
            "misses": misses,
            "calibration": calibration,
            "coverage": coverage,
        }


    def render_eval_tables(tables):
        """Lay the tables from `eval_tables` out as a summary plus tabs."""

        def pct(value):
            return "-" if value is None else f"{value:.0%}"

        def points(value):
            return "-" if value is None else f"{value * 100:+.0f} pts"

        formats = {
            **{c: pct for c in ["baseline", "hit rate", "coverage", "mean p(yes)", "actual yes", "calibration error", *tables["series"]]},
            "lift": points,
            "gap": points,
        }

        def table(rows):
            return mo.ui.table(rows, selection=None, format_mapping=formats, page_size=25)

        return mo.vstack([
            table(tables["summary"]),
            mo.ui.tabs({
                "Purity": table(tables["purity"]),
                "By question": table(tables["by_question"]),
                "By example": table(tables["by_example"]),
                "Calibration": table(tables["calibration"]),
                "Confidence vs. hit rate": table(tables["coverage"]),
                f"Misses ({len(tables['misses'])})": table(tables["misses"]),
            }),
        ])

    return (
        collect_eval_rows,
        eval_tables,
        make_run_meta,
        question_stats,
        render_eval_tables,
        write_jsonl,
    )


@app.cell(disabled=True)
def _(mo):
    eval_models = mo.ui.multiselect(
        options=["english", "typed-decisions", "multilingual"],
        value=["english", "typed-decisions"],
        label="Models",
    )
    run_eval = mo.ui.run_button(label="Run eval")
    mo.vstack([
        mo.md("## Eval"),
        mo.hstack([eval_models, run_eval], justify="start", align="end"),
    ])
    return eval_models, run_eval


@app.cell
def _(
    collect_eval_rows,
    eval_models,
    examples,
    labels,
    make_run_meta,
    mo,
    questions,
    router,
    run_eval,
):
    mo.stop(
        not run_eval.value,
        mo.md("*Press **Run eval** to score the selected models against `labels.json`.*"),
    )
    mo.stop(not eval_models.value, mo.md("*Select at least one model.*"))

    with mo.status.progress_bar(
        total=len(eval_models.value) * len(labels), title="Evaluating"
    ) as _bar:
        eval_rows = collect_eval_rows(
            router,
            examples,
            labels,
            questions,
            eval_models.value,
            run_meta=make_run_meta(questions, labels),
            on_step=_bar.update,
        )
    return (eval_rows,)


@app.cell
def _(eval_rows, mo, write_jsonl):
    results_dir = mo.notebook_dir() / "results"
    results_dir.mkdir(exist_ok=True)

    eval_path = results_dir / f"eval-{eval_rows[0]['run_id']}.jsonl"
    write_jsonl(eval_rows, eval_path)

    mo.md(
        f"Exported {len(eval_rows)} rows to `{eval_path.relative_to(mo.notebook_dir())}` "
        f"({eval_path.stat().st_size / 1024:.0f} KiB)"
    )
    return


@app.cell
def _(eval_rows, eval_tables, labels, questions, render_eval_tables):
    render_eval_tables(
        eval_tables([{**r, "series": r["model"]} for r in eval_rows], labels, questions)
    )
    return


@app.cell(disabled=True)
def _(
    eval_tables,
    labels,
    make_run_meta,
    mo,
    questions,
    render_eval_tables,
    saved_run_rows,
    saved_runs,
):
    mo.stop(not saved_runs.value, mo.md("*No saved runs to show yet.*"))

    saved_rows = [
        {**row, "series": row["model"] if len(saved_run_rows) == 1 else f"{row['model']} {run_id}"}
        for run_id, rows in saved_run_rows.items()
        for row in rows
    ]

    _current = make_run_meta(questions, labels)
    _stale = sorted({
        r["run_id"]
        for r in saved_rows
        if (r["questions_sha"], r["labels_sha"]) != (_current["questions_sha"], _current["labels_sha"])
    })
    mo.vstack([
        mo.callout(
            mo.md(f"Runs {', '.join(_stale)} used different questions or labels than this notebook has now."),
            kind="warn",
        )
        if _stale
        else mo.md(f"{len(saved_rows)} rows from {len(saved_run_rows)} run(s)"),
        render_eval_tables(eval_tables(saved_rows, labels, questions)),
    ])
    return


if __name__ == "__main__":
    app.run()
