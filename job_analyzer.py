import csv
import os

from skill_matcher import match_resume


INPUT_FILE = "data/job_details.csv"
OUTPUT_FILE = "data/job_analysis.csv"

if not os.path.exists(INPUT_FILE):
    print("job_details.csv not found.")
    exit()

jobs = []

with open(INPUT_FILE, "r", encoding="utf-8") as f:

    reader = csv.DictReader(f)

    for row in reader:

        description = row.get("Description", "")

        score, matched, missing = match_resume(description)

        jobs.append({
            "Title": row.get("Title", ""),
            "Company": row.get("Company", ""),
            "Location": row.get("Location", ""),
            "Easy Apply": row.get("Easy Apply", ""),
            "Match Score": f"{score}%",
            "Matched Skills": ", ".join(sorted(matched)),
            "Missing Skills": ", ".join(sorted(missing)),
            "Link": row.get("Link", "")
        })

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:

    writer = csv.DictWriter(
        f,
        fieldnames=[
            "Title",
            "Company",
            "Location",
            "Easy Apply",
            "Match Score",
            "Matched Skills",
            "Missing Skills",
            "Link"
        ]
    )

    writer.writeheader()
    writer.writerows(jobs)

print()
print("=" * 50)
print("AI JOB ANALYSIS COMPLETED")
print("=" * 50)
print(f"Jobs analyzed : {len(jobs)}")
print(f"Saved file    : {OUTPUT_FILE}")