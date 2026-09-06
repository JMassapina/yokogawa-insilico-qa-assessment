# 🐛 Defect Registry Log — Discovered Subsystem Findings

The automated test framework discovered **ten distinct defects** across the simulation service API and the Escher canvas front-end viewer. This ledger details the structural analysis, severity classifications, and reproduction steps for each defect.

---

## 🐍 Python Simulation Microservice Defects

### `API-01` — Unhandled NumPy Float64 Overflow Triggers Bare 500 Crash
*   **Severity:** 🔴 **Major / Blocker**
*   **Mathematical Cause:** The `Model.simulate` equation contains `math.exp(-a * i1)`. When a payload is submitted where $a \times i1 \le -710.0$ (e.g., $i1 = 710.0, a = -1.0$), the outcome exceeds the double-precision boundary of $\exp(709.78)$, turning into `inf`. NumPy allows infinity inside memory loops, but FastAPI's native JSON encoder rejects serialization compliance entirely, returning a bare HTTP 500 error instead of a handled 422 tracking message.
*   **Reproduction:** Execute `api-tests/tests/test_invariants.py::test_overflow_inputs_are_handled_rather_than_crashing`.

### `API-02` — Missing OpenAPI Output Contract Mapping
*   **Severity:** 🟡 **Minor**
*   **Structural Cause:** The `@app.post("/simulate/")` route handler declares no explicit `response_model` parameter. As a result, the generated dynamic `openapi.json` contract leaves its successful response schema block completely blank, preventing end-user teams from auto-generating typed API client software.
*   **Reproduction:** Execute `api-tests/tests/test_contract.py::test_success_response_is_described_in_the_schema`.

### `API-03` — Synthetic Envelope Wrapper Rejects Flat Body Input Shapes
*   **Severity:** 🔵 **Trivial / Style Variation**
*   **Structural Cause:** Declaring `input_data: SimulationInput` and `model_params: ModelParams` as two separate input parameters forces FastAPI to generate a nested structural JSON envelope wrapper. End-users naturally guess a flat body layout, which is rejected with an HTTP 422 error.
*   **Reproduction:** Execute `api-tests/tests/test_contract.py::test_flat_body_is_rejected`.

### `API-04` — Loose Pydantic Lax Validation Layer Parameters
*   **Severity:** 🔵 **Trivial**
*   **Structural Cause:** Pydantic is configured to run under default lax evaluation parameters, meaning it silently coerces string numeric characters (e.g., `"1.5"`) to float numbers and transforms booleans (`True` to `1.0`), masking client payload serialization bugs.
*   **Reproduction:** Execute `api-tests/tests/test_functional.py::test_inputs_are_coerced_rather_than_rejected`.

### `API-05` — Module-Level Global State Variable Shadowing
*   **Severity:** 🟡 **Minor**
*   **Structural Cause:** The API script initiates a global module-level tracker `model_instance = Model(a=1.0, b=1.0)`, but the route handler shadows this with a local variable of the exact same name. While it remains dead code today rather than an active multi-tenant race condition, it introduces immense technical debt for future refactoring work.
*   **Reproduction:** Static analysis audit of `api-tests/app/qa_simulation_api.py`.

### `API-06` — Inconsistent Trailing Slash Route Processing Limits
*   **Severity:** 🟡 **Minor**
*   **Structural Cause:** Hitting `/simulate` returns an HTTP 307 redirect to `/simulate/`. POST redirect handshakes are frequently dropped or stripped of their body payloads by simple frontend HTTP clients, leading to silent calculation losses.
*   **Reproduction:** Execute `api-tests/tests/test_contract.py::test_path_without_trailing_slash_redirects`.

### `API-07` — Undocumented 400 Bad Request Payload Return
*   **Severity:** 🟡 **Minor**
*   **Structural Cause:** Submitting non-UTF8 binary data streams crashes the parsing layers before Pydantic constraints evaluate, throwing an undocumented HTTP 400 bad request error.
*   **Reproduction:** Execute `api-tests/tests/test_contract.py::test_undecodable_body_returns_an_undocumented_400`.

---

## 🌐 Escher Visualization Canvas Frontend Viewer Defects

### `ESC-01` — Data Clearance Action Control Fails to Transition State
*   **Severity:** 🔴 **Major / Blocker**
*   **UI Execution Cause:** After loading valid telemetry data matrices onto the canvas map view, the `Clear reaction data` interactive selection item inside the `Data` dropdown remains permanently in its disabled state (`id="disabled"`). This renders the data clearing functionality unusable through the UI, leaving scientists reading stale data overlays.
*   **Reproduction:** Execute `web-tests/tests/clear-data.spec.ts`.

### `ESC-02` — Cold URL Route Parameter Ingestion Flakiness
*   **Severity:** 🔴 **Major**
*   **UI Execution Cause:** Initializing browser paths directly with the fragment parameter `/#/app?tool=Viewer` causes the core application menu bar header layout elements to fail to load intermittently, breaking automated UI scripting runs.
*   **Reproduction:** Execute browser sweeps headlessly inside `web-tests/tests/load-map.spec.ts`.

### `ESC-03` — Structurally Malformed JSON Uploads Break Menu Interactions
*   **Severity:** 🔴 **Major**
*   **UI Execution Cause:** Uploading valid JSON with a non-compliant map schema hits an uncaught `TypeError` inside Escher's engine core. This error breaks the browser DOM render loop, permanently removing the top-level menu bar and requiring a full page refresh to recover the application state.
*   **Reproduction:** Execute `web-tests/tests/load-map.spec.ts` under the invalid input descriptor blocks.
