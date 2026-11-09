import { useState } from "react";
import BracketViewer from "../BracketViewer";

export default function HomePage() {
  const [promptText, setPromptText] = useState("");
  const [allowDefaults, setAllowDefaults] = useState(true);
  const [nSamples, setNSamples] = useState(400);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [llmInterpretation, setLlmInterpretation] = useState(null);
  const [designReasoning, setDesignReasoning] = useState(null);

  // Mandatory engineering inputs the user can provide directly.
  // These map to spec_overrides sent to the backend /design/run endpoint.
  const [mandatoryInputs, setMandatoryInputs] = useState({
    payload_mass_kg: "",
    load_offset_mm: "",
    max_deflection_mm: ""
  });

  const updateMandatoryInput = (key, value) => {
    setMandatoryInputs((prev) => ({ ...prev, [key]: value }));
  };

  const [bracketParams, setBracketParams] = useState({
    arm_length_mm: 300,
    width_mm: 60,
    thickness_mm: 8,
    rib_thickness_mm: 6,
    rib_height_mm: 25,
    rib_length_mm: 200,
    material_key: "AL6061-T6"
  });

  const handleRun = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setLlmInterpretation(null);
    setDesignReasoning(null);

    try {
      // Build spec_overrides from any mandatory inputs the user provided.
      // The backend's _apply_overrides() only fills fields the parser left as None,
      // so user-entered values take priority over LLM inference and defaults.
      const spec_overrides = {};
      for (const key of ["payload_mass_kg", "load_offset_mm", "max_deflection_mm"]) {
        const val = mandatoryInputs[key];
        if (val !== "" && val != null && !Number.isNaN(Number(val))) {
          spec_overrides[key] = Number(val);
        }
      }

      const response = await fetch("/design/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: promptText,
          allow_defaults: allowDefaults,
          n_samples: Number(nSamples),
          seed: 42,
          spec_overrides
        })
      });

      if (!response.ok) {
        throw new Error(`Server returned status ${response.status}. Make sure the FastAPI backend is running on port 8000.`);
      }

      const data = await response.json();
      setResult(data);

      // Display LLM analysis steps if available
      if (data.llm_step) {
        if (data.llm_step.step_1_extraction) {
          setLlmInterpretation({
            success: data.llm_step.step_1_extraction.success,
            model: data.llm_step.step_1_extraction.model_used,
            note: "LLM interpreted your request and extracted engineering parameters"
          });
        }
        if (data.llm_step.step_2_design_reasoning) {
          setDesignReasoning({
            success: data.llm_step.step_2_design_reasoning.success,
            model: data.llm_step.step_2_design_reasoning.model_used,
            notes: data.llm_step.step_2_design_reasoning.design_notes || [],
            violations: data.llm_step.step_2_design_reasoning.constraint_violations || []
          });
        }
      }

      // Extract best design parameters if available
      // Handle different response structures
      const params = data.best_params || data.best_feasible?.params || data.params;
      if (params) {
        setBracketParams({
          arm_length_mm: params.arm_length_mm || 300,
          width_mm: params.width_mm || 60,
          thickness_mm: params.thickness_mm || 8,
          rib_thickness_mm: params.rib_thickness_mm || 6,
          rib_height_mm: (params.rib_height_frac || 0.3) * (params.width_mm || 60),
          rib_length_mm: (params.rib_length_frac || 0.8) * params.arm_length_mm,
          material_key: data.spec?.material_key || data.material_key || "AL6061-T6"
        });
      }
    } catch (err) {
      setError(err.message || "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page home-page" style={{ padding: "2rem", maxWidth: "1200px", margin: "0 auto" }}>
      <div style={{ marginBottom: "2rem", textAlign: "center" }}>
        <h2 style={{ fontSize: "2.2rem", marginBottom: "0.5rem" }}>prosBuilder Design Studio</h2>
        <p style={{ color: "var(--muted)", fontSize: "1.1rem" }}>
          Type your engineering requirements in natural language. The AI interprets your request and optimizes geometry, evaluates physics, and renders the 3D model instantly.
        </p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "2rem", alignItems: "start" }}>
        {/* Left column: Input Form & Controls */}
        <div style={{ background: "var(--card-bg)", padding: "1.8rem", borderRadius: "12px", border: "1px solid var(--line)", boxShadow: "0 4px 12px rgba(0,0,0,0.05)" }}>
          <h3 style={{ marginBottom: "1rem", fontSize: "1.2rem" }}>Design Request Prompt</h3>

          <form onSubmit={handleRun}>
            <div style={{ marginBottom: "1.2rem" }}>
              <textarea
                value={promptText}
                onChange={(e) => setPromptText(e.target.value)}
                rows={4}
                style={{
                  width: "100%",
                  padding: "12px",
                  borderRadius: "8px",
                  border: "1px solid var(--line)",
                  background: "var(--bg-color)",
                  color: "var(--text-color)",
                  fontFamily: "inherit",
                  fontSize: "0.95rem",
                  resize: "vertical"
                }}
                placeholder="e.g., Design a lightweight aluminum bracket for a 25 kg payload, 300 mm from the wall, max deflection 1 mm"
                required
              />
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginBottom: "1.2rem" }}>
              <div>
                <label style={{ display: "block", fontSize: "0.85rem", marginBottom: "0.4rem", color: "var(--muted)" }}>
                  Optimization Samples
                </label>
                <input
                  type="number"
                  value={nSamples}
                  onChange={(e) => setNSamples(e.target.value)}
                  min={100}
                  max={2000}
                  step={100}
                  style={{
                    width: "100%",
                    padding: "8px 12px",
                    borderRadius: "6px",
                    border: "1px solid var(--line)",
                    background: "var(--bg-color)",
                    color: "var(--text-color)"
                  }}
                />
              </div>

              <div style={{ display: "flex", alignItems: "center", paddingTop: "1.5rem" }}>
                <label style={{ display: "flex", alignItems: "center", gap: "0.5rem", cursor: "pointer", fontSize: "0.9rem" }}>
                  <input
                    type="checkbox"
                    checked={allowDefaults}
                    onChange={(e) => setAllowDefaults(e.target.checked)}
                    style={{ width: "16px", height: "16px" }}
                  />
                  Allow smart defaults for missing fields
                </label>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              style={{
                width: "100%",
                padding: "0.9rem",
                background: "var(--primary-blue, #3182ce)",
                color: "white",
                border: "none",
                borderRadius: "8px",
                fontWeight: 600,
                fontSize: "1rem",
                cursor: loading ? "wait" : "pointer",
                transition: "opacity 0.2s"
              }}
            >
              {loading ? "System is optimizing your design..." : "Run Design Optimization 🚀"}
            </button>
          </form>

          {error && (
            <div style={{ marginTop: "1rem", padding: "10px", background: "#fee2e2", color: "#991b1b", borderRadius: "6px", fontSize: "0.9rem" }}>
              {error}
            </div>
          )}

          {/* Mandatory engineering inputs - the values the optimizer actually needs.
              These are sent as spec_overrides so they take priority over LLM inference. */}
          <div style={{ marginTop: "1.5rem", padding: "1rem", background: "var(--surface)", borderRadius: "8px", border: "1px solid var(--line)" }}>
            <h4 style={{ marginBottom: "0.25rem", fontSize: "1rem", color: "var(--text-color)" }}>Additional input needed</h4>
            <p style={{ fontSize: "0.8rem", color: "var(--muted)", marginBottom: "0.75rem" }}>
              Provide the mandatory engineering parameters here. Leave blank to let the system infer them from your request.
            </p>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.75rem" }}>
              <div>
                <label style={{ display: "block", fontSize: "0.8rem", marginBottom: "0.3rem", color: "var(--muted)" }}>
                  Payload mass (kg)
                </label>
                <input
                  type="number"
                  step="any"
                  value={mandatoryInputs.payload_mass_kg}
                  onChange={(e) => updateMandatoryInput("payload_mass_kg", e.target.value)}
                  placeholder="e.g. 25"
                  style={{
                    width: "100%",
                    padding: "8px 10px",
                    borderRadius: "6px",
                    border: "1px solid var(--line)",
                    background: "var(--bg-color)",
                    color: "var(--text-color)",
                    fontSize: "0.9rem"
                  }}
                />
              </div>
              <div>
                <label style={{ display: "block", fontSize: "0.8rem", marginBottom: "0.3rem", color: "var(--muted)" }}>
                  Load offset (mm)
                </label>
                <input
                  type="number"
                  step="any"
                  value={mandatoryInputs.load_offset_mm}
                  onChange={(e) => updateMandatoryInput("load_offset_mm", e.target.value)}
                  placeholder="e.g. 300"
                  style={{
                    width: "100%",
                    padding: "8px 10px",
                    borderRadius: "6px",
                    border: "1px solid var(--line)",
                    background: "var(--bg-color)",
                    color: "var(--text-color)",
                    fontSize: "0.9rem"
                  }}
                />
              </div>
              <div style={{ display: "flex", flexDirection: "column" }}>
                <label style={{ display: "block", fontSize: "0.8rem", marginBottom: "0.3rem", color: "var(--muted)" }}>
                  Max deflection (mm)
                </label>
                <input
                  type="number"
                  step="any"
                  value={mandatoryInputs.max_deflection_mm}
                  onChange={(e) => updateMandatoryInput("max_deflection_mm", e.target.value)}
                  placeholder="e.g. 1.0"
                  style={{
                    width: "100%",
                    padding: "8px 10px",
                    borderRadius: "6px",
                    border: "1px solid var(--line)",
                    background: "var(--bg-color)",
                    color: "var(--text-color)",
                    fontSize: "0.9rem"
                  }}
                />
              </div>
              <div style={{ display: "flex", alignItems: "flex-end" }}>
                <button
                  type="button"
                  onClick={() => setMandatoryInputs({ payload_mass_kg: "", load_offset_mm: "", max_deflection_mm: "" })}
                  style={{
                    width: "100%",
                    padding: "8px",
                    background: "transparent",
                    color: "var(--muted)",
                    border: "1px solid var(--line)",
                    borderRadius: "6px",
                    cursor: "pointer",
                    fontSize: "0.85rem"
                  }}
                >
                  Clear all
                </button>
              </div>
            </div>
          </div>

          {/* LLM Interpretation display */}
          {llmInterpretation && (
            <div style={{ marginTop: "1rem", padding: "1rem", background: "var(--surface)", borderRadius: "8px", border: "1px dashed var(--line)" }}>
              <h4 style={{ marginBottom: "0.5rem", color: "var(--accent)" }}>LLM Interpretation (Step 1)</h4>
              <p style={{ fontSize: "0.9rem", color: "var(--muted)" }}>
                <strong>Model:</strong> {llmInterpretation.model} | <strong>Status:</strong> {llmInterpretation.success ? "✓ Success" : "✗ Failed"}
              </p>
              <p style={{ fontSize: "0.85rem", marginTop: "0.5rem" }}>
                {llmInterpretation.note}
              </p>
            </div>
          )}

          {/* Design Reasoning display */}
          {designReasoning && (
            <div style={{ marginTop: "1rem", padding: "1rem", background: "var(--surface)", borderRadius: "8px", border: "1px dashed var(--line)" }}>
              <h4 style={{ marginBottom: "0.5rem", color: "var(--accent)" }}>LLM Design Reasoning (Step 2)</h4>
              <p style={{ fontSize: "0.9rem", color: "var(--muted)" }}>
                <strong>Model:</strong> {designReasoning.model} | <strong>Status:</strong> {designReasoning.success ? "✓ Success" : "✗ Failed"}
              </p>
              {designReasoning.notes.length > 0 && (
                <div style={{ marginTop: "0.5rem" }}>
                  <strong style={{ fontSize: "0.9rem", color: "var(--muted)" }}>Design Notes:</strong>
                  <ul style={{ fontSize: "0.8rem", marginLeft: "1.2rem", marginTop: "0.25rem" }}>
                    {designReasoning.notes.map((note, i) => <li key={i}>{note}</li>)}
                  </ul>
                </div>
              )}
              {designReasoning.violations.length > 0 && (
                <div style={{ marginTop: "0.5rem", color: "#f59e0b" }}>
                  <strong>Constraint Issues:</strong>
                  <ul style={{ fontSize: "0.8rem", marginLeft: "1.2rem", marginTop: "0.25rem" }}>
                    {designReasoning.violations.map((v, i) => <li key={i}>{v}</li>)}
                  </ul>
                </div>
              )}
            </div>
          )}

          {result && result.questions && result.questions.length > 0 && (
            <div style={{ marginTop: "1rem", padding: "10px", background: "#fef3c7", color: "#92400e", borderRadius: "6px", fontSize: "0.9rem" }}>
              <strong>Additional input needed:</strong>
              <ul style={{ margin: "0.5rem 0 0 1rem" }}>
                {result.questions.map((q, i) => <li key={i}>{q}</li>)}
              </ul>
            </div>
          )}

          {result && result.best_feasible && (
            <div style={{ marginTop: "1.5rem", borderTop: "1px solid var(--line)", paddingTop: "1.2rem" }}>
              <h4 style={{ marginBottom: "0.8rem", color: "var(--accent)" }}>Optimization Results</h4>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.8rem", fontSize: "0.9rem" }}>
                <div style={{ background: "var(--surface)", padding: "10px", borderRadius: "6px" }}>
                  <strong>Mass:</strong> {result.best_feasible.mass_kg} kg
                </div>
                <div style={{ background: "var(--surface)", padding: "10px", borderRadius: "6px" }}>
                  <strong>Von Mises Stress:</strong> {result.best_feasible.max_stress_mpa} MPa
                </div>
                <div style={{ background: "var(--surface)", padding: "10px", borderRadius: "6px" }}>
                  <strong>Deflection:</strong> {result.best_feasible.max_deflection_mm} mm
                </div>
                <div style={{ background: "var(--surface)", padding: "10px", borderRadius: "6px" }}>
                  <strong>Safety Factor:</strong> {result.best_feasible.fos_yield}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Right column: Interactive 3D Viewer */}
        <div>
          <div style={{ marginBottom: "1rem", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <h3 style={{ fontSize: "1.2rem" }}>Interactive 3D Model</h3>
            <span style={{ fontSize: "0.8rem", color: "var(--muted)", background: "var(--surface)", padding: "4px 8px", borderRadius: "4px" }}>
              Hover over faces for details
            </span>
          </div>
          <BracketViewer params={bracketParams} />
        </div>
      </div>
    </div>
  );
}