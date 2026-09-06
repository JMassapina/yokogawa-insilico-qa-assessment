"""Contract layer — the shape of the interface, independent of what the maths returns.

These are the tests that protect consumers. They fail when the API changes in a way that
breaks a client, and they say nothing about whether the science is right. Keeping that
separation is what lets the contract suite run on every pull request in a couple of
seconds while heavier layers run less often.
"""

from __future__ import annotations

import pytest

from conftest import ENDPOINT, body, simulate

pytestmark = pytest.mark.contract


def test_openapi_is_served_and_describes_the_endpoint(client):
    spec = client.get("/openapi.json")
    assert spec.status_code == 200
    assert ENDPOINT in spec.json()["paths"]


def test_request_body_is_the_nested_envelope(client):
    """The wire format is `{input_data: {...}, model_params: {...}}`.

    Pinned because it is surprising. Two body parameters make FastAPI generate a
    synthetic wrapper schema, so the obvious flat body is rejected. If someone later
    refactors to a single request model, this test fails and the breaking change gets
    discussed rather than shipped.
    """
    schema_ref = (
        client.get("/openapi.json")
        .json()["paths"][ENDPOINT]["post"]["requestBody"]["content"]["application/json"]["schema"]["$ref"]
    )
    wrapper = client.get("/openapi.json").json()["components"]["schemas"][schema_ref.rsplit("/", 1)[-1]]
    assert set(wrapper["required"]) == {"input_data", "model_params"}


def test_flat_body_is_rejected(client):
    assert client.post(ENDPOINT, json={"i1": 1.5, "i2": 2.5, "a": 1.2, "b": 0.8}).status_code == 422


def test_successful_response_has_exactly_the_documented_keys(client):
    payload = simulate(client, 1.5, 2.5, 1.2, 0.8).json()
    assert set(payload) == {"inputs", "outputs"}
    assert set(payload["inputs"]) == {"i1", "i2"}
    assert set(payload["outputs"]) == {"o1", "o2", "o3"}


def test_response_echoes_the_inputs_it_used(client):
    """An echo is only worth having if it reports what the service actually computed with."""
    payload = simulate(client, 1.5, 2.5, 1.2, 0.8).json()
    assert payload["inputs"] == {"i1": 1.5, "i2": 2.5}


@pytest.mark.parametrize(
    ("case", "payload"),
    [
        ("missing model_params.b", {"input_data": {"i1": 1.5, "i2": 2.5}, "model_params": {"a": 1.2}}),
        ("missing input_data", {"model_params": {"a": 1.2, "b": 0.8}}),
        ("null i1", {"input_data": {"i1": None, "i2": 2.5}, "model_params": {"a": 1.2, "b": 0.8}}),
        ("non-numeric i1", {"input_data": {"i1": "abc", "i2": 2.5}, "model_params": {"a": 1.2, "b": 0.8}}),
        ("empty body", {}),
    ],
)
def test_invalid_bodies_are_rejected_with_422(client, case, payload):
    assert client.post(ENDPOINT, json=payload).status_code == 422, case


def test_validation_errors_locate_the_offending_field(client):
    """Assert the machine-readable `loc`, not the human-readable `msg`.

    Every draft solution I reviewed asserted on the string "field required". Pydantic v2
    emits "Field required" with a capital F, so those assertions fail against the very
    version they pin. `loc` and `type` are the stable parts of the contract; prose is not.
    """
    detail = client.post(
        ENDPOINT, json={"input_data": {"i1": 1.5, "i2": 2.5}, "model_params": {"a": 1.2}}
    ).json()["detail"]
    assert [e["loc"] for e in detail] == [["body", "model_params", "b"]]
    assert detail[0]["type"] == "missing"


def test_wrong_method_is_405_not_404(client):
    assert client.get(ENDPOINT).status_code == 405


def test_path_without_trailing_slash_redirects(client):
    """Documents finding API-06.

    `/simulate` answers 307. Redirect handling on a POST is inconsistent across HTTP
    clients and some drop the body, so callers who omit the slash can see a silent
    failure. Pinned so the behaviour is a decision rather than an accident.
    """
    response = client.post(
        "/simulate", json=body(1.0, 1.0, 1.0, 1.0), follow_redirects=False
    )
    assert response.status_code == 307
    assert response.headers["location"].endswith(ENDPOINT)


def test_undecodable_body_returns_an_undocumented_400(client):
    """Documents finding API-07 as observed behaviour.

    A body of bytes that are not valid UTF-8 produces 400, not 422. Found by the fuzz
    layer, not by me — I had assumed every rejection on this endpoint was a 422 from
    Pydantic, and never thought to send a body that fails before validation runs.
    """
    response = client.post(
        ENDPOINT, content=b"\x78\x58\xd7\xb5\x77\x35\xc0\x15", headers={"content-type": "application/json"}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "There was an error parsing the body"}


@pytest.mark.xfail(
    strict=True,
    reason="API-07: 400 is reachable but the OpenAPI document declares only 200 and 422",
)
def test_every_reachable_status_code_is_documented(client):
    """A generated client built from this document will not know 400 exists.

    It will fall into whatever its default branch is — commonly retry, or an exception
    typed as a transport failure — for what is actually a permanent client error.
    """
    documented = set(
        client.get("/openapi.json").json()["paths"][ENDPOINT]["post"]["responses"]
    )
    assert {"200", "400", "422"} <= documented


@pytest.mark.xfail(
    strict=True,
    reason="API-02: no response_model, so the 200 response has an empty schema and no output contract",
)
def test_success_response_is_described_in_the_schema(client):
    """The output shape is undocumented and therefore unprotected.

    `responses.200` carries an empty schema, so nothing stops `o1` being renamed and
    nothing lets a consumer generate a typed client. Marked strict-xfail: it is a real
    gap, the suite stays green today, and the moment someone adds a `response_model`
    this test fails loudly and gets promoted to a normal assertion.
    """
    schema = (
        client.get("/openapi.json")
        .json()["paths"][ENDPOINT]["post"]["responses"]["200"]["content"]["application/json"]["schema"]
    )
    assert schema != {}
