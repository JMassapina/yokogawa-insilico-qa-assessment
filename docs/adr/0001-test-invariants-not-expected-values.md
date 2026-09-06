# ADR-0001: Test Invariants Over Static Expected Numbers
**Status:** Accepted  

### Context
When testing software that models complex, non-linear biological kinetics, asserting hardcoded numerical output literals is a distinct quality trap. A simulation exists because the true scientific target is unknown. Asserting static constants derived from a specific version of code means the test framework simply validates that the software agrees with itself—silently pinning legacy model bugs into golden baseline files.

### Decision
We permanently drop example-based static number testing across our computational pipelines. The framework will exclusively assert rule-based physical and metamorphic properties that must remain true across every execution, regardless of what the final answer turns out to be:
1.  **Mass Balance Conservation:** Mass input parameters must cleanly align with mass accumulation arrays ($Mass_{in} = Mass_{out} + Mass_{acc}$).
2.  **Directional Sanity:** Increasing a substrate profile constraint (e.g., Feed1 Glucose) must never result in a negative cell density slope under positive parameters.
3.  **Boundary Caps:** Output properties like `o2` or `o3` must strictly obey analytical boundary limits derived from equations (e.g., $|o2| \le 2.0$) across the full input spectrum.

### Consequences
This decouples our automated validation signals from legitimate updates made by scientists to the core differential equations. Tests remain robust across architectural shifts, surface real-world algorithmic regressions, and can be easily verified by scientific subject matter experts without requiring code tracing.
