import { lazy, Suspense, useState, useEffect } from "react";
import { Routes, Route, NavLink } from "react-router-dom";
import "./index.css";

const HomePage = lazy(() => import("./components/HomePage"));
const AboutPage = lazy(() => import("./components/AboutPage"));
const FeaturesPage = lazy(() => import("./components/FeaturesPage"));
const PerformancePage = lazy(() => import("./components/PerformancePage"));
const DocumentationPage = lazy(() => import("./components/DocumentationPage"));

function App() {
  const [theme, setTheme] = useState(localStorage.getItem("theme") || "light");

  useEffect(() => {
    const root = document.documentElement;
    root.classList.remove("light", "dark");
    root.classList.add(theme);
    localStorage.setItem("theme", theme);

    const manageTheme = (e) => {
      if (e.detail && e.detail.theme) {
        setTheme(e.detail.theme);
      }
    };

    window.addEventListener("theme-change", manageTheme);
    return () => {
      window.removeEventListener("theme-change", manageTheme);
    };
  }, [theme]);

  const toggleTheme = () => {
    const nextTheme = theme === "light" ? "dark" : "light";
    setTheme(nextTheme);
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content" style={{ display: "flex", alignItems: "center", justifyContent: "space-between", width: "100%" }}>
          <h1 className="logo">prosBuilder<span>.ai</span></h1>
          <nav className="main-nav">
            <ul>
              <li>
                <NavLink
                  to="/"
                  className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
                >
                  Design Studio
                </NavLink>
              </li>
              <li>
                <NavLink
                  to="/features"
                  className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
                >
                  Features
                </NavLink>
              </li>
              <li>
                <NavLink
                  to="/performance"
                  className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
                >
                  Performance
                </NavLink>
              </li>
              <li>
                <NavLink
                  to="/about"
                  className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
                >
                  About
                </NavLink>
              </li>
              <li>
                <NavLink
                  to="/documentation"
                  className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
                >
                  Documentation
                </NavLink>
              </li>
            </ul>
          </nav>
          <button type="button" className="theme-toggle" onClick={toggleTheme}>
            {theme === "light" ? "🌙 Dark Mode" : "☀️ Light Mode"}
          </button>
        </div>
      </header>

      <main className="app-main">
        <Suspense fallback={<div className="viewer-loading">Loading page...</div>}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/features" element={<FeaturesPage />} />
            <Route path="/performance" element={<PerformancePage />} />
            <Route path="/about" element={<AboutPage />} />
            <Route path="/documentation" element={<DocumentationPage />} />
          </Routes>
        </Suspense>
      </main>

      <footer className="app-footer" style={{ padding: "1.5rem 2rem", borderTop: "1px solid var(--line)", textAlign: "center", color: "var(--muted)" }}>
        <p>
          © {new Date().getFullYear()} prosBuilder. Made with ❤️ by Kartikay Tewari
        </p>
        <p className="footer-contributors" style={{ marginTop: "0.5rem", fontSize: "0.85rem" }}>
          Contributors: Bhavya Garg, Gautam Singh, Dev Bharadwaj
        </p>
      </footer>
    </div>
  );
}

export default App;