# 🤖 AI Job Automation

<div align="center">

### AI-Powered LinkedIn Job Search & Resume Matching Automation

Automate job discovery, analyze resume compatibility, identify skill gaps, and streamline your job search using **Python** and **Playwright**.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Playwright](https://img.shields.io/badge/Playwright-Automation-green?logo=playwright)
![GitHub](https://img.shields.io/badge/GitHub-Portfolio-black?logo=github)
![Status](https://img.shields.io/badge/Status-Active-success)
![License](https://img.shields.io/badge/License-MIT-blue)

</div>

---

# 📖 Overview

Finding and applying for software engineering jobs manually is repetitive and time-consuming.

**AI Job Automation** is a Python-based automation project that simplifies the job application process by automating LinkedIn job search, extracting job information, parsing resumes, matching skills, and preparing for AI-powered application automation.

The project is designed with a modular architecture, making it scalable for future AI enhancements and additional job platforms.

---

# ✨ Features

## ✅ Implemented

### 🔹 LinkedIn Automation

- Automated LinkedIn job search
- Chrome DevTools Protocol (CDP) integration
- Persistent login session
- Automatic navigation to LinkedIn Jobs
- Job data extraction

### 🔹 Job Extraction

Extracts:

- Job Title
- Company Name
- Location
- Easy Apply Status
- Job URL

Exports all collected jobs into CSV format.

---

### 🔹 Resume Analysis

- Resume PDF parsing
- Resume text extraction
- Technical skill extraction
- Resume skill database
- Resume vs Job skill comparison
- Missing skills identification

---

### 🔹 AI Job Analysis

- Resume matching
- Job analysis report generation
- CSV export
- Best matching job identification

---

# 🚧 Upcoming Features

- One-click Easy Apply Automation
- Automatic Resume Upload
- Form Autofill
- AI Resume Optimization
- AI Cover Letter Generator
- Recruiter Message Generator
- Application Tracking Dashboard
- Email Notifications
- Multi-Platform Job Search

---

# 🏗️ System Architecture

```text
                Resume.pdf
                     │
                     ▼
              Resume Parser
                     │
                     ▼
            Skill Extraction
                     │
                     ▼
         LinkedIn Job Search
                     │
                     ▼
            Job Information
                     │
                     ▼
               CSV Storage
                     │
                     ▼
          AI Resume Matching
                     │
                     ▼
        Missing Skills Analysis
                     │
                     ▼
        Best Job Recommendation
                     │
                     ▼
         Easy Apply Automation
```

---

# 📂 Project Structure

```text
AI-Job-Automation/
│
├── data/
│   ├── jobs.csv
│   ├── job_details.csv
│   └── job_analysis.csv
│
├── resume/
│   └── resume.pdf
│
├── screenshots/
│
├── config.py
├── connect.py
├── login.py
├── job_search.py
├── job_details.py
├── job_analyzer.py
├── resume_matcher.py
├── skill_matcher.py
├── test_matcher.py
├── start_chrome.bat
├── requirements.txt
├── README.md
└── .gitignore
```

---

# ⚙️ Technologies Used

| Technology | Purpose |
|------------|----------|
| Python | Core Programming |
| Playwright | Browser Automation |
| pdfplumber | Resume Parsing |
| CSV | Data Storage |
| Git | Version Control |
| GitHub | Source Code Hosting |

---

# 🚀 Installation

Clone the repository

```bash
git clone https://github.com/gbhanuprasad5261/AI-Job-Automation.git
```

Navigate into the project

```bash
cd AI-Job-Automation
```

Create Virtual Environment

```bash
python -m venv venv
```

Activate Virtual Environment

### Windows

```bash
venv\Scripts\activate
```

Install Dependencies

```bash
pip install -r requirements.txt
```

---

# ▶️ Usage

## Start Chrome with Remote Debugging

```bash
start_chrome.bat
```

---

## Search Jobs

```bash
python job_search.py
```

---

## Extract Job Details

```bash
python job_details.py
```

---

## Analyze Jobs

```bash
python job_analyzer.py
```

---

## Resume Matching

```bash
python resume_matcher.py
```

---

# 📊 Sample Output

```text
==========================================
AI JOB ANALYSIS COMPLETED
==========================================

Jobs analyzed : 20

Best Match

Title      : Java Backend Developer
Company    : ABC Technologies
Match Score: 92%

Missing Skills:
Docker
AWS
```

---

# 📈 Project Progress

| Module | Status |
|----------|:------:|
| Playwright Setup | ✅ |
| LinkedIn Automation | ✅ |
| Chrome CDP Integration | ✅ |
| Job Search | ✅ |
| Job Extraction | ✅ |
| CSV Export | ✅ |
| Resume Parsing | ✅ |
| Skill Extraction | ✅ |
| Resume Matching | ✅ |
| AI Job Analysis | ✅ |
| Missing Skills Detection | ✅ |
| Best Job Recommendation | 🚧 |
| Easy Apply Automation | 🚧 |

---

# 🎯 Skills Demonstrated

This project demonstrates practical experience with:

- Python Programming
- Browser Automation
- Playwright
- Resume Parsing
- Web Scraping
- CSV Processing
- File Handling
- Software Design
- Git & GitHub
- AI-Based Resume Matching

---

# 📸 Screenshots

> Screenshots will be added as the project progresses.

```
screenshots/
│
├── linkedin_jobs.png
├── job_search.png
├── job_details.png
├── job_analysis.png
└── resume_matching.png
```

---

# 🛣️ Roadmap

- AI Job Ranking
- Skill Gap Analysis
- One-Click Easy Apply
- Resume Optimization
- Recruiter Message Generator
- Dashboard & Analytics
- Email Notifications
- Support for Multiple Job Portals

---

# 🤝 Contributing

Contributions are welcome.

1. Fork the repository
2. Create a feature branch

```bash
git checkout -b feature-name
```

3. Commit your changes

```bash
git commit -m "Add new feature"
```

4. Push the branch

```bash
git push origin feature-name
```

5. Open a Pull Request

---

# 👨‍💻 Author

## G. Bhanu Prasad

**Java Backend Developer | Python Automation Enthusiast**

GitHub

https://github.com/gbhanuprasad5261

LinkedIn

https://www.linkedin.com/in/g-bhanu-prasad/

---

# ⭐ Support

If you found this project useful, please consider giving it a ⭐ on GitHub.

It motivates me to build more open-source projects.

---

# 📄 License

This project is licensed under the **MIT License**.

---

## 💡 Project Vision

The long-term goal of this project is to build an intelligent AI-powered job assistant capable of searching jobs, analyzing resume compatibility, identifying skill gaps, generating personalized application materials, and automating suitable job applications while keeping the user in control of the process.


