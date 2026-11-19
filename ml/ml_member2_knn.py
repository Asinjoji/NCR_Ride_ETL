"""Member 2 ML: K-Nearest Neighbours for both tasks."""
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor

import ml_common as ml

MEMBER = 2
K_VALUES = [3, 5, 11, 21, 41, 81]


def tune_k(task, make_estimator, score):
    """Try each k on a validation part of the training sample.

    Returns (best k, list of (k, score)). A higher score is better.
    """
    X, y = ml.sample_train(task)
    stratify = y if task.name == "classification" else None
    X_fit, X_val, y_fit, y_val = train_test_split(
        X, y, test_size=0.25, random_state=ml.SEED, stratify=stratify)
    results = []
    for k in K_VALUES:
        model = ml.make_pipeline(task, make_estimator(k))
        model.fit(X_fit, y_fit)
        results.append((k, score(model, X_val, y_val)))
    best = max(results, key=lambda pair: pair[1])[0]
    return best, results


def auc_score(model, X, y):
    from sklearn.metrics import roc_auc_score
    return roc_auc_score(y, ml.get_scores(model, X))


def neg_mae(model, X, y):
    from sklearn.metrics import mean_absolute_error
    return -mean_absolute_error(y, model.predict(X))


def plot_k(clf_results, reg_results):
    fig, (left, right) = ml.plt.subplots(1, 2, figsize=(12, 4.5))
    ks = [str(k) for k, _ in clf_results]
    left.plot(ks, [s for _, s in clf_results], marker="o", color=ml.ec.BLUE)
    left.set_title("Classification: validation ROC-AUC")
    right.plot(ks, [-s for _, s in reg_results], marker="o",
               color=ml.ec.ORANGE)
    right.set_title("Regression: validation MAE (lower is better)")
    for ax in (left, right):
        ax.set_xlabel("k (number of neighbours)")
    return ml.save_fig(fig, "m2_choosing_k.png")


def main():
    tasks = ml.load_tasks()
    report = ml.Report(MEMBER, "K-Nearest Neighbours")
    ml.describe_tasks(report, tasks)
    clf, reg = tasks["classification"], tasks["regression"]
    rows = []

    best_c, clf_results = tune_k(
        clf, lambda k: KNeighborsClassifier(n_neighbors=k, n_jobs=-1),
        auc_score)
    best_r, reg_results = tune_k(
        reg, lambda k: KNeighborsRegressor(n_neighbors=k, n_jobs=-1),
        neg_mae)

    report.heading("2. Choosing k")
    report.bullet("KNN predicts by looking at the k most similar training "
                  "rides and voting (classification) or averaging "
                  "(regression). Too small a k follows noise; too large a "
                  "k blurs everything.")
    report.bullet(f"KNN is slow on large data, so it trains on a random "
                  f"sample of {ml.HEAVY_TRAIN_ROWS:,} rides and is tested "
                  f"on the full test set.")
    report.bullet(f"Best k on a validation set: {best_c} for "
                  f"classification, {best_r} for regression.")
    report.figure(plot_k(clf_results, reg_results), "Choosing k")

    X, y = ml.sample_train(clf)
    knn_c = ml.make_pipeline(
        clf, KNeighborsClassifier(n_neighbors=best_c, n_jobs=-1))
    secs = ml.fit_model(knn_c, X, y)
    scores = ml.classification_metrics(knn_c, clf)
    rows.append(ml.result_row(MEMBER, "KNN", clf, scores, len(X), secs,
                              f"k={best_c}"))
    base = ml.baseline(clf)
    report.heading("3. KNN classifier: will the customer cancel?")
    report.bullet(f"Test results: accuracy {scores['accuracy']:.3f} "
                  f"(baseline {base['accuracy']:.3f}), precision "
                  f"{scores['precision']:.3f}, recall {scores['recall']:.3f}, "
                  f"F1 {scores['f1']:.3f}, ROC-AUC {scores['roc_auc']:.3f}.")
    report.bullet(f"ROC-AUC {scores['roc_auc']:.2f} is "
                  f"{ml.auc_label(scores['roc_auc'])}. KNN has no "
                  f"class-weight option, so it rarely predicts the rare "
                  f"'cancelled' class; look at recall.")
    report.figure(ml.plot_confusion(knn_c, clf, f"KNN (k={best_c})",
                                    "m2_knn_confusion.png"),
                  "Confusion matrix")
    report.figure(ml.plot_roc({"KNN": knn_c}, clf, "KNN ROC curve",
                              "m2_knn_roc.png"), "ROC curve")

    X, y = ml.sample_train(reg)
    knn_r = ml.make_pipeline(
        reg, KNeighborsRegressor(n_neighbors=best_r, n_jobs=-1))
    secs = ml.fit_model(knn_r, X, y)
    scores = ml.regression_metrics(knn_r, reg)
    rows.append(ml.result_row(MEMBER, "KNN", reg, scores, len(X), secs,
                              f"k={best_r}"))
    base = ml.baseline(reg)
    report.heading("4. KNN regressor: predicting the fare")
    report.bullet(f"Test results: MAE {scores['mae']:,.0f} (baseline "
                  f"{base['mae']:,.0f}), RMSE {scores['rmse']:,.0f}, "
                  f"R-squared {scores['r2']:.3f}.")
    report.bullet(f"The inputs explain {ml.r2_label(scores['r2'])} of the "
                  f"variation in fare.")
    report.figure(ml.plot_pred_actual(knn_r, reg, f"KNN (k={best_r})",
                                      "m2_knn_pred_vs_actual.png"),
                  "Predicted vs actual fare")

    ml.save_results(MEMBER, rows)
    report.write([
        "How did the value of k change the score, and why did you pick "
        "the best one?",
        "Does KNN predict cancellations better than guessing? Look at ROC-AUC "
        "and recall.",
        "What are the weaknesses of KNN on a large dataset like this one?",
    ])


if __name__ == "__main__":
    main()
