# 🤖 AI Job Automation

<div align="center">

### AI-Powered LinkedIn Job Search, Resume Matching & Application Tracking

Automate job discovery, extract job details, analyze resume compatibility, identify skill gaps, rank job opportunities, and track your job applications using **Python** and **Playwright**.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Playwright](https://img.shields.io/badge/Playwright-Automation-green?logo=playwright)
![Git](https://img.shields.io/badge/Git-Version_Control-orange?logo=git)
![GitHub](https://img.shields.io/badge/GitHub-Portfolio-black?logo=github)
![Status](https://img.shields.io/badge/Status-Active-success)
![License](https://img.shields.io/badge/License-MIT-blue)

</div>

---

# 📖 Overview

Finding relevant software engineering jobs, checking resume compatibility, identifying missing skills, and tracking applications manually can be repetitive and time-consuming.

**AI Job Automation** is a Python-based automation project designed to streamline the job-search workflow.

The system currently automates:

- LinkedIn job search
- Job data collection
- Job detail extraction
- Company and location extraction
- Job description extraction
- Resume skill matching
- Weighted compatibility scoring
- Missing skill detection
- Skill-gap analysis
- Job ranking
- Application tracking
- Application pipeline analysis
- Job-search dashboard

The project follows a modular architecture so that advanced AI capabilities can be added in future versions.

---

# ✨ Features

## 🔎 1. LinkedIn Job Search Automation

The project uses **Playwright** to automate LinkedIn job searching.

### Features

- Automated LinkedIn job search
- Chrome DevTools Protocol (CDP) integration
- Persistent Chrome profile
- LinkedIn session reuse
- Automatic job-page navigation
- Job information collection
- Job URL extraction
- Easy Apply detection
- CSV-based job storage

Collected jobs are stored in:

```text
jobs.csv
