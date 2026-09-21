# 🚀 JobPilot

### AI-Powered Job Search, Application & Response Tracking Agent

JobPilot is an AI/ML-powered job search assistant that helps users discover relevant job opportunities based on their skills, preferences, resume, location, experience, salary expectations, and job type.

It automatically analyzes available jobs, matches them with the user's profile, tracks applications, and helps monitor employer responses.

---

## 🎯 Problem Statement

Searching and applying for jobs manually can be time-consuming.

Job seekers often need to:

- Search through multiple job platforms
- Identify jobs matching their skills
- Compare job requirements with their resume
- Track applications manually
- Remember application status
- Monitor employer responses

JobPilot brings these activities into one platform.

---

## 💡 Key Features

- 👤 User profile creation
- 📄 Resume upload and skill extraction
- 🔎 Job discovery
- 🤖 AI/ML-based job matching
- 🎯 Personalized job ranking
- 📝 Application tracking
- 📊 Application dashboard
- 📅 Daily job discovery agent
- ⏰ Scheduled daily agent
- 📈 Application history
- 📬 Employer response tracking
- 🧠 Email response classification
- 🔔 Response status updates
- 📌 Daily application limit
- 💾 SQLite database

---

## 🧠 AI/ML Features

JobPilot uses machine-learning concepts to compare user profiles with job requirements.

The matching system considers:

- Skills
- Job role
- Experience
- Job type
- Work mode
- Location
- Salary expectations
- Resume information

The system generates a matching score to help identify relevant opportunities.

---

## 🏗️ System Architecture

```text
                    ┌─────────────────────┐
                    │       User          │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   React Frontend    │
                    │     Dashboard       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    FastAPI Backend  │
                    └──────────┬──────────┘
                               │
             ┌─────────────────┼─────────────────┐
             ▼                 ▼                 ▼
      ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
      │ Job         │   │ Matching    │   │ Application │
      │ Discovery   │   │ Engine      │   │ Tracking    │
      └─────────────┘   └─────────────┘   └─────────────┘
             │                 │                 │
             └─────────────────┼─────────────────┘
                               ▼
                    ┌─────────────────────┐
                    │   SQLite Database   │
                    └─────────────────────┘

                    ┌─────────────────────┐
                    │ Daily Job Agent     │
                    │     Scheduler       │
                    └─────────────────────┘
```
