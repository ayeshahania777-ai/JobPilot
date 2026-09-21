import re
from pypdf import PdfReader


# ============================================================
# TECHNICAL SKILLS JOBPILOT CAN DETECT
# ============================================================

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
# NORMALIZE TEXT
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
        "natural-language-processing":
            "natural language processing",
        "computer-vision":
            "computer vision",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# EXTRACT SKILLS FROM TEXT
# ============================================================

def extract_skills(text):

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
# EXTRACT TEXT FROM PDF
# ============================================================

def extract_text_from_pdf(file_path):

    reader = PdfReader(file_path)

    pages_text = []

    for page in reader.pages:

        text = page.extract_text()

        if text:
            pages_text.append(text)

    return "\n".join(pages_text)


# ============================================================
# EXTRACT SKILLS FROM RESUME PDF
# ============================================================

def extract_resume_skills(file_path):

    resume_text = extract_text_from_pdf(
        file_path
    )

    skills = extract_skills(
        resume_text
    )

    return {
        "skills": skills,
        "text_length": len(resume_text),
        "resume_text": resume_text
    }