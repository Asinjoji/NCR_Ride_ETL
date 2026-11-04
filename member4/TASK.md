# Member 4 task

**What you do:** Steps 7, 8 and 10: the 14 reports, `load()`, the final README, the generated `reports/` and `output/` files, and the final screenshots.

**Before you start:** Members 1, 2 and 3 must be merged.

**Your files:** `etl/member4_reports_and_load.py, README.md, reports/, output/, screenshots/`

## Steps (PowerShell, inside the `NCR_Ride_Bookings_ETL` folder)

1. Get the latest code (clone the first time, `git pull` afterwards)
```powershell
git clone https://github.com/Abhijithsk/NCR_Ride_Bookings_ETL.git
cd NCR_Ride_Bookings_ETL
git pull origin main
```
2. Create your branch
```powershell
git checkout -b feature/member4-reports-load
pip install -r requirements-dev.txt
```
3. Copy your code in (this replaces the stub)
```powershell
Copy-Item ..\member_code\member4\etl\*.py etl\ -Force
Copy-Item ..\member_code\member4\README.md . -Force
```
If the paths fail, drag the files from the `member_code\member4` folder into the matching folders and choose Replace.
Then open the file and **read it**: you will be asked to explain it.

4. Check it
```powershell
flake8 .
pytest
python check_member.py 4
```
You should see: `flake8` prints nothing; pytest ends with **16 passed**; the checker ends with
**CHECK OK after Member 4: 14 reports, clean 148,767 rows x 30 columns, 0 null values**.
For Member 4 the checker also runs the whole pipeline, so you will see all 15 files being saved.

5. Screenshot: Windows + Shift + S around the full `PIPELINE FINISHED` output and the CHECK OK line, saved as `screenshots/pipeline_run.png`. Save it in the screenshots folder.

6. Save and upload
```powershell
git add etl README.md reports output screenshots
git status
git commit -m "feat: reports, load, README and final outputs"
git push -u origin feature/member4-reports-load
```
`git status` must list only your own files. If it lists anything else (for example `__pycache__` or `*_raw_copy.csv`), stop and tell the lead.

7. On GitHub click **Compare & pull request**, fill in the template, paste your screenshot, **Create pull request**,
wait for the green tick, and ask the lead to review and merge.

## Questions you must be able to answer
- Which reports are produced and what question does each answer?
- Why are top/bottom 10 locations based on completed rides only?
- What does `load()` write and where?
- Walk through `run_etl_pipeline()` and why `if __name__ == '__main__'` is used.
