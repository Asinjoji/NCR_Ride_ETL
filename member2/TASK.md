# Member 2 task

**What you do:** Transformations 5-7: merge the three sparse reason columns, handle missing values, and validate the data.

**Before you start:** Member 1 must be merged (a stub from Member 1 makes your check fail).

**Your files:** `etl/member2_missing_and_validation.py`

## Steps (PowerShell, inside the `NCR_Ride_Bookings_ETL` folder)

1. Get the latest code (clone the first time, `git pull` afterwards)
```powershell
git clone https://github.com/Abhijithsk/NCR_Ride_Bookings_ETL.git
cd NCR_Ride_Bookings_ETL
git pull origin main
```
2. Create your branch
```powershell
git checkout -b feature/member2-missing-validation
pip install -r requirements-dev.txt
```
3. Copy your code in (this replaces the stub)
```powershell
Copy-Item ..\member_code\member2\etl\*.py etl\ -Force

```
If the paths fail, drag the files from the `member_code\member2` folder into the matching folders and choose Replace.
Then open the file and **read it**: you will be asked to explain it.

4. Check it
```powershell
flake8 .
pytest
python check_member.py 2
```
You should see: `flake8` prints nothing; pytest ends with **8 passed, 8 skipped**; the checker ends with
**CHECK OK after Member 2: 148,767 rows x 23 columns, 0 null values**.


5. Screenshot: Windows + Shift + S around the `[05]`-`[07]` lines and the CHECK OK line.

6. Save and upload
```powershell
git add etl
git status
git commit -m "feat: merge reason columns, handle missing values, validate data"
git push -u origin feature/member2-missing-validation
```
`git status` must list only your own files. If it lists anything else (for example `__pycache__` or `*_raw_copy.csv`), stop and tell the lead.

7. On GitHub click **Compare & pull request**, fill in the template, paste your screenshot, **Create pull request**,
wait for the green tick, and ask the lead to review and merge.

## Questions you must be able to answer
- Why are most nulls 'structural' (a cancelled ride has no fare)?
- Which three columns are merged, and what do `cancelled_by` and `reason` hold?
- Which validation rules are applied? Why did they remove 0 rows here?
- Why are numeric nulls filled with 0 (and valid ratings are 1-5)? Why must validation run before the fill?
