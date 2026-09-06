"""Shared fixtures and domain helpers for the simulation API suite.

Two client fixtures, deliberately:

`client` sets ``raise_server_exceptions=False`` so an unhandled exception inside the
application surfaces as the 500 a real HTTP caller would receive. That is the behaviour
under test. The default TestClient re-raises instead, which turns a production outage
into a Python traceback and quietly changes what the test is asserting about.

`strict_client` keeps the re-raising behaviour, for the one place where seeing the
underlying exception type is the point.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from qa_simulation_api import app  # noqa: E402

ENDPOINT = "/simulate/"


@pytest.fixture(scope="session")
def client() -> TestClient:
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture(scope="session")
def strict_client() -> TestClient:
    return TestClient(app, raise_server_exceptions=True)


def body(i1: float, i2: float, a: float, b: float) -> dict:
    """Build the request envelope.

    The endpoint declares two Pydantic models as separate body parameters, so FastAPI
    nests them under their parameter names. Nothing in the service source says so and
    the flat body a caller would guess is rejected — see finding API-03. Every test
    goes through this helper so that contract lives in exactly one place.
    """
    return {"input_data": {"i1": i1, "i2": i2}, "model_params": {"a": a, "b": b}}


def expected_outputs(i1: float, i2: float, a: float, b: float) -> dict[str, float]:
    """Reference implementation of the documented model equations.

    Written from the specification of the model, not by importing the service's own
    `Model` class. Importing it would make the test assert that the code equals itself,
    which passes for every bug that lives in the equations.
    """
    return {
        "o1": a * i1 + b * i2,
        "o2": math.sin(a * i1) + math.cos(b * i2),
        "o3": math.exp(-a * i1) + math.log1p(abs(b * i2 - 2)),
    }


def simulate(client: TestClient, i1: float, i2: float, a: float, b: float):
    return client.post(ENDPOINT, json=body(i1, i2, a, b))
