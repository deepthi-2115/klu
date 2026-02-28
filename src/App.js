import React, { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [resume, setResume] = useState(null);
  const [role, setRole] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!resume || !role) {
      alert("Please upload resume and enter role");
      return;
    }

    const formData = new FormData();
    formData.append("resume", resume);
    formData.append("role", role);

    try {
      setLoading(true);
      setResult(null);

      const response = await axios.post(
        "http://127.0.0.1:8000/analyze-role",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      setResult(response.data);
    } catch (error) {
      console.error(error);
      alert("Error connecting to backend. Make sure FastAPI is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>SkillGapAI 🚀</h1>

      {/* Upload Form */}
      <form onSubmit={handleSubmit} className="form">
        <input
          type="file"
          accept=".pdf,.docx,.txt"
          onChange={(e) => setResume(e.target.files[0])}
        />

        <input
          type="text"
          placeholder="Enter target job role (e.g., AI Engineer)"
          value={role}
          onChange={(e) => setRole(e.target.value)}
        />

        <button type="submit">
          {loading ? "Analyzing Resume..." : "Analyze Resume"}
        </button>
      </form>

      {/* Results Section */}
      {result && (
        <div className="result">
          <h2>Analysis Results</h2>

          {/* Predicted Role */}
          <p>
            <strong>Predicted Role:</strong> {result.predicted_role}
          </p>

          {/* Overall Match */}
          <p>
            <strong>Overall Match:</strong>{" "}
            {result.overall_match_percentage}%
          </p>

          <div className="progress-container">
            <div
              className="progress-bar"
              style={{
                width: `${result.overall_match_percentage}%`,
              }}
            ></div>
          </div>

          <p style={{ marginTop: "15px", fontStyle: "italic" }}>
            {result.analysis_summary}
          </p>

          {/* Matched Skills */}
          <h3>✅ Matched Skills</h3>
          <div className="badge-container">
            {result.matched_skills.length > 0 ? (
              result.matched_skills.map((skill, index) => (
                <span className="badge success" key={index}>
                  {skill}
                </span>
              ))
            ) : (
              <p>No matched skills found</p>
            )}
          </div>

          {/* Missing Skills */}
          <h3>⚠ Missing Skills</h3>
          <div className="badge-container">
            {result.missing_skills.length > 0 ? (
              result.missing_skills.map((skill, index) => (
                <span className="badge danger" key={index}>
                  {skill}
                </span>
              ))
            ) : (
              <p>No missing skills 🎉</p>
            )}
          </div>

          {/* Category Breakdown */}
          <h3>📊 Category Breakdown</h3>
          {Object.keys(result.category_breakdown).length > 0 ? (
            Object.entries(result.category_breakdown).map(
              ([category, score]) => (
                <div key={category} style={{ marginBottom: "10px" }}>
                  <p>
                    {category} – {score}%
                  </p>
                  <div className="progress-container">
                    <div
                      className="progress-bar"
                      style={{ width: `${score}%` }}
                    ></div>
                  </div>
                </div>
              )
            )
          ) : (
            <p>No category data available</p>
          )}

          {/* Recommendations */}
          <h3>🎓 Recommended Trainings</h3>
          {result.recommendations.length > 0 ? (
            <ul>
              {result.recommendations.map((rec, index) => (
                <li key={index}>
                  <strong>{rec.skill}</strong> → {rec.course} (
                  {rec.provider}) - {rec.level}
                </li>
              ))}
            </ul>
          ) : (
            <p>No recommendations available</p>
          )}
        </div>
      )}
    </div>
  );
}

export default App;