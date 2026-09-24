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
    # Laya playground\n\nlaya `{laya.__version__}`
    """)
    return


@app.cell
def _(laya):
    router = laya.Router()
    return (router,)


@app.cell
def _(mo):
    examples_dir = mo.notebook_dir() / "examples"
    examples = {p.name: p.read_text() for p in sorted(examples_dir.iterdir()) if p.is_file()}

    example_picker = mo.ui.dropdown(
        options=list(examples),
        value=next(iter(examples)),
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
def _():
    programming_languages = set(["C", "Python", "Rust", "C++", "C#", "Perl", "JavaScript", "Zig", "Julia", "ASM", "Clojure", "Lisp", "Haskell", "F#", "R", "Fortran", "ALGOL", "COBOL", "Smalltalk", "Verilog", "Objective-C", "Swift", "BASIC", "Visual Basic", "Erlang", "Bash", "OCaml", "GDScript", "Java", "Scratch", "Nix", "Scala", "Kotlin", "Lean", "other"])
    return (programming_languages,)


@app.cell
def _(programming_languages):
    def _yes_no(text):
        return {"type": "noul", "instructions": text}


    question_groups = {
        "Language": {
            "programming_language": {
                "type": "choice",
                "instructions": "Which programming language is this?",
                "criteria": sorted(programming_languages),
            },
        },
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
def _(message, model_picker, questions, router):
    result = router.predict(
        message.value,
        questions,
        model=None if model_picker.value == "auto" else model_picker.value,
    )
    return (result,)


@app.cell
def _(mo, question_groups, result):
    import html

    _CSS = """
    <style>
    .lm { font-size: 0.9rem; }
    .lm-route { opacity: 0.7; margin-bottom: 0.5rem; }
    .lm h3 { margin: 1.2rem 0 0.2rem; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.06em; opacity: 0.65; }
    .lm h3 .lm-flag { text-transform: none; letter-spacing: 0; margin-left: 0.5rem; color: #d97706; opacity: 1; }
    .lm-row { display: grid; grid-template-columns: minmax(0, 1.3fr) minmax(0, 1fr); gap: 0.2rem 1rem; align-items: center;
              padding: 0.4rem 0; border-bottom: 1px solid color-mix(in srgb, currentColor 10%, transparent); }
    .lm-q code { display: block; font-size: 0.72rem; opacity: 0.55; background: none; padding: 0; }
    .lm-line { display: flex; align-items: center; gap: 0.6rem; }
    .lm-meter { flex: 1; min-width: 4rem; height: 0.5rem; border-radius: 0.25rem; overflow: hidden;
                background: color-mix(in srgb, currentColor 12%, transparent); }
    .lm-fill { height: 100%; background: #3b82f6; }
    .lm-fill.lm-unsure { background: #f59e0b; }
    .lm-val { min-width: 10rem; white-space: nowrap; font-variant-numeric: tabular-nums; }
    .lm-chips { font-size: 0.72rem; opacity: 0.6; margin-top: 0.15rem; }
    .lm-chips span { margin-right: 0.6rem; }
    @media (max-width: 640px) { .lm-row { grid-template-columns: 1fr; } .lm-val { min-width: 0; } }
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


    def _row(key, question, body):
        return (
            f'<div class="lm-row"><div class="lm-q">{html.escape(question["instructions"])}'
            f"<code>{key}</code></div><div>{body}</div></div>"
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
    _body = "".join(_section(title, group) for title, group in question_groups.items())

    mo.vstack([
        mo.Html(f'{_CSS}<div class="lm">{_header}{_body}</div>'),
        mo.accordion({"Raw result": mo.json(result)}),
    ])
    return


@app.cell
def _(examples, mo, questions):
    import json

    labels = json.loads((mo.notebook_dir() / "labels.json").read_text())

    _unlabelled = sorted(set(examples) - set(labels))
    _orphaned = sorted(set(labels) - set(examples))
    _missing_keys = sorted(
        f"{name}:{key}" for name, truth in labels.items() for key in questions if key not in truth
    )
    _problems = [
        f"{title}: {', '.join(items)}"
        for title, items in [
            ("examples without labels", _unlabelled),
            ("labels without an example", _orphaned),
            ("labels missing a question", _missing_keys),
        ]
        if items
    ]
    mo.callout(mo.md("\n\n".join(_problems)), kind="warn") if _problems else mo.md(
        f"`labels.json`: {len(labels)} labelled examples, {len(questions)} questions each"
    )
    return json, labels


@app.cell
def _(json, laya, mo):
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
                result = router.predict(examples[name], questions, model=model)
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


    def eval_tables(rows, labels, questions):
        """Aggregate scored rows into report tables, one column per series.

        Each row needs a `series` (what to compare, e.g. a model or a model and run).
        """
        series = list(dict.fromkeys(r["series"] for r in rows))
        by_series = {s: [r for r in rows if r["series"] == s] for s in series}

        def rate(rs):
            return sum(r["hit"] for r in rs) / len(rs) if rs else None

        by_question = []
        for key, question in questions.items():
            truths = [t[key] for t in labels.values() if key in t]
            by_question.append({
                "question": key,
                "type": question["type"],
                "baseline": baseline_hit_rate(question, truths) if truths else None,
                **{s: rate([r for r in rs if r["question"] == key]) for s, rs in by_series.items()},
            })

        def beats(s):
            wins = [q for q in by_question if q[s] is not None and q["baseline"] is not None and q[s] > q["baseline"]]
            return f"{len(wins)} of {len(by_question)} questions"

        baselines = [q["baseline"] for q in by_question if q["baseline"] is not None]
        summary = [
            {
                "series": s,
                "hit rate": rate(rs),
                "baseline": sum(baselines) / len(baselines),
                "beats baseline": beats(s),
                "mean loss": round(sum(r["loss"] for r in rs) / len(rs), 3),
                "ms/example": round(sum(r.get("predict_ms") or 0 for r in rs) / len(rs)),
            }
            for s, rs in by_series.items()
        ]

        by_example = [
            {"example": name, **{s: rate([r for r in rs if r["example"] == name]) for s, rs in by_series.items()}}
            for name in labels
        ]

        misses = sorted((r for r in rows if not r["hit"]), key=lambda r: -r["loss"])
        misses = [
            {"series": r["series"], **{k: r[k] for k in ("example", "question", "predicted", "truth")}, "loss": round(r["loss"], 3)}
            for r in misses
        ]

        edges = [0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0001]
        calibration = []
        for s, rs in by_series.items():
            yes_no = [r for r in rs if r["type"] == "noul"]
            for lo, hi in zip(edges, edges[1:]):
                bucket = [r for r in yes_no if lo <= r["value"] < hi]
                if bucket:
                    calibration.append({
                        "series": s,
                        "p(yes) range": f"{lo:.1f}-{min(hi, 1):.1f}",
                        "n": len(bucket),
                        "mean p(yes)": sum(r["value"] for r in bucket) / len(bucket),
                        "actual yes": sum(bool(r["truth"]) for r in bucket) / len(bucket),
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
                        "coverage": len(kept) / len(scored),
                        "hit rate": rate(kept),
                    })

        return {
            "series": series,
            "summary": summary,
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

        percent = {
            c: pct
            for c in ["baseline", "hit rate", "coverage", "mean p(yes)", "actual yes", *tables["series"]]
        }

        def table(rows):
            return mo.ui.table(rows, selection=None, format_mapping=percent, page_size=25)

        return mo.vstack([
            table(tables["summary"]),
            mo.ui.tabs({
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
        render_eval_tables,
        write_jsonl,
    )


@app.cell
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
        mo.md("## Saved runs"),
        mo.hstack([saved_runs, rescan], justify="start", align="end"),
    ])
    return run_files, saved_runs


@app.cell
def _(
    eval_tables,
    json,
    labels,
    make_run_meta,
    mo,
    questions,
    render_eval_tables,
    run_files,
    saved_runs,
):
    mo.stop(not saved_runs.value, mo.md("*No saved runs to show yet.*"))

    saved_rows = []
    for _run_id in saved_runs.value:
        for _line in run_files[_run_id].read_text().splitlines():
            _row = json.loads(_line)
            _series = _row["model"] if len(saved_runs.value) == 1 else f"{_row['model']} {_run_id}"
            saved_rows.append({**_row, "series": _series})

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
        else mo.md(f"{len(saved_rows)} rows from {len(saved_runs.value)} run(s)"),
        render_eval_tables(eval_tables(saved_rows, labels, questions)),
    ])
    return


if __name__ == "__main__":
    app.run()
