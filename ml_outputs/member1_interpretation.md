## Member 1: my interpretation

- Linear Regression explains very little of the fare: R-squared is only about 0.06, and its MAE (272) is just 11 better than always guessing the average fare (283). The largest effect is is_weekend (coefficient about +93), meaning weekend rides cost more, while distance and vehicle type barely matter.
- Logistic Regression is clearly better than guessing at spotting customer cancellations (ROC-AUC 0.74, where 0.5 is guessing). It catches about 63% of real cancellations (recall 0.63), but only 17% of the rides it flags are real cancellations (precision 0.17), so it raises many false alarms. The strongest input is the driver's arrival time (vtat): the longer the wait, the more likely the customer cancels.
- Accuracy is a poor score here because only about 10% of rides are customer cancellations. A model that always says "completed" would be 90% accurate and still never find a cancellation, so I used ROC-AUC, precision, recall and F1 instead.
