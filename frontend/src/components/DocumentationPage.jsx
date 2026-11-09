import { lazy, Suspense, useState, useEffect } from "react";

function DocumentationPage() {
  const [theme, setTheme] = useState(
    localStorage.getItem("theme") || "light"
  );

  useEffect(() => {
    const html = document.documentElement;
    html.classList.remove("light", "dark");
    html.classList.add(theme);
    localStorage.setItem("theme", theme);
  }, [theme]);

  const docsSections = [
    {
      id: "installation",
      title: "Installation",
      content:
        "To get started with AI Engineering Agent, install the package and set up the required dependencies.",
    },
    {
      id: "quick-start",
      title: "Quick Start",
      content:
        "Run your first design: `python -m engagent run \"your brief\" --out runs/out --allow-defaults`",
    },
    {
      id: "requirements",
      title: "Requirements Syntax",
      content:
        "Supported syntax for parsing engineering requirements including payload, offset, material, safety factor, and deflection limits.",
    },
    {
      id: "parameters",
      title: "Design Parameters",
      content:
        "Understanding the parametric bracket design space and variable ranges.",
    },
    {
      id: "optimization",
      title: "Optimization",
      content:
        "How differential evolution optimization works with constraint penalties.",
    },
    {
      id: "limitations",
      title: "Known Limitations",
      content:
        "The system uses 1D beam theory as a screening model. FEA validation is recommended for final designs.",
    },
  ];

  const toggleTheme = () => setTheme(theme === "light" ? "dark" : "light");

  return (
    <div className="page documentation-page" style={{ padding: "2rem" }}>
      <h2 style={{ color: theme === "light" ? "#1a1a2e" : "#f0f0f0" }}>
        Documentation
      </h2>

      <p style={{ marginBottom: "2rem", lineHeight: 1.6, color: theme === "light" ? "#4a5568" : "#a0a0a0" }}>
        Comprehensive documentation for the AI Engineering Agent system.
      </p>

      <div style={{ background: theme === "light" ? "#f8f9fa" : "#2d3748", borderRadius: "8px", border: `1px solid ${theme === "light" ? "#e2e8f0" : "#4a5568"}`, padding: "1.5rem", marginBottom: "2rem" }}>
        <nav style={{ marginBottom: "1.5rem" }}>
          {docsSections.map((section) => (
            <a
              key={section.id}
              href={`#${section.id}`}
              style={{
                marginRight: "1rem",
                color: theme === "light" ? "#2b6cb0" : "#63b3ed",
                textDecoration: "none",
                fontWeight: "500",
              }}
            >
              {section.title}
            </a>
          ))}
        </nav>
      </div>

      <div style={{ display: "grid", gap: "2rem" }}>
        {docsSections.map((section) => (
          <div
            key={section.id}
            style={{
              background: theme === "light" ? "#fafafa" : "#4a5568",
              borderRadius: "8px",
              padding: "1.5rem",
              color: theme === "light" ? "#2d3748" : "#fff",
            }}
          >
            <h3 style={{ marginBottom: "1rem", borderBottom: `1px solid ${theme === "light" ? "#e2e8f0" : "#4a5568"}`, paddingBottom: "0.5rem" }}>
              {section.title}
            </h3>
            <p style={{ lineHeight: 1.6, margin: "0" }}>
              {section.content}
            </p>
          </div>
        ))}
      </div>

      <div style={{ marginTop: "3rem", paddingTop: "1.5rem", borderTopStyle: "solid", borderTopWidth: "1px" }}>
        <p style={{ fontSize: "0.9rem", color: theme === "light" ? "#718096" : "#718096" }}>
          © {new Date().getFullYear()} prosBuilder
        </p>
        <p style={{ fontSize: "0.8rem", margin: "0.5rem 0 0", color: theme === "light" ? "#718096" : "#718096" }}>
          Contributors: Bhavya Garg, Gautam Singh, Dev Bharadwaj
        </p>
      </div>
    </div>
  );
}

export default DocumentationPage;
