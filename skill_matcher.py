import re


# ---------------------------------------
# Resume Skills
# ---------------------------------------

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


# ---------------------------------------
# Skill Weights
# ---------------------------------------

skill_weights = {

    # Core Java Backend
    "java": 10,
    "spring": 8,
    "spring boot": 10,
    "spring mvc": 7,
    "spring data jpa": 8,
    "hibernate": 7,
    "jdbc": 6,
    "mysql": 6,
    "sql": 8,
    "rest api": 8,
    "microservices": 10,

    # Java Concepts
    "oop": 5,
    "multithreading": 7,

    # Development Tools
    "git": 3,
    "github": 2,
    "maven": 4,
    "postman": 3,

    # Testing
    "junit": 4,
    "mockito": 4,

    # Other technologies
    "javalin": 3,
    "spring mvc": 7,
    "angular js basics": 2,

    # Development practices
    "sdlc": 2,
    "agile model": 2,
    "waterfall model": 1,

    # DSA
    "dsa": 5,
}


# ---------------------------------------
# Extract Skills
# ---------------------------------------

def extract_skills(text):

    text = text.lower()

    found = set()

    for skill in resume_skills:

        pattern = r"\b" + re.escape(skill) + r"\b"

        if re.search(pattern, text):

            found.add(skill)

    return found


# ---------------------------------------
# Match Resume Against Job
# ---------------------------------------

def match_resume(job_description):

    job_skills = extract_skills(job_description)

    matched = resume_skills.intersection(job_skills)

    missing = job_skills - resume_skills

    # ---------------------------------------
    # Calculate weighted score
    # ---------------------------------------

    if not job_skills:
        return 0, matched, missing

    total_weight = 0
    matched_weight = 0

    for skill in job_skills:

        weight = skill_weights.get(
            skill,
            3
        )

        total_weight += weight

        if skill in matched:
            matched_weight += weight

    score = round(
        (matched_weight / total_weight) * 100
    )

    return score, matched, missing