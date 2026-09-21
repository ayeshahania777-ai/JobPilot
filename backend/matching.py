import re


# ============================================================
# JOBPILOT RANKING ENGINE
# ============================================================

KNOWN_SKILLS = {
    "python",
    "sql",
    "excel",
    "power bi",
    "tableau",
    "pandas",
    "numpy",
    "matplotlib",
    "seaborn",
    "machine learning",
    "deep learning",
    "scikit-learn",
    "tensorflow",
    "pytorch",
    "nlp",
    "natural language processing",
    "computer vision",
    "data science",
    "data analysis",
    "data analytics",
    "statistics",
    "data mining",
    "artificial intelligence",
    "ai",
    "aws",
    "azure",
    "gcp",
    "git",
    "github",
    "docker",
    "kubernetes",
    "java",
    "c++",
    "javascript",
    "typescript",
    "react",
    "node.js",
    "html",
    "css",
    "flask",
    "fastapi",
    "django",
    "spark",
    "hadoop",
    "mlops",
    "recommendation systems",
    "a/b testing",
}


TECHNICAL_SKILLS = {
    "python",
    "sql",
    "excel",
    "power bi",
    "tableau",
    "pandas",
    "numpy",
    "matplotlib",
    "seaborn",
    "machine learning",
    "deep learning",
    "scikit-learn",
    "tensorflow",
    "pytorch",
    "nlp",
    "natural language processing",
    "computer vision",
    "statistics",
    "data mining",
    "aws",
    "azure",
    "gcp",
    "git",
    "github",
    "docker",
    "kubernetes",
    "java",
    "c++",
    "javascript",
    "typescript",
    "react",
    "node.js",
    "html",
    "css",
    "flask",
    "fastapi",
    "django",
    "spark",
    "hadoop",
    "mlops",
    "recommendation systems",
    "a/b testing",
}


# ============================================================
# CAREER ROLES
# ============================================================

ROLE_KEYWORDS = {

    "machine learning": [
        "machine learning",
        "ml engineer",
        "machine learning engineer",
        "ml engineering",
        "ml intern",
        "machine learning intern",
        "machine learning developer",
        "ml developer",
        "machine learning development",
    ],

    "data science": [
        "data scientist",
        "data science",
        "data science intern",
        "data scientist intern",
        "data science developer",
        "data science internship",
    ],

    "data analytics": [
        "data analyst",
        "data analytics",
        "data analyst intern",
        "business intelligence",
        "bi analyst",
        "business analyst",
        "analytics intern",
        "data analytics intern",
    ],

    "artificial intelligence": [
        "artificial intelligence",
        "ai engineer",
        "ai engineering",
        "ai intern",
        "ai developer",
        "generative ai",
        "genai",
    ],

    "python development": [
        "python developer",
        "python development",
        "python intern",
        "python engineer",
        "python developer intern",
    ],

    "software development": [
        "software engineer",
        "software developer",
        "software development",
        "software engineering",
    ],
}


# ============================================================
# DOMAINS
# ============================================================

DOMAIN_KEYWORDS = {

    "machine learning": [
        "machine learning",
        "ml",
        "classification",
        "regression",
        "clustering",
        "prediction",
        "predictive modeling",
        "scikit-learn",
    ],

    "data science": [
        "data science",
        "data scientist",
        "data analysis",
        "data analytics",
        "statistics",
        "data mining",
        "predictive analysis",
    ],

    "data analytics": [
        "data analyst",
        "data analytics",
        "data analysis",
        "business intelligence",
        "dashboard",
        "reporting",
        "visualization",
        "power bi",
        "tableau",
    ],

    "artificial intelligence": [
        "artificial intelligence",
        "ai",
        "machine learning",
        "deep learning",
        "generative ai",
        "nlp",
    ],

    "python development": [
        "python",
        "python developer",
        "python development",
        "flask",
        "fastapi",
        "django",
    ],
}


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_text(text):

    if not text:
        return ""

    text = str(text).lower()

    replacements = {
        "scikit learn": "scikit-learn",
        "scikitlearn": "scikit-learn",
        "power-bi": "power bi",
        "machine-learning": "machine learning",
        "deep-learning": "deep learning",
        "data-science": "data science",
        "data-analysis": "data analysis",
        "data-analytics": "data analytics",
        "natural-language-processing": "natural language processing",
        "computer-vision": "computer vision",
        "business-intelligence": "business intelligence",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# SKILL EXTRACTION
# ============================================================

def extract_skills(text):

    text = normalize_text(text)

    found_skills = set()

    for skill in KNOWN_SKILLS:

        pattern = (
            r"(?<!\w)"
            + re.escape(skill)
            + r"(?!\w)"
        )

        if re.search(pattern, text):
            found_skills.add(skill)

    return sorted(found_skills)


def extract_technical_skills(text):

    text = normalize_text(text)

    found_skills = set()

    for skill in TECHNICAL_SKILLS:

        pattern = (
            r"(?<!\w)"
            + re.escape(skill)
            + r"(?!\w)"
        )

        if re.search(pattern, text):
            found_skills.add(skill)

    return sorted(found_skills)


# ============================================================
# ROLE DETECTION
# ============================================================

def detect_roles(text):

    text = normalize_text(text)

    detected = set()

    for role, keywords in ROLE_KEYWORDS.items():

        for keyword in keywords:

            if keyword in text:
                detected.add(role)
                break

    return detected


# ============================================================
# DOMAIN DETECTION
# ============================================================

def detect_domains(text):

    text = normalize_text(text)

    detected = set()

    for domain, keywords in DOMAIN_KEYWORDS.items():

        for keyword in keywords:

            if keyword in text:
                detected.add(domain)
                break

    return detected


# ============================================================
# TITLE SCORE
# Maximum = 25
# ============================================================

def calculate_title_score(
    user_skills,
    job_title
):

    title = normalize_text(job_title)

    if not title:
        return 0

    user_roles = detect_roles(user_skills)
    job_roles = detect_roles(title)

    if user_roles.intersection(job_roles):

        return 25

    user_skill_set = set(
        extract_skills(user_skills)
    )

    title_skill_set = set(
        extract_skills(title)
    )

    if user_skill_set.intersection(title_skill_set):

        return 15

    return 0


# ============================================================
# SKILL SCORE
# Maximum = 40
# ============================================================

def calculate_skill_score(
    user_skills,
    job_skills
):

    user_skill_set = set(
        extract_skills(user_skills)
    )

    job_skill_set = set(
        extract_skills(job_skills)
    )

    if not job_skill_set:

        return 0, set(), set()

    matched = (
        user_skill_set
        .intersection(job_skill_set)
    )

    missing = (
        job_skill_set
        .difference(user_skill_set)
    )

    # Each matching skill contributes 8 points.
    # Maximum skill contribution = 40.
    score = len(matched) * 8

    score = min(score, 40)

    return (
        score,
        matched,
        missing
    )


# ============================================================
# TECHNICAL SKILL GAP
# ============================================================

def calculate_skill_gap(
    user_skills,
    job_skills,
    job_description
):

    user_skill_set = set(
        extract_technical_skills(user_skills)
    )

    job_text = (
        normalize_text(job_skills)
        + " "
        + normalize_text(job_description)
    )

    job_skill_set = set(
        extract_technical_skills(job_text)
    )

    missing = (
        job_skill_set
        .difference(user_skill_set)
    )

    return sorted(missing)


# ============================================================
# DESCRIPTION SCORE
# Maximum = 10
# ============================================================

def calculate_description_score(
    user_skills,
    job_description
):

    user_skill_set = set(
        extract_skills(user_skills)
    )

    description_skill_set = set(
        extract_skills(job_description)
    )

    if not description_skill_set:
        return 0

    matches = (
        user_skill_set
        .intersection(description_skill_set)
    )

    if not matches:
        return 0

    score = (
        len(matches)
        / len(description_skill_set)
    ) * 10

    return min(score, 10)


# ============================================================
# DOMAIN SCORE
# Maximum = 15
# ============================================================

def calculate_domain_score(
    user_skills,
    job_text
):

    user_domains = detect_domains(
        user_skills
    )

    job_domains = detect_domains(
        job_text
    )

    if not user_domains or not job_domains:
        return 0

    common_domains = (
        user_domains
        .intersection(job_domains)
    )

    if not common_domains:
        return 0

    score = (
        len(common_domains)
        / len(user_domains)
    ) * 15

    return min(score, 15)


# ============================================================
# JOB TYPE SCORE
# Maximum = 5
# ============================================================

def calculate_job_type_score(
    user_job_type,
    job_type
):

    user_type = normalize_text(
        user_job_type
    )

    current_type = normalize_text(
        job_type
    )

    if not user_type or not current_type:
        return 0

    if (
        user_type in current_type
        or current_type in user_type
        or (
            user_type in ["intern", "internship"]
            and current_type in ["intern", "internship"]
        )
    ):
        return 5

    return 0


# ============================================================
# WORK MODE SCORE
# Maximum = 5
# ============================================================

def calculate_work_mode_score(
    user_work_mode,
    job_work_mode
):

    user_mode = normalize_text(
        user_work_mode
    )

    current_mode = normalize_text(
        job_work_mode
    )

    if not user_mode or not current_mode:
        return 0

    if (
        user_mode in current_mode
        or current_mode in user_mode
    ):
        return 5

    return 0


# ============================================================
# LOCATION SCORE
# Maximum = 5
# ============================================================

def calculate_location_score(
    user_location,
    job_location,
    job_work_mode
):

    user_location = normalize_text(
        user_location
    )

    job_location = normalize_text(
        job_location
    )

    job_work_mode = normalize_text(
        job_work_mode
    )

    # No location preference
    if not user_location:

        return 5

    # User explicitly wants remote
    if user_location == "remote":

        if "remote" in job_work_mode:
            return 5

        return 0

    # Location matches
    if user_location in job_location:

        return 5

    # Remote jobs can satisfy a location preference
    if "remote" in job_work_mode:

        return 5

    return 0


# ============================================================
# MAIN RANKING FUNCTION
# ============================================================

def calculate_skill_match(
    user_skills,
    job_skills,
    job_description="",
    job_title="",
    job_type="",
    work_mode="",
    location="",
    user_job_type="",
    user_work_mode="",
    user_location=""
):

    job_text = (
        normalize_text(job_title)
        + " "
        + normalize_text(job_skills)
        + " "
        + normalize_text(job_description)
    )

    # --------------------------------------------------------
    # 1. SKILL MATCH
    # --------------------------------------------------------

    (
        skill_score,
        matched_skills,
        _
    ) = calculate_skill_score(
        user_skills,
        job_skills
    )

    # --------------------------------------------------------
    # 2. TITLE / ROLE MATCH
    # --------------------------------------------------------

    title_score = calculate_title_score(
        user_skills,
        job_title
    )

    # --------------------------------------------------------
    # 3. DOMAIN MATCH
    # --------------------------------------------------------

    domain_score = calculate_domain_score(
        user_skills,
        job_text
    )

    # --------------------------------------------------------
    # 4. DESCRIPTION MATCH
    # --------------------------------------------------------

    description_score = calculate_description_score(
        user_skills,
        job_description
    )

    # --------------------------------------------------------
    # 5. JOB TYPE
    # --------------------------------------------------------

    job_type_score = calculate_job_type_score(
        user_job_type,
        job_type
    )

    # --------------------------------------------------------
    # 6. WORK MODE
    # --------------------------------------------------------

    work_mode_score = calculate_work_mode_score(
        user_work_mode,
        work_mode
    )

    # --------------------------------------------------------
    # 7. LOCATION
    # --------------------------------------------------------

    location_score = calculate_location_score(
        user_location,
        location,
        work_mode
    )

    # --------------------------------------------------------
    # 8. SKILL GAP
    # --------------------------------------------------------

    missing_skills = calculate_skill_gap(
        user_skills,
        job_skills,
        job_description
    )

    # --------------------------------------------------------
    # TOTAL
    # --------------------------------------------------------

    total_score = (
        skill_score
        + title_score
        + domain_score
        + description_score
        + job_type_score
        + work_mode_score
        + location_score
    )

    total_score = round(
        min(total_score, 100)
    )

    # --------------------------------------------------------
    # LOW MATCH PROTECTION
    # Prevent unrelated jobs from receiving high scores
    # just because they are remote/internship jobs.
    # --------------------------------------------------------

    if (
        len(matched_skills) == 0
        and title_score == 0
        and domain_score == 0
    ):

        total_score = min(
            total_score,
            20
        )

    elif (
        len(matched_skills) == 1
        and title_score == 0
        and domain_score == 0
    ):

        total_score = min(
            total_score,
            45
        )

    return {

        "match_score":
            total_score,

        "matched_skills":
            sorted(matched_skills),

        "missing_skills":
            missing_skills
    }