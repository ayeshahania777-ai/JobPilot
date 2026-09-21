import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import "./Jobs.css";

type Job = {
  id: number;
  title: string;
  company: string;
  location: string;
  work_mode: string;
  job_type: string;
  salary: string;
  description: string;
  skills: string;
  source: string;
  url: string;
  posted_date: string;
  match_score: number;
  matched_skills: string[];
  missing_skills: string[];
};

function Jobs() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);

  const [profileId, setProfileId] = useState<number | null>(null);

  const [applyingJobId, setApplyingJobId] = useState<number | null>(null);

  const [appliedJobs, setAppliedJobs] = useState<number[]>([]);

  useEffect(() => {
    loadJobs();
    loadProfile();
  }, []);

  const loadJobs = async () => {
    try {
      const response = await fetch(
        "http://127.0.0.1:8000/jobs"
      );

      if (!response.ok) {
        throw new Error("Could not load jobs");
      }

      const data = await response.json();

      setJobs(data);
    } catch (error) {
      console.error("Could not load jobs:", error);
    } finally {
      setLoading(false);
    }
  };

  const loadProfile = async () => {
    try {
      const response = await fetch(
        "http://127.0.0.1:8000/profile"
      );

      if (!response.ok) {
        throw new Error("Could not load profile");
      }

      const data = await response.json();

      if (data.id) {
        setProfileId(data.id);
      }
    } catch (error) {
      console.error("Could not load profile:", error);
    }
  };

  const applyToJob = async (job: Job) => {
    if (!profileId) {
      alert("Please create your profile first.");
      return;
    }

    setApplyingJobId(job.id);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/applications",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            profile_id: profileId,
            job_id: job.id
          })
        }
      );

      const data = await response.json();

      if (!response.ok) {
        alert(
          data.detail ||
            "Could not record application."
        );
        return;
      }

      if (
        data.message ===
        "Already applied to this job"
      ) {
        alert("You already applied to this job.");
      } else {
        alert(
          `Application recorded successfully! 🚀\n\n${job.company} - ${job.title}`
        );
      }

      setAppliedJobs((previous) => {
        if (previous.includes(job.id)) {
          return previous;
        }

        return [...previous, job.id];
      });
    } catch (error) {
      console.error(
        "Application error:",
        error
      );

      alert(
        "Could not connect to JobPilot backend ❌"
      );
    } finally {
      setApplyingJobId(null);
    }
  };

  return (
    <div className="jobs-page">

      <nav className="jobs-navbar">

        <div className="jobs-logo">
          🚀 JobPilot
        </div>

        <div className="jobs-nav-links">

          <Link to="/">
            Home
          </Link>

          <Link to="/profile">
            Profile
          </Link>

          <Link to="/dashboard">
            Dashboard
          </Link>

          <span className="active-job-link">
            Find Jobs
          </span>

        </div>

      </nav>

      <main className="jobs-container">

        <div className="jobs-header">

          <div>

            <h1>
              Find Jobs 🔎
            </h1>

            <p>
              Discover job opportunities
              matched to your profile.
            </p>

          </div>

          <div className="job-count">
            {jobs.length} Jobs Found
          </div>

        </div>

        {loading && (
          <div className="jobs-message">
            Loading jobs...
          </div>
        )}

        {!loading && jobs.length === 0 && (
          <div className="jobs-message">

            <div className="jobs-empty-icon">
              📋
            </div>

            <h2>
              No jobs found
            </h2>

            <p>
              JobPilot hasn't discovered
              any jobs yet.
            </p>

          </div>
        )}

        {!loading && jobs.length > 0 && (

          <div className="jobs-grid">

            {jobs.map((job) => (

              <div
                className="job-card"
                key={job.id}
              >

                <div className="job-card-top">

                  <div className="company-icon">

                    {job.company
                      ? job.company
                          .charAt(0)
                          .toUpperCase()
                      : "J"}

                  </div>

                  <div>

                    <h2>
                      {job.title}
                    </h2>

                    <h3>
                      {job.company}
                    </h3>

                  </div>

                </div>

                <div className="match-section">

                  <div className="match-header">

                    <strong>
                      🎯 Job Match
                    </strong>

                    <span className="match-score">
                      {job.match_score}%
                      Match
                    </span>

                  </div>

                  <div className="match-bar">

                    <div
                      className="match-progress"
                      style={{
                        width:
                          `${job.match_score}%`
                      }}
                    ></div>

                  </div>

                </div>

                <div className="job-details">

                  <span>
                    📍{" "}
                    {job.location ||
                      "Not specified"}
                  </span>

                  <span>
                    💼{" "}
                    {job.job_type ||
                      "Not specified"}
                  </span>

                  <span>
                    🏠{" "}
                    {job.work_mode ||
                      "Remote"}
                  </span>

                  {job.salary && (
                    <span>
                      💰 {job.salary}
                    </span>
                  )}

                </div>

                {job.description && (

                  <p className="job-description">

                    {job.description.length >
                    180
                      ? job.description.substring(
                          0,
                          180
                        ) + "..."
                      : job.description}

                  </p>

                )}

                <div className="skills-section">

                  <strong>
                    ✅ Matched Skills
                  </strong>

                  <div className="skill-tags">

                    {job.matched_skills &&
                    job.matched_skills.length >
                      0 ? (

                      job.matched_skills.map(
                        (skill, index) => (

                          <span key={index}>
                            {skill}
                          </span>

                        )
                      )

                    ) : (

                      <small>
                        No matching skills
                      </small>

                    )}

                  </div>

                </div>

                <div className="missing-section">

                  <strong>
                    📚 Skills to Learn
                  </strong>

                  <div className="missing-tags">

                    {job.missing_skills &&
                    job.missing_skills.length >
                      0 ? (

                      job.missing_skills
                        .slice(0, 6)
                        .map(
                          (skill, index) => (

                            <span key={index}>
                              {skill}
                            </span>

                          )
                        )

                    ) : (

                      <small>
                        No missing skills 🎉
                      </small>

                    )}

                  </div>

                </div>

                <div className="skills-section">

                  <strong>
                    💡 Job Skills
                  </strong>

                  <div className="skill-tags">

                    {job.skills ? (

                      job.skills
                        .split(",")
                        .slice(0, 8)
                        .map(
                          (skill, index) => (

                            <span key={index}>
                              {skill.trim()}
                            </span>

                          )
                        )

                    ) : (

                      <small>
                        Not specified
                      </small>

                    )}

                  </div>

                </div>

                <div className="job-card-bottom">

                  <small>
                    Posted:{" "}
                    {job.posted_date ||
                      "Recently"}
                  </small>

                  <a
                    href={job.url}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    View Job →
                  </a>

                </div>

                <div
                  style={{
                    marginTop: "15px"
                  }}
                >

                  <button
                    onClick={() =>
                      applyToJob(job)
                    }
                    disabled={
                      applyingJobId ===
                        job.id ||
                      appliedJobs.includes(
                        job.id
                      )
                    }
                    style={{
                      width: "100%",
                      padding: "12px",
                      border: "none",
                      borderRadius: "8px",
                      background:
                        appliedJobs.includes(
                          job.id
                        )
                          ? "#16a34a"
                          : "#2563eb",
                      color: "white",
                      fontSize: "15px",
                      fontWeight: 600,
                      cursor:
                        appliedJobs.includes(
                          job.id
                        )
                          ? "default"
                          : "pointer"
                    }}
                  >

                    {appliedJobs.includes(
                      job.id
                    )
                      ? "✅ Applied"
                      : applyingJobId ===
                        job.id
                      ? "Applying..."
                      : "🚀 Apply Now"}

                  </button>

                </div>

              </div>

            ))}

          </div>

        )}

      </main>

    </div>
  );
}

export default Jobs;