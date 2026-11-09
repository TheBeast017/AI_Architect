# Engineering Design Report

**Status:** `feasible_found`

## 1. Specification

| Field | Value | Provenance |
|---|---|---|
| component_type | wall_bracket | n/a |
| payload_mass_kg | 25.0 | explicit |
| load_offset_mm | 300.0 | explicit |
| dynamic_factor | 1.5 | assumed |
| material_key | AL6061-T6 | inferred |
| max_deflection_mm | 1.0 | explicit |
| safety_factor | 2.0 | assumed |
| max_width_mm | 150.0 | assumed |
| max_height_mm | 120.0 | assumed |
| min_wall_mm | 3.0 | assumed |

### Assumptions (review before use)
- material grade not stated; AL6061-T6 inferred from generic name - confirm
- dynamic_factor = 1.5 (assumed: allowance for arm acceleration; confirm load case)
- safety_factor = 2.0 (assumed: generic factor on yield; confirm with applicable standard)
- max_width_mm = 150.0 (assumed: placeholder envelope)
- max_height_mm = 120.0 (assumed: placeholder envelope)
- min_wall_mm = 3.0 (assumed: placeholder machining limit)

## 2. Search statistics

| Metric | Value |
|---|---|
| unique designs evaluated | 7647 |
| geometry validity rate | 100.0% |
| simulation completion rate | 99.7% |
| constraint satisfaction rate | 62.8% |
| feasible designs | 4800 |

Differential evolution: nit=40, nfev=3075, message: Maximum number of iterations has been exceeded.. Local/stochastic search result. Global optimality is NOT proven.

## 3. Result

Best feasible (min mass): `D69e7f1b61a` - mass 0.1603 kg, von Mises 123.3 MPa, deflection 0.923 mm, FoS(yield) 2.24, cost proxy 29.24.

### Pareto set (mass, cost proxy, deflection)

| design_id | mass kg | cost proxy | defl mm | vM MPa | width | t | rib t | rib h | rib L |
|---|---|---|---|---|---|---|---|---|---|
| D69e7f1b61a | 0.1603 | 29.24 | 0.923 | 123.3 | 20.1 | 3.4 | 3.1 | 84.6 | 299.7 |
| D3bf155ee67 | 0.1813 | 28.65 | 0.868 | 97.8 | 20.7 | 4.8 | 3.1 | 79.8 | 297.3 |
| D4fb04cd1fb | 0.1934 | 31.61 | 0.745 | 116.2 | 20.2 | 4.2 | 3.4 | 91.3 | 293.1 |
| D978af43e69 | 0.2071 | 32.43 | 0.597 | 72.7 | 21.3 | 5.0 | 3.4 | 88.3 | 299.9 |
| D34d143cc55 | 0.2196 | 32.36 | 0.587 | 80.3 | 21.1 | 4.1 | 4.1 | 90.3 | 298.6 |
| Dbde783f064 | 0.2449 | 35.37 | 0.423 | 73.5 | 20.1 | 4.2 | 4.2 | 104.8 | 297.5 |
| Dae077e00a1 | 0.2697 | 20.22 | 0.844 | 57.7 | 20.5 | 7.0 | 6.5 | 60.4 | 290.6 |
| D1bf1cb6ff2 | 0.2971 | 31.61 | 0.372 | 46.7 | 20.2 | 6.6 | 5.1 | 94.0 | 294.8 |
| D2ec76ece3d | 0.3415 | 28.72 | 0.347 | 30.6 | 20.2 | 14.4 | 3.3 | 80.9 | 292.6 |
| Dde1aa5477b | 0.3778 | 42.59 | 0.250 | 31.6 | 23.0 | 13.2 | 3.3 | 104.8 | 280.0 |
| Db4211c14c8 | 0.4098 | 31.03 | 0.258 | 23.6 | 21.3 | 15.0 | 4.6 | 84.6 | 285.7 |
| D83f8b77ef8 | 0.4378 | 26.21 | 0.260 | 20.6 | 20.1 | 20.0 | 3.8 | 73.7 | 295.7 |
| D3e91c0500b | 0.4808 | 35.62 | 0.191 | 17.3 | 23.9 | 15.9 | 5.0 | 86.2 | 298.0 |
| D1cad4773e8 | 0.5383 | 11.01 | 0.693 | 20.5 | 25.3 | 18.0 | 19.1 | 27.4 | 238.4 |
| D8acbe7ca32 | 0.6382 | 13.52 | 0.274 | 12.6 | 20.1 | 22.7 | 17.5 | 46.4 | 244.7 |
| Df7b27f9af5 | 0.7072 | 20.55 | 0.156 | 9.5 | 21.4 | 15.0 | 15.5 | 71.3 | 299.0 |
| D432f63d982 | 0.7554 | 4.36 | 0.934 | 29.1 | 36.9 | 25.0 | 15.1 | 2.3 | 183.1 |
| D16d7716b4f | 0.7854 | 3.14 | 0.954 | 27.4 | 38.8 | 25.0 | 16.2 | 0.0 | 208.5 |
| Dac64bb15ec | 0.8073 | 4.50 | 0.887 | 27.4 | 39.7 | 24.9 | 15.9 | 2.0 | 191.8 |
| D2023f01245 | 0.8622 | 5.33 | 0.853 | 26.9 | 43.0 | 24.5 | 14.0 | 2.7 | 177.8 |
| Dfae45eccd5 | 0.9354 | 38.30 | 0.070 | 6.2 | 26.7 | 22.2 | 12.7 | 91.8 | 288.4 |
| Ded6e1a3e61 | 1.0602 | 6.43 | 0.690 | 23.0 | 52.2 | 25.0 | 7.1 | 2.4 | 231.3 |
| Dd14147674c | 1.2581 | 5.03 | 0.618 | 17.4 | 63.4 | 24.5 | 7.5 | 0.0 | 227.0 |
| D6c6be6080c | 1.8369 | 7.35 | 0.423 | 11.9 | 92.5 | 24.5 | 17.0 | 0.0 | 232.5 |
| D0e1b4192b6 | 2.7844 | 11.14 | 0.276 | 7.8 | 139.6 | 24.6 | 13.2 | 0.0 | 197.3 |

## 4. Limitations
- 1D beam theory (analytical-1D fidelity)
- back plate and bolts not designed or analysed
- cost is an illustrative proxy, not a quote
- material values are typical handbook numbers, not design allowables
- no shear deflection, buckling or fatigue
- no stress concentration at wall interface or bolts
- stochastic search: a feasible design is not proven globally optimal

> Satisfying the encoded constraints is **not** a safety certification. Verify with FEA, testing and qualified engineering review before real-world use.