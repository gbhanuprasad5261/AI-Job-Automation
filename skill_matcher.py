import re

resume_skills = {
    "java",
    "spring",
    "spring boot",
    "spring mvc",
    "spring data jpa",
    "hibernate",
    "jdbc",
    "mysql",
    "sql",
    "rest api",
    "git",
    "github",
    "maven",
    "postman",
    "junit",
    "mockito",
    "microservices",
    "oop",
    "multithreading",
    "javalin",
    "sdlc",
    "angular js basics",
    "waterfall model",
    "agile model",
    "dsa",
}


def extract_skills(text):
    text = text.lower()
    found = set()

    for skill in resume_skills:
        if re.search(r"\b" + re.escape(skill) + r"\b", text):
            found.add(skill)

    return found


def match_resume(job_description):
    job_skills = extract_skills(job_description)

    matched = resume_skills.intersection(job_skills)
    missing = job_skills - resume_skills

    score = 0
    if job_skills:
        score = round((len(matched) / len(job_skills)) * 100)

    return score, matched, missing