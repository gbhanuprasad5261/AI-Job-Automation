import csv
import os
from collections import Counter

from skill_matcher import match_resume


INPUT_FILE = "data/job_details.csv"
OUTPUT_FILE = "data/job_analysis.csv"


def analyze_jobs():

    # ---------------------------------------
    # Check input file
    # ---------------------------------------

    if not os.path.exists(INPUT_FILE):
        print("job_details.csv not found.")
        return

    jobs = []

    # ---------------------------------------
    # Read job details
    # ---------------------------------------

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:

            description = row.get(
                "Description",
                ""
            )

            score, matched, missing = match_resume(
                description
            )

            # ---------------------------------------
            # Determine priority
            # ---------------------------------------

            if score >= 80:
                priority = "HIGH"
            elif score >= 60:
                priority = "MEDIUM"
            else:
                priority = "LOW"

            # ---------------------------------------
            # Add analyzed job
            # ---------------------------------------

            jobs.append({
                "Title": row.get("Title", ""),
                "Company": row.get("Company", ""),
                "Location": row.get("Location", ""),
                "Easy Apply": row.get("Easy Apply", ""),
                "Match Score": f"{score}%",
                "Priority": priority,
                "Matched Skills": ", ".join(
                    sorted(matched)
                ),
                "Missing Skills": ", ".join(
                    sorted(missing)
                ),
                "Link": row.get("Link", "")
            })

    # ---------------------------------------
    # Save analysis
    # ---------------------------------------

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=[
                "Title",
                "Company",
                "Location",
                "Easy Apply",
                "Match Score",
                "Priority",
                "Matched Skills",
                "Missing Skills",
                "Link"
            ]
        )

        writer.writeheader()
        writer.writerows(jobs)

    # ---------------------------------------
    # Analysis completed
    # ---------------------------------------

    print()
    print("=" * 60)
    print("AI JOB ANALYSIS COMPLETED")
    print("=" * 60)

    print(f"Jobs analyzed : {len(jobs)}")
    print(f"Saved file    : {OUTPUT_FILE}")

    # ---------------------------------------
    # TOP 3 JOB MATCHES
    # ---------------------------------------

    if jobs:

        ranked_jobs = sorted(
            jobs,
            key=lambda x: int(
                x["Match Score"].replace("%", "")
            ),
            reverse=True
        )

        print()
        print("=" * 60)
        print("TOP 3 JOB MATCHES")
        print("=" * 60)

        for index, job in enumerate(
            ranked_jobs[:3],
            start=1
        ):

            score = int(
                job["Match Score"].replace("%", "")
            )

            if score >= 80:
                priority = "HIGH PRIORITY"
            elif score >= 60:
                priority = "MEDIUM PRIORITY"
            else:
                priority = "LOW PRIORITY"

            print()
            print(f"{index}. {job['Title']}")
            print(f"   Company : {job['Company']}")
            print(f"   Location: {job['Location']}")
            print(f"   Score   : {job['Match Score']}")
            print(f"   Priority: {priority}")

            print(
                f"   Missing : "
                f"{job['Missing Skills'] or 'None'}"
            )

        # ---------------------------------------
        # SKILL GAP ANALYSIS
        # ---------------------------------------

        skill_counter = Counter()

        for job in jobs:

            missing = job["Missing Skills"]

            if missing:

                skills = [
                    skill.strip()
                    for skill in missing.split(",")
                    if skill.strip()
                ]

                skill_counter.update(skills)

        print()
        print("=" * 60)
        print("SKILL GAP ANALYSIS")
        print("=" * 60)

        if skill_counter:

            print()
            print(
                "Skills to improve based on "
                "collected jobs:"
            )
            print()

            for rank, (
                skill,
                count
            ) in enumerate(
                skill_counter.most_common(10),
                start=1
            ):

                print(
                    f"{rank}. {skill} -> "
                    f"{count} job(s)"
                )

            recommended = [
                skill
                for skill, count
                in skill_counter.most_common(5)
            ]

            print()
            print("Recommended Focus:")
            print(
                ", ".join(recommended)
            )

        else:

            print()
            print(
                "No missing skills identified."
            )


if __name__ == "__main__":
    analyze_jobs()