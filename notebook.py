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
def _():
    # questions = {
    #     "department": {
    #         "type": "choice",
    #         "instructions": "Which department should handle this?",
    #         "criteria": {
    #             "billing": "invoices, payments, refunds",
    #             "technical": "bugs, outages, system errors",
    #             "other": "everything else",
    #         },
    #     },
    #     "urgency": {
    #         "type": "score",
    #         "instructions": "How urgent is this?",
    #         "criteria": ["not urgent", "soon", "blocking"],
    #     },
    #     "churn_risk": {
    #         "type": "noul",
    #         "instructions": "Does the user threaten to cancel or leave?",
    #     },
    # }
    return


@app.cell
def _():
    programming_languages = set(["C", "Python", "Rust", "C++", "C#", "Perl", "JavaScript", "Zig", "Julia", "ASM", "Clojure", "Lisp", "Haskell", "F#", "R", "Fortran", "ALGOL", "COBOL", "Smalltalk", "Verilog", "Objective-C", "Swift", "BASIC", "Visual Basic", "Erlang", "Bash", "OCaml", "GDScript", "Java", "Scratch", "Nix", "Scala", "Kotlin", "Lean", "other"])
    return (programming_languages,)


@app.cell
def _(programming_languages):
    questions = {
        "programming_language": {
            "type": "choice",
            "instructions": "Which programming language is this?",
            "criteria": list(programming_languages),
        },
    }
    return (questions,)


@app.cell
def _(mo):
    message = mo.ui.text_area(
        value="""
    import marimo as mo
    import laya
    """,
        label="Message",
        full_width=True,
    )
    message
    return (message,)


@app.cell
def _(message, questions, router):
    result = router.predict(message.value, questions)
    result
    return (result,)


@app.cell
def _(mo, result):
    def _summarize(a):
        if a["type"] == "choice":
            return a["choice"], a.get("confidence")
        if a["type"] == "score":
            return round(a["score"], 2), a.get("confidence")
        return round(a["noul"], 3), a.get("confidence")


    summary = [
        {"question": k, "answer": _summarize(v)[0], "confidence": _summarize(v)[1]}
        for k, v in result["answers"].items()
    ]
    mo.vstack([
        mo.md(f"Routed to **{result['routing']['model']}** ({result['routing']['reason']})"),
        mo.ui.table(summary, selection=None),
    ])
    return


if __name__ == "__main__":
    app.run()
