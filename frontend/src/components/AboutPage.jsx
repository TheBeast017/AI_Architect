import { lazy, Suspense, useState, useEffect } from "react";

function AboutPage() {
  const [theme, setTheme] = useState(
    localStorage.getItem("theme") || "light"
  );

  useEffect(() => {
    const html = document.documentElement;
    html.classList.remove("light", "dark");
    html.classList.add(theme);
    localStorage.setItem("theme", theme);
  }, [theme]);

  const contributors = [
    {
      name: "Kartikay Tewari",
      role: "Lead Developer & AI Architect",
      contributed: "Full system architecture, core algorithm development, FEA integration, documentation",
    },
    {
      name: "Bhavya Garg",
      role: "Co-Developer & ML Engineer",
      contributed: "Surrogate model development, dataset generation, optimization algorithms",
    },
    {
      name: "Gautam Singh",
      role: "CAD & Simulation Engineer",
      contributed: "CAD generation, mesh optimization, validation workflows",
    },
    {
      name: "Dev Bharadwaj",
      role: "Testing & DevOps",
      contributed: "Test suite development, CI/CD pipelines, deployment configuration",
    },
  ];

  const toggleTheme = () => setTheme(theme === "light" ? "dark" : "light");

  return (
    <div className="page about-page" style={{ padding: "2rem" }}>
      <h2 style={{ color: theme === "light" ? "#1a1a2e" : "#f0f0f0" }}>
        About prosBuilder
      </h2>
      <p style={{ marginBottom: "1.5rem", lineHeight: 1.6 }}>
        An autonomous mechanical design optimization system that converts natural
        language engineering requirements into optimized, manufacturable designs
        through AI-driven generation, FEA simulation, and constrained optimization.
      </p>

      <h3 style={{ marginBottom: "1rem", color: theme === "light" ? "#1a1a2e" : "#e0e0e0" }}>
        Team Contributors
      </h3>

      <div style={{ display: "grid", gap: "1.5rem", marginBottom: "2rem" }}>
        {contributors.map((c, idx) => (
          <div
            key={idx}
            style={{
              background: theme === "light" ? "#f8f9fa" : "#2d3748",
              border: `1px solid ${theme === "light" ? "#e2e8f0" : "#4a5568"}`,
              borderRadius: "8px",
              padding: "1.5rem",
            }}
          >
            <h4 style={{ margin: "0 0 0.5rem", color: theme === "light" ? "#2d3748" : "#fff" }}>
              {c.name}
            </h4>
            <p style={{ margin: "0", fontSize: "0.9rem", color: theme === "light" ? "#4a5568" : "#a0a0a0" }}>
              {c.role}
            </p>
            <p style={{ margin: "0.5rem 0 0", fontSize: "0.8rem", color: theme === "light" ? "#718096" : "#718096" }}>
              Contributions: {c.contributed}
            </p>
          </div>
        ))}
      </div>

      <div>
        <h4 style={{ marginBottom: "0.5rem" }}>
          Project Overview
        </h4>
        <p style={{ lineHeight: 1.6, color: theme === "light" ? "#4a5568" : "#a0a0a0" }}>
          AI Engineering Agent bridges the gap between conceptual design and
          engineering validation. The system takes natural language requirements
          like "Design a lightweight aluminum mounting bracket that supports a
          500 N downward load" and produces optimized CAD geometries with
          comprehensive FEA validation reports.
        </p>

        <div style={{
          marginTop: "1.5rem",
          padding: "1.5rem",
          background: theme === "light" ? "#f8f9fa" : "#2d3748",
          borderRadius: "8px",
          border: `1px solid ${theme === "light" ? "#e2e8f0" : "#4a5568"}`,
        }}>
          <h5 style={{ marginBottom: "0.5rem", color: theme === "light" ? "#2d3748" : "#fff" }}>
            Key Capabilities
          </h5>
          <ul style={{ margin: "0", paddingLeft: "1.2rem", color: theme === "light" ? "#4a5568" : "#a0a0a0" }}>
            <li>Natural language to engineering specification conversion</li>
            <li>Parametric design space generation</li>
            <li>Analytical and FEA-based simulation</li>
            <li>Differential evolution optimization</li>
            <li>Pareto-optimal design selection</li>
            <li>Interactive 3D visualization</li>
            <li>Manufacturing constraint enforcement</li>
            <li>Comprehensive engineering reports</li>
          </ul>
        </div>
      </div>

      <footer style={{ marginTop: "2rem", paddingTop: "1.5rem", borderTopStyle: "solid", borderTopWidth: "1px" }}>
        <p>
          © {new Date().getFullYear()} prosBuilder • Made with ❤️ by Kartikay Tewari
        </p>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginTop: "0.5rem" }}>
          <span style={{ fontSize: "0.8rem", color: theme === "light" ? "#718096" : "#718096" }}>
            Contributors:
          </span>
          {[...Array(3)].map((_, idx) => (
            <span
              key={idx}
              style={{
                display: "inline-flex",
                alignItems: "center",
                justifyContent: "center",
                width: "20px",
                height: "20px",
                background: theme === "light" ? "#e2e8f0" : "#4a5568",
                borderRadius: "50%",
                marginLeft: "0.2rem",
                fontSize: "0.6rem",
                fontWeight: "bold",
                color: theme === "light" ? "#2d3748" : "#f0f0f0",
              }}
            >
              ●
            </span>
          ))}
          <span style={{ fontSize: "0.8rem", color: theme === "light" ? "#718096" : "#718096" }}>
            {theme === "light" ? "Bhavya Garg, Gautam Singh, Dev Bharadwaj" : "Bhavya Garg, Gautam Singh, Dev Bharadwaj"}
          </span>
        </div>
      </footer>
    </div>
  );
}

export default AboutPage;