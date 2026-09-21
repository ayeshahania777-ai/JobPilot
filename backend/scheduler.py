import requests
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

# JobPilot backend URL
AGENT_URL = "http://127.0.0.1:8000/run-agent/apply"

scheduler = BackgroundScheduler()


def run_daily_agent():
    print("\n========================================")
    print("🤖 JobPilot Daily Agent Started")
    print("🕐 Time:", datetime.now())
    print("========================================")

    try:
        response = requests.post(
            AGENT_URL,
            timeout=120
        )

        if response.status_code == 200:
            result = response.json()

            print("✅ Daily Agent completed")
            print(
                "📊 Jobs analyzed:",
                result.get("jobs_analyzed", 0)
            )
            print(
                "🎯 Jobs after preferences:",
                result.get("jobs_after_preferences", 0)
            )
            print(
                "📨 Applications created:",
                result.get("applications_created", 0)
            )

        else:
            print(
                "❌ Daily Agent failed"
            )
            print(
                "Status:",
                response.status_code
            )
            print(
                "Response:",
                response.text
            )

    except requests.exceptions.RequestException as error:
        print(
            "❌ Could not connect to JobPilot backend:"
        )
        print(error)

    print("========================================\n")


def start_scheduler():
    """
    Start the JobPilot automatic daily scheduler.
    """

    if scheduler.running:
        return

    # Run every day at 9:00 AM
    scheduler.add_job(
        run_daily_agent,
        trigger="cron",
        hour=9,
        minute=0,
        id="jobpilot_daily_agent",
        replace_existing=True,
        max_instances=1
    )

    scheduler.start()

    print("========================================")
    print("⏰ JobPilot Scheduler Started")
    print("📅 Daily Agent time: 9:00 AM")
    print("========================================")


def stop_scheduler():
    """
    Stop the scheduler when the backend shuts down.
    """

    if scheduler.running:
        scheduler.shutdown(
            wait=False
        )

        print(
            "🛑 JobPilot Scheduler Stopped"
        )