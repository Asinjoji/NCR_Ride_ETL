"""Lead only: run every member's ML script, compare models, build the report.

Usage:  python ml/run_all_ml.py            (runs scripts, then the report)
        python ml/run_all_ml.py --report   (only rebuild comparison + report)
"""
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

import ml_common as ml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPORT = ROOT / "docs" / "ML_report.md"
PLT = ml.plt


def run_scripts():
    for script in sorted(HERE.glob("ml_member*.py")):
        print(f"\n=== {script.name}")
        subprocess.run([sys.executable, str(script)], check=True,
                       cwd=str(ROOT))


def load_results():
    files = sorted(ml.RES_DIR.glob("member*_results.csv"))
    if not files:
        sys.exit("No results found. Run the member scripts first.")
    return pd.concat([pd.read_csv(f) for f in files], ignore_index=True)


def compare_chart(table, task, metrics, base, name, title):
    """Bars of one task's metrics for every algorithm."""
    data = table[table["task"] == task].set_index("algorithm")
    fig, axes = PLT.subplots(1, len(metrics), figsize=(6 * len(metrics), 5))
    for ax, (col, label, line) in zip(np.atleast_1d(axes), metrics):
        values = data[col]
        bars = ax.bar(values.index, values.values, color=ml.ec.BLUE)
        ax.bar_label(bars, labels=[f"{v:.3f}" for v in values.values],
                     fontsize=8)
        if line is not None:
            ax.axhline(line, color=ml.ec.ORANGE, linestyle="--",
                       label=f"Baseline {line:,.3f}")
            ax.legend()
        ax.set_title(label)
        PLT.setp(ax.get_xticklabels(), rotation=30, ha="right")
    fig.suptitle(title, fontweight="bold")
    return ml.save_fig(fig, name)


def build_comparison():
    table = load_results()
    ml.OUT_DIR.mkdir(parents=True, exist_ok=True)
    table.to_csv(ml.OUT_DIR / "model_comparison.csv", index=False)
    tasks = ml.load_tasks()
    clf_base = ml.baseline(tasks["classification"])
    reg_base = ml.baseline(tasks["regression"])
    links = {}
    if (table["task"] == "classification").any():
        links["classification"] = compare_chart(
            table, "classification",
            [("roc_auc", "ROC-AUC (higher is better)", 0.5),
             ("f1", "F1 score (higher is better)", None)],
            clf_base, "all_classification_comparison.png",
            "Will the customer cancel? All models")
    if (table["task"] == "regression").any():
        links["regression"] = compare_chart(
            table, "regression",
            [("r2", "R-squared (higher is better)", 0.0),
             ("mae", "MAE (lower is better)", reg_base["mae"])],
            reg_base, "all_regression_comparison.png",
            "What is the fare? All models")
    return table, links, clf_base, reg_base


def drop_task_section(text):
    """Remove the repeated 'prediction tasks' section (see report part 1)."""
    start = text.find("## 1. The two prediction tasks")
    if start < 0:
        return text
    end = text.find("\n## ", start + 5)
    return text[:start] + (text[end + 1:] if end >= 0 else "")


def demote(text):
    """Make every heading one level smaller so the report nests properly."""
    return "\n".join("#" + line if line.startswith("#") else line
                     for line in text.split("\n"))


def md_table(df):
    df = df.fillna("")
    cols = [str(c) for c in df.columns]
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for row in df.itertuples(index=False):
        lines.append("| " + " | ".join(
            f"{v:,.3f}" if isinstance(v, float) else str(v)
            for v in row) + " |")
    return "\n".join(lines)


def best_lines(table):
    lines = []
    clf = table[table["task"] == "classification"]
    if len(clf):
        top = clf.sort_values("roc_auc", ascending=False).iloc[0]
        lines.append(f"- Best classifier by ROC-AUC: **{top['algorithm']}** "
                     f"({top['roc_auc']:.3f}, {ml.auc_label(top['roc_auc'])}"
                     f"). Its F1 is {top['f1']:.3f} and recall "
                     f"{top['recall']:.3f}.")
    reg = table[table["task"] == "regression"]
    if len(reg):
        top = reg.sort_values("r2", ascending=False).iloc[0]
        lines.append(f"- Best regressor by R-squared: "
                     f"**{top['algorithm']}** (R-squared {top['r2']:.3f}, "
                     f"MAE {top['mae']:,.0f}).")
    return lines


def build_report(table, links, clf_base, reg_base):
    tasks = ml.load_tasks()
    parts = ["# Machine Learning: NCR Ride Bookings", "",
             "## 1. Problem setup", "",
             "Six algorithms were trained on the cleaned ride data: Linear "
             "Regression, Logistic Regression, KNN, SVM, Decision Tree and "
             "Random Forest. Every model uses the same train/test split "
             "(80/20, random seed 42), so the scores can be compared.", ""]
    for task in tasks.values():
        total = len(task.X_train) + len(task.X_test)
        inputs = ", ".join(c.replace("x_", "") for c in task.cat + task.num)
        parts.append(f"- **{task.name.title()}**: predict the "
                     f"{task.target}. {total:,} rides. Inputs: {inputs}.")
    parts += [f"- Classification baseline: always guessing 'completed' "
              f"scores {100 * clf_base['accuracy']:.1f}% accuracy, F1 0 and "
              f"ROC-AUC 0.5. Regression baseline: always predicting the "
              f"average fare gives MAE {reg_base['mae']:,.0f}, R-squared 0.",
              "- Only information known before the ride finishes is used, "
              "so the models cannot cheat with results such as fare, rating "
              "or payment method.", "",
              "## 2. Model comparison", ""]
    parts += best_lines(table) + [""]
    cols = ["algorithm", "task", "train_rows", "seconds", "note"]
    for task, metrics in [("classification", ["accuracy", "precision",
                                              "recall", "f1", "roc_auc"]),
                          ("regression", ["mae", "rmse", "r2"])]:
        data = table[table["task"] == task]
        if len(data):
            parts += [f"### {task.title()} results", "",
                      md_table(data[cols[:1] + metrics + cols[2:]]), ""]
            if task in links:
                parts += [f"![{task} comparison]({links[task]})", ""]
    for number in range(1, 5):
        for kind in ("findings", "interpretation"):
            path = ml.OUT_DIR / f"member{number}_{kind}.md"
            if path.exists():
                text = path.read_text(encoding="utf-8")
                parts += [demote(drop_task_section(text)), ""]
    note = ml.OUT_DIR / "team_conclusion.md"
    if not note.exists():
        note.write_text(
            "## Team conclusion\n\n(Lead: replace each line with 1-2 "
            "sentences.)\n\n- Which model is best for each task, and is it "
            "good enough to use?\n- What do the models tell us about "
            "cancellations and fares?\n- What are the limits of this "
            "analysis, and what would you try next?\n", encoding="utf-8")
    parts.append(note.read_text(encoding="utf-8"))
    text = "\n".join(parts).replace("](figures/", "](../ml_outputs/figures/")
    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_text(text, encoding="utf-8")
    print(f"\nReport written to {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    if "--report" not in sys.argv:
        run_scripts()
    results = build_comparison()
    build_report(*results)
