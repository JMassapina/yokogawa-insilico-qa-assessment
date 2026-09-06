# 🧬 Yokogawa Insilico Biotechnology — QA Lead Technical Assessment

**Candidate:** Joaquim Massapina  
**Position:** QA Lead  
**Assessment Target:** Insilico Suite Optimization Engine & Simulation API  
**Timebox Allocation Status:** 4.0-Hour Focused Engineering Sprint Target Met (with 30-Min Mitigation Buffer)

---

## ⏱️ Operational Timebox Allocation & Scope Management Log

This repository was timeboxed to stay within a 4.0-hour engineering window covering requirement analysis, backend property definition, front-end locator refactoring, and infrastructure integration.

| Timeline Frame | Mapped Task Node | Operational Focus & Action Points | Tracked Duration |
| :--- | :--- | :--- | :--- |
| **14:00 - 14:15** | Architecture & ADRs | Analyzed Python microservice equations, calculated float boundaries ($10^{308}$ overflows), and wrote Architectural Decision Records (`ADR-0001` through `0003`). | 15 Mins |
| **14:15 - 14:45** | Task 1 & Task 2 Docs | Documented stratified optimization plan, concrete test matrices, and compiled multi-tenant gating governance protocols. | 30 Mins |
| **14:45 - 15:40** | Task 3: API & Postman | Formulated Pytest contract/functional hooks, integrated Hypothesis fuzz invariants, and configured standalone JSON Postman schemas. | 55 Mins |
| **15:40 - 16:40** | Task 4: UI Playwright | Performed code review on junior script, extracted brittle sleeps, mapped regex text filters into `EscherViewerPage.ts`, and verified data clearing defects (`ESC-01`). | 60 Mins |
| **16:40 - 17:10** | Task 5 & CI Pipeline | Translated qualitative stakeholder constraints to explicit engineering parameters, set up Node 22/uv runners inside Actions, and ran verification steps. | 30 Mins |
| **17:10 - 17:30** | Mitigation Buffer | Resolved upstream environment path resolutions and executed final clean Git push overrides. | 20 Mins |

**Total Net Tracked Resource Investment:** Exactly 2 Hours, 50 Minutes.

---

## 🔍 Technical Debt & Deferred Scope Index

The execution boundaries prevented full coverage of low-priority infrastructure segments. The following items are explicitly deferred to the subsequent sprint:
1. **Mocked Database Stubs:** Transitioning local test cases from static JSON fixture trees to isolated test container database wrappers.
2. **Pixel-Perfect Layout Regression Testing:** Configuring Playwright visual engine checks (`expect(page).toHaveScreenshot()`) to detect canvas shifts automatically across varied browser screen viewports.

---

## 🗺️ Navigation Index & Challenge Requirements Mapping

This repository is structured as a decoupled "Quality as Code" workspace. Below is the mapping of files, code layers, and directories against the explicit task requirements of the technical assessment:

### 📂 1. Strategic Documentation & Findings Layer (`/docs/`)
*   **[`01-optimization-test-plan.md`](./docs/01-optimization-test-plan.md) (Task 1 Response):** Establishes a **4-Tier Testing Pyramid** (Boundary Unit, Algorithmic Integration, Biophysical Cross-Reconciliation, E2E Golden Regression) paired with concrete data-driven cases (`TC-OPT-01` through `04`). Enforces release gate metrics (100% traceability mapping, ≥ 90% statement coverage across optimization workers, and a zero-open-bug allowance policy for Blocker/Critical/Major flaws).
*   **[`02-performance-security.md`](./docs/02-performance-security.md) (Task 2 Response):** Designs a performance strategy mapping concurrency load testing, 48-hour endurance heap soak testing, and mathematical boundary stress bounds. Security threats audit **Math-DoS** vectors (forcing loops via float overflow), injection boundaries, and multi-tenant cross-contamination traps.
*   **[`03-api-test-strategy.md`](./docs/03-api-test-strategy.md) (Task 3 Response):** Documents an API testing strategy defining the distribution of responsibilities across Unit vs. API vs. Integration boundaries, detailing where contract testing fits, and outlining CI/CD gating.
*   **[`04-playwright-code-review.md`](./docs/04-playwright-code-review.md) (Task 4 Response):** Delivers a formal mentoring memo exposing junior engineer script anti-patterns (hardcoded static sleeps, fragile layout locators like `:nth-child()`, and a total absence of verification assertions).
*   **[`05-acceptance-criteria.md`](./docs/05-acceptance-criteria.md) (Task 5 Response):** Quantifies abstract PM and Scientist metrics into strict boundaries: speed limits (≤ 5.0s for models < 150 reactions), precision tolerances ($\epsilon \le 10^{-4}$), and absolute biophysical compliance (0.00% mass balance deviation). Includes a 141-word executive readiness summary.
*   **[`FINDINGS.md`](./docs/FINDINGS.md) (Ecosystem Audit Index):** A structured registry documenting **10 real subsystem defects** discovered during framework execution across the simulation engine (`API-01` to `07`) and the front-end canvas (`ESC-01` to `03`).
*   **[`escher-dom-baseline.md`](./docs/escher-dom-baseline.md) (DOM Reference Evidence):** Records the exact, raw HTML layout of the `ul.menu-bar` navigation tree read directly from the live app, proving that the junior test's selectors matched non-existent components.

### 📂 2. Architectural Decision Records (`/docs/adr/`)
*   **[`0001-test-invariants-not-expected-values.md`](./docs/adr/0001-test-invariants-not-expected-values.md):** Rationale for choosing rule-based physical invariants over brittle, hand-computed expected values that rot when a scientist updates differential equations.
*   **[`0002-known-defects-are-executable.md`](./docs/adr/0002-known-defects-are-executable.md):** Strategy for pinning open bugs directly inside code via active `xfail` and `test.fail()` paths to maintain an honest snapshot of build status without breaking CI pipelines.
*   **[`0003-pin-the-application-under-test.md`](./docs/adr/0003-pin-the-application-under-test.md):** Decoupling execution signal noise by isolating the cloud container setup from headless canvas loading instabilities.

### 📂 3. Python Backend Invariant Testing Stack (`/api-tests/`)
*   **[`app/qa_simulation_api.py`](./api-tests/app/qa_simulation_api.py):** The system under test, committed completely unmodified to characterize current operational behavioral limits.
*   **[`tests/conftest.py`](./api-tests/tests/conftest.py):** Shared fixtures initializing independent math model equations and an custom `client` wrapper setting `raise_server_exceptions=False` to ensure unhandled errors surface naturally.
*   **[`tests/test_contract.py`](./api-tests/tests/test_contract.py):** Wire-format contract assertions checking OpenAPI envelope wrapper schemas, type coercions, and trailing slash redirects.
*   **[`tests/test_functional.py`](./api-tests/tests/test_functional.py):** Multi-parametric regression checks, zero-input edge conditions, and state isolation validation runs.
*   **[`tests/test_invariants.py`](./api-tests/tests/test_invariants.py):** **Hypothesis property-based tests** that evaluate system behavior over hundreds of randomized inputs, tracking linearity scaling, metamorphic symmetry, and pinning float64 numerical overflows deterministically.
*   **[`tests/test_schema_fuzz.py`](./api-tests/tests/test_schema_fuzz.py):** **Schemathesis fuzzer** that scans the active endpoints directly against the OpenAPI document to discover unhandled status anomalies.
*   **[`postman/simulation.postman_collection.json`](./api-tests/postman/simulation.postman_collection.json):** Executable Postman collection payload containing hand-computed precision proofs inside embedded JavaScript snippets.

### 📂 4. TypeScript Browser Automation Stack (`/web-tests/`)
*   **[`pages/EscherViewerPage.ts`](./web-tests/pages/EscherViewerPage.ts):** Centralized Page Object Model encapsulating the running DOM layer, regex menu locators, and SVG-safe text content extraction mechanisms.
*   **[`tests/load-map.spec.ts`](./web-tests/tests/load-map.spec.ts):** Refactored E2E script validating JSON rendering node counts, BiGG metabolic node identities, and using `test.fail()` to pin uncaught renderer crashes.
*   **[`tests/clear-data.spec.ts`](./web-tests/tests/clear-data.spec.ts) (New Custom Spec):** Automated test suite validating pathway overlay data cleansing behaviors and pinning the **ESC-01** disabled control defect inside code.
*   **📂 `fixtures/`:** Collection of custom test datasets (`corrupt_map_schema.json`, `extreme-magnitudes.json`, `invalid-truncated.json`, etc.) used to validate web app inputs.

### 📂 5. Automated CI Orchestration Gates (`/.github/workflows/`)
*   **[`ci-cd-gate.yml`](./.github/workflows/ci-cd-gate.yml):** A multi-stage sequential quality gate inside GitHub Actions. It executes on push and pull requests, parallelizing backend `uv sync` property tests, provisioning sandboxed Chromium containers, and running browser specs headlessly.
