import requests
import re
from datetime import datetime


HIMALAYAS_API_URL = "https://himalayas.app/jobs/api/search"


def fetch_himalayas_jobs(
    query="python",
    employment_type="Intern",
    pages=3
):
    """
    Fetch real remote jobs from the Himalayas public API.
    No API key is required.
    """

    all_jobs = []

    for page in range(1, pages + 1):

        params = {
            "q": query,
            "employment_type": employment_type,
            "sort": "recent",
            "page": page
        }

        try:
            response = requests.get(
                HIMALAYAS_API_URL,
                params=params,
                timeout=20
            )

            response.raise_for_status()

            data = response.json()

            jobs = data.get("jobs", [])

            for job in jobs:

                all_jobs.append({
                    "title": job.get(
                        "title",
                        ""
                    ),

                    "company": job.get(
                        "companyName",
                        ""
                    ),

                    "location": ", ".join(
                        job.get(
                            "locationRestrictions",
                            []
                        )
                    ),

                    "work_mode": "Remote",

                    "job_type": job.get(
                        "employmentType",
                        "Intern"
                    ),

                    "salary": format_salary(job),

                    "description": clean_description(
                        job.get(
                            "description",
                            ""
                        )
                    ),

                    "skills": extract_skills(job),

                    "source": "Himalayas",

                    "url": job.get(
                        "applicationLink",
                        job.get(
                            "guid",
                            ""
                        )
                    ),

                    "posted_date": format_date(
                        job.get("pubDate")
                    ),

                    "external_id": job.get(
                        "guid",
                        ""
                    )
                })

        except requests.RequestException as error:

            print(
                f"Error fetching Himalayas page {page}:",
                error
            )

    return all_jobs


def format_salary(job):
    """
    Convert salary information into a readable string.
    """

    minimum = job.get("minSalary")
    maximum = job.get("maxSalary")
    currency = job.get("currency")
    period = job.get("salaryPeriod")

    if minimum is None and maximum is None:
        return "Not specified"

    currency = currency or ""

    period = period or "annual"

    if minimum is not None and maximum is not None:

        return (
            f"{currency} "
            f"{minimum} - "
            f"{maximum} / "
            f"{period}"
        )

    if minimum is not None:

        return (
            f"{currency} "
            f"{minimum} / "
            f"{period}"
        )

    return (
        f"{currency} "
        f"{maximum} / "
        f"{period}"
    )


def clean_description(description):
    """
    Remove HTML tags from the job description.
    """

    if not description:
        return ""

    description = re.sub(
        r"<[^>]+>",
        " ",
        description
    )

    description = re.sub(
        r"\s+",
        " ",
        description
    )

    return description.strip()


def extract_skills(job):
    """
    Extract useful skills from Himalayas
    categories and parent categories.
    """

    categories = job.get(
        "categories",
        []
    )

    parent_categories = job.get(
        "parentCategories",
        []
    )

    all_categories = (
        categories
        + parent_categories
    )

    skills = []

    for category in all_categories:

        category = category.replace(
            "-",
            " "
        )

        category = category.strip()

        if category:
            skills.append(category)

    return ", ".join(skills)


def format_date(timestamp):
    """
    Convert Himalayas Unix timestamp
    into YYYY-MM-DD.
    """

    if not timestamp:
        return ""

    try:

        return datetime.fromtimestamp(
            timestamp
        ).strftime("%Y-%m-%d")

    except (ValueError, TypeError, OSError):

        return ""


def get_default_jobs():
    """
    Fetch several types of jobs useful
    for JobPilot.
    """

    queries = [
        "python",
        "data analyst",
        "data science",
        "machine learning",
        "SQL"
    ]

    all_jobs = []

    for query in queries:

        print(
            f"🔎 Searching for: {query}"
        )

        jobs = fetch_himalayas_jobs(
            query=query,
            employment_type="Intern",
            pages=2
        )

        all_jobs.extend(jobs)

    return remove_duplicates(
        all_jobs
    )


def remove_duplicates(jobs):
    """
    Remove duplicate jobs using
    the Himalayas GUID.
    """

    unique_jobs = {}

    for job in jobs:

        job_id = job.get(
            "external_id"
        )

        if not job_id:

            job_id = (
                job.get("title", "")
                + "_"
                + job.get("company", "")
            )

        unique_jobs[job_id] = job

    return list(
        unique_jobs.values()
    )