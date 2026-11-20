## Member 3: my interpretation

\- The linear kernel with C=1 worked best for both tasks in the tuning round: validation ROC-AUC about 0.76, against about 0.75 for the rbf kernel and about 0.73 for rbf with C=10, and the lowest fare error as well. A curved boundary did not help, which suggests the relationships in this data are simple.

\- For cancellations the SVM beats guessing (ROC-AUC 0.74, moderate). It finds about 62% of real cancellations (recall 0.62), but only 17% of its alarms are real (precision 0.17), which is why its accuracy (0.66) is below the 0.90 of always guessing "completed". For fares it cuts the error from 283 to about 264, but R-squared is only about 0.01, so it barely explains the variation. SVR is less affected by very expensive rides, so it predicts a more typical fare than the average does.

\- An SVM gets much slower as the number of rides grows, so it cannot be trained on all 100,000+ rides in a reasonable time. It trained on 15,000 rides, was tuned on 5,000, and was tested on the full test set.

