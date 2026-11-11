"""Shared helpers for the model-training scripts. The lead adds this file.

Two prediction tasks are built from the cleaned ride data:
  classification - will the customer cancel? (cancelled = 1, completed = 0)
  regression     - what fare will a completed ride cost?
Only information known before the ride finishes is used as input.
"""
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score,
                             mean_absolute_error, mean_squared_error,
                             precision_score, r2_score, recall_score,
                             roc_auc_score, roc_curve)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "eda"))
import eda_common as ec  # noqa: E402
from eda_common import plt  # noqa: E402

OUT_DIR = ROOT / "ml_outputs"
FIG_DIR = OUT_DIR / "figures"
RES_DIR = OUT_DIR / "results"
SEED = 42
TEST_SIZE = 0.2
HEAVY_TRAIN_ROWS = 15000  # KNN and SVM are slow, so they train on a sample

CLF_CAT = ["x_vehicle", "x_time_of_day"]
CLF_NUM = ["x_vtat", "x_hour", "x_month", "x_is_weekend"]
REG_CAT = ["x_vehicle", "x_time_of_day"]
REG_NUM = ["x_distance", "x_hour", "x_month", "x_is_weekend"]
CLASS_NAMES = ["Completed", "Customer cancelled"]


@dataclass
class Task:
    """One prediction task with its fixed train/test split."""

    name: str
    target: str
    X_train: pd.DataFrame
    X_test: pd.DataFrame
    y_train: pd.Series
    y_test: pd.Series
    cat: list
    num: list


def _split(X, y, name, target, cat, num, stratify):
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=SEED,
        stratify=y if stratify else None)
    return Task(name, target, X_tr, X_te, y_tr, y_te, cat, num)


def load_tasks():
    """Build both tasks from the cleaned data. Same split for every model."""
    df, _ = ec.prepare(ec.load_clean())
    df["x_is_weekend"] = df["x_is_weekend"].astype(int)

    cols = CLF_CAT + CLF_NUM
    keep = df["x_outcome"].isin(["Completed", "Cancelled by Customer"])
    sub = df[keep].dropna(subset=cols)
    target = (sub["x_outcome"] == "Cancelled by Customer").astype(int)
    clf = _split(sub[cols], target, "classification",
                 "customer cancels the booking (1) or completes (0)",
                 CLF_CAT, CLF_NUM, True)

    cols = REG_CAT + REG_NUM
    sub = ec.completed(df).dropna(subset=cols + ["x_value"])
    reg = _split(sub[cols], sub["x_value"], "regression",
                 "fare (booking value) of a completed ride",
                 REG_CAT, REG_NUM, False)
    for task in (clf, reg):
        if len(task.X_train) < 1000:
            sys.exit(f"Too few rows for the {task.name} task. Check data.")
    return {"classification": clf, "regression": reg}


def make_pipeline(task, estimator, scale=True):
    """Scale numbers, one-hot the labels, then apply the estimator."""
    prep = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False),
         task.cat),
        ("num", StandardScaler() if scale else "passthrough", task.num),
    ])
    return Pipeline([("prep", prep), ("model", estimator)])


def sample_train(task, rows=HEAVY_TRAIN_ROWS):
    """A reproducible training sample for the slow models (KNN, SVM)."""
    if len(task.X_train) <= rows:
        return task.X_train, task.y_train
    X, _, y, _ = train_test_split(
        task.X_train, task.y_train, train_size=rows, random_state=SEED,
        stratify=task.y_train if task.name == "classification" else None)
    return X, y


def fit_model(model, X, y):
    """Fit and return the seconds it took."""
    start = time.time()
    model.fit(X, y)
    return time.time() - start


def get_scores(model, X):
    """Probability of the positive class (or the SVM decision score)."""
    if hasattr(model, "predict_proba"):
        return model.predict_proba(X)[:, 1]
    return model.decision_function(X)


def classification_metrics(model, task):
    """Accuracy, precision, recall, F1 and ROC-AUC on the test set."""
    y = task.y_test
    pred = model.predict(task.X_test)
    return {
        "accuracy": accuracy_score(y, pred),
        "precision": precision_score(y, pred, zero_division=0),
        "recall": recall_score(y, pred, zero_division=0),
        "f1": f1_score(y, pred, zero_division=0),
        "roc_auc": roc_auc_score(y, get_scores(model, task.X_test)),
    }


def regression_metrics(model, task):
    """MAE, RMSE and R-squared on the test set."""
    y = task.y_test
    pred = model.predict(task.X_test)
    return {
        "mae": mean_absolute_error(y, pred),
        "rmse": mean_squared_error(y, pred) ** 0.5,
        "r2": r2_score(y, pred),
    }


def baseline(task):
    """What a model that learns nothing would score."""
    if task.name == "classification":
        return {"accuracy": 1 - float(task.y_test.mean()), "f1": 0.0,
                "roc_auc": 0.5}
    guess = float(task.y_train.mean())
    return {"mae": float(np.abs(task.y_test - guess).mean()),
            "rmse": float(((task.y_test - guess) ** 2).mean() ** 0.5),
            "r2": 0.0}


def auc_label(auc):
    """Plain-English meaning of a ROC-AUC value."""
    if auc < 0.55:
        return "no better than guessing"
    if auc < 0.65:
        return "weak"
    if auc < 0.8:
        return "moderate"
    return "strong"


def r2_label(r2):
    """Plain-English meaning of an R-squared value."""
    if r2 < 0.05:
        return "almost nothing"
    if r2 < 0.3:
        return "a small part"
    if r2 < 0.6:
        return "a moderate part"
    return "most"


def result_row(member, algorithm, task, metrics, train_rows, seconds,
               note=""):
    """One line of the results table for a trained model."""
    row = {"member": member, "algorithm": algorithm, "task": task.name,
           "train_rows": int(train_rows), "test_rows": len(task.X_test),
           "seconds": round(seconds, 1), "note": note}
    row.update({k: round(float(v), 4) for k, v in metrics.items()})
    return row


def save_results(member, rows):
    """Save this member's results so the lead can compare all models."""
    RES_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(RES_DIR / f"member{member}_results.csv",
                              index=False)


def save_fig(fig, name):
    """Save a figure in ml_outputs/figures and return its link."""
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(FIG_DIR / name, dpi=130, facecolor="white")
    plt.close(fig)
    print(f"  saved ml_outputs/figures/{name}")
    return f"figures/{name}"


def feature_names(model):
    """Readable names of the columns the estimator sees."""
    raw = model.named_steps["prep"].get_feature_names_out()
    return [n.split("__", 1)[-1].replace("x_", "") for n in raw]


def plot_confusion(model, task, title, name):
    cm = confusion_matrix(task.y_test, model.predict(task.X_test))
    fig, ax = plt.subplots(figsize=(5.5, 5))
    ax.imshow(cm, cmap="Blues")
    ax.set_xticks([0, 1], CLASS_NAMES)
    ax.set_yticks([0, 1], CLASS_NAMES, rotation=90, va="center")
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    for i in range(2):
        for j in range(2):
            color = "white" if cm[i, j] > cm.max() / 2 else "black"
            ax.text(j, i, f"{cm[i, j]:,}", ha="center", va="center",
                    color=color, fontsize=12)
    ax.set_title(title, fontweight="bold")
    return save_fig(fig, name)


def plot_roc(models, task, title, name):
    """ROC curves for {label: fitted model}."""
    fig, ax = plt.subplots(figsize=(6, 5.5))
    for label, model in models.items():
        fpr, tpr, _ = roc_curve(task.y_test, get_scores(model, task.X_test))
        auc = roc_auc_score(task.y_test, get_scores(model, task.X_test))
        ax.plot(fpr, tpr, label=f"{label} (AUC {auc:.2f})")
    ax.plot([0, 1], [0, 1], "--", color="grey", label="Guessing")
    ax.set_xlabel("False positive rate")
    ax.set_ylabel("True positive rate")
    ax.set_title(title, fontweight="bold")
    ax.legend(loc="lower right")
    return save_fig(fig, name)


def plot_pred_actual(model, task, title, name):
    """Predicted vs actual fare, and the residual histogram."""
    pred = model.predict(task.X_test)
    actual = task.y_test.to_numpy()
    pick = np.random.RandomState(SEED).choice(
        len(actual), min(3000, len(actual)), replace=False)
    fig, (left, right) = plt.subplots(1, 2, figsize=(12, 5))
    left.scatter(actual[pick], pred[pick], s=6, alpha=0.3, color=ec.BLUE)
    top = max(actual.max(), pred.max())
    left.plot([0, top], [0, top], "--", color="grey")
    left.set_xlabel("Actual fare")
    left.set_ylabel("Predicted fare")
    left.set_title("Predicted vs actual (3,000 test rides)")
    right.hist(actual - pred, bins=40, color=ec.ORANGE, edgecolor="white")
    right.set_xlabel("Actual minus predicted fare")
    right.set_title("Residuals")
    fig.suptitle(title, fontweight="bold")
    return save_fig(fig, name)


def plot_importance(names, values, title, name, top=12, signed=False):
    """Horizontal bars of the largest values (coefficients or importances)."""
    order = np.argsort(np.abs(values))[::-1][:top]
    labels = [names[i] for i in order]
    vals = np.asarray(values)[order]
    fig, ax = plt.subplots(figsize=(8, 5.5))
    colors = [ec.BLUE if v >= 0 or not signed else ec.ORANGE for v in vals]
    ax.barh(labels, vals, color=colors)
    ax.invert_yaxis()
    ax.set_title(title, fontweight="bold")
    ax.set_xlabel("Coefficient" if signed else "Importance")
    return save_fig(fig, name)


class Report(ec.Findings):
    """Same as the EDA findings file, but saved in ml_outputs/."""

    def write(self, prompts):
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        path = OUT_DIR / f"member{self.member}_findings.md"
        path.write_text("\n".join(self.lines) + "\n", encoding="utf-8")
        note = OUT_DIR / f"member{self.member}_interpretation.md"
        if not note.exists():
            body = [f"## Member {self.member}: my interpretation", "",
                    "(Replace each prompt with 1-2 sentences in your own "
                    "words, using the numbers and charts above.)", ""]
            body += [f"- {p}" for p in prompts]
            note.write_text("\n".join(body) + "\n", encoding="utf-8")
        print(f"  wrote {path.relative_to(ROOT)}")


def describe_tasks(report, tasks):
    """Add the task and data description to a findings file."""
    report.heading("1. The two prediction tasks")
    for task in tasks.values():
        total = len(task.X_train) + len(task.X_test)
        report.bullet(f"{task.name.title()}: predict the {task.target}. "
                      f"{total:,} rows ({len(task.X_train):,} train, "
                      f"{len(task.X_test):,} test).")
        report.bullet("Inputs: " + ", ".join(
            c.replace("x_", "") for c in task.cat + task.num) + ".")
    base = baseline(tasks["classification"])
    rate = 100 * float(tasks["classification"].y_test.mean())
    report.bullet(f"Only {rate:.1f}% of rides in the classification task "
                  f"are customer cancellations, so accuracy alone is "
                  f"misleading (always guessing 'completed' scores "
                  f"{100 * base['accuracy']:.1f}%). ROC-AUC and F1 are "
                  f"the fairer scores.")
    reg_base = baseline(tasks["regression"])
    report.bullet(f"Regression baseline (always predict the average fare): "
                  f"MAE {reg_base['mae']:,.0f}, R-squared 0.")
