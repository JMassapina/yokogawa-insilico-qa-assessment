# Task 3: REST API Testing Architecture & Decoupled Quality Gates

## 1. Testing Pyramid Isolation Boundaries
To maximize testing velocity and minimize maintenance overhead, testing responsibilities are decoupled across distinct layers:
*   **Unit Layer (Developer Driven):** Validates underlying core code behaviors, math formulas, and isolated classes. Executed via Pytest locally on every pre-commit hook.
*   **API / Contract Layer (QA + Developer Driven):** Enforces strict contract structures on request bodies via Pydantic model configurations.
*   **Integration Layer (QA Driven):** Validates full lifecycle tracking. Gated inside the CI/CD pipeline via automated Postman/Newman collections.

## 2. Local Verification Manual
The executable Postman suite payload is located at `api-tests/postman/simulation.postman_collection.json`. To run this collection locally against a live uvicorn thread:
```bash
cd api-tests
uv sync
uv run uvicorn app.qa_simulation_api:app --host 127.0.0.1 --port 8000 &
sleep 3
npm install -g newman
newman run postman/simulation.postman_collection.json --env-var baseUrl=http://127.0.0.1:8000