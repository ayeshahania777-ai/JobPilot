import requests


jobs = [
    {
        "title": "Data Analyst Intern",
        "company": "TechNova",
        "location": "Hyderabad",
        "work_mode": "Remote",
        "job_type": "Internship",
        "salary": "₹20,000 - ₹25,000",
        "description": "Analyze business data, create dashboards, prepare reports and identify useful insights.",
        "skills": "Python, SQL, Pandas, Power BI, Excel",
        "source": "JobPilot Demo",
        "url": "https://example.com/data-analyst-intern",
        "posted_date": "2026-09-17"
    },

    {
        "title": "Machine Learning Intern",
        "company": "AI Labs",
        "location": "Remote",
        "work_mode": "Remote",
        "job_type": "Internship",
        "salary": "₹25,000 - ₹35,000",
        "description": "Build machine learning models, clean datasets and evaluate predictive algorithms.",
        "skills": "Python, Machine Learning, Scikit-learn, Pandas, NumPy",
        "source": "JobPilot Demo",
        "url": "https://example.com/ml-intern",
        "posted_date": "2026-09-17"
    },

    {
        "title": "Data Science Intern",
        "company": "DataWorks",
        "location": "Bangalore",
        "work_mode": "Hybrid",
        "job_type": "Internship",
        "salary": "₹35,000 - ₹45,000",
        "description": "Work on data analysis, machine learning experiments and visualization projects.",
        "skills": "Python, SQL, Machine Learning, Pandas, Matplotlib, Statistics",
        "source": "JobPilot Demo",
        "url": "https://example.com/data-science-intern",
        "posted_date": "2026-09-17"
    },

    {
        "title": "Python Developer Intern",
        "company": "CodeCraft",
        "location": "Hyderabad",
        "work_mode": "Remote",
        "job_type": "Internship",
        "salary": "₹18,000 - ₹22,000",
        "description": "Develop Python applications and work with APIs, databases and backend services.",
        "skills": "Python, FastAPI, SQL, Git, REST API",
        "source": "JobPilot Demo",
        "url": "https://example.com/python-intern",
        "posted_date": "2026-09-17"
    },

    {
        "title": "Business Intelligence Intern",
        "company": "InsightTech",
        "location": "Remote",
        "work_mode": "Remote",
        "job_type": "Internship",
        "salary": "₹30,000 - ₹40,000",
        "description": "Create business dashboards, analyze company performance and communicate data-driven insights.",
        "skills": "Power BI, SQL, Excel, Python, Data Visualization",
        "source": "JobPilot Demo",
        "url": "https://example.com/bi-intern",
        "posted_date": "2026-09-17"
    },

    {
        "title": "ML Engineer Intern",
        "company": "FutureAI",
        "location": "Hyderabad",
        "work_mode": "Remote",
        "job_type": "Internship",
        "salary": "₹40,000 - ₹50,000",
        "description": "Develop machine learning pipelines and experiment with predictive models.",
        "skills": "Python, Machine Learning, Scikit-learn, NumPy, SQL",
        "source": "JobPilot Demo",
        "url": "https://example.com/ml-engineer-intern",
        "posted_date": "2026-09-17"
    }
]


print("Adding JobPilot demo jobs...\n")


for job in jobs:

    try:

        response = requests.post(
            "http://127.0.0.1:8000/jobs",
            json=job
        )

        if response.status_code == 200:

            print(
                "Added:",
                job["title"]
            )

        else:

            print(
                "Failed:",
                job["title"],
                response.text
            )

    except Exception as error:

        print(
            "Could not connect to backend:",
            error
        )


print("\nFinished adding jobs 🚀")