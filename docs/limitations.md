# Known limitations (read before trusting any number)
1. The only working evaluator is 1D Euler-Bernoulli beam theory. No FEA yet (plan.md Phase 4).
2. No buckling / lateral-torsional / local plate-buckling calculation. A conservative gusset height/thickness
   screening cap prevents the optimiser exploiting very thin, tall ribs, but it is not an eigenvalue or nonlinear
   buckling analysis; validate the final part with FEA.
3. Wall interface (back plate, bolts, hole stress concentrations) is not designed or analysed.
4. Material values are typical handbook numbers; cost is an illustrative proxy; defaults are flagged assumptions.
5. Differential evolution / LHS find feasible designs; they do not prove global optimality.
6. Meeting encoded constraints is NOT a safety certification (doc 15.7).
