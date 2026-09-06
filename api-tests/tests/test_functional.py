"""Functional layer — does the service compute what the model says it should.

Expected values come from `expected_outputs`, a reference implementation written from
the model equations. Two independent implementations of the same specification will not
usually share a bug; a test that recomputes using the code under test shares all of them.
"""

from __future__ import annotations

import math

import pytest

from conftest import ENDPOINT, expected_outputs, simulate

pytestmark = pytest.mark.functional

TOLERANCE = 1e-12  # double-precision arithmetic on both sides; nothing here is stochastic


@pytest.mark.parametrize(
    ("i1", "i2", "a", "b"),
    [
        (1.5, 2.5, 1.2, 0.8),      # nominal
        (0.0, 0.0, 1.0, 1.0),      # zero inputs
        (1.0, 2.0, 0.0, 0.0),      # zero parameters: outputs collapse to constants
        (-3.25, 4.75, 0.5, -1.5),  # mixed signs
        (1e-9, 1e-9, 1e-9, 1e-9),  # near-zero, where cancellation would show up
    ],
)
def test_outputs_match_the_model_equations(client, i1, i2, a, b):
    response = simulate(client, i1, i2, a, b)
    assert response.status_code == 200
    outputs = response.json()["outputs"]
    for key, expected in expected_outputs(i1, i2, a, b).items():
        assert outputs[key] == pytest.approx(expected, abs=TOLERANCE, rel=TOLERANCE), key


def test_zero_input_gives_the_analytically_known_answer(client):
    """One case where the right answer is known by hand rather than by reimplementation.

    At i1 = i2 = 0 the equations reduce to o1 = 0, o2 = sin 0 + cos 0 = 1,
    o3 = exp 0 + log1p 2 = 1 + ln 3. Worth having at least one anchor that a reader can
    verify without trusting either implementation.
    """
    outputs = simulate(client, 0.0, 0.0, 1.0, 1.0).json()["outputs"]
    assert outputs["o1"] == pytest.approx(0.0, abs=TOLERANCE)
    assert outputs["o2"] == pytest.approx(1.0, abs=TOLERANCE)
    assert outputs["o3"] == pytest.approx(1.0 + math.log(3.0), abs=TOLERANCE)


def test_log1p_argument_is_singular_where_b_times_i2_is_two(client):
    """`abs(b*i2 - 2)` is zero here, so o3 = exp(-a*i1) + log1p(0) = exp(-a*i1).

    The kink in `abs()` is the one place in these equations where the derivative is
    discontinuous, which makes it the place a numerical optimizer would get stuck. Worth
    a named test even though the service handles it correctly.
    """
    outputs = simulate(client, 1.0, 2.0, 1.0, 1.0).json()["outputs"]
    assert outputs["o3"] == pytest.approx(math.exp(-1.0), abs=TOLERANCE)


@pytest.mark.parametrize(
    ("case", "sent", "coerced"),
    [
        ("numeric strings", "1.5", 1.5),
        ("booleans", True, 1.0),
        ("integers", 2, 2.0),
    ],
)
def test_inputs_are_coerced_rather_than_rejected(client, case, sent, coerced):
    """Documents finding API-04 as current behaviour, not as approval.

    Pydantic's lax mode accepts `true` as a concentration and `"1.5"` as a float. For a
    scientific service I would argue for strict mode and `extra="forbid"`, because a
    client that sends a boolean where a titer belongs has a bug the API should surface.
    Pinning it means that argument gets had deliberately, and the day someone tightens
    validation this test tells them exactly who they might break.
    """
    response = client.post(
        ENDPOINT,
        json={"input_data": {"i1": sent, "i2": 2.5}, "model_params": {"a": 1.0, "b": 1.0}},
    )
    assert response.status_code == 200, case
    assert response.json()["inputs"]["i1"] == coerced


def test_unknown_fields_are_silently_ignored(client):
    """Also API-04. A misspelled field name disappears instead of being reported."""
    response = client.post(
        ENDPOINT,
        json={
            "input_data": {"i1": 1.5, "i2": 2.5, "i3_typo": 99.0},
            "model_params": {"a": 1.0, "b": 1.0},
        },
    )
    assert response.status_code == 200
    assert "i3_typo" not in response.json()["inputs"]


def test_repeated_identical_requests_return_identical_bytes(client):
    """No hidden state between calls.

    The service keeps a module-level `model_instance` that the handler shadows with a
    local of the same name (finding API-05). Today that makes the global dead code rather
    than a race, and this test is what would notice if a future refactor made the
    endpoint genuinely stateful.
    """
    first = simulate(client, 1.5, 2.5, 1.2, 0.8)
    second = simulate(client, 1.5, 2.5, 1.2, 0.8)
    assert first.text == second.text


def test_parameters_do_not_leak_between_requests(client):
    """Interleaved calls with different parameters must not contaminate each other."""
    a_first = simulate(client, 1.0, 1.0, 2.0, 3.0).json()["outputs"]
    simulate(client, 5.0, 5.0, 99.0, 99.0)
    a_again = simulate(client, 1.0, 1.0, 2.0, 3.0).json()["outputs"]
    assert a_first == a_again
