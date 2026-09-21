import { useEffect, useState } from "react";
import "./Profile.css";

function Profile() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [resume, setResume] = useState<File | null>(null);
  const [skills, setSkills] = useState("");
  const [jobType, setJobType] = useState("Internship");
  const [workMode, setWorkMode] = useState("Remote");
  const [location, setLocation] = useState("");
  const [salary, setSalary] = useState("");
  const [experience, setExperience] = useState("Fresher");
  const [applicationsPerDay, setApplicationsPerDay] = useState("");
  const [agentEnabled, setAgentEnabled] = useState(false);

  const [extractedSkills, setExtractedSkills] = useState<string[]>([]);
  const [resumeAnalyzed, setResumeAnalyzed] = useState(false);

  useEffect(() => {
    const loadProfile = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/profile");

        if (!response.ok) {
          throw new Error("Could not load profile");
        }

        const data = await response.json();

        if (data.name) {
          setName(data.name);
          setEmail(data.email || "");
          setSkills(data.skills || "");
          setJobType(data.job_type || "Internship");
          setWorkMode(data.work_mode || "Remote");
          setLocation(data.location || "");
          setSalary(data.salary || "");
          setExperience(data.experience || "Fresher");
          setApplicationsPerDay(
            data.applications_per_day?.toString() || ""
          );
          setAgentEnabled(data.agent_enabled || false);

          if (data.resume_filename) {
            setResumeAnalyzed(true);

            const skillList = data.skills
              ? data.skills
                  .split(",")
                  .map((skill: string) => skill.trim())
                  .filter((skill: string) => skill.length > 0)
              : [];

            setExtractedSkills(skillList);
          }
        }
      } catch (error) {
        console.error("Could not load profile:", error);
      }
    };

    loadProfile();
  }, []);

  const handleSave = async () => {
    if (!name || !email) {
      alert("Please enter your name and email.");
      return;
    }

    try {
      const profileData = {
        name,
        email,
        skills,
        job_type: jobType,
        work_mode: workMode,
        location,
        salary,
        experience,
        applications_per_day: applicationsPerDay,
        agent_enabled: agentEnabled
      };

      const profileResponse = await fetch(
        "http://127.0.0.1:8000/profile",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify(profileData)
        }
      );

      if (!profileResponse.ok) {
        throw new Error("Could not save profile");
      }

      const profileResult = await profileResponse.json();

      console.log("Profile response:", profileResult);

      const profileId = profileResult.profile?.id;

      if (!profileId) {
        throw new Error("Profile response did not include an id");
      }

      if (resume) {
        const formData = new FormData();

        formData.append("file", resume);

        const resumeResponse = await fetch(
          `http://127.0.0.1:8000/profile/${profileId}/resume`,
          {
            method: "POST",
            body: formData
          }
        );

        const resumeResult = await resumeResponse.json();

        console.log("Resume response:", resumeResult);

        if (!resumeResponse.ok) {
          alert("Profile saved, but resume upload failed ❌");
          return;
        }

        if (resumeResult.extracted_skills) {
          setExtractedSkills(resumeResult.extracted_skills);
          setResumeAnalyzed(true);
        }

        alert("Profile and resume analyzed successfully! 🚀");
      } else {
        alert("Profile saved successfully! 🚀");
      }
    } catch (error) {
      console.error("Error:", error);

      alert("Could not connect to JobPilot backend ❌");
    }
  };

  return (
    <div className="profile-page">

      {/* NAVBAR */}

      <nav className="profile-navbar">

        <div className="profile-logo">
          🚀 JobPilot
        </div>

        <span>
          Step 1 of 1
        </span>

      </nav>


      {/* MAIN */}

      <main className="profile-container">

        <div className="profile-heading">

          <h1>
            Create Your Profile
          </h1>

          <p>
            Tell JobPilot about yourself so we can find
            opportunities that match you.
          </p>

        </div>


        <div className="profile-card">


          {/* PERSONAL DETAILS */}

          <section className="profile-section">

            <h2>
              👤 Personal Details
            </h2>

            <div className="form-row">

              <div className="form-group">

                <label>
                  Full Name
                </label>

                <input
                  type="text"
                  placeholder="Enter your full name"
                  value={name}
                  onChange={(e) =>
                    setName(e.target.value)
                  }
                />

              </div>


              <div className="form-group">

                <label>
                  Email
                </label>

                <input
                  type="email"
                  placeholder="Enter your email"
                  value={email}
                  onChange={(e) =>
                    setEmail(e.target.value)
                  }
                />

              </div>

            </div>

          </section>


          {/* RESUME */}

          <section className="profile-section">

            <h2>
              📄 Resume
            </h2>

            <div className="resume-upload">

              <div className="upload-icon">
                📄
              </div>

              <h3>
                Upload your resume
              </h3>

              <p>
                PDF format recommended • Maximum 5 MB
              </p>


              <label className="upload-btn">

                Choose Resume

                <input
                  type="file"
                  accept=".pdf"
                  onChange={(e) => {

                    if (e.target.files) {

                      const selectedFile =
                        e.target.files[0];

                      if (
                        selectedFile.type !==
                        "application/pdf"
                      ) {
                        alert(
                          "Please select a PDF file."
                        );
                        return;
                      }

                      if (
                        selectedFile.size >
                        5 * 1024 * 1024
                      ) {
                        alert(
                          "Resume must be smaller than 5 MB."
                        );
                        return;
                      }

                      setResume(selectedFile);

                      setResumeAnalyzed(false);
                    }

                  }}
                />

              </label>


              {resume && (
                <p>
                  Selected: {resume.name}
                </p>
              )}

            </div>

          </section>


          {/* RESUME ANALYSIS */}

          {resumeAnalyzed && (

            <section className="profile-section">

              <div
                style={{
                  background: "#f0fdf4",
                  border: "1px solid #bbf7d0",
                  borderRadius: "12px",
                  padding: "20px"
                }}
              >

                <h2
                  style={{
                    marginTop: 0
                  }}
                >
                  🧠 Resume Analysis
                </h2>

                <p
                  style={{
                    color: "#166534",
                    fontWeight: 600
                  }}
                >
                  ✅ Resume analyzed successfully
                </p>

                <p>
                  JobPilot detected{" "}
                  <strong>
                    {extractedSkills.length}
                  </strong>{" "}
                  technical skills from your resume.
                </p>


                <div
                  style={{
                    display: "flex",
                    flexWrap: "wrap",
                    gap: "8px",
                    marginTop: "15px"
                  }}
                >

                  {extractedSkills.map(
                    (skill, index) => (

                      <span
                        key={index}
                        style={{
                          background: "#ffffff",
                          border: "1px solid #d1d5db",
                          borderRadius: "20px",
                          padding: "7px 12px",
                          fontSize: "14px",
                          fontWeight: 500
                        }}
                      >
                        {skill}
                      </span>

                    )
                  )}

                </div>

              </div>

            </section>

          )}


          {/* SKILLS */}

          <section className="profile-section">

            <h2>
              🧠 Skills
            </h2>

            <div className="form-group">

              <label>
                Your Skills
              </label>

              <input
                type="text"
                placeholder="Example: Python, SQL, Machine Learning, Power BI"
                value={skills}
                onChange={(e) =>
                  setSkills(e.target.value)
                }
              />

              <p className="helper-text">
                Add the skills you currently have.
              </p>

            </div>

          </section>


          {/* JOB PREFERENCES */}

          <section className="profile-section">

            <h2>
              💼 Job Preferences
            </h2>

            <div className="form-row">

              <div className="form-group">

                <label>
                  Job Type
                </label>

                <select
                  value={jobType}
                  onChange={(e) =>
                    setJobType(e.target.value)
                  }
                >

                  <option>
                    Internship
                  </option>

                  <option>
                    Full-time
                  </option>

                  <option>
                    Part-time
                  </option>

                </select>

              </div>


              <div className="form-group">

                <label>
                  Work Mode
                </label>

                <select
                  value={workMode}
                  onChange={(e) =>
                    setWorkMode(e.target.value)
                  }
                >

                  <option>
                    Remote
                  </option>

                  <option>
                    Hybrid
                  </option>

                  <option>
                    On-site
                  </option>

                </select>

              </div>

            </div>


            <div className="form-row">

              <div className="form-group">

                <label>
                  Preferred Location
                </label>

                <input
                  type="text"
                  placeholder="Hyderabad, Bangalore, Remote..."
                  value={location}
                  onChange={(e) =>
                    setLocation(e.target.value)
                  }
                />

              </div>


              <div className="form-group">

                <label>
                  Minimum Salary
                </label>

                <input
                  type="number"
                  placeholder="₹ Minimum salary"
                  value={salary}
                  onChange={(e) =>
                    setSalary(e.target.value)
                  }
                />

              </div>

            </div>


            <div className="form-group">

              <label>
                Experience
              </label>

              <select
                value={experience}
                onChange={(e) =>
                  setExperience(e.target.value)
                }
              >

                <option>
                  Fresher
                </option>

                <option>
                  Less than 1 year
                </option>

                <option>
                  1-2 years
                </option>

                <option>
                  2+ years
                </option>

              </select>

            </div>

          </section>


          {/* DAILY AGENT */}

          <section className="profile-section">

            <h2>
              🤖 Daily Application Agent
            </h2>

            <div className="form-row">

              <div className="form-group">

                <label>
                  Applications per day
                </label>

                <input
                  type="number"
                  placeholder="Example: 10"
                  value={applicationsPerDay}
                  onChange={(e) =>
                    setApplicationsPerDay(
                      e.target.value
                    )
                  }
                />

              </div>


              <div className="agent-toggle">

                <label>

                  <input
                    type="checkbox"
                    checked={agentEnabled}
                    onChange={(e) =>
                      setAgentEnabled(
                        e.target.checked
                      )
                    }
                  />

                  <span>
                    Enable Daily JobPilot Agent
                  </span>

                </label>

                <p>
                  JobPilot will search for matching
                  opportunities every day.
                </p>

              </div>

            </div>

          </section>


          {/* SAVE */}

          <button
            className="save-profile-btn"
            onClick={handleSave}
          >
            Save Profile →
          </button>

        </div>

      </main>

    </div>
  );
}

export default Profile;