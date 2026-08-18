🤖 AI Job Automation

<div align="center">

AI-Powered LinkedIn Job Search, Resume Matching & Application Automation

Automate job discovery, analyze resume compatibility, identify skill gaps, filter suitable opportunities, and streamline LinkedIn Easy Apply applications using Python and Playwright.







</div>

📖 Overview

Applying for software engineering jobs manually is repetitive and time-consuming.

AI Job Automation is a Python-based job search and application automation system designed to reduce the repetitive work involved in discovering suitable jobs, evaluating resume compatibility, and completing supported application steps.

The system connects to an authenticated Chrome session, searches LinkedIn jobs, extracts job information, analyzes job descriptions, compares job requirements with the user's resume, calculates match scores, identifies missing skills, filters suitable Easy Apply jobs, opens application forms, fills supported fields, validates required information, and tracks application activity.

The project is built as a modular automation pipeline, making it easier to extend with smarter eligibility checks, application-question handling, resume selection, notifications, and additional job platforms.

Current focus: improving application eligibility filtering, handling dynamic Easy Apply questions, making resume selection reliable, and safely completing the final review/submission flow.

🎯 Project Goal

The primary goal of this project is to automate the repetitive parts of the job application process.

LinkedIn
    │
    ▼
Job Search
    │
    ▼
Job Collection
    │
    ▼
Job Details Extraction
    │
    ▼
Resume & Skill Matching
    │
    ▼
Match Score
    │
    ▼
Eligibility Filtering
    │
    ▼
Easy Apply Detection
    │
    ▼
Application Form
    │
    ▼
Automatic Form Filling
    │
    ▼
Required Field Validation
    │
    ▼
Review
    │
    ▼
Application Submission
    │
    ▼
Application Tracking

✨ Features

🔎 LinkedIn Job Search

The system uses Playwright to interact with LinkedIn through an existing authenticated Chrome session.

Features include:

LinkedIn job search automation

Search by target job title

Job result collection

Job title extraction

Company extraction

Job URL extraction

Easy Apply detection

Active applicant/recruiter status detection

CSV-based job storage

Example search:

Java Backend Developer

🧾 Job Information Extraction

The system opens collected job pages and extracts detailed job information.

Collected information includes:

Job Title

Company

Location

Easy Apply status

Job URL

Job Description

Output:

data/job_details.csv

📄 Resume Analysis

The system uses the user's resume as the basis for job matching.

Current capabilities include:

Resume PDF parsing

Resume text extraction

Technical skill extraction

Resume skill matching

Job requirement comparison

Missing skill identification

Resume location:

resume/resume.pdf

🧠 Resume-to-Job Matching

The system compares the user's technical skills against skills and requirements found in job descriptions.

Each job can receive a match score.

Example:

Java Software Engineer

Match Score : 96%

Missing Skills:
AWS
Docker
Redis

The match score is used to rank jobs and identify the strongest opportunities.

🎯 Job Ranking & Recommendation

Jobs are ranked according to their compatibility with the user's profile.

The system considers factors such as:

Resume match score

Required skills

Missing skills

Easy Apply availability

Application status

Example:

1. Java Software Engineer
   Score   : 96%
   Priority: HIGH
   Easy Apply: Yes

2. Java Backend Developer
   Score   : 92%
   Priority: HIGH
   Easy Apply: Yes

3. Java Spring Boot Developer
   Score   : 81%
   Priority: HIGH
   Easy Apply: Yes

🚦 Eligibility Filtering

A high technical match does not necessarily mean that a job is suitable.

The automation is designed to evaluate additional eligibility criteria such as:

Experience requirements

Job level

Easy Apply availability

Application status

Job availability

Technical compatibility

For example:

Job Requirement:
7–12 Years Experience

Candidate Experience:
0 Years

Result:
❌ Not Eligible

This prevents the automation from applying to jobs that match technically but require significantly more experience.

⚡ Easy Apply Automation

The project includes an Easy Apply automation module for processing suitable application forms.

It can:

Identify recommended Easy Apply jobs

Open the selected job

Detect whether the job is still active

Detect Easy Apply

Open the application form

Process application pages

Fill supported fields

Validate required fields

Navigate between application pages

Detect the review page

Example:

Recommended Jobs
       │
       ▼
Select Job
       │
       ▼
Open LinkedIn Job
       │
       ▼
Check Job Status
       │
       ▼
Check Easy Apply
       │
       ▼
Open Application

📝 Application Form Automation

The application form module processes LinkedIn Easy Apply forms.

Supported form elements include:

Name fields

Email fields

Phone fields

Phone country code

Text inputs

Number inputs

Dropdowns

Radio buttons

Checkboxes

Resume upload fields

Required field detection

Next / Continue buttons

Review buttons

Submit button detection

The automation supports multi-page application forms.

Example:

Easy Apply
    │
    ▼
Application Page 1
    │
    ▼
Application Page 2
    │
    ▼
Application Page 3
    │
    ▼
Application Page 4
    │
    ▼
Final Review

📎 Resume Upload

The application automation supports detecting resume upload fields and using the configured resume.

Default resume:

resume/resume.pdf

The system is designed to use the user's configured resume rather than selecting arbitrary files.

🔍 Required Field Validation

Before continuing through an application, the automation checks required fields.

Example:

Checking required fields...

Required elements found: 3

Empty required fields:
- Phone
- Experience
- Work Authorization

If the system cannot safely determine an answer, it should stop rather than submit an incorrect response.

🛑 Closed Job Detection

LinkedIn jobs may stop accepting applications after they have already been collected.

The automation checks for closed jobs.

Example:

JOB CLOSED

This job is no longer accepting applications.

Skipping job...

Trying next eligible job...

This allows the system to move to another suitable job instead of attempting to apply to an unavailable position.

📋 Application Tracking

The project includes application tracking so completed and in-progress applications can be recorded and excluded from repeated processing.

Application data is stored in:

data/application_tracker.csv

Possible application states include:

NOT APPLIED
APPLIED
ASSESSMENT
INTERVIEW
OFFER
REJECTED

The tracker helps prevent repeatedly processing jobs that have already been applied to.

📊 Dashboard

The project includes a dashboard for monitoring job statistics, recommendations, and application activity.

Example:

JOB STATISTICS

Total Jobs          : 20
High Priority       : 5
Medium Priority     : 8
Low Priority        : 7

Application pipeline:

Not Applied
Applied
Assessment
Interview
Offers
Rejected

The dashboard also displays top job recommendations and application activity.

🧩 System Architecture

                         LinkedIn
                            │
                            ▼
                    ┌───────────────┐
                    │  Job Search   │
                    │ job_search.py │
                    └───────┬───────┘
                            │
                            ▼
                       jobs.csv
                            │
                            ▼
                  ┌──────────────────┐
                  │  Job Details     │
                  │ job_details.py   │
                  └────────┬─────────┘
                           │
                           ▼
                   job_details.csv
                           │
                           ▼
             ┌─────────────────────────┐
             │ Resume / Skill Matching │
             │ resume_matcher.py       │
             │ skill_matcher.py        │
             └────────────┬────────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │  Job Analyzer   │
                 │ job_analyzer.py │
                 └────────┬────────┘
                          │
                          ▼
                  job_analysis.csv
                          │
                          ▼
                ┌───────────────────┐
                │ Eligibility Filter│
                └─────────┬─────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │   Easy Apply    │
                 │  easy_apply.py  │
                 └────────┬────────┘
                          │
                          ▼
                ┌────────────────────┐
                │ Application Form   │
                │ application_form.py│
                └─────────┬──────────┘
                          │
                          ▼
                     Application
                          │
                          ▼
                ┌────────────────────┐
                │ Application Tracker│
                └────────────────────┘

📂 Project Structure

AI-Job-Automation/
│
├── auth/
│
├── data/
│   ├── application_tracker.csv
│   ├── job_analysis.csv
│   ├── job_details.csv
│   ├── logs/
│   └── screenshots/
│
├── resume/
│   └── resume.pdf
│
├── screenshots/
│
├── application_form.py
├── application_tracker.py
├── config.py
├── connect.py
├── dashboard.py
├── debug_jobs.py
├── easy_apply.py
├── job_analyzer.py
├── job_details.py
├── job_scraper.py
├── job_search.py
├── linkedin_bot.py
├── login.py
├── main.py
├── profile.py
├── resume_matcher.py
├── skill_matcher.py
├── test_matcher.py
├── start_chrome.bat
├── requirements.txt
├── .gitignore
└── README.md

⚙️ Technologies Used

Technology

Purpose

Python

Core programming and automation

Playwright

Browser automation

Chrome CDP

Connect to existing Chrome session

pdfplumber

Resume PDF parsing

CSV

Job and application data storage

Regular Expressions

Data extraction and matching

Git

Version control

GitHub

Source code management

💻 Requirements

Before running the project, install:

Python 3.11+

Google Chrome

Git

Playwright

LinkedIn account

🚀 Installation

1. Clone Repository

git clone https://github.com/gbhanuprasad5261/AI-Job-Automation.git

cd AI-Job-Automation

2. Create Virtual Environment

python -m venv venv

3. Activate Virtual Environment

Windows

venv\Scripts\activate

4. Install Dependencies

pip install -r requirements.txt

5. Install Playwright

playwright install

🔐 Configuration

Use environment variables for private information.

Example:

LINKEDIN_EMAIL=your_email
LINKEDIN_PASSWORD=your_password

APPLICANT_NAME=Your Name
EMAIL=your_email@example.com
PHONE=your_phone_number

YEARS_OF_EXPERIENCE=0

RESUME_PATH=resume/resume.pdf

Do not commit passwords, authentication tokens, personal documents, or private credentials to GitHub.

🌐 Chrome CDP Setup

The project connects Playwright to an existing Chrome session using Chrome DevTools Protocol.

Start Chrome using:

.\start_chrome.bat

The Chrome session uses:

Remote Debugging Port: 9222

Playwright connects through:

http://127.0.0.1:9222

This allows the automation to reuse the authenticated browser session.

🔑 LinkedIn Authentication

The project uses an existing authenticated Chrome session.

If LinkedIn requests:

CAPTCHA

Email verification

Two-factor authentication

Security verification

complete the verification manually.

The automation should continue after authentication is completed.

▶️ Usage

Note: LinkedIn can change its UI, application flow, selectors, and security checks. Review the application before relying on final submission automation.

Step 1 — Start Chrome

.\start_chrome.bat

Step 2 — Search Jobs

python job_search.py

This searches LinkedIn and saves collected jobs to:

jobs.csv

Step 3 — Extract Job Details

python job_details.py

Output:

data/job_details.csv

Step 4 — Analyze Jobs

python job_analyzer.py

Output:

data/job_analysis.csv

The analyzer calculates:

Match score

Priority

Missing skills

Easy Apply status

Recommended jobs

Step 5 — Run Dashboard

python dashboard.py

Displays:

Job statistics

Application pipeline

Top recommendations

Easy Apply jobs

Application rate

Step 6 — Run Easy Apply

python easy_apply.py

The system selects jobs according to configured filters such as:

Match Score
Easy Apply
Application Status
Job Availability

📊 Example Output

======================================================================
AI JOB AUTOMATION - EASY APPLY
======================================================================

Eligible jobs: 3

======================================================================
RECOMMENDED EASY APPLY JOBS
======================================================================

1. Java Software Engineer
   Company : Tata Consultancy Services
   Score   : 96%
   Priority: HIGH
   Easy Apply: Yes
   Status  : NOT APPLIED

2. Java Backend Developer
   Company : Example Company
   Score   : 92%
   Priority: HIGH
   Easy Apply: Yes
   Status  : NOT APPLIED

3. Java Spring Boot Developer
   Company : Example Company
   Score   : 81%
   Priority: HIGH
   Easy Apply: Yes
   Status  : NOT APPLIED

🧪 Testing

Test each module independently.

Job Search

python job_search.py

Job Details

python job_details.py

Job Analyzer

python job_analyzer.py

Dashboard

python dashboard.py

Easy Apply

python easy_apply.py

🐛 Debugging

A debugging utility is included to inspect LinkedIn's current page structure.

Run:

python debug_jobs.py

This can be used to inspect:

Job titles

Job links

Page elements

Application buttons

Form elements

LinkedIn DOM changes

LinkedIn's page structure can change over time, so selectors may occasionally require maintenance.

📈 Project Progress

Module

Status

Python Environment

✅

Playwright Setup

✅

Chrome CDP Integration

✅

LinkedIn Session

✅

LinkedIn Job Search

✅

Job Collection

✅

Job URL Extraction

✅

Easy Apply Detection

✅

Job Description Extraction

✅

CSV Data Storage

✅

Resume PDF Parsing

✅

Skill Extraction

✅

Resume Matching

✅

Match Score Calculation

✅

Missing Skills Detection

✅

Job Ranking

✅

Job Closed Detection

✅

Easy Apply Job Filtering

✅

Easy Apply Form Opening

✅

Application Form Navigation

✅

Contact Information Filling

✅

Phone Country Selection

✅

Required Field Detection

✅

Application Tracking

✅

Dashboard

✅

Experience Eligibility Filtering

🚧

Advanced Application Questions

🚧

Resume Selection & Upload Reliability

🚧

Final Submission Automation

🚧

Fully Automated End-to-End Workflow

🚧

🛣️ Roadmap

Phase 1 — Job Discovery

LinkedIn job search

Job collection

Job URL extraction

Job description extraction

Status: Completed

Phase 2 — Resume Intelligence

Resume parsing

Skill extraction

Job requirement extraction

Resume matching

Match scoring

Missing skill detection

Job ranking

Status: Completed

Phase 3 — Job Eligibility

Improve filtering for:

Experience requirements

Entry-level/fresher roles

Job level

Location

Employment type

Easy Apply availability

Application status

Status: In Progress

Phase 4 — Application Automation

Improve:

Resume upload

Form field detection

Dropdown handling

Radio button handling

Checkbox handling

Application questions

Multi-page applications

Required field validation

Status: In Progress

Phase 5 — Application Submission

Final workflow:

Find Job
   ↓
Check Eligibility
   ↓
Match Resume
   ↓
Open Easy Apply
   ↓
Fill Application
   ↓
Validate Required Fields
   ↓
Review
   ↓
Submit
   ↓
Track Application

Status: In Progress

Phase 6 — Intelligent Automation

Future improvements:

AI-powered application question answering

Job-specific resume selection

Job-specific cover letter generation

Personalized recruiter messages

Better job ranking

Duplicate job detection

Automatic application scheduling

Email notifications

Multi-platform job search

Status: Planned

⚠️ Safety & Reliability

This project interacts with LinkedIn through browser automation.

LinkedIn may change:

Page layouts

CSS selectors

Button names

Application workflows

Authentication requirements

Security checks

Therefore, the automation may require maintenance when LinkedIn changes its interface.

The automation does not attempt to bypass:

CAPTCHA

Security verification

Authentication controls

Access restrictions

When LinkedIn requests verification, complete it manually.

The automation should never guess an answer to an application question when the correct response cannot be determined safely.

🔒 Privacy & Security

Never commit the following to GitHub:

.env
Passwords
Authentication tokens
Private resume
Personal documents
Browser session data
Private application information

Recommended .gitignore entries:

venv/
.env
playwright-profile/
auth/
__pycache__/
*.pyc
.vscode/

resume/resume.pdf

data/*.csv
data/logs/
data/screenshots/

.DS_Store
Thumbs.db

📁 Generated Data

The project generates several files during execution.

Job Search

jobs.csv

Job Details

data/job_details.csv

Job Analysis

data/job_analysis.csv

Application Tracking

data/application_tracker.csv

These files may change after each execution.

🔄 Recommended Workflow

For normal use:

1. Start Chrome
       ↓
2. Authenticate LinkedIn
       ↓
3. Search Jobs
       ↓
4. Extract Job Details
       ↓
5. Analyze Jobs
       ↓
6. Filter Eligible Jobs
       ↓
7. Select Easy Apply Jobs
       ↓
8. Open Application
       ↓
9. Fill Supported Fields
       ↓
10. Validate Application
       ↓
11. Review
       ↓
12. Submit
       ↓
13. Track Application

🧠 Why This Project?

Traditional job searching requires repeatedly performing the same tasks:

Search
 ↓
Open Job
 ↓
Read Description
 ↓
Compare Resume
 ↓
Check Skills
 ↓
Apply
 ↓
Fill Form
 ↓
Track Application

This project aims to automate the repetitive parts of that workflow.

The user can therefore spend more time on:

Interview preparation

Coding practice

Technical skills

Resume improvement

Career development

🎯 Final Project Vision

The long-term goal is to build a personal AI-powered job assistant that can intelligently manage the complete job search workflow.

                 JOB SEARCH
                     │
                     ▼
              JOB UNDERSTANDING
                     │
                     ▼
              RESUME MATCHING
                     │
                     ▼
             ELIGIBILITY CHECK
                     │
                     ▼
              JOB PRIORITIZATION
                     │
                     ▼
               EASY APPLY
                     │
                     ▼
            APPLICATION FILLING
                     │
                     ▼
               VALIDATION
                     │
                     ▼
                 REVIEW
                     │
                     ▼
                SUBMISSION
                     │
                     ▼
             APPLICATION TRACKING

The objective is to create a reliable personal automation system that reduces repetitive job application work while keeping the user in control of uncertain or important decisions.

👨‍💻 Author

G. Bhanu Prasad

Java Backend Developer | Python Automation Enthusiast

GitHub

https://github.com/gbhanuprasad5261

LinkedIn

https://www.linkedin.com/in/g-bhanu-prasad/

📄 License

This project is licensed under the MIT License.

⭐ Project Status

Active Development

The core job discovery, extraction, resume matching, ranking, Easy Apply detection, application form navigation, and application tracking components are implemented.

The current development focus is improving:

Eligibility Filtering
        ↓
Application Question Handling
        ↓
Resume Upload
        ↓
Final Review
        ↓
Safe Submission
        ↓
End-to-End Automation
