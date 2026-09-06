# Task 3: API Testing Strategy & Gating Manual

## 1. Testing Pyramid Isolation Boundaries
*   **Unit Layer (Developers):** Validates core algorithmic code variations inside `Model.simulate()` directly. Focuses on mathematical invariant loops before applying any runtime server contexts.
*   **API / Contract Layer (QA + Devs):** Enforces strict contract structures on request bodies via Pydantic model configurations. Changes to input/output keys fail instantly at the compilation layer, protecting downstream microservice layers.
*   **Integration Layer (QA):** Validates multi-endpoint sequence flows, error mappings, content headers, and resource exhaustion bounds under peak concurrent stress loops.

## 2. Contract Testing Framework Integration
Contract testing acts as our interface shield. By checking microservices API payloads directly against consumer-driven contracts (via Pact) inside the pull request pipeline, we prevent structural backend modifications from silently breaking frontend visualization tools before end-to-end browser automation suites are even executed.

## 3. Local Verification Manual
The executable Postman suite payload is located at `./simulation_tests.json`. To run this collection locally:
```bash
# 1. Install dependencies and start the local server daemon
pip3 install fastapi pydantic numpy uvicorn httpx pytest
uvicorn qa_simulation_api:app --host 127.0.0.1 --port 8000 &

# 2. Execute tests headlessly via Newman
npm install -g newman
newman run simulation_tests.json --env-var baseUrl=http://127.0.0.1:8000
```
