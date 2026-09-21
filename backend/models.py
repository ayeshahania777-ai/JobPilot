from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime
from database import Base
from datetime import datetime


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String)
    email = Column(String)
    skills = Column(String)

    job_type = Column(String)
    work_mode = Column(String)
    location = Column(String)
    salary = Column(String)
    experience = Column(String)

    applications_per_day = Column(Integer)

    agent_enabled = Column(Boolean, default=False)

    resume_filename = Column(
        String,
        nullable=True
    )


class Job(Base):
    __tablename__ = "jobs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    title = Column(String)
    company = Column(String)
    location = Column(String)
    work_mode = Column(String)
    job_type = Column(String)
    salary = Column(String)

    description = Column(Text)
    skills = Column(String)

    source = Column(String)
    url = Column(String)

    posted_date = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


class Application(Base):
    __tablename__ = "applications"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    profile_id = Column(
        Integer,
        nullable=False
    )

    job_id = Column(
        Integer,
        nullable=False
    )

    company = Column(String)
    job_title = Column(String)
    job_url = Column(String)

    applied_date = Column(
        DateTime,
        default=datetime.utcnow
    )

    status = Column(
        String,
        default="Applied"
    )

    response_type = Column(
        String,
        nullable=True
    )

    notes = Column(
        Text,
        nullable=True
    )


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    run_date = Column(
        DateTime,
        default=datetime.utcnow
    )

    jobs_analyzed = Column(
        Integer,
        default=0
    )

    jobs_after_preferences = Column(
        Integer,
        default=0
    )

    applications_created = Column(
        Integer,
        default=0
    )