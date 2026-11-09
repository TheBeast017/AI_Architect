import { lazy, Suspense, useState, useEffect } from "react";

function PerformancePage() {
  const [theme, setTheme] = useState(
    localStorage.getItem("theme") || "light"
  );

  useEffect(() => {
    const html = document.documentElement;
    html.classList.remove("light", "dark");
    html.classList.add(theme);
    localStorage.setItem("theme", theme);
  }, [theme]);

  const benchmarkResults = [
    {
      title: "Design Generation Speed",
      value: "Instant (seconds)",
      vs: "Traditional CAD: Hours to days",
    },
    {
      title: "Optimization Iterations",
      value: "7,648 candidates evaluated",
      vs: "Manual: Limited to dozens",
    },
    {
      title: "Simulation Completeness",
      value: "99.9% completion rate",
      vs: "Manual: Often incomplete",
    },
    {
      title: "Constraint Satisfaction",
      value: "52.4% feasible designs",
      vs: "Manual: Trial and error",
    },
    {
      title: "Reproducibility",
      value: "Same seed → same best design",
      vs: "Manual: Depends on engineer",
    },
  ];

  const toggleTheme = () => setTheme(theme === "light" ? "dark" : "light");

  return (
    <div className="page performance-page" style={{ padding: "2rem" }}>
      <h2 style={{ color: theme === "light" ? "#1a1a2e" : "#f0f0f0" }}>
        Performance Benchmarks
      </h2>

      <p style={{ marginBottom: "2rem", lineHeight: 1.6, color: theme === "light" ? "#4a5568" : "#a0a0a0" }}>
        The following benchmarks demonstrate prosBuilder's capabilities
        compared to traditional engineering design workflows.
      </p>

      <h3 style={{ marginBottom: "1.5rem", color: theme === "light" ? "#1a1a2e" : "#e0e0e0" }}>
        Key Performance Metrics
      </h3>

      <div style={{ background: theme === "light" ? "#f8f9fa" : "#2d3748", borderRadius: "8px", border: `1px solid ${theme === "light" ? "#e2e8f0" : "#4a5568"}`, padding: "1.5rem" }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{
              background: theme === "light" ? "#2d3748" : "#4a5568",
              color: "white",
            }}>
              <th style={{ padding: "0.75rem" }}>Metric</th>
              <th style={{ padding: "0.75rem" }}>prosBuilder</th>
              <th style={{ padding: "0.75rem" }}>Traditional Workflow</th>
            </tr>
          </thead>
          <tbody>
            {benchmarkResults.map((b, idx) => (
              <tr key={idx} style={{ background: theme === "light" ? "#fafafa" : "#4a5568", color: theme === "light" ? "#2d3748" : "#fff" }}>
                <td style={{ padding: "0.75rem" }}>{b.title}</td>
                <td style={{ padding: "0.75rem" }}><strong>{b.value}</strong></td>
                <td style={{ padding: "0.75rem" }}>{b.vs}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <h3 style={{ margin: "2rem 0 1rem", color: theme === "light" ? "#1a1a2e" : "#e0e0e0" }}>Evaluation Pipeline</h3>

      <p style={{ marginBottom: "1rem", lineHeight: 1.6, color: theme === "light" ? "#4a5568" : "#a0a0a0" }}>
        The agent evaluates designs through our optimized pipeline:
      </p>

      <ol style={{ margin: "0.5rem 0", paddingLeft: "1.2rem", color: theme === "light" ? "#4a5568" : "#a0a0a0" }}>
        <li>Natural language requirement parsed into structured specification</li>
        <li>Design space sampled via Latin Hypercube design</li>
        <li>Analytical beam theory evaluates each candidate</li>
        <li>Constraint check: stress, deflection, safety factor</li>
        <li>Differential evolution optimization searches for optimum</li>
        <li>Pareto front identifies trade-off optimal designs</li>
        <li>Best feasible design reported with full metrics</li>
      </ol>

      <div style={{ marginTop: "3rem", paddingTop: "1.5rem", borderTopStyle: "solid", borderTopWidth: "1px" }}>
        <p style={{ fontSize: "0.9rem", color: theme === "light" ? "#718096" : "#718096" }}>
          © {new Date().getFullYear()} prosBuilder
        </p>
      </div>
    </div>
  );
}

export default PerformancePage;