from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from database import SessionLocal, engine
from models import Base, Profile, Job, Application, AgentRun

from matching import (
    calculate_skill_match,
    extract_technical_skills,
    normalize_text,
    TECHNICAL_SKILLS
)

from resume_parser import extract_resume_skills

from datetime import datetime
import requests
import re
import os
import uuid


# =========================================================
# DATABASE
# =========================================================

Base.metadata.create_all(bind=engine)


# =========================================================
# FASTAPI
# =========================================================

app = FastAPI(
    title="JobPilot API",
    description="AI-powered job discovery and application assistant",
    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# =========================================================
# GENERAL HELPERS
# =========================================================

def normalize_job_type(job_type):

    job_type = normalize_text(
        job_type or ""
    )

    if job_type in [
        "intern",
        "internship"
    ]:
        return "internship"

    if (
        "full-time" in job_type
        or "full time" in job_type
    ):
        return "full-time"

    if (
        "part-time" in job_type
        or "part time" in job_type
    ):
        return "part-time"

    return job_type


def extract_salary_values(text):

    if not text:
        return []

    text = str(text)

    matches = re.findall(
        r"\d+(?:,\d{3})*(?:\.\d+)?",
        text
    )

    values = []

    for value in matches:

        try:
            values.append(
                float(
                    value.replace(",", "")
                )
            )
        except:
            pass

    return values


def is_real_job(job):

    if not job:
        return False

    title = normalize_text(
        job.title or ""
    )

    company = normalize_text(
        job.company or ""
    )

    if not title:
        return False

    # Exclude obvious education/training listings.
    blocked_words = [
        "course",
        "courses",
        "training",
        "certificate",
        "certification",
        "certifications",
        "bootcamp",
        "workshop",
        "weiterbildung",
        "thesis",
        "learn",
        "learning program"
    ]

    text = (
        title
        + " "
        + company
    )

    for word in blocked_words:

        if word in text:
            return False

    return True


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():

    return {
        "message": "JobPilot API is running 🚀",
        "status": "online"
    }


# =========================================================
# GET PROFILE
# =========================================================

@app.get("/profile")
def get_profile():

    db = SessionLocal()

    try:

        profile = (
            db.query(Profile)
            .order_by(
                Profile.id.desc()
            )
            .first()
        )

        if not profile:

            return {
                "message": "No profile found."
            }

        return {
            "id": profile.id,
            "name": profile.name,
            "email": profile.email,
            "skills": profile.skills,
            "job_type": profile.job_type,
            "work_mode": profile.work_mode,
            "location": profile.location,
            "salary": profile.salary,
            "experience": profile.experience,
            "applications_per_day":
                profile.applications_per_day,
            "agent_enabled":
                profile.agent_enabled,
            "resume_filename":
                profile.resume_filename
        }

    finally:

        db.close()


# =========================================================
# CREATE / UPDATE PROFILE
# =========================================================

@app.post("/profile")
def create_or_update_profile(
    data: dict
):

    db = SessionLocal()

    try:

        profile = (
            db.query(Profile)
            .order_by(
                Profile.id.desc()
            )
            .first()
        )

        try:

            applications_per_day = int(
                data.get(
                    "applications_per_day",
                    5
                )
            )

        except:

            applications_per_day = 5

        if applications_per_day < 1:

            applications_per_day = 1

        if applications_per_day > 20:

            applications_per_day = 20

        if profile:

            profile.name = data.get(
                "name",
                profile.name
            )

            profile.email = data.get(
                "email",
                profile.email
            )

            profile.skills = data.get(
                "skills",
                profile.skills
            )

            profile.job_type = data.get(
                "job_type",
                profile.job_type
            )

            profile.work_mode = data.get(
                "work_mode",
                profile.work_mode
            )

            profile.location = data.get(
                "location",
                profile.location
            )

            profile.salary = data.get(
                "salary",
                profile.salary
            )

            profile.experience = data.get(
                "experience",
                profile.experience
            )

            profile.applications_per_day = (
                applications_per_day
            )

            profile.agent_enabled = data.get(
                "agent_enabled",
                profile.agent_enabled
            )

        else:

            profile = Profile(

                name=data.get(
                    "name",
                    ""
                ),

                email=data.get(
                    "email",
                    ""
                ),

                skills=data.get(
                    "skills",
                    ""
                ),

                job_type=data.get(
                    "job_type",
                    "Internship"
                ),

                work_mode=data.get(
                    "work_mode",
                    "Remote"
                ),

                location=data.get(
                    "location",
                    ""
                ),

                salary=data.get(
                    "salary",
                    ""
                ),

                experience=data.get(
                    "experience",
                    "Fresher"
                ),

                applications_per_day=
                    applications_per_day,

                agent_enabled=data.get(
                    "agent_enabled",
                    False
                )
            )

            db.add(profile)

        db.commit()

        db.refresh(profile)

        return {
            "message":
                "Profile saved successfully.",

            "profile": {
                "id": profile.id,
                "name": profile.name,
                "email": profile.email,
                "skills": profile.skills,
                "job_type": profile.job_type,
                "work_mode": profile.work_mode,
                "location": profile.location,
                "salary": profile.salary,
                "experience": profile.experience,
                "applications_per_day":
                    profile.applications_per_day,
                "agent_enabled":
                    profile.agent_enabled,
                "resume_filename":
                    profile.resume_filename
            }
        }

    finally:

        db.close()


# =========================================================
# RESUME UPLOAD
# =========================================================

@app.post("/profile/{profile_id}/resume")
async def upload_resume(
    profile_id: int,
    file: UploadFile = File(...)
):

    db = SessionLocal()

    try:

        profile = (
            db.query(Profile)
            .filter(
                Profile.id == profile_id
            )
            .first()
        )

        if not profile:

            raise HTTPException(
                status_code=404,
                detail="Profile not found."
            )

        if not file.filename:

            raise HTTPException(
                status_code=400,
                detail="Please select a resume."
            )

        if not file.filename.lower().endswith(
            ".pdf"
        ):

            raise HTTPException(
                status_code=400,
                detail="Only PDF resumes are supported."
            )

        contents = await file.read()

        if len(contents) > 5 * 1024 * 1024:

            raise HTTPException(
                status_code=400,
                detail="Resume must be smaller than 5 MB."
            )

        upload_dir = "uploads"

        os.makedirs(
            upload_dir,
            exist_ok=True
        )

        unique_filename = (
            str(uuid.uuid4())
            + "_"
            + file.filename
        )

        file_path = os.path.join(
            upload_dir,
            unique_filename
        )

        with open(
            file_path,
            "wb"
        ) as output_file:

            output_file.write(contents)

        # -------------------------------------------------
        # EXTRACT RESUME TEXT
        # -------------------------------------------------

        try:

            resume_text = extract_resume_text(
                file_path
            )

        except Exception:

            resume_text = ""

        # -------------------------------------------------
        # EXTRACT SKILLS
        # -------------------------------------------------

        try:

            resume_skills = extract_skills_from_resume(
                resume_text
            )

        except Exception:

            resume_skills = []

        existing_skills = []

        if profile.skills:

            existing_skills = [
                skill.strip()
                for skill in profile.skills.split(",")
                if skill.strip()
            ]

        combined_skills = []

        for skill in (
            existing_skills
            + resume_skills
        ):

            if skill.lower() not in [
                x.lower()
                for x in combined_skills
            ]:

                combined_skills.append(skill)

        profile.skills = ", ".join(
            combined_skills
        )

        profile.resume_filename = (
            unique_filename
        )

        db.commit()

        db.refresh(profile)

        return {

            "message":
                "Resume uploaded successfully.",

            "filename":
                unique_filename,

            "extracted_skills":
                resume_skills,

            "skills":
                profile.skills

        }

    finally:

        db.close()


# =========================================================
# DISCOVER JOBS
# =========================================================

@app.post("/discover-jobs")
def discover_jobs():

    db = SessionLocal()

    try:

        url = (
            "https://himalayas.app/jobs/api"
            "?limit=100"
        )

        response = requests.get(
            url,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        jobs_data = data.get(
            "jobs",
            []
        )

        added = 0

        for job_data in jobs_data:

            title = job_data.get(
                "title",
                ""
            )

            company = job_data.get(
                "companyName",
                ""
            )

            if not title:
                continue

            application_url = (
                job_data.get(
                    "applicationLink",
                    ""
                )
                or job_data.get(
                    "guid",
                    ""
                )
            )

            existing = None

            if application_url:

                existing = (
                    db.query(Job)
                    .filter(
                        Job.url
                        == application_url
                    )
                    .first()
                )

            if existing:

                continue

            employment_type = (
                job_data.get(
                    "employmentType",
                    ""
                )
            )

            if employment_type:

                if (
                    "intern" in
                    employment_type.lower()
                ):

                    employment_type = "Internship"

            location_restrictions = (
                job_data.get(
                    "locationRestrictions",
                    []
                )
            )

            if isinstance(
                location_restrictions,
                list
            ):

                location = ", ".join(
                    str(x)
                    for x in location_restrictions
                )

            else:

                location = str(
                    location_restrictions
                    or "Remote"
                )

            if not location:

                location = "Remote"

            salary = "Not specified"

            min_salary = job_data.get(
                "minSalary"
            )

            max_salary = job_data.get(
                "maxSalary"
            )

            if (
                min_salary is not None
                and max_salary is not None
            ):

                salary = (
                    f"{min_salary} - "
                    f"{max_salary}"
                )

            elif min_salary is not None:

                salary = str(
                    min_salary
                )

            description = (
                job_data.get(
                    "description",
                    ""
                )
            )

            categories = job_data.get(
                "categories",
                []
            )

            skills = ""

            if isinstance(
                categories,
                list
            ):

                skills = ", ".join(
                    str(x)
                    for x in categories
                )

            job = Job(

                title=title,

                company=company,

                location=location,

                work_mode="Remote",

                job_type=employment_type,

                salary=salary,

                description=description,

                skills=skills,

                source="Himalayas",

                url=application_url,

                posted_date=str(
                    job_data.get(
                        "pubDate",
                        ""
                    )
                )
            )

            db.add(job)

            added += 1

        db.commit()

        return {
            "message":
                "Job discovery completed.",

            "jobs_added":
                added,

            "total_jobs":
                db.query(Job).count()
        }

    except Exception as error:

        db.rollback()

        return {
            "message":
                "Job discovery failed.",

            "error":
                str(error)
        }

    finally:

        db.close()


# =========================================================
# GET JOBS
# =========================================================

@app.get("/jobs")
def get_jobs():

    db = SessionLocal()

    try:

        profile = (
            db.query(Profile)
            .order_by(Profile.id.desc())
            .first()
        )

        jobs = (
            db.query(Job)
            .order_by(
                Job.created_at.desc()
            )
            .all()
        )

        if not profile:

            return []

        user_skills = (
            profile.skills or ""
        )

        result = []

        for job in jobs:

            if not is_real_job(job):
                continue

            try:

                match_result = (
                    calculate_skill_match(

                        user_skills,

                        job.skills or "",

                        job.description or "",

                        job.title or "",

                        job.job_type or "",

                        job.work_mode or "",

                        job.location or "",

                        profile.job_type or "",

                        profile.work_mode or "",

                        profile.location or ""
                    )
                )

            except Exception as error:

                print(
                    f"Matching error for job {job.id}:",
                    error
                )

                continue

            result.append({

                "id":
                    job.id,

                "title":
                    job.title,

                "company":
                    job.company,

                "location":
                    job.location,

                "work_mode":
                    job.work_mode,

                "job_type":
                    job.job_type,

                "salary":
                    job.salary,

                "description":
                    job.description,

                "skills":
                    job.skills,

                "url":
                    job.url,

                "match_score":
                    match_result.get(
                        "match_score",
                        0
                    ),

                "matched_skills":
                    match_result.get(
                        "matched_skills",
                        []
                    ),

                "missing_skills":
                    match_result.get(
                        "missing_skills",
                        []
                    )
            })

        result.sort(
            key=lambda x:
                x["match_score"],
            reverse=True
        )

        return result

    finally:

        db.close()


# =========================================================
# RUN DAILY AGENT
# =========================================================
# =========================================================
# CREATE APPLICATION
# =========================================================

@app.post("/applications")
def create_application(data: dict):

    db = SessionLocal()

    try:

        profile_id = data.get("profile_id")
        job_id = data.get("job_id")

        if not profile_id:
            raise HTTPException(
                status_code=400,
                detail="Profile ID is required."
            )

        if not job_id:
            raise HTTPException(
                status_code=400,
                detail="Job ID is required."
            )

        # -------------------------------------------------
        # CHECK PROFILE
        # -------------------------------------------------

        profile = (
            db.query(Profile)
            .filter(
                Profile.id == profile_id
            )
            .first()
        )

        if not profile:

            raise HTTPException(
                status_code=404,
                detail="Profile not found."
            )

        # -------------------------------------------------
        # CHECK JOB
        # -------------------------------------------------

        job = (
            db.query(Job)
            .filter(
                Job.id == job_id
            )
            .first()
        )

        if not job:

            raise HTTPException(
                status_code=404,
                detail="Job not found."
            )

        # -------------------------------------------------
        # CHECK DUPLICATE
        # -------------------------------------------------

        existing = (
            db.query(Application)
            .filter(
                Application.profile_id
                == profile_id,
                Application.job_id
                == job_id
            )
            .first()
        )

        if existing:

            return {
                "message":
                    "Already applied to this job",

                "application": {
                    "id":
                        existing.id,

                    "job_id":
                        existing.job_id,

                    "company":
                        existing.company,

                    "job_title":
                        existing.job_title,

                    "status":
                        existing.status
                }
            }

        # -------------------------------------------------
        # CREATE APPLICATION
        # -------------------------------------------------

        application = Application(

            profile_id=
                profile_id,

            job_id=
                job_id,

            company=
                job.company,

            job_title=
                job.title,

            job_url=
                job.url,

            status=
                "Applied",

            response_type=
                None,

            notes=
                "Application submitted through JobPilot."
        )

        db.add(application)

        db.commit()

        db.refresh(application)

        return {

            "message":
                "Application recorded successfully",

            "application": {

                "id":
                    application.id,

                "profile_id":
                    application.profile_id,

                "job_id":
                    application.job_id,

                "company":
                    application.company,

                "job_title":
                    application.job_title,

                "job_url":
                    application.job_url,

                "status":
                    application.status,

                "applied_date":
                    application.applied_date
            }
        }

    except HTTPException:

        raise

    except Exception as error:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    finally:

        db.close()
        # =========================================================
# GET APPLICATIONS
# =========================================================

@app.get("/applications")
def get_applications(profile_id: int = None):

    db = SessionLocal()

    try:

        query = db.query(Application)

        if profile_id:
            query = query.filter(
                Application.profile_id == profile_id
            )

        applications = (
            query
            .order_by(Application.applied_date.desc())
            .all()
        )

        return [
            {
                "id": application.id,
                "profile_id": application.profile_id,
                "job_id": application.job_id,
                "company": application.company,
                "job_title": application.job_title,
                "job_url": application.job_url,
                "applied_date": application.applied_date,
                "status": application.status,
                "response_type": application.response_type,
                "notes": application.notes
            }
            for application in applications
        ]

    finally:
        db.close()
        # =========================================================
# UPDATE APPLICATION STATUS
# =========================================================

# =========================================================
# UPDATE APPLICATION STATUS / RESPONSE
# =========================================================

@app.put("/applications/{application_id}")
def update_application_status(
    application_id: int,
    data: dict
):
    db = SessionLocal()

    try:
        application = (
            db.query(Application)
            .filter(
                Application.id == application_id
            )
            .first()
        )

        if not application:
            raise HTTPException(
                status_code=404,
                detail="Application not found."
            )

        # -------------------------------------------------
        # Allowed application statuses
        # -------------------------------------------------

        allowed_statuses = [
            "Applied",
            "Under Review",
            "Assessment",
            "Interview",
            "Rejected",
            "Offer"
        ]

        # -------------------------------------------------
        # Allowed response types
        # -------------------------------------------------

        allowed_responses = [
            "Application Received",
            "Under Review",
            "Assessment",
            "Interview",
            "Rejected",
            "Offer",
            "Other"
        ]

        # -------------------------------------------------
        # UPDATE STATUS
        # -------------------------------------------------

        if "status" in data:

            new_status = data.get("status")

            if new_status not in allowed_statuses:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid application status."
                )

            application.status = new_status

        # -------------------------------------------------
        # UPDATE RESPONSE TYPE
        # -------------------------------------------------

        if "response_type" in data:

            new_response = data.get("response_type")

            # Allow None so response can be cleared
            if (
                new_response is not None
                and new_response not in allowed_responses
            ):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid response type."
                )

            application.response_type = new_response

        # -------------------------------------------------
        # SAVE CHANGES
        # -------------------------------------------------

        db.commit()
        db.refresh(application)

        return {
            "message": "Application updated successfully",

            "application": {
                "id": application.id,
                "job_id": application.job_id,
                "company": application.company,
                "job_title": application.job_title,
                "status": application.status,
                "response_type": application.response_type
            }
        }

    except HTTPException:
        raise

    except Exception as error:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    finally:
        db.close()
@app.post("/run-agent/apply")
def run_agent_and_apply():

    db = SessionLocal()

    try:

        # -------------------------------------------------
        # PROFILE
        # -------------------------------------------------

        profile = (
            db.query(Profile)
            .order_by(
                Profile.id.desc()
            )
            .first()
        )

        if not profile:

            raise HTTPException(
                status_code=404,
                detail="Please create your profile first."
            )

        # -------------------------------------------------
        # AGENT ENABLED
        # -------------------------------------------------

        if not profile.agent_enabled:

            return {

                "message":
                    "JobPilot Agent is disabled.",

                "jobs_analyzed":
                    0,

                "jobs_after_preferences":
                    0,

                "applications_created":
                    0,

                "applications":
                    []
            }

        # -------------------------------------------------
        # JOBS
        # -------------------------------------------------

        jobs = db.query(Job).all()

        if not jobs:

            return {

                "message":
                    "No jobs available.",

                "jobs_analyzed":
                    0,

                "jobs_after_preferences":
                    0,

                "applications_created":
                    0,

                "applications":
                    []
            }

        # -------------------------------------------------
        # USER PREFERENCES
        # -------------------------------------------------

        user_skills = (
            profile.skills or ""
        )

        preferred_job_type = (
            normalize_job_type(
                profile.job_type or ""
            )
        )

        preferred_work_mode = (
            normalize_text(
                profile.work_mode or ""
            )
        )

        preferred_location = (
            normalize_text(
                profile.location or ""
            )
        )

        try:

            minimum_salary = float(
                profile.salary or 0
            )

        except:

            minimum_salary = 0

        daily_limit = (
            profile.applications_per_day
            or 5
        )

        # -------------------------------------------------
        # SALARY MATCH
        # -------------------------------------------------

        def salary_matches(
            job_salary
        ):

            if minimum_salary <= 0:
                return True

            if not job_salary:
                return True

            salary_text = str(
                job_salary
            ).strip().lower()

            if salary_text in [
                "",
                "not specified",
                "not disclosed",
                "unspecified",
                "n/a",
                "na",
                "negotiable"
            ]:

                return True

            if (
                "₹" in salary_text
                or "inr" in salary_text
                or "rs." in salary_text
                or "rs " in salary_text
            ):

                values = (
                    extract_salary_values(
                        salary_text
                    )
                )

                if not values:
                    return True

                return (
                    max(values)
                    >= minimum_salary
                )

            if any(
                currency in salary_text
                for currency in [
                    "usd",
                    "eur",
                    "gbp",
                    "cad",
                    "aud"
                ]
            ):

                return True

            values = (
                extract_salary_values(
                    salary_text
                )
            )

            if not values:
                return True

            return (
                max(values)
                >= minimum_salary
            )

        # -------------------------------------------------
        # LOCATION MATCH
        # -------------------------------------------------

        def location_matches(job):

            if not preferred_location:
                return True

            job_location = (
                normalize_text(
                    job.location or ""
                )
            )

            job_work_mode = (
                normalize_text(
                    job.work_mode or ""
                )
            )

            if preferred_location == "remote":

                return (
                    "remote"
                    in job_location
                    or
                    "remote"
                    in job_work_mode
                )

            if "remote" in job_work_mode:

                return True

            preferred_words = [
                word
                for word in re.findall(
                    r"\b[a-zA-Z]+\b",
                    preferred_location
                )
                if len(word) > 2
            ]

            return any(
                word in job_location
                for word in preferred_words
            )

        # -------------------------------------------------
        # EXISTING APPLICATIONS
        # -------------------------------------------------

        existing_applications = (
            db.query(Application)
            .filter(
                Application.profile_id
                == profile.id
            )
            .all()
        )

        existing_job_ids = {
            application.job_id
            for application
            in existing_applications
        }

        # -------------------------------------------------
        # FILTER COUNTERS
        # -------------------------------------------------

        filtered_out = {

            "job_type":
                0,

            "work_mode":
                0,

            "location":
                0,

            "salary":
                0,

            "match_score":
                0
        }

        matching_jobs = []

        # -------------------------------------------------
        # PROCESS JOBS
        # -------------------------------------------------

        for job in jobs:

            if not is_real_job(job):
                continue

            # -------------------------------------------------
            # JOB TYPE
            # -------------------------------------------------

            if preferred_job_type:

                job_type = (
                    normalize_job_type(
                        job.job_type or ""
                    )
                )

                if (
                    job_type
                    and
                    preferred_job_type
                    != job_type
                ):

                    filtered_out[
                        "job_type"
                    ] += 1

                    continue

            # -------------------------------------------------
            # WORK MODE
            # -------------------------------------------------

            if preferred_work_mode:

                job_work_mode = (
                    normalize_text(
                        job.work_mode or ""
                    )
                )

                if (
                    preferred_work_mode
                    == "remote"
                ):

                    if (
                        "remote"
                        not in job_work_mode
                    ):

                        filtered_out[
                            "work_mode"
                        ] += 1

                        continue

                elif (
                    preferred_work_mode
                    not in job_work_mode
                ):

                    filtered_out[
                        "work_mode"
                    ] += 1

                    continue

            # -------------------------------------------------
            # LOCATION
            # -------------------------------------------------

            if not location_matches(job):

                filtered_out[
                    "location"
                ] += 1

                continue

            # -------------------------------------------------
            # SALARY
            # -------------------------------------------------

            if not salary_matches(
                job.salary
            ):

                filtered_out[
                    "salary"
                ] += 1

                continue

            # -------------------------------------------------
            # AI MATCHING
            # -------------------------------------------------

            try:

                match_result = (
                    calculate_skill_match(

                        user_skills,

                        job.skills or "",

                        job.description or "",

                        job.title or "",

                        job.job_type or "",

                        job.work_mode or "",

                        job.location or "",

                        profile.job_type or "",

                        profile.work_mode or "",

                        profile.location or ""
                    )
                )

                match_score = int(
                    match_result.get(
                        "match_score",
                        0
                    )
                )

                matched_skills = (
                    match_result.get(
                        "matched_skills",
                        []
                    )
                )

                missing_skills = (
                    match_result.get(
                        "missing_skills",
                        []
                    )
                )

            except Exception as error:

                print(
                    f"Matching error for job {job.id}:",
                    error
                )

                continue

            # -------------------------------------------------
            # MINIMUM MATCH
            # -------------------------------------------------

            if match_score < 50:

                filtered_out[
                    "match_score"
                ] += 1

                continue

            # -------------------------------------------------
            # ADD MATCH
            # -------------------------------------------------

            matching_jobs.append({

                "job":
                    job,

                "match_score":
                    match_score,

                "matched_skills":
                    matched_skills,

                "missing_skills":
                    missing_skills
            })

        # -------------------------------------------------
        # BEST MATCH FIRST
        # -------------------------------------------------

        matching_jobs.sort(
            key=lambda item:
                item["match_score"],
            reverse=True
        )

        # -------------------------------------------------
        # CREATE APPLICATIONS
        # -------------------------------------------------

        created_applications = []

        for item in matching_jobs:

            if (
                len(created_applications)
                >= daily_limit
            ):
                break

            job = item["job"]

            # Already applied
            if job.id in existing_job_ids:
                continue

            application = Application(

                profile_id=
                    profile.id,

                job_id=
                    job.id,

                company=
                    job.company,

                job_title=
                    job.title,

                job_url=
                    job.url,

                status=
                    "Applied",

                response_type=
                    None,

                notes=(
                    "Selected by JobPilot Daily Agent. "
                    f"AI Match: "
                    f"{item['match_score']}%. "
                    "Profile preferences matched."
                )
            )

            db.add(
                application
            )

            created_applications.append({

                "job_id":
                    job.id,

                "company":
                    job.company,

                "job_title":
                    job.title,

                "location":
                    job.location,

                "work_mode":
                    job.work_mode,

                "job_type":
                    job.job_type,

                "salary":
                    job.salary,

                "url":
                    job.url,

                "match_score":
                    item["match_score"],

                "matched_skills":
                    item["matched_skills"],

                "missing_skills":
                    item["missing_skills"],

                "status":
                    "Applied"
            })

            existing_job_ids.add(
                job.id
            )

        # -------------------------------------------------
        # SAVE APPLICATIONS
        # -------------------------------------------------

        db.commit()

        # -------------------------------------------------
        # SAVE AGENT RUN
        # -------------------------------------------------

        agent_run = AgentRun(

            jobs_analyzed=
                len(jobs),

            jobs_after_preferences=
                len(matching_jobs),

            applications_created=
                len(created_applications)
        )

        db.add(
            agent_run
        )

        db.commit()

        db.refresh(
            agent_run
        )

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------

        return {

            "message":
                "JobPilot Agent completed successfully 🚀",

            "jobs_analyzed":
                len(jobs),

            "jobs_after_preferences":
                len(matching_jobs),

            "applications_created":
                len(created_applications),

            "daily_application_limit":
                daily_limit,

            "agent_run_id":
                agent_run.id,

            "last_run":
                agent_run.run_date,

            "preferences": {

                "job_type":
                    profile.job_type,

                "work_mode":
                    profile.work_mode,

                "location":
                    profile.location,

                "minimum_salary":
                    profile.salary,

                "experience":
                    profile.experience
            },

            "filtered_out":
                filtered_out,

            "applications":
                created_applications
        }

    except Exception as error:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    finally:

        db.close()


# =========================================================
# GET LATEST AGENT STATUS
# =========================================================

@app.get("/agent-status")
def get_agent_status():

    db = SessionLocal()

    try:

        profile = (
            db.query(Profile)
            .order_by(
                Profile.id.desc()
            )
            .first()
        )

        latest_run = (
            db.query(AgentRun)
            .order_by(
                AgentRun.id.desc()
            )
            .first()
        )

        agent_enabled = False

        daily_application_limit = 5

        if profile:

            agent_enabled = bool(
                profile.agent_enabled
            )

            daily_application_limit = (
                profile.applications_per_day
                or 5
            )

        if not latest_run:

            return {

                "has_run":
                    False,

                "agent_enabled":
                    agent_enabled,

                "daily_application_limit":
                    daily_application_limit,

                "jobs_analyzed":
                    0,

                "jobs_after_preferences":
                    0,

                "applications_created":
                    0,

                "last_run":
                    None
            }

        return {

            "has_run":
                True,

            "agent_enabled":
                agent_enabled,

            "daily_application_limit":
                daily_application_limit,

            "jobs_analyzed":
                latest_run.jobs_analyzed,

            "jobs_after_preferences":
                latest_run.jobs_after_preferences,

            "applications_created":
                latest_run.applications_created,

            "last_run":
                latest_run.run_date
        }

    finally:

        db.close()
        # =========================================================
# ANALYZE EMPLOYER EMAIL
# =========================================================

@app.post("/analyze-email")
def analyze_email(data: dict):

    subject = data.get("subject", "")
    body = data.get("body", "")

    text = (
        str(subject)
        + " "
        + str(body)
    ).lower()

    response_type = "Other"

    if any(
        word in text
        for word in [
            "offer",
            "congratulations",
            "pleased to offer",
            "job offer"
        ]
    ):
        response_type = "Offer"

    elif any(
        word in text
        for word in [
            "interview",
            "interview invitation",
            "schedule an interview",
            "technical interview"
        ]
    ):
        response_type = "Interview"

    elif any(
        word in text
        for word in [
            "assessment",
            "coding test",
            "technical test",
            "online assessment"
        ]
    ):
        response_type = "Assessment"

    elif any(
        word in text
        for word in [
            "under review",
            "reviewing your application",
            "application is being reviewed"
        ]
    ):
        response_type = "Under Review"

    elif any(
        word in text
        for word in [
            "received your application",
            "application received",
            "thank you for applying",
            "application has been received"
        ]
    ):
        response_type = "Application Received"

    elif any(
        word in text
        for word in [
            "unfortunately",
            "regret to inform",
            "not selected",
            "rejected",
            "will not be moving forward"
        ]
    ):
        response_type = "Rejected"

    return {
        "message": "Email analyzed successfully",
        "response_type": response_type
    }
# =========================================================
# ANALYZE EMAIL AND UPDATE APPLICATION
# =========================================================

# =========================================================
# ANALYZE EMAIL AND UPDATE APPLICATION
# =========================================================

@app.post("/analyze-email/update")
def analyze_email_and_update(data: dict):

    db = SessionLocal()

    try:

        subject = data.get("subject", "")
        body = data.get("body", "")
        application_id = data.get("application_id")

        if not application_id:
            raise HTTPException(
                status_code=400,
                detail="application_id is required"
            )

        text = (
            str(subject)
            + " "
            + str(body)
        ).lower()

        response_type = "Other"

        if any(
            word in text
            for word in [
                "offer",
                "congratulations",
                "pleased to offer",
                "job offer"
            ]
        ):
            response_type = "Offer"

        elif any(
            word in text
            for word in [
                "interview",
                "interview invitation",
                "schedule an interview",
                "technical interview"
            ]
        ):
            response_type = "Interview"

        elif any(
            word in text
            for word in [
                "assessment",
                "coding test",
                "technical test",
                "online assessment"
            ]
        ):
            response_type = "Assessment"

        elif any(
            word in text
            for word in [
                "under review",
                "reviewing your application",
                "application is being reviewed"
            ]
        ):
            response_type = "Under Review"

        elif any(
            word in text
            for word in [
                "received your application",
                "application received",
                "thank you for applying",
                "application has been received"
            ]
        ):
            response_type = "Application Received"

        elif any(
            word in text
            for word in [
                "unfortunately",
                "regret to inform",
                "not selected",
                "rejected",
                "will not be moving forward"
            ]
        ):
            response_type = "Rejected"

        application = (
            db.query(Application)
            .filter(
                Application.id == application_id
            )
            .first()
        )

        if not application:
            raise HTTPException(
                status_code=404,
                detail="Application not found"
            )

        application.response_type = response_type

        if response_type == "Interview":
            application.status = "Interview"

        elif response_type == "Offer":
            application.status = "Offer"

        elif response_type == "Rejected":
            application.status = "Rejected"

        elif response_type == "Assessment":
            application.status = "Assessment"

        elif response_type == "Under Review":
            application.status = "Under Review"

        db.commit()
        db.refresh(application)

        return {
            "message": "Email analyzed and application updated successfully",
            "application_id": application.id,
            "response_type": application.response_type,
            "status": application.status
        }

    except HTTPException:
        raise

    except Exception as error:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    finally:

        db.close()