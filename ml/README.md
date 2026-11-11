# Machine learning scripts

Run from the project root, after `python pipeline.py` has created
`output/cleaned_ride_bookings.csv`. Needs scikit-learn
(`pip install -r requirements-dev.txt`).

Two tasks, one fixed train/test split shared by every model:

* Classification: will the customer cancel? (customer cancelled vs completed)
* Regression: what is the fare of a completed ride?

| Member | Script | Algorithms |
|---|---|---|
| 1 | `ml_member1_linear_logistic.py` | Linear Regression (fare), Logistic Regression (cancel) |
| 2 | `ml_member2_knn.py` | KNN (both tasks, k tuned) |
| 3 | `ml_member3_svm.py` | SVM / SVR (both tasks, kernel tuned) |
| 4 | `ml_member4_tree_forest.py` | Decision Tree and Random Forest (both tasks) |

Each script saves charts in `ml_outputs/figures/`, a results table in
`ml_outputs/results/`, a facts file `ml_outputs/memberN_findings.md` and a
template `ml_outputs/memberN_interpretation.md` for the member to fill in.
`run_all_ml.py` (lead only) compares all models and writes
`docs/ML_report.md`.
