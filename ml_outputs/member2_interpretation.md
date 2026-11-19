## Member 2: my interpretation

- On a validation set, k=21 gave the best ROC-AUC for cancellations and k=81 gave the lowest error for fares. Because fares hardly depend on the inputs, the regression keeps preferring a large k that just averages many rides.
- KNN beats guessing for cancellations (ROC-AUC 0.70, moderate), but its recall is only 0.08: it almost never predicts a cancellation, although it is right when it does (precision 1.00). Its accuracy of 0.907 barely beats the 0.899 baseline, so accuracy hides how little it finds.
- KNN is slow on large data, so it trained on 15,000 of the 100,000+ rides. It has no class-weight option for the rare cancellations, needs scaled inputs, and cannot explain which inputs matter.
