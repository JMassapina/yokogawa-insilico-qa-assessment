# --- Stage 1: Build base operating system & runtime variables ---
FROM python:3.10-slim AS base-backend-env
WORKDIR /app

# Install baseline compilation utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential && \
    rm -rf /var/lib/apt/lists/*

# Copy dependency records and inject libraries
COPY requirements.txt .
RUN pip install --no-cache-dir fastapi pydantic numpy uvicorn httpx pytest

# --- Stage 2: Ingest source artifacts and initialize worker ---
FROM base-backend-env AS server-runtime
COPY qa_simulation_api.py .

# Expose standard FastAPI network port node
EXPOSE 8000

# Execute server worker daemon upon container deployment
CMD ["uvicorn", "qa_simulation_api:app", "--host", "0.0.0.0", "--port", "8000"]
