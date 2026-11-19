"""Member 1 ML: Linear Regression (fare) and Logistic Regression (cancel)."""
import numpy as np
from sklearn.linear_model import LinearRegression, LogisticRegression

import ml_common as ml

MEMBER = 1


def main():
    tasks = ml.load_tasks()
    report = ml.Report(MEMBER, "Linear and Logistic Regression")
    ml.describe_tasks(report, tasks)
    rows = []

    reg = tasks["regression"]
    linear = ml.make_pipeline(reg, LinearRegression())
    secs = ml.fit_model(linear, reg.X_train, reg.y_train)
    scores = ml.regression_metrics(linear, reg)
    rows.append(ml.result_row(MEMBER, "Linear Regression", reg, scores,
                              len(reg.X_train), secs))
    base = ml.baseline(reg)

    report.heading("2. Linear Regression: predicting the fare")
    report.bullet("Linear Regression fits one straight-line formula: fare = "
                  "intercept + a sum of (coefficient x input).")
    report.bullet(f"Test results: MAE {scores['mae']:,.0f}, RMSE "
                  f"{scores['rmse']:,.0f}, R-squared {scores['r2']:.3f}.")
    report.bullet(f"The baseline MAE is {base['mae']:,.0f}, so the model "
                  f"improves it by {base['mae'] - scores['mae']:,.0f}.")
    report.bullet(f"R-squared {scores['r2']:.3f} means the inputs explain "
                  f"{ml.r2_label(scores['r2'])} of the variation in fare.")
    names = ml.feature_names(linear)
    coefs = linear.named_steps["model"].coef_
    link = ml.plot_importance(names, coefs, "Linear Regression coefficients",
                              "m1_linear_coefficients.png", signed=True)
    report.figure(link, "Linear regression coefficients")
    top = int(np.argmax(np.abs(coefs)))
    report.bullet(f"Largest coefficient: {names[top]} ({coefs[top]:+.1f}). "
                  f"Numbers are scaled, so coefficients are comparable.")
    link = ml.plot_pred_actual(linear, reg, "Linear Regression",
                               "m1_linear_pred_vs_actual.png")
    report.figure(link, "Predicted vs actual fare")

    clf = tasks["classification"]
    logit = ml.make_pipeline(
        clf, LogisticRegression(class_weight="balanced", max_iter=1000))
    secs = ml.fit_model(logit, clf.X_train, clf.y_train)
    scores = ml.classification_metrics(logit, clf)
    rows.append(ml.result_row(MEMBER, "Logistic Regression", clf, scores,
                              len(clf.X_train), secs,
                              "class_weight=balanced"))
    base = ml.baseline(clf)

    report.heading("3. Logistic Regression: will the customer cancel?")
    report.bullet("Logistic Regression turns the same kind of formula into "
                  "a probability between 0 and 1. class_weight='balanced' "
                  "makes the rare cancellations count more during training.")
    report.bullet(f"Test results: accuracy {scores['accuracy']:.3f} "
                  f"(baseline {base['accuracy']:.3f}), precision "
                  f"{scores['precision']:.3f}, recall {scores['recall']:.3f}, "
                  f"F1 {scores['f1']:.3f}, ROC-AUC {scores['roc_auc']:.3f}.")
    report.bullet(f"ROC-AUC {scores['roc_auc']:.2f} is "
                  f"{ml.auc_label(scores['roc_auc'])} (0.5 is guessing, "
                  f"1.0 is perfect).")
    names = ml.feature_names(logit)
    coefs = logit.named_steps["model"].coef_.ravel()
    top = int(np.argmax(np.abs(coefs)))
    report.bullet(f"Strongest input: {names[top]} (coefficient "
                  f"{coefs[top]:+.2f}; positive means more cancellations).")
    link = ml.plot_importance(names, coefs, "Logistic Regression coefficients",
                              "m1_logistic_coefficients.png", signed=True)
    report.figure(link, "Logistic regression coefficients")
    link = ml.plot_confusion(logit, clf, "Logistic Regression",
                             "m1_logistic_confusion.png")
    report.figure(link, "Confusion matrix")
    link = ml.plot_roc({"Logistic Regression": logit}, clf,
                       "Logistic Regression ROC curve", "m1_logistic_roc.png")
    report.figure(link, "ROC curve")

    ml.save_results(MEMBER, rows)
    report.write([
        "What does R-squared tell you about how well fare can be predicted, "
        "and which input matters most?",
        "How good is the cancellation model compared with guessing, and "
        "what do precision and recall mean here?",
        "Why is accuracy a poor score for the cancellation task?",
    ])


if __name__ == "__main__":
    main()
