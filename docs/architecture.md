# Architecture (maps to concept doc section 3)
```
text -> requirements.py -> EngineeringSpec (schemas.py; explicit/inferred/assumed, unresolved never invented)
     -> design_space.py (variables, LHS) -> generators/bracket.py (geometry validation)
     -> sim/* backend (analytical_beam now; calculix later) -> verify.py (constraints, failure class)
     -> records.py (1 row per candidate) -> optimize.py (LHS + differential evolution) -> pareto.py
     -> report.py + cad/stl.py -> agent.py (orchestrates) -> cli.py / api/main.py
```
Failure classes are kept separate: GEOMETRY_INVALID, SOLVER_FAILED (calculation unreliable), CONSTRAINT_VIOLATED, FEASIBLE.
To add a component family: new params dataclass + generator/validator + backend support + design space builder.
