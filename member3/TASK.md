# Member 3 task

**What you do:** Transformations 8-12: data types, calculated columns, categories, outlier flag and sorting.

**Before you start:** Members 1 and 2 must be merged.

**Your files:** `etl/member3_types_and_features.py`

## Steps (PowerShell, inside the `NCR_Ride_Bookings_ETL` folder)

1. Get the latest code (clone the first time, `git pull` afterwards)
```powershell
git clone https://github.com/Abhijithsk/NCR_Ride_Bookings_ETL.git
cd NCR_Ride_Bookings_ETL
git pull origin main
```
2. Create your branch
```powershell
git checkout -b feature/member3-types-features
pip install -r requirements-dev.txt
```
3. Copy your code in (this replaces the stub)
```powershell
Copy-Item ..\member_code\member3\etl\*.py etl\ -Force

```
If the paths fail, drag the files from the `member_code\member3` folder into the matching folders and choose Replace.
Then open the file and **read it**: you will be asked to explain it.

4. Check it
```powershell
flake8 .
pytest
python check_member.py 3
```
You should see: `flake8` prints nothing; pytest ends with **13 passed, 3 skipped**; the checker ends with
**CHECK OK after Member 3: 148,767 rows x 30 columns, 0 null values**.


5. Screenshot: Windows + Shift + S around the `[08]`-`[12]` lines and the CHECK OK line.

6. Save and upload
```powershell
git add etl
git status
git commit -m "feat: data types, calculated columns, categories, outliers, sorting"
git push -u origin feature/member3-types-features
```
`git status` must list only your own files. If it lists anything else (for example `__pycache__` or `*_raw_copy.csv`), stop and tell the lead.

7. On GitHub click **Compare & pull request**, fill in the template, paste your screenshot, **Create pull request**,
wait for the green tick, and ask the lead to review and merge.

## Questions you must be able to answer
- Why use `category` and `int16` types?
- How is `fare_per_km` calculated and why is it 0 for cancelled rides?
- How does the IQR rule work, and why flag outliers instead of deleting them?
- How are `time_of_day`, `distance_category` and `fare_category` defined?
