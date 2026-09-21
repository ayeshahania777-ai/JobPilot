import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import "./Dashboard.css";

type Application = {
  id: number;
  job_id: number;
  company: string;
  job_title: string;
  job_url: string;
  applied_date: string;
  status: string;
  response_type: string | null;
  notes: string | null;
};

type AgentStatus = {
  agent_enabled: boolean;
  daily_application_limit: number;
  jobs_analyzed: number;
  jobs_after_preferences: number;
  applications_created: number;
  last_run: string | null;
};

const STATUS_OPTIONS = [
  "Applied",
  "Under Review",
  "Assessment",
  "Interview",
  "Rejected",
  "Offer"
];

const RESPONSE_OPTIONS = [
  "Application Received",
  "Under Review",
  "Assessment",
  "Interview",
  "Rejected",
  "Offer",
  "Other"
];

function Dashboard() {
  const [applications, setApplications] = useState<Application[]>([]);
  const [loadingApplications, setLoadingApplications] =
    useState(true);

  const [updatingApplicationId, setUpdatingApplicationId] =
    useState<number | null>(null);

  const [agentStatus, setAgentStatus] =
    useState<AgentStatus>({
      agent_enabled: false,
      daily_application_limit: 0,
      jobs_analyzed: 0,
      jobs_after_preferences: 0,
      applications_created: 0,
      last_run: null
    });

  const [loadingAgent, setLoadingAgent] = useState(true);

  // =========================================================
  // LOAD DATA
  // =========================================================

  useEffect(() => {
    loadApplications();
    loadAgentStatus();
  }, []);

  const loadApplications = async () => {
    try {
      const response = await fetch(
        "http://127.0.0.1:8000/applications"
      );

      if (!response.ok) {
        throw new Error(
          "Could not load applications"
        );
      }

      const data = await response.json();

      setApplications(data);
    } catch (error) {
      console.error(
        "Could not load applications:",
        error
      );
    } finally {
      setLoadingApplications(false);
    }
  };

  const loadAgentStatus = async () => {
    try {
      const response = await fetch(
        "http://127.0.0.1:8000/agent-status"
      );

      if (!response.ok) {
        throw new Error(
          "Could not load agent status"
        );
      }

      const data = await response.json();

      setAgentStatus(data);
    } catch (error) {
      console.error(
        "Could not load agent status:",
        error
      );
    } finally {
      setLoadingAgent(false);
    }
  };

  // =========================================================
  // UPDATE APPLICATION STATUS / RESPONSE
  // =========================================================

  const updateApplication = async (
    applicationId: number,
    newStatus?: string,
    newResponse?: string
  ) => {
    setUpdatingApplicationId(applicationId);

    try {
      const body: {
        status?: string;
        response_type?: string;
      } = {};

      if (newStatus !== undefined) {
        body.status = newStatus;
      }

      if (newResponse !== undefined) {
        body.response_type = newResponse;
      }

      const response = await fetch(
        `http://127.0.0.1:8000/applications/${applicationId}`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify(body)
        }
      );

      const data = await response.json();

      if (!response.ok) {
        alert(
          data.detail ||
            "Could not update application."
        );

        return;
      }

      setApplications(
        (previousApplications) =>
          previousApplications.map(
            (application) =>
              application.id === applicationId
                ? {
                    ...application,

                    status:
                      newStatus !== undefined
                        ? newStatus
                        : application.status,

                    response_type:
                      newResponse !== undefined
                        ? newResponse
                        : application.response_type
                  }
                : application
          )
      );
    } catch (error) {
      console.error(
        "Application update error:",
        error
      );

      alert(
        "Could not connect to JobPilot backend ❌"
      );
    } finally {
      setUpdatingApplicationId(null);
    }
  };

  // =========================================================
  // FORMAT DATES
  // =========================================================

  const formatDate = (
    dateString: string
  ) => {
    if (!dateString) {
      return "Unknown";
    }

    const date = new Date(dateString);

    return date.toLocaleDateString(
      "en-IN",
      {
        day: "2-digit",
        month: "short",
        year: "numeric"
      }
    );
  };

  const formatDateTime = (
    dateString: string | null
  ) => {
    if (!dateString) {
      return "No agent run yet";
    }

    const date = new Date(dateString);

    return date.toLocaleString(
      "en-IN",
      {
        day: "2-digit",
        month: "short",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit"
      }
    );
  };

  // =========================================================
  // TODAY'S APPLICATIONS
  // =========================================================

  const todayApplications =
    applications.filter(
      (application) => {
        const applicationDate =
          new Date(
            application.applied_date
          );

        const today = new Date();

        return (
          applicationDate.getDate() ===
            today.getDate() &&
          applicationDate.getMonth() ===
            today.getMonth() &&
          applicationDate.getFullYear() ===
            today.getFullYear()
        );
      }
    );

  // =========================================================
  // STATISTICS
  // =========================================================

  const totalApplications =
    applications.length;

  const interviewCount =
    applications.filter(
      (application) =>
        application.status ===
        "Interview"
    ).length;

  const responseCount =
    applications.filter(
      (application) =>
        application.response_type !==
          null &&
        application.response_type !== ""
    ).length;

  // =========================================================
  // RESPONSE STYLE
  // =========================================================

  const getResponseStyle = (
    response: string | null
  ) => {
    if (!response) {
      return {
        background: "#f3f4f6",
        color: "#6b7280"
      };
    }

    if (
      response === "Interview" ||
      response === "Offer"
    ) {
      return {
        background: "#dcfce7",
        color: "#166534"
      };
    }

    if (
      response === "Rejected"
    ) {
      return {
        background: "#fee2e2",
        color: "#991b1b"
      };
    }

    if (
      response === "Assessment" ||
      response === "Under Review"
    ) {
      return {
        background: "#fef3c7",
        color: "#92400e"
      };
    }

    return {
      background: "#dbeafe",
      color: "#1d4ed8"
    };
  };

  // =========================================================
  // STATUS STYLE
  // =========================================================

  const getStatusStyle = (
    status: string
  ) => {
    if (status === "Interview") {
      return {
        background: "#dcfce7",
        color: "#166534"
      };
    }

    if (status === "Offer") {
      return {
        background: "#dbeafe",
        color: "#1d4ed8"
      };
    }

    if (status === "Rejected") {
      return {
        background: "#fee2e2",
        color: "#991b1b"
      };
    }

    if (
      status === "Assessment" ||
      status === "Under Review"
    ) {
      return {
        background: "#fef3c7",
        color: "#92400e"
      };
    }

    return {
      background: "#f3f4f6",
      color: "#374151"
    };
  };

  // =========================================================
  // LOADING
  // =========================================================

  if (
    loadingApplications ||
    loadingAgent
  ) {
    return (
      <div
        style={{
          padding: "40px",
          fontFamily: "Arial"
        }}
      >
        <h2>Loading JobPilot Dashboard...</h2>
      </div>
    );
  }

  // =========================================================
  // DASHBOARD
  // =========================================================

  return (
    <div className="dashboard-container">

      {/* =====================================================
          HEADER
      ===================================================== */}

      <div className="dashboard-header">

        <div>
          <h1>🚀 JobPilot Dashboard</h1>

          <p>
            Manage your job applications,
            track responses and monitor your
            AI job agent.
          </p>
        </div>

        <div className="dashboard-actions">

          <Link to="/jobs">
            <button className="primary-button">
              🔎 Find Jobs
            </button>
          </Link>

          <Link to="/profile">
            <button className="secondary-button">
              👤 Profile
            </button>
          </Link>

        </div>

      </div>

      {/* =====================================================
          STATISTICS
      ===================================================== */}

      <div className="stats-grid">

        <div className="stat-card">
          <div className="stat-icon">
            📋
          </div>

          <div>
            <h3>Applications</h3>

            <strong>
              {totalApplications}
            </strong>

            <p>Total applications</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            📅
          </div>

          <div>
            <h3>Today</h3>

            <strong>
              {todayApplications.length}
            </strong>

            <p>
              Applications today
            </p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            🎯
          </div>

          <div>
            <h3>Interviews</h3>

            <strong>
              {interviewCount}
            </strong>

            <p>
              Interview stages
            </p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            📩
          </div>

          <div>
            <h3>Responses</h3>

            <strong>
              {responseCount}
            </strong>

            <p>
              Employer responses
            </p>
          </div>
        </div>

      </div>

      {/* =====================================================
          DAILY AGENT
      ===================================================== */}

      <div className="dashboard-card">

        <div className="section-header">

          <div>
            <h2>
              🤖 Daily JobPilot Agent
            </h2>

            <p>
              Automatic job discovery and
              application monitoring.
            </p>
          </div>

          <div
            style={{
              padding: "8px 14px",
              borderRadius: "20px",
              background:
                agentStatus.agent_enabled
                  ? "#dcfce7"
                  : "#fee2e2",
              color:
                agentStatus.agent_enabled
                  ? "#166534"
                  : "#991b1b",
              fontWeight: 600
            }}
          >
            {agentStatus.agent_enabled
              ? "● Active"
              : "● Disabled"}
          </div>

        </div>

        <div className="agent-grid">

          <div className="agent-item">
            <span>
              Jobs Analyzed
            </span>

            <strong>
              {agentStatus.jobs_analyzed}
            </strong>
          </div>

          <div className="agent-item">
            <span>
              Matching Jobs
            </span>

            <strong>
              {
                agentStatus.jobs_after_preferences
              }
            </strong>
          </div>

          <div className="agent-item">
            <span>
              Applications Created
            </span>

            <strong>
              {
                agentStatus.applications_created
              }
            </strong>
          </div>

          <div className="agent-item">
            <span>
              Daily Limit
            </span>

            <strong>
              {
                agentStatus.daily_application_limit
              }
            </strong>
          </div>

        </div>

        <div
          style={{
            marginTop: "20px",
            padding: "14px",
            background: "#f8fafc",
            borderRadius: "10px"
          }}
        >
          <strong>
            Last Agent Run:
          </strong>{" "}
          {formatDateTime(
            agentStatus.last_run
          )}
        </div>

      </div>

      {/* =====================================================
          TODAY'S APPLICATIONS
      ===================================================== */}

      <div className="dashboard-card">

        <div className="section-header">

          <div>
            <h2>
              📅 Today's Applications
            </h2>

            <p>
              Jobs you applied to today.
            </p>
          </div>

          <strong>
            {todayApplications.length}
          </strong>

        </div>

        {todayApplications.length ===
        0 ? (
          <div className="empty-state">
            <h3>
              No applications today
            </h3>

            <p>
              Find matching jobs and
              start applying.
            </p>

            <Link to="/jobs">
              <button className="primary-button">
                Find Jobs
              </button>
            </Link>
          </div>
        ) : (
          <div className="today-list">

            {todayApplications.map(
              (application) => (
                <div
                  className="today-item"
                  key={application.id}
                >

                  <div>
                    <strong>
                      {application.company}
                    </strong>

                    <p>
                      {application.job_title}
                    </p>
                  </div>

                  <span
                    style={{
                      ...getStatusStyle(
                        application.status
                      ),
                      padding:
                        "6px 12px",
                      borderRadius:
                        "20px",
                      fontSize:
                        "13px",
                      fontWeight: 600
                    }}
                  >
                    {application.status}
                  </span>

                </div>
              )
            )}

          </div>
        )}

      </div>

      {/* =====================================================
          AGENT ACTIVITY
      ===================================================== */}

      <div className="dashboard-card">

        <div className="section-header">

          <div>
            <h2>
              ⚡ Agent Activity
            </h2>

            <p>
              Latest JobPilot agent activity.
            </p>
          </div>

        </div>

        <div className="activity-list">

          <div className="activity-item">

            <span className="activity-dot">
              ●
            </span>

            <div>
              <strong>
                Daily Agent
              </strong>

              <p>
                {
                  agentStatus.agent_enabled
                    ? "Agent is active and monitoring jobs."
                    : "Agent is currently disabled."
                }
              </p>
            </div>

          </div>

          <div className="activity-item">

            <span className="activity-dot">
              ●
            </span>

            <div>
              <strong>
                Jobs Analyzed
              </strong>

              <p>
                JobPilot analyzed{" "}
                <strong>
                  {agentStatus.jobs_analyzed}
                </strong>{" "}
                jobs during the latest run.
              </p>
            </div>

          </div>

          <div className="activity-item">

            <span className="activity-dot">
              ●
            </span>

            <div>
              <strong>
                Matching Jobs
              </strong>

              <p>
                {
                  agentStatus.jobs_after_preferences
                }{" "}
                jobs matched your current
                preferences.
              </p>
            </div>

          </div>

          <div className="activity-item">

            <span className="activity-dot">
              ●
            </span>

            <div>
              <strong>
                Last Run
              </strong>

              <p>
                {formatDateTime(
                  agentStatus.last_run
                )}
              </p>
            </div>

          </div>

        </div>

      </div>

      {/* =====================================================
          APPLICATION HISTORY
      ===================================================== */}

      <div className="dashboard-card">

        <div className="section-header">

          <div>
            <h2>
              📋 Application History
            </h2>

            <p>
              Track application status and
              employer responses.
            </p>
          </div>

          <span>
            {applications.length} applications
          </span>

        </div>

        {applications.length ===
        0 ? (
          <div className="empty-state">

            <h3>
              No applications yet
            </h3>

            <p>
              Your application history
              will appear here.
            </p>

          </div>
        ) : (
          <div className="table-container">

            <table className="applications-table">

              <thead>

                <tr>

                  <th>
                    Company
                  </th>

                  <th>
                    Position
                  </th>

                  <th>
                    Date
                  </th>

                  <th>
                    Status
                  </th>

                  <th>
                    Response
                  </th>

                </tr>

              </thead>

              <tbody>

                {applications.map(
                  (application) => (
                    <tr
                      key={
                        application.id
                      }
                    >

                      {/* COMPANY */}

                      <td>

                        <strong>
                          {
                            application.company
                          }
                        </strong>

                      </td>

                      {/* POSITION */}

                      <td>

                        <div>
                          {
                            application.job_title
                          }
                        </div>

                        {application.job_url && (
                          <a
                            href={
                              application.job_url
                            }
                            target="_blank"
                            rel="noreferrer"
                            style={{
                              fontSize:
                                "12px"
                            }}
                          >
                            View Job →
                          </a>
                        )}

                      </td>

                      {/* DATE */}

                      <td>
                        {formatDate(
                          application.applied_date
                        )}
                      </td>

                      {/* STATUS */}

                      <td>

                        <select
                          value={
                            application.status
                          }
                          disabled={
                            updatingApplicationId ===
                            application.id
                          }
                          onChange={(event) =>
                            updateApplication(
                              application.id,
                              event.target.value,
                              undefined
                            )
                          }
                          style={{
                            padding:
                              "7px 10px",
                            borderRadius:
                              "8px",
                            border:
                              "1px solid #d1d5db",
                            background:
                              getStatusStyle(
                                application.status
                              ).background,
                            color:
                              getStatusStyle(
                                application.status
                              ).color,
                            fontWeight: 600
                          }}
                        >

                          {STATUS_OPTIONS.map(
                            (status) => (
                              <option
                                key={status}
                                value={status}
                              >
                                {status}
                              </option>
                            )
                          )}

                        </select>

                      </td>

                      {/* RESPONSE */}

                      <td>

                        <div
                          style={{
                            display:
                              "flex",
                            flexDirection:
                              "column",
                            gap: "8px"
                          }}
                        >

                          <select
                            value={
                              application.response_type ||
                              ""
                            }
                            disabled={
                              updatingApplicationId ===
                              application.id
                            }
                            onChange={(event) =>
                              updateApplication(
                                application.id,
                                undefined,
                                event.target
                                  .value
                              )
                            }
                            style={{
                              padding:
                                "7px 10px",
                              borderRadius:
                                "8px",
                              border:
                                "1px solid #d1d5db",
                              background:
                                getResponseStyle(
                                  application.response_type
                                ).background,
                              color:
                                getResponseStyle(
                                  application.response_type
                                ).color,
                              fontWeight: 600
                            }}
                          >

                            <option value="">
                              No response
                            </option>

                            {RESPONSE_OPTIONS.map(
                              (response) => (
                                <option
                                  key={
                                    response
                                  }
                                  value={
                                    response
                                  }
                                >
                                  {response}
                                </option>
                              )
                            )}

                          </select>

                          {application.response_type && (
                            <span
                              style={{
                                ...getResponseStyle(
                                  application.response_type
                                ),
                                padding:
                                  "4px 8px",
                                borderRadius:
                                  "12px",
                                fontSize:
                                  "12px",
                                fontWeight:
                                  600,
                                width:
                                  "fit-content"
                              }}
                            >
                              {
                                application.response_type
                              }
                            </span>
                          )}

                        </div>

                      </td>

                    </tr>
                  )
                )}

              </tbody>

            </table>

          </div>
        )}

      </div>

      {/* =====================================================
          QUICK ACTIONS
      ===================================================== */}

      <div className="dashboard-card">

        <div className="section-header">

          <div>
            <h2>
              ⚡ Quick Actions
            </h2>

            <p>
              Continue using JobPilot.
            </p>
          </div>

        </div>

        <div
          style={{
            display: "flex",
            gap: "15px",
            flexWrap: "wrap"
          }}
        >

          <Link to="/jobs">
            <button className="primary-button">
              🔎 Find Matching Jobs
            </button>
          </Link>

          <Link to="/profile">
            <button className="secondary-button">
              👤 Update Profile
            </button>
          </Link>

          <Link to="/">
            <button className="secondary-button">
              🏠 Home
            </button>
          </Link>

        </div>

      </div>

    </div>
  );
}

export default Dashboard;