## Member 4: my interpretation

\- The driver's arrival time (vtat) is the most important input for cancellations in both the tree and the forest, and the small tree diagram shows why: rides where the driver took more than about 15 minutes to arrive were all cancelled by the customer, and none were cancelled when the driver arrived in under about 5 minutes. For fares, is\_weekend matters most, which fits weekend fares being higher. This agrees with the EDA, where cancelled rides had longer arrival times than completed ones.



\- In this data the random forest is not clearly better than a single tree: both have ROC-AUC about 0.745 (0.744 against 0.746) and R-squared about 0.05. The single tree even has the better F1 (0.50 against 0.43) and much higher precision (0.90 against 0.52), while the forest finds slightly more real cancellations (recall 0.37 against 0.34). A forest usually helps because averaging many trees cancels out their individual mistakes, but here the main pattern is simple enough for one tree to capture.



\- max\_depth was chosen by trying 3, 5, 8, 12 and 16 on a validation set; the best was 5 for cancellations and 3 for fares. A tree that is too deep memorises noise in the training rides and does worse on new ones, which is why the fare tree prefers a very shallow tree: there is almost no real pattern to learn.

