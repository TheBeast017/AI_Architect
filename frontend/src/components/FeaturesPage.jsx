import { lazy, Suspense, useState, useEffect } from "react";

function FeaturesPage() {
  const [theme, setTheme] = useState(
    localStorage.getItem("theme") || "light"
  );

  useEffect(() => {
    const html = document.documentElement;
    html.classList.remove("light", "dark");
    html.classList.add(theme);
    localStorage.setItem("theme", theme);
  }, [theme]);

  const compareWithOthers = [
    {
      title: "Traditional CAD Workflows",
      advantages: [
        "prosBuilder: Instant generation from natural language",
        "Traditional CAD: Manual sketching, hours to days",
      ],
    },
    {
      title: "General AI Design Tools",
      advantages: [
        "prosBuilder: Physics-informed optimization",
        "General AI: Purely generative, no performance guarantees",
      ],
    },
    {
      title: "Manual FEA + Optimization",
      advantages: [
        "prosBuilder: Integrated workflow, automated",
        "Manual: Separate tools, manual iteration, days to weeks",
      ],
    },
  ];

  const keyFeatures = [
    {
      icon: "📝",
      title: "Natural Language Input",
      description:
        "Describe your design in plain English - no engineering jargon required",
    },
    {
      icon: "🎯",
      title: "Constrained Optimization",
      description:
        "Differential evolution optimization with penalty-based constraint handling",
    },
    {
      icon: "📊",
      title: "Pareto Front Analysis",
      description:
        "Multi-objective trade-off visualization between mass, stress, and deflection",
    },
    {
      icon: "🔬",
      title: "Physics-Based Simulation",
      description:
        "Analytical beam theory with von Mises stress and displacement calculations",
    },
    {
      icon: "🎨",
      title: "Interactive 3D Viewer",
      description:
        "Three.js-powered real-time visualization with cursor hover details",
    },
    {
      icon: "📄",
      title: "Engineering Reports",
      description:
        "Comprehensive markdown reports with assumptions, search stats, and limitations",
    },
  ];

  const toggleTheme = () => setTheme(theme === "light" ? "dark" : "light");

  return (
    <div className="page features-page" style={{ padding: "2rem" }}>
      <h2 style={{ color: theme === "light" ? "#1a1a2e" : "#f0f0f0" }}>
        Key Features
      </h2>

      <p style={{ marginBottom: "2rem", lineHeight: 1.6, color: theme === "light" ? "#4a5568" : "#a0a0a0" }}>
        prosBuilder combines rule-based engineering expertise with AI-driven
        optimization to deliver feasible, optimized designs from simple text prompts.
      </p>

      <h3 style={{ marginBottom: "1rem", color: theme === "light" ? "#1a1a2e" : "#e0e0e0" }}>
        How We Outperform Other Applications
      </h3>

      <div style={{ background: theme === "light" ? "#f8f9fa" : "#2d3748", borderRadius: "8px", border: `1px solid ${theme === "light" ? "#e2e8f0" : "#4a5568"}`, padding: "1.5rem", marginBottom: "2rem" }}>
        <h4 style={{ marginBottom: "1rem", color: theme === "light" ? "#2d3748" : "#fff" }}>
          Superior to Traditional CAD Workflows
        </h4>
        <ul style={{ margin: "0", paddingLeft: "1.2rem", color: theme === "light" ? "#4a5568" : "#a0a0a0" }}>
          {compareWithOthers[0].advantages.map((adv, i) => (
            <li key={i} style={{ marginBottom: "0.5rem" }}>
              <span style={{ color: theme === "light" ? "#2d3748" : "#fff", marginRight: "0.5rem" }}>{i + 1}. </span>{adv}
            </li>
          ))}
        </ul>
      </div>

      <div style={{ background: theme === "light" ? "#f8f9fa" : "#2d3748", borderRadius: "8px", border: `1px solid ${theme === "light" ? "#e2e8f0" : "#4a5568"}`, padding: "1.5rem", marginBottom: "2rem" }}>
        <h4 style={{ marginBottom: "1rem", color: theme === "light" ? "#2d3748" : "#fff" }}>
          Superior to General AI Design Tools
        </h4>
        <ul style={{ margin: "0", paddingLeft: "1.2rem", color: theme === "light" ? "#4a5568" : "#a0a0a0" }}>
          {compareWithOthers[1].advantages.map((adv, i) => (
            <li key={i} style={{ marginBottom: "0.5rem" }}>
              <span style={{ color: theme === "light" ? "#2d3748" : "#fff", marginRight: "0.5rem" }}>{i + 1}. </span>{adv}
            </li>
          ))}
        </ul>
      </div>

      <div style={{ background: theme === "light" ? "#f8f9fa" : "#2d3748", borderRadius: "8px", border: `1px solid ${theme === "light" ? "#e2e8f0" : "#4a5568"}`, padding: "1.5rem", marginBottom: "2rem" }}>
        <h4 style={{ marginBottom: "1rem", color: theme === "light" ? "#2d3748" : "#fff" }}>
          Superior to Manual FEA + Optimization
        </h4>
        <ul style={{ margin: "0", paddingLeft: "1.2rem", color: theme === "light" ? "#4a5568" : "#a0a0a0" }}>
          {compareWithOthers[2].advantages.map((adv, i) => (
            <li key={i} style={{ marginBottom: "0.5rem" }}>
              <span style={{ color: theme === "light" ? "#2d3748" : "#fff", marginRight: "0.5rem" }}>{i + 1}. </span>{adv}
            </li>
          ))}
        </ul>
      </div>

      <h3 style={{ margin: "2rem 0 1rem", color: theme === "light" ? "#1a1a2e" : "#e0e0e0" }}>Feature Details</h3>

      <div style={{ display: "grid", gap: "1.5rem", marginBottom: "1.5rem" }}>
        {keyFeatures.map((feature, idx) => (
          <div
            key={idx}
            style={{
              background: theme === "light" ? "#f8f9fa" : "#2d3748",
              border: `1px solid ${theme === "light" ? "#e2e8f0" : "#4a5568"}`,
              borderRadius: "8px",
              padding: "1.5rem",
            }}
          >
            <div style={{ fontSize: "2.5rem", marginBottom: "0.5rem" }}>
              {feature.icon}
            </div>
            <h4 style={{ margin: "0 0 0.5rem", color: theme === "light" ? "#2d3748" : "#fff" }}>
              {feature.title}
            </h4>
            <p style={{ margin: "0", fontSize: "0.9rem", lineHeight: 1.5, color: theme === "light" ? "#4a5568" : "#a0a0a0" }}>
              {feature.description}
            </p>
          </div>
        ))}

      </div>

      <div>
        <h4 style={{ marginBottom: "0.5rem" }}>Integration Workflow</h4>
        <ol style={{ margin: "0", paddingLeft: "1.2rem", color: theme === "light" ? "#4a5568" : "#a0a0a0" }}>
          <li>Input natural language design brief</li>
          <li>AI parses requirement into structured engineering specification</li>
          <li>Design space generated with parametric geometry</li>
          <li>Differential evolution optimization runs candidate search</li>
          <li>Pareto front identifies trade-off optimal designs</li>
          <li>Interactive 3D viewer inspects selected design</li>
          <li>Comprehensive engineering report generated</li>
        </ol>
      </div>
      <div style={{ marginTop: "2rem", paddingTop: "1.5rem", borderTopStyle: "solid", borderTopWidth: "1px" }}>
        <p style={{ fontSize: "0.9rem", color: theme === "light" ? "#718096" : "#718096" }}>
          © {new Date().getFullYear()} prosBuilder
        </p>
      </div>
    </div>
  );
}

export default FeaturesPage;