# ADR-0002: Pinning Open Subsystem Defects inside the Codebase
**Status:** Accepted  

### Context
When automated testing suites uncover deep structural bugs in an application under test, engineers often lazily disable the test blocks (`skip`) or alter the system logic using dirty conditional statements to force a green pipeline build. This practice hides active technical debt and desensitizes teams to system regressions.

### Decision
Every confirmed software bug uncovered by the testing suites must be explicitly written into an executable, active test path marked with strict upstream failure markers:
1.  **Backend Pytest Layers:** Marked with `@pytest.mark.xfail(strict=True)`.
2.  **Frontend Playwright Layers:** Marked with `test.fail(true, 'Reason description')`.

### Consequences
The pipeline remains green under active technical debt while keeping open defects fully visible. The moment a developer pushes a code fix, the test path returns an unexpected pass (`XPASS` or unexpected success), forcing the builder to immediately remove the flag and promote the path to a standard live assertion block. This ensures that fixes are consciously verified and never missed.
