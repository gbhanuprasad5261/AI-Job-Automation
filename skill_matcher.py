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
# Known Job Skills
# ---------------------------------------

job_skill_weights = {

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

    # Java concepts
    "oop": 5,
    "multithreading": 7,
    "dsa": 5,

    # Databases
    "mongodb": 6,
    "postgresql": 6,
    "redis": 6,

    # Cloud
    "aws": 8,
    "azure": 7,
    "gcp": 7,

    # DevOps
    "docker": 7,
    "kubernetes": 8,
    "jenkins": 5,
    "ci/cd": 5,
    "linux": 4,

    # Messaging
    "kafka": 7,
    "rabbitmq": 6,

    # Development tools
    "git": 3,
    "github": 2,
    "maven": 4,
    "postman": 3,

    # Testing
    "junit": 4,
    "mockito": 4,

    # Frontend
    "javascript": 3,
    "html": 2,
    "css": 2,
    "angular": 4,
    "react": 4,

    # Other languages
    "python": 4,

    # Development practices
    "sdlc": 2,
    "agile": 2,
    "waterfall": 1,
}


# ---------------------------------------
# Extract Job Skills
# ---------------------------------------

def extract_job_skills(text):

    text = text.lower()

    found = set()

    for skill in job_skill_weights:

        pattern = r"\b" + re.escape(skill) + r"\b"

        if re.search(pattern, text):
            found.add(skill)

    return found


# ---------------------------------------
# Match Resume Against Job
# ---------------------------------------

def match_resume(job_description):

    job_skills = extract_job_skills(job_description)

    matched = resume_skills.intersection(job_skills)

    missing = job_skills - resume_skills

    # ---------------------------------------
    # No skills detected
    # ---------------------------------------

    if not job_skills:
        return 0, matched, missing

    # ---------------------------------------
    # Weighted score
    # ---------------------------------------

    total_weight = 0
    matched_weight = 0

    for skill in job_skills:

        weight = job_skill_weights.get(
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