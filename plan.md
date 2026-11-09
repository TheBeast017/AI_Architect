# plan.md — Engineering Design Agent

> **Resume protocol:** read this file top to bottom, run `make test`,
> then take the first unchecked `[ ]` item under **"Next 5 actions"**. When an item is truly finished
> (code written **and** verified by a test/run), change `[ ]` to `[x]` and add a one-line note.
> Never tick a box for code that was written but not run. Items marked `(written, unverified)` stay `[ ]`.

Source of truth for scope: the concept doc (sections referenced as "doc §x").
Start narrow: **one component family = wall-mounted cantilever bracket** (doc §15.1, §17.4).

Legend: `[x]` done & verified · `[ ]` not done · `(written, unverified)` code exists but was never run in a real environment

---

## Status snapshot
- Working today: text → spec → LHS + differential-evolution search → analytical-beam evaluation → constraints → Pareto → markdown report + STL + JSONL/CSV records; CLI + FastAPI; FreeCAD STEP export and Gmsh tet meshing; repeatable aluminium-vs-steel screening comparison; React presentation UI. **15/15 tests pass.**
- NOT working yet: CalculiX solve / real FEA results, full buckling FEA, ML surrogate, MLflow, datasets downloaded.
- Known risk: the 1D model cannot judge buckling; a conservative rib-slenderness screen now blocks its most obvious thin/tall-rib exploit (see `docs/limitations.md`).

## Next 5 actions (do in order)
- [x] 1. Install FreeCAD (`freecadcmd`), run `cad/freecad_script.py` output, confirm valid STEP + non-zero volume → Phase 3 — FreeCAD 1.1.4 exported and re-imported one valid solid; volume 312,000 mm³.
- [ ] 2. Install Gmsh + CalculiX (`ccx`), mesh the STEP, solve one bracket → Phase 4 — Gmsh 4.13.1 produced a verified 8,610-tet mesh; `ccx` is not installed or available in winget, and CalculiX’s official site provides source release 2.23 rather than a checksum-backed Windows binary, so no unverified download or solve has been claimed.
- [ ] 3. Cross-check beam vs FEA on 20 random designs; record the error → Phase 4
- [x] 4. Add rib slenderness / buckling constraint so the optimiser stops exploiting the 1D model → Phase 5 — 15:1 height/thickness screen added and regression-tested; FEA buckling remains required.
- [ ] 5. Run `scripts/fetch_datasets.py zenodo-files zenodo_topopt_v2` and record license/size → Phase 2

---

## Phase 0 — Foundation
- [x] Repo layout, `pyproject.toml`, Makefile, `.gitignore`
- [x] Package `src/engagent/` with modules mapped to doc §3 (`docs/architecture.md`)
- [x] Data folder structure from doc §17.5 (`engineering-agent-data/`)
- [x] pytest suite (`tests/`) — 15 passing
- [ ] CI (GitHub Actions: install, `pytest`)
- [ ] Pre-commit (ruff/black)

## Phase 1 — Requirements → Engineering spec (doc §3.2–3.3, §7.1)
- [x] `EngineeringSpec` schema with provenance (explicit / inferred / assumed) — `schemas.py`
- [x] Rule-based parser (kg, mm/cm/m, deflection, material, safety factor, objectives) — `requirements.py`
- [x] Rule: payload & load offset are NEVER defaulted; other defaults are flagged assumptions (tested)
- [x] `NEEDS_INPUT` status returns questions instead of inventing values
- [ ] More units: inches, lb/lbf, N directly, degrees
- [ ] Load direction, load application point, multiple load cases, moment-only loads
- [ ] Interactive clarification loop (CLI/API asks → user answers → re-parse)
- [ ] Mounting-hole pattern + bolt size in spec

## Phase 2 — Data acquisition (doc §17)
- [x] Source registry with all doc links — `datasets/sources.json`
- [x] `scripts/fetch_datasets.py list` works offline
- [ ] `zenodo-files` command tested with network (check size + license of record 8191138) (written, unverified)
- [ ] `download` command tested on one small file; manifest line written (written, unverified)
- [ ] Stage 1: download a SMALL ABC sample; confirm it opens/validates in FreeCAD
- [ ] Stage 2: small subset of Zenodo topology-opt data OR reproduce a DTU example (do NOT pull the 17 GB archive blindly)
- [ ] Record license + citation per source in `engineering-agent-data/licenses/`
- [ ] Build `manifests/` index (design_id → files) and `splits/` (split by design family, doc §17.4)
- [ ] Unit-normalisation + comparability check before merging any external labels (doc §17.7)

## Phase 3 — CAD / geometry (doc §4, §10, §12.1)
- [x] Parametric bracket (`BracketParams`) + design space + LHS sampling
- [x] Geometry validation rules (envelope, min wall, rib limits) — `generators/bracket.py`
- [x] Dependency-free STL export for visualisation — `cad/stl.py` (overlapping solids, display only)
- [x] FreeCAD script emitter — `cad/freecad_script.py` — emitted representative bracket script and executed in FreeCAD 1.1.4.
- [x] FreeCAD installed; script produces valid STEP + FCStd; solid `isValid()` — re-imported STEP is valid, one solid, 312,000 mm³ volume.
- [ ] Replace overlapped-box STL with a real fused solid (via FreeCAD or CadQuery/OCCT)
- [ ] Additional configurations: L-bracket, box section, truss/lattice (doc §4.2)
- [ ] Back plate + bolt holes parameterised (currently fixed 10 mm plate, not analysed)
- [ ] Interference check against reserved regions
- [ ] Export STEP, STL, 3MF, PNG/PDF set (doc §10.4)

## Phase 4 — Meshing & simulation (doc §5)
- [x] `SimBackend` protocol + `SimResult` (solver failure ≠ structural failure)
- [x] Analytical beam backend (variable T-section, unit-load deflection)
- [x] Closed-form validation test (deflection, stress, mass) passes
- [x] Numerical checks: finite results, discretisation convergence
- [x] Gmsh meshing script (STEP → 3D tet mesh, size control) — Gmsh 4.13.1 generated `bracket.msh`: 2,632 nodes / 8,610 tetrahedra (3–6 mm size control).
- [ ] CalculiX `.inp` writer: material, fixed wall face, distributed tip load
- [ ] Run `ccx`, parse `.frd/.dat` → `SimResult(fidelity="FEA-3D")`
- [ ] Mesh-refinement study (3 mesh sizes) + reaction-force equilibrium check
- [ ] Cross-validate beam model vs FEA; document error and where beam is non-conservative
- [ ] Linear buckling (eigenvalue) analysis for ribs/plates
- [ ] Stress singularity handling at load/support patches
- [ ] Optional: modal, fatigue, thermal (only if component needs them, doc §5.7–5.8)

## Phase 5 — Optimisation & decision loop (doc §6, §8, §9)
- [x] Latin-hypercube candidate sampling
- [x] SciPy differential evolution with penalty for hard constraints
- [x] Pareto filter + ranks (mass, cost proxy, deflection)
- [x] Honest termination wording (feasible found ≠ global optimum)
- [x] Reproducibility test (same seed → same best design)
- [x] Rib slenderness / min-web screening constraint (stops thin-tall-rib exploit) — configurable 15:1 height/thickness cap; verified by regression test (not a buckling analysis)
- [ ] Failure-diagnosis-driven modification (doc §8.5–8.6): use violated constraint to propose the next design, instead of blind search
- [ ] NSGA-II or similar true multi-objective optimiser (e.g. pymoo)
- [ ] Bayesian optimisation for expensive FEA evaluations
- [ ] Robustness under uncertainty (load ±, tolerance, material scatter) (doc §9.5)
- [ ] Manufacturing-aware ranking (machined vs additive rules) (doc §9.4, §10.3)
- [ ] Topology optimisation prototype (SIMP, 2D) + reconstruction to CAD (doc §4.3, §10.1)
- [ ] Early-stopping on no-improvement + evaluation budget in spec

## Phase 6 — AI components (doc §7, §12.4)
- [x] LLM extractor written, forced-INFERRED provenance, no-invention prompt — `llm/anthropic_extractor.py` (written, unverified)
- [ ] LLM extractor tested live (API key) against a set of 20 sample prompts; compare with rule parser
- [ ] LLM-written plain-language summary of results (numbers inserted from records, never computed by LLM)
- [ ] Failure classifier narrative (geometry vs mesh vs solver vs constraint)
- [ ] Retrieval over approved material DB / standards (doc §7.2)
- [ ] Surrogate v1: scikit-learn regressors on `records.csv` (mass, stress, deflection)
- [ ] Surrogate evaluation: MAE/RMSE/bias + constraint-boundary classification accuracy (doc §14.5)
- [ ] Held-out test split by parameter region; periodic real-solver correction loop
- [ ] PyTorch surrogate / geometry model (only after v1 baseline is beaten)

## Phase 7 — Data management & tracking (doc §11)
- [x] One record per candidate/simulation with provenance fields (`records.py`), JSONL + CSV
- [x] Duplicate designs reused, not re-recorded (same params + spec hash)
- [ ] Persist solver version + mesh settings once FEA exists
- [ ] MLflow tracking of optimisation runs
- [ ] PostgreSQL store (specs, designs, runs)
- [ ] Background job queue for long simulations (RQ/Celery)
- [ ] Software-version capture (FreeCAD, CalculiX, Gmsh) in every record

## Phase 8 — API & UI (doc §12.5)
- [x] FastAPI: `/health`, `/spec/parse`, `/design/run` (tested)
- [ ] Async run endpoint + job status polling
- [x] React front-end: request form, assumptions panel, results table — Vite-built React UI is served at `/`; verified interactive design run.
- [ ] Three.js STL viewer; clearly separate geometry view vs simulation vs conclusions — parametric Three.js preview (rotate/pan/zoom) is now in the React UI; loading exported STL files remains to be added.
- [ ] Dockerfile / docker-compose (api + postgres + mlflow)

## Phase 9 — Reporting (doc §3.8, §10.5, §14)
- [x] Markdown report: spec + provenance, assumptions, search stats, Pareto table, limitations, no-certification note
- [x] Feasibility metrics: geometry validity, simulation completion, constraint satisfaction rates
- [ ] Stress / deflection plots (PNG) embedded in report
- [ ] PDF report export
- [ ] Dimensioned drawing output
- [ ] Optimisation-history plot (convergence, Pareto front)

## Phase 10 — Validation & hardening (doc §14–15)
- [ ] Benchmark vs textbook problems with known answers (beyond the rectangular cantilever)
- [ ] Compare DE vs random search vs Bayesian on equal evaluation budgets
- [ ] Sensitivity to initial candidates / repeated-run stability
- [ ] Unit-consistency test suite
- [ ] Review all defaults/assumptions with a qualified engineer before any real use

---

## Decisions log
- Brackets only, first. Generalising to arbitrary components is out of scope (doc §15.1).
- Analytical beam is a *screening* model, not a verdict; FEA is the target evaluator.
- LLM never computes stress/safety; it only fills a schema and summarises stored numbers.
- Units everywhere: mm, N, MPa, kg.

## Change log
- v0.1 — Scaffold created; Phases 0, 1 (core), 4 (analytical), 5 (core), 7 (records), 9 (markdown) working; FreeCAD/CalculiX/data/UI pending.
