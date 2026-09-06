"""Invariant layer — properties that must hold without anyone knowing the right answer.

This is the layer the assessment is really about, so it is worth saying why it exists.

A simulation exists because nobody knows what it will output. If a scientist could state
the expected titer in advance there would be nothing to simulate, so a test suite built on
expected values can only ever cover the cases somebody already solved by hand. Golden
files inherit the same problem one step removed: they pin whatever the code did on the day
they were recorded, bug included, and they go stale on every legitimate model improvement.

What survives is the set of rules the answer must obey regardless of what it turns out to
be. Four families, and they carry over directly to the optimizer in Task 1:

  Conservation   quantities that must balance          — mass in = mass out + accumulation
  Direction      the sign of a response, not its size  — more substrate must not reduce titer
  Range          physically impossible states          — no negative volume, no NaN to a client
  Reproducibility same inputs, same answer             — identical request, identical bytes

Below, those are exercised against the toy service. `o2` is a sum of a sine and a cosine,
so it is bounded by 2 whatever the parameters — a range invariant that needs no oracle.
`o1` is linear, so scaling both inputs must scale the output — a metamorphic relation. The
technique is identical for a bioreactor model; only the physics changes.

Ranges are bounded deliberately. Outside them the service returns HTTP 500 rather than a
result (finding API-01), so the bound is not a convenience — it is the shape of the defect,
and `test_overflow_*` below pins the edge exactly.
"""

from __future__ import annotations

import math
import pytest
from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st

from conftest import expected_outputs, simulate

pytestmark = pytest.mark.invariant

SETTINGS = settings(
    max_examples=150,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)

# The supported envelope, derived rather than guessed.
#
# o3 contains exp(-a*i1), and math.exp overflows a float64 above an argument of about
# 709.78. Every strategy below is bounded so that |a * i1| stays under MAX_SAFE_PRODUCT
# for the request actually sent — including tests that scale an input before sending it,
# where the effective product is a * k * i1 rather than a * i1.
#
# An earlier version of this file bounded the base inputs and forgot the scaling factor.
# Hypothesis found it in seconds by driving o1 past the ceiling, which is a fair
# demonstration of why property-based tests belong in a suite like this: I had reasoned
# about the envelope and reasoned wrong.
MAX_SAFE_PRODUCT = 500.0

PARAM_LIMIT = 5.0
SCALE_LIMIT = 5.0
INPUT_LIMIT = MAX_SAFE_PRODUCT / PARAM_LIMIT              # 100.0
SCALED_INPUT_LIMIT = INPUT_LIMIT / SCALE_LIMIT            # 20.0

params = st.floats(min_value=-PARAM_LIMIT, max_value=PARAM_LIMIT, allow_nan=False, allow_infinity=False)
inputs = st.floats(min_value=-INPUT_LIMIT, max_value=INPUT_LIMIT, allow_nan=False, allow_infinity=False)
scalable_inputs = st.floats(
    min_value=-SCALED_INPUT_LIMIT, max_value=SCALED_INPUT_LIMIT, allow_nan=False, allow_infinity=False
)
positive_params = st.floats(min_value=0.1, max_value=PARAM_LIMIT, allow_nan=False, allow_infinity=False)
scale_factors = st.floats(min_value=0.1, max_value=SCALE_LIMIT, allow_nan=False, allow_infinity=False)


# --------------------------------------------------------------------------------------
# Range invariants — states the system must never reach
# --------------------------------------------------------------------------------------

@SETTINGS
@given(i1=inputs, i2=inputs, a=params, b=params)
def test_every_supported_request_returns_a_result(client, i1, i2, a, b):
    """Availability: a schema-valid request inside the supported envelope answers 200.

    The single most valuable property for a compute service. It says nothing about
    correctness and everything about whether a scientist's afternoon survives.
    """
    response = simulate(client, i1, i2, a, b)
    assert response.status_code == 200, response.text


@SETTINGS
@given(i1=inputs, i2=inputs, a=params, b=params)
def test_outputs_are_always_finite_json_numbers(client, i1, i2, a, b):
    """No NaN and no infinity may reach a client.

    Not a style preference. `NaN` is not valid JSON, so a non-finite value either crashes
    the serializer or produces a document that strict parsers reject — and downstream it
    silently poisons every aggregate it touches.
    """
    outputs = simulate(client, i1, i2, a, b).json()["outputs"]
    for key, value in outputs.items():
        assert isinstance(value, (int, float)), f"{key} is not numeric: {value!r}"
        assert math.isfinite(value), f"{key} is not finite: {value!r}"


@SETTINGS
@given(i1=inputs, i2=inputs, a=params, b=params)
def test_o2_is_bounded_by_two(client, i1, i2, a, b):
    """|sin(x) + cos(y)|  0 and log1p(|y|) >= 0, so their sum is strictly positive."""
    o3 = simulate(client, i1, i2, a, b).json()["outputs"]["o3"]
    assert o3 > 0.0, f"o3 must be positive, got {o3}"


# --------------------------------------------------------------------------------------
# Metamorphic relations — how outputs must move when inputs move
# --------------------------------------------------------------------------------------

@SETTINGS
@given(i1=scalable_inputs, i2=scalable_inputs, a=params, b=params, k=scale_factors)
def test_o1_scales_linearly_with_its_inputs(client, i1, i2, a, b, k):
    """MR-1: o1 is linear, so scaling both inputs by k scales o1 by k.

    The relation holds without knowing either value. This is the shape of the check that
    matters for the optimizer: doubling a feed volume must double its contribution to the
    material balance, whatever the balance works out to be.
    """
    base = simulate(client, i1, i2, a, b).json()["outputs"]["o1"]
    scaled = simulate(client, k * i1, k * i2, a, b).json()["outputs"]["o1"]
    assert scaled == pytest.approx(k * base, rel=1e-9, abs=1e-9)


@SETTINGS
@given(i1=inputs, i2=inputs, a=params, b=params)
def test_o1_is_symmetric_under_swapping_input_parameter_pairs(client, i1, i2, a, b):
    """MR-2: o1(i1, i2, a, b) == o1(i2, i1, b, a), because addition commutes."""
    original = simulate(client, i1, i2, a, b).json()["outputs"]["o1"]
    swapped = simulate(client, i2, i1, b, a).json()["outputs"]["o1"]
    assert original == pytest.approx(swapped, rel=1e-12, abs=1e-12)


@SETTINGS
@given(
    i1=st.floats(min_value=-INPUT_LIMIT / 2, max_value=INPUT_LIMIT / 2),
    delta=st.floats(min_value=0.5, max_value=INPUT_LIMIT / 2),
    i2=inputs,
    a=positive_params,
    b=params,
)
def test_o1_increases_with_i1_when_a_is_positive(client, i1, delta, i2, a, b):
    """MR-3: direction, not magnitude.

    With a positive coefficient, raising i1 must raise o1. No expected value is involved.
    This is the same assertion as "adding glucose must not reduce predicted biomass" —
    the test a scientist can sign off on without knowing the answer.
    """
    lower = simulate(client, i1, i2, a, b).json()["outputs"]["o1"]
    upper = simulate(client, i1 + delta, i2, a, b).json()["outputs"]["o1"]
    assert upper > lower, f"o1 fell from {lower} to {upper} when i1 rose by {delta}"


@SETTINGS
@given(i1=inputs, i2=inputs, a=params, b=params)
def test_o3_decreases_as_a_times_i1_increases(client, i1, i2, a, b):
    """MR-4: exp(-a*i1) is monotonically decreasing in a*i1, and the log term is untouched by i1."""
    assume(abs(a) > 0.1)
    product = a * i1
    assume(-100.0 < product < 100.0)
    lower = simulate(client, i1, i2, a, b).json()["outputs"]["o3"]
    higher = simulate(client, i1 + 1.0 / a, i2, a, b).json()["outputs"]["o3"]
    assert higher <= lower + 1e-12, f"o3 rose from {lower} to {higher} as a*i1 increased"


# --------------------------------------------------------------------------------------
# Reproducibility
# --------------------------------------------------------------------------------------

@SETTINGS
@given(i1=inputs, i2=inputs, a=params, b=params)
def test_the_same_request_always_produces_the_same_bytes(client, i1, i2, a, b):
    """Determinism. Without it, no regression baseline in this repository means anything."""
    assert simulate(client, i1, i2, a, b).text == simulate(client, i1, i2, a, b).text


@SETTINGS
@given(i1=inputs, i2=inputs, a=params, b=params)
def test_service_agrees_with_an_independent_implementation(client, i1, i2, a, b):
    """Differential testing against the reference in conftest, across the whole envelope.

    Cheap here because the model is three lines. For a real mechanistic model the same
    role is played by a slower trusted solver run nightly rather than per commit.
    """
    outputs = simulate(client, i1, i2, a, b).json()["outputs"]
    for key, expected in expected_outputs(i1, i2, a, b).items():
        assert outputs[key] == pytest.approx(expected, rel=1e-9, abs=1e-12), key

# --------------------------------------------------------------------------------------
# The edge of the envelope — finding API-01, pinned deterministically
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize(
    ("case", "i1", "i2", "a", "b"),
    [
        ("o1 overflows to infinity", 1e308, 1e308, 10.0, 10.0),
        ("o3 overflows through exp(-a*i1)", -1000.0, 1.0, 1.0, 1.0),
    ],
)
@pytest.mark.xfail(
    strict=True,
    reason="API-01: non-finite model output crashes JSON serialisation and returns HTTP 500",
)
def test_overflow_inputs_are_handled_rather_than_crashing(client, case, i1, i2, a, b):
    """Every value here is an ordinary JSON number that passes validation.

    The model amplifies them past the double-precision ceiling, the response serialiser
    refuses to encode the result, and the caller receives a bare 500 with no diagnostic.
    Unauthenticated, one request, entirely deterministic.

    Marked strict-xfail on purpose: the defect is recorded and executable, the suite stays
    honest about the current state, and the day someone clamps the outputs or returns a
    422 this test fails and must be promoted. A skip would have said nothing and a plain
    failure would have trained the team to ignore a red pipeline.
    """
    assert simulate(client, i1, i2, a, b).status_code != 500, case


def test_overflow_response_carries_no_diagnostic_detail(client):
    """What a caller actually receives today. Documented so the fix has a target."""
    response = simulate(client, 1e308, 1e308, 10.0, 10.0)
    assert response.status_code == 500
    assert "detail" not in response.text

