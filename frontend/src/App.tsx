import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import Profile from "./Profile";
import Dashboard from "./Dashboard";
import Jobs from "./Jobs";

function Home() {
  return (
    <div style={{ padding: "40px", fontFamily: "Arial" }}>
      <h1>🚀 JobPilot</h1>

      <p>
        Your AI-powered job search and application assistant.
      </p>

      <br />

      <Link to="/profile">
        <button
          style={{
            padding: "12px 20px",
            marginRight: "10px"
          }}
        >
          Create Profile
        </button>
      </Link>

      <Link to="/dashboard">
        <button
          style={{
            padding: "12px 20px",
            marginRight: "10px"
          }}
        >
          Open Dashboard
        </button>
      </Link>

      <Link to="/jobs">
        <button
          style={{
            padding: "12px 20px"
          }}
        >
          Find Jobs
        </button>
      </Link>
    </div>
  );
}


function App() {
  return (
    <BrowserRouter>

      <Routes>

        <Route
          path="/"
          element={<Home />}
        />

        <Route
          path="/profile"
          element={<Profile />}
        />

        <Route
          path="/dashboard"
          element={<Dashboard />}
        />

        <Route
          path="/jobs"
          element={<Jobs />}
        />

      </Routes>

    </BrowserRouter>
  );
}


export default App;