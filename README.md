# 🤖 AI Job Automation

<div align="center">

### AI-Powered LinkedIn Job Search, Resume Matching & Application Automation

Automate job discovery, analyze resume compatibility, identify skill gaps, rank suitable opportunities, and streamline supported LinkedIn Easy Apply applications using Python and Playwright.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-Automation-45ba4b?logo=playwright&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active%20Development-yellow)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

</div>

---

## 📖 Overview

Applying for software engineering jobs manually is repetitive and time-consuming — searching, opening dozens of tabs, reading job descriptions, comparing them against a resume, and filling near-identical forms over and over.

**AI Job Automation** is a Python-based personal job search automation system built to eliminate that repetition while keeping the applicant in full control of important decisions.

The system:

- Finds relevant jobs on LinkedIn
- Collects and stores job information
- Extracts full job descriptions
- Compares jobs against a resume
- Calculates resume-to-job match scores
- Identifies missing/required skills
- Ranks opportunities by suitability
- Detects Easy Apply availability
- Fills supported application fields
- Validates required fields before submission
- Tracks every submitted application

Built with **Python, Playwright, Chrome DevTools Protocol (CDP), PDF parsing, CSV-based data processing, and rule-based resume/job matching.**

> The long-term goal is a personal AI-powered job assistant that handles the repetitive parts of the job search while the user stays in control of uncertain or high-stakes decisions.

---

## 🎯 Project Goal

Reduce the repetitive work involved in applying for software engineering jobs — without removing the human from decisions that matter.

### 🔄 Workflow

```text
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
Job Ranking
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
Supported Form Filling
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
```

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🔍 **Automated Job Search** | Searches LinkedIn using configurable keywords, location, and filters |
| 📋 **Job Data Collection** | Scrapes and stores job title, company, location, and description via Playwright + CDP |
| 📄 **Resume Parsing** | Extracts structured data (skills, experience, projects) from a PDF resume |
| 🧮 **Match Scoring** | Rule-based algorithm scoring each job against the resume |
| 🕳️ **Skill Gap Detection** | Flags skills mentioned in the job description but missing from the resume |
| 🏆 **Job Ranking** | Sorts opportunities by match score and eligibility |
| ✅ **Eligibility Filtering** | Filters out jobs that don't meet experience/location/visa constraints |
| ⚡ **Easy Apply Detection** | Identifies which listings support LinkedIn Easy Apply |
| 📝 **Supported Form Filling** | Auto-fills recognized application fields |
| 🛡️ **Field Validation** | Checks required fields before allowing submission |
| 👀 **Human-in-the-loop Review** | Pauses for review on uncertain or unsupported fields |
| 📊 **Application Tracking** | Logs every submission to CSV for follow-up |

---

## 🧱 Tech Stack

- **Language:** Python 3.10+
- **Browser Automation:** Playwright + Chrome DevTools Protocol (CDP)
- **Resume Parsing:** PDF text extraction
- **Data Storage:** CSV-based pipelines
- **Matching Engine:** Rule-based resume/job comparison

---

## 📂 Project Structure

```text
ai-job-automation/
├── scraper/            # LinkedIn search & job collection (Playwright/CDP)
├── extractor/          # Job description parsing
├── resume/             # Resume PDF parsing & data extraction
├── matcher/            # Match scoring & skill gap detection
├── ranker/             # Job ranking & eligibility filtering
├── apply/              # Easy Apply detection & form filling
├── tracker/            # Application tracking (CSV logs)
├── config/             # Search keywords, filters, credentials (gitignored)
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- Google Chrome installed
- A LinkedIn account

### Installation

```bash
git clone https://github.com/gbhanuprasad5261/ai-job-automation.git
cd ai-job-automation
pip install -r requirements.txt
playwright install chromium
```

### Configuration

1. Add your resume PDF to `resume/`
2. Set search keywords, location, and filters in `config/`
3. Launch Chrome with remote debugging enabled for CDP-based session reuse:
   ```bash
   chrome --remote-debugging-port=9222
   ```

### Run

```bash
python main.py
```

---

## 🛣️ Roadmap

- [ ] LLM-based resume-to-job matching (beyond rule-based scoring)
- [ ] Support for additional job boards beyond LinkedIn
- [ ] Cover letter auto-drafting per job
- [ ] Web dashboard for reviewing ranked jobs and tracking applications
- [ ] Notification system for high-match new postings

---

## ⚠️ Disclaimer

This project automates parts of the job application process for **personal use only**. It is designed to keep a human in the loop for final review and submission, and respects LinkedIn's terms where applicable. Use responsibly and at your own risk.

---

## 👤 Author

**G Bhanu Prasad**
📧 gbhanuprasad1236@gmail.com
🔗 [LinkedIn](https://linkedin.com/in/g-bhanu-prasad-66ab1b225) · [GitHub](https://github.com/gbhanuprasad5261)

---

## 📄 License

This project is licensed under the MIT License.
