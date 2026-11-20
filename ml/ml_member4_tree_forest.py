"""Member 4 ML: Decision Tree and Random Forest for both tasks."""
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import r2_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.tree import (DecisionTreeClassifier, DecisionTreeRegressor,
                          plot_tree)

import ml_common as ml

MEMBER = 4
DEPTHS = [3, 5, 8, 12, 16]
LEAF = 20


def make_tree(task, depth):
    if task.name == "classification":
        est = DecisionTreeClassifier(
            max_depth=depth, min_samples_leaf=LEAF,
            class_weight="balanced", random_state=ml.SEED)
    else:
        est = DecisionTreeRegressor(
            max_depth=depth, min_samples_leaf=LEAF, random_state=ml.SEED)
    return ml.make_pipeline(task, est)


def make_forest(task):
    if task.name == "classification":
        est = RandomForestClassifier(
            n_estimators=100, max_depth=12, min_samples_leaf=LEAF,
            class_weight="balanced_subsample", n_jobs=-1,
            random_state=ml.SEED)
    else:
        est = RandomForestRegressor(
            n_estimators=100, max_depth=12, min_samples_leaf=LEAF,
            n_jobs=-1, random_state=ml.SEED)
    return ml.make_pipeline(task, est)


def tune_depth(task):
    """Score each depth on a validation part of the training data."""
    stratify = task.y_train if task.name == "classification" else None
    X_fit, X_val, y_fit, y_val = train_test_split(
        task.X_train, task.y_train, test_size=0.25, random_state=ml.SEED,
        stratify=stratify)
    results = []
    for depth in DEPTHS:
        model = make_tree(task, depth).fit(X_fit, y_fit)
        if task.name == "classification":
            score = roc_auc_score(y_val, ml.get_scores(model, X_val))
        else:
            score = r2_score(y_val, model.predict(X_val))
        results.append((depth, score))
    best = max(results, key=lambda pair: pair[1])[0]
    return best, results


def plot_depths(clf_results, reg_results):
    fig, (left, right) = ml.plt.subplots(1, 2, figsize=(12, 4.5))
    for ax, results, title in [
            (left, clf_results, "Classification: validation ROC-AUC"),
            (right, reg_results, "Regression: validation R-squared")]:
        ax.plot([str(d) for d, _ in results], [s for _, s in results],
                marker="o", color=ml.ec.BLUE)
        ax.set_title(title)
        ax.set_xlabel("max_depth")
    return ml.save_fig(fig, "m4_tree_depth.png")


def plot_small_tree(task):
    """A depth-3 tree in real units (minutes, hours) so it is readable."""
    est = DecisionTreeClassifier(max_depth=3, min_samples_leaf=LEAF,
                                 random_state=ml.SEED)
    model = ml.make_pipeline(task, est, scale=False)
    model.fit(task.X_train, task.y_train)
    fig, ax = ml.plt.subplots(figsize=(16, 7))
    names = ml.feature_names(model)
    plot_tree(model.named_steps["model"], feature_names=names,
              class_names=ml.CLASS_NAMES, filled=True, rounded=True,
              fontsize=7, ax=ax)
    ax.set_title("Decision Tree (depth 3) for cancellations",
                 fontweight="bold")
    return ml.save_fig(fig, "m4_tree_diagram.png")


def evaluate(task, model, algorithm, note, rows):
    secs = ml.fit_model(model, task.X_train, task.y_train)
    if task.name == "classification":
        scores = ml.classification_metrics(model, task)
    else:
        scores = ml.regression_metrics(model, task)
    rows.append(ml.result_row(MEMBER, algorithm, task, scores,
                              len(task.X_train), secs, note))
    return scores


def describe(report, task, algorithm, scores):
    base = ml.baseline(task)
    if task.name == "classification":
        report.bullet(
            f"{algorithm} test results: accuracy {scores['accuracy']:.3f} "
            f"(baseline {base['accuracy']:.3f}), precision "
            f"{scores['precision']:.3f}, recall {scores['recall']:.3f}, F1 "
            f"{scores['f1']:.3f}, ROC-AUC {scores['roc_auc']:.3f} "
            f"({ml.auc_label(scores['roc_auc'])}).")
    else:
        report.bullet(
            f"{algorithm} test results: MAE {scores['mae']:,.0f} (baseline "
            f"{base['mae']:,.0f}), RMSE {scores['rmse']:,.0f}, R-squared "
            f"{scores['r2']:.3f} (explains "
            f"{ml.r2_label(scores['r2'])} of the variation).")


def main():
    tasks = ml.load_tasks()
    report = ml.Report(MEMBER, "Decision Tree and Random Forest")
    ml.describe_tasks(report, tasks)
    clf, reg = tasks["classification"], tasks["regression"]
    rows = []

    best_c, clf_depths = tune_depth(clf)
    best_r, reg_depths = tune_depth(reg)
    report.heading("2. Decision Tree")
    report.bullet("A decision tree asks a series of yes/no questions about "
                  "the inputs and ends in a prediction. A deeper tree can "
                  "fit more detail but starts memorising noise.")
    report.bullet(f"Best max_depth on a validation set: {best_c} for "
                  f"classification, {best_r} for regression (every leaf "
                  f"holds at least {LEAF} rides).")
    report.figure(plot_depths(clf_depths, reg_depths), "Choosing the depth")

    tree_c = make_tree(clf, best_c)
    scores = evaluate(clf, tree_c, "Decision Tree", f"max_depth={best_c}",
                      rows)
    report.heading("3. Decision Tree: will the customer cancel?")
    describe(report, clf, "Decision Tree", scores)
    imp = tree_c.named_steps["model"].feature_importances_
    names = ml.feature_names(tree_c)
    report.bullet(f"Most important input: {names[int(imp.argmax())]}.")
    report.figure(ml.plot_importance(
        names, imp, "Decision Tree feature importance",
        "m4_tree_importance.png"), "Feature importance")
    report.figure(plot_small_tree(clf), "Small decision tree")

    tree_r = make_tree(reg, best_r)
    scores = evaluate(reg, tree_r, "Decision Tree", f"max_depth={best_r}",
                      rows)
    report.heading("4. Decision Tree: predicting the fare")
    describe(report, reg, "Decision Tree", scores)

    forest_c = make_forest(clf)
    scores = evaluate(clf, forest_c, "Random Forest",
                      "100 trees, max_depth=12", rows)
    report.heading("5. Random Forest: will the customer cancel?")
    report.bullet("A random forest trains many different trees on random "
                  "parts of the data and averages their answers, which is "
                  "usually steadier than one tree.")
    describe(report, clf, "Random Forest", scores)
    imp = forest_c.named_steps["model"].feature_importances_
    names = ml.feature_names(forest_c)
    report.bullet(f"Most important input: {names[int(imp.argmax())]}.")
    report.figure(ml.plot_importance(
        names, imp, "Random Forest feature importance",
        "m4_forest_importance.png"), "Feature importance")
    report.figure(ml.plot_confusion(forest_c, clf, "Random Forest",
                                    "m4_forest_confusion.png"),
                  "Confusion matrix")
    report.figure(ml.plot_roc(
        {"Decision Tree": tree_c, "Random Forest": forest_c}, clf,
        "Tree vs forest ROC curves", "m4_tree_forest_roc.png"), "ROC curves")

    forest_r = make_forest(reg)
    scores = evaluate(reg, forest_r, "Random Forest",
                      "100 trees, max_depth=12", rows)
    report.heading("6. Random Forest: predicting the fare")
    describe(report, reg, "Random Forest", scores)
    imp = forest_r.named_steps["model"].feature_importances_
    names = ml.feature_names(forest_r)
    report.bullet(f"Most important input: {names[int(imp.argmax())]}.")
    report.figure(ml.plot_importance(
        names, imp, "Random Forest feature importance (fare)",
        "m4_forest_fare_importance.png"), "Feature importance (fare)")
    report.figure(ml.plot_pred_actual(forest_r, reg, "Random Forest",
                                      "m4_forest_pred_vs_actual.png"),
                  "Predicted vs actual fare")

    ml.save_results(MEMBER, rows)
    report.write([
        "Which input matters most for cancellations and for fares, and "
        "does that match what you saw in the EDA?",
        "Is the random forest better than a single tree? Why might it be?",
        "How did you choose max_depth, and what happens if a tree is too "
        "deep?",
    ])


if __name__ == "__main__":
    main()
