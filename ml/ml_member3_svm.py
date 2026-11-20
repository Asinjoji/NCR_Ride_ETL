"""Member 3 ML: Support Vector Machines for both tasks."""
import pandas as pd
from sklearn.compose import TransformedTargetRegressor
from sklearn.metrics import mean_absolute_error, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC, SVR

import ml_common as ml

MEMBER = 3
TUNE_ROWS = 5000
CANDIDATES = [("linear", 1.0), ("rbf", 1.0), ("rbf", 10.0)]


def make_svm(task, kernel, c):
    if task.name == "classification":
        return ml.make_pipeline(
            task, SVC(kernel=kernel, C=c, class_weight="balanced"))
    wrapped = TransformedTargetRegressor(
        regressor=SVR(kernel=kernel, C=c), transformer=StandardScaler())
    return ml.make_pipeline(task, wrapped)


def validation_score(task, model, X, y):
    if task.name == "classification":
        return roc_auc_score(y, ml.get_scores(model, X))
    return -mean_absolute_error(y, model.predict(X))


def tune(task):
    """Compare kernels and C on a small sample. Returns (best, table)."""
    X, y = ml.sample_train(task, TUNE_ROWS)
    stratify = y if task.name == "classification" else None
    X_fit, X_val, y_fit, y_val = train_test_split(
        X, y, test_size=0.25, random_state=ml.SEED, stratify=stratify)
    table = []
    for kernel, c in CANDIDATES:
        model = make_svm(task, kernel, c)
        secs = ml.fit_model(model, X_fit, y_fit)
        score = validation_score(task, model, X_val, y_val)
        table.append({"kernel": kernel, "C": c,
                      "validation score": round(score, 4),
                      "seconds": round(secs, 1)})
    best = max(table, key=lambda row: row["validation score"])
    return best, pd.DataFrame(table).set_index("kernel")


def main():
    tasks = ml.load_tasks()
    report = ml.Report(MEMBER, "Support Vector Machine")
    ml.describe_tasks(report, tasks)
    clf, reg = tasks["classification"], tasks["regression"]
    rows = []

    report.heading("2. How an SVM works and how it was tuned")
    report.bullet("An SVM looks for the boundary (classification) or curve "
                  "(regression) that separates or follows the data with the "
                  "widest safe margin. The 'rbf' kernel allows curved "
                  "boundaries; 'linear' allows only straight ones. C sets "
                  "how strictly mistakes are punished.")
    report.bullet(f"SVMs are very slow on large data, so the final model "
                  f"trains on {ml.HEAVY_TRAIN_ROWS:,} random rides and the "
                  f"settings were compared on {TUNE_ROWS:,} rides. Scores "
                  f"are on the full test set. The classification tuning "
                  f"score is ROC-AUC; the regression score is negative MAE.")

    best, table = tune(clf)
    report.bullet("Classification tuning (higher is better):")
    report.table(table)
    X, y = ml.sample_train(clf)
    svc = make_svm(clf, best["kernel"],
                   best["C"])
    secs = ml.fit_model(svc, X, y)
    scores = ml.classification_metrics(svc, clf)
    note = f"kernel={svc.named_steps['model'].kernel}, C={best['C']}"
    rows.append(ml.result_row(MEMBER, "SVM", clf, scores, len(X), secs,
                              note))
    base = ml.baseline(clf)
    report.heading("3. SVM classifier: will the customer cancel?")
    report.bullet(f"Chosen settings: {note}.")
    report.bullet(f"Test results: accuracy {scores['accuracy']:.3f} "
                  f"(baseline {base['accuracy']:.3f}), precision "
                  f"{scores['precision']:.3f}, recall {scores['recall']:.3f}, "
                  f"F1 {scores['f1']:.3f}, ROC-AUC {scores['roc_auc']:.3f}.")
    report.bullet(f"ROC-AUC {scores['roc_auc']:.2f} is "
                  f"{ml.auc_label(scores['roc_auc'])}.")
    report.figure(ml.plot_confusion(svc, clf, "SVM",
                                    "m3_svm_confusion.png"),
                  "Confusion matrix")
    report.figure(ml.plot_roc({"SVM": svc}, clf, "SVM ROC curve",
                              "m3_svm_roc.png"), "ROC curve")

    best, table = tune(reg)
    X, y = ml.sample_train(reg)
    svr = make_svm(reg, best["kernel"],
                   best["C"])
    secs = ml.fit_model(svr, X, y)
    scores = ml.regression_metrics(svr, reg)
    kernel = svr.named_steps["model"].regressor_.kernel
    note = f"kernel={kernel}, C={best['C']}"
    rows.append(ml.result_row(MEMBER, "SVM", reg, scores, len(X), secs,
                              note))
    base = ml.baseline(reg)
    report.heading("4. SVR: predicting the fare")
    report.bullet("Regression tuning (higher is better, score is negative "
                  "MAE):")
    report.table(table)
    report.bullet(f"Chosen settings: {note}.")
    report.bullet(f"Test results: MAE {scores['mae']:,.0f} (baseline "
                  f"{base['mae']:,.0f}), RMSE {scores['rmse']:,.0f}, "
                  f"R-squared {scores['r2']:.3f}.")
    report.bullet(f"The inputs explain {ml.r2_label(scores['r2'])} of the "
                  f"variation in fare.")
    report.figure(ml.plot_pred_actual(svr, reg, "SVR",
                                      "m3_svr_pred_vs_actual.png"),
                  "Predicted vs actual fare")

    ml.save_results(MEMBER, rows)
    report.write([
        "Which kernel and C worked best, and what does that say about the "
        "shape of the data?",
        "How does the SVM compare with guessing for cancellations and for "
        "fares?",
        "Why can an SVM not be trained on all 100,000+ rides here?",
    ])


if __name__ == "__main__":
    main()
