# Engineering Design Agent

Natural-language requirement → structured spec → candidate bracket designs → simulation → constrained
optimisation → Pareto set → traceable report.

```bash
pip install -e ".[api,dev]"
make test
python -m engagent run "25 kg payload, 300 mm from the wall, aluminium, max deflection 1 mm" --out runs/demo --allow-defaults
uvicorn engagent.api.main:app --reload      # http://127.0.0.1:8000/docs
```
Outputs in `runs/demo/`: `report.md`, `records.jsonl/csv`, `spec.json`, `cad/*.stl`. Example: `docs/example_report.md`.

Key behaviours
- Missing payload or load distance → the agent asks instead of guessing. Other defaults need `--allow-defaults` and are listed as assumptions.
- Solver failure, invalid geometry, and constraint violation are separate outcomes.
- Current evaluator is a 1D beam model (screening only). See `docs/limitations.md`. Not a safety certification.
