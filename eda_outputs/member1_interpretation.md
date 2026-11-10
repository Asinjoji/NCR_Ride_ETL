## Member 1: my interpretation

\- The cleaned data is clean enough to analyse. The pipeline removed 1,233 duplicate rows (150,000 to 148,767), renamed columns, fixed IDs and dates, and left no blank cells. However, cancelled and failed bookings have a fare, distance and rating of 0 because those values never existed, so I only used the 92,248 completed rides (62.0% of bookings) for money, distance and rating analysis.

\- Fare has about 3,125 outliers (above roughly 1,369) and price per km has about 9,147 outliers, while distance has none. The high fares are real long or premium rides, so I would keep them but flag them. The very high price per km mostly comes from short rides with a high fare, so analysts should use the median (about 17.7) instead of the mean (about 33.9).

\- Fare and distance are almost unrelated (correlation about 0.01), which is surprising because longer rides normally cost more. The other numeric columns also show very weak links, which suggests the dataset is synthetic and not real ride data.

