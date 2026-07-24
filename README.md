# 🤖 AI Job Automation

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Playwright](https://img.shields.io/badge/Playwright-Automation-green?logo=playwright)
![GitHub](https://img.shields.io/badge/GitHub-Project-black?logo=github)
![Status](https://img.shields.io/badge/Status-Under%20Development-orange)

An AI-powered LinkedIn job automation project built with **Python** and **Playwright** to automate job discovery and intelligently match opportunities against a candidate's resume.

The project is designed to reduce manual effort during job hunting by automating repetitive tasks such as searching for jobs, collecting job information, parsing resumes, and preparing for automated application workflows.

---

# 📌 Features

## ✅ Implemented

- LinkedIn automation using Playwright
- Persistent Chrome login session
- Automatic LinkedIn Jobs navigation
- Job scraping
- Export jobs to CSV
- Resume PDF parsing
- Resume skill extraction
- GitHub project structure
- Modular Python architecture

---

## 🚧 In Progress

- Full job description extraction
- Resume vs Job matching
- Match score generation
- Easy Apply automation
- Automatic resume upload
- Form autofill
- Application reporting

---

# 🏗️ Project Architecture

```
Resume PDF
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
Job Scraper
      │
      ▼
CSV Storage
      │
      ▼
AI Resume Matching
      │
      ▼
Easy Apply Automation
```

---

# 📂 Project Structure

```
AI-Job-Automation/
│
├── auth/
├── data/
├── logs/
├── resume/
├── screenshots/
│
├── connect.py
├── config.py
├── login.py
├── job_scraper.py
├── job_details.py
├── resume_matcher.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

# 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| Python | Programming Language |
| Playwright | Browser Automation |
| pdfplumber | Resume PDF Parsing |
| CSV | Data Storage |
| Git | Version Control |
| GitHub | Repository Hosting |

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

Create a virtual environment

```bash
python -m venv venv
```

Activate the environment

### Windows

```bash
venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# ▶️ Running the Project

Start Chrome with remote debugging enabled.

Run the required modules.

Example:

```bash
python login.py
```

```bash
python job_scraper.py
```

```bash
python resume_matcher.py
```

---

# 📊 Current Progress

| Module | Status |
|---------|:------:|
| Playwright Setup | ✅ |
| LinkedIn Login | ✅ |
| Job Search | ✅ |
| Job Scraper | ✅ |
| CSV Export | ✅ |
| Resume Reader | ✅ |
| Skill Extraction | ✅ |
| Resume Matching | 🚧 |
| Easy Apply | 🚧 |

---

# 📈 Future Enhancements

- AI-powered job ranking
- Skill gap analysis
- Automatic Easy Apply
- Recruiter message generation
- Dashboard for tracking applications
- Email notifications
- Interview preparation suggestions

---

# 🎯 Learning Outcomes

This project demonstrates practical experience with:

- Browser Automation
- Web Scraping
- Python Programming
- File Handling
- Resume Parsing
- Data Processing
- Git & GitHub
- Software Project Structure

---

# 👨‍💻 Author

**G. Bhanu Prasad**

Java Backend Developer | Python Automation Enthusiast

GitHub:
https://github.com/gbhanuprasad5261

LinkedIn:
https://www.linkedin.com/in/g-bhanu-prasad/

---

# ⭐ Support

If you found this project useful, consider giving it a **Star ⭐** on GitHub.

---

# 📄 License

This project is intended for educational and portfolio purposes.
