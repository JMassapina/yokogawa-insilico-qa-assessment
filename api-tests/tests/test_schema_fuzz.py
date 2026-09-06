"""Schema-driven fuzzing — generated from the OpenAPI document, not from my imagination.

The tests in the other modules probe cases I thought of. This module probes the ones I
did not: Schemathesis reads the served OpenAPI document and generates requests from it,
then checks the responses back against the same document.

Why it earns its place in a suite this small: it is the only layer that stays correct for
free when the API grows. Add a `/optimize/` endpoint tomorrow and this file covers it
without being edited, which is the difference between a suite that scales with the service
and one that becomes a maintenance tax. That is also its limitation — it can only ever
check conformance to the contract, never whether the science is right.

Marked `fuzz` and excluded from the fast pull-request gate. It runs nightly and on demand.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import schemathesis
from hypothesis import HealthCheck, assume, settings

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from qa_simulation_api import app  # noqa: E402

pytestmark = pytest.mark.fuzz

schema = schemathesis.openapi.from_asgi("/openapi.json", app)

# The double-precision ceiling for exp(). Schemathesis minimised the API-01 crash to
# i1 = 710.0 with a = -1.0 on its own, which lands exactly here — a sharper reproduction
# than the one I wrote by hand, and the reason the finding quotes 709.78 as the threshold.
EXP_OVERFLOW_THRESHOLD = 709.78


def within_supported_envelope(case) -> bool:
    """Whether a generated request is one the service can be expected to answer.

    This filter should not need to exist, and saying why is the point.

    The published schema types `i1`, `i2`, `a` and `b` as unbounded numbers, so every
    value Schemathesis generates is contract-valid — including the ones that drive
    exp(-a*i1) past the float64 ceiling and crash the response serialiser. The contract
    promises a range of inputs that the implementation cannot serve. That gap is the
    contract-level form of API-01.

    The remediation is on the service, not on this file: constrain the Pydantic fields so
    the OpenAPI document expresses the envelope the service actually supports. On the day
    that lands, this function and its `assume` call get deleted, and generation is bounded
    by the contract itself, which is where a bound belongs.
    """
    body = case.body
    if not isinstance(body, dict):
        return True
    inputs = body.get("input_data")
    params = body.get("model_params")
    if not isinstance(inputs, dict) or not isinstance(params, dict):
        return True  # malformed shapes are the validation layer's business, not ours
    def as_float(value, default=0.0) -> float | None:
        """None when the value is not a number at all — those belong to the validation layer."""
        if isinstance(value, bool) or value is None:
            return default
        if isinstance(value, (int, float)):
            return float(value)
        return None

    a = as_float(params.get("a"))
    i1 = as_float(inputs.get("i1"))
    if a is None or i1 is None:
        return True

    # Generated bodies can carry junk keys alongside the real ones — an earlier version of
    # this filter crashed on `{"": null, "a": 1.0}` and let the overflow through, so every
    # value is now converted defensively rather than assumed numeric.
    magnitudes = [
        abs(v)
        for v in (as_float(x, default=None) for x in (*inputs.values(), *params.values()))
        if v is not None
    ]
    return -EXP_OVERFLOW_THRESHOLD < a * i1 and max(magnitudes, default=0.0) < 1e150


@schema.parametrize()
@settings(max_examples=40, deadline=None, suppress_health_check=list(HealthCheck))
def test_api_conforms_to_its_own_schema(case):
    """Responses must conform to the document: status codes, content types, payload shapes.

    Two checks are deliberately excluded, each because it duplicates a defect that is
    already pinned by a precise, deterministic test elsewhere in this suite. A defect
    should fail one test, in the place that explains it. Letting it also fail here would
    add noise without adding information, and a check that is always red is a check
    everybody learns to ignore.

    `not_a_server_error` — Schemathesis generates the very large floats that trigger
        API-01, so this fails on essentially every run. Pinned instead by
        `test_invariants.py::test_overflow_inputs_are_handled_rather_than_crashing`.

    `status_code_conformance` — the document declares 200 and 422 only, and an
        undecodable request body produces 400 `{"detail": "There was an error parsing the
        body"}`. Also found by Schemathesis unprompted, from a body of invalid UTF-8 bytes
        that I would not have thought to send. Pinned as API-07 by
        `test_contract.py::test_undecodable_body_returns_an_undocumented_400`. With only
        two documented codes and one known omission, leaving the check on would rediscover
        the same gap on every run rather than finding a new one.

    `negative_data_rejection` — Schemathesis found this one on its own, which is the
        argument for having it: sending `model_params.b = false` violates the published
        schema and the API accepts it, coercing the boolean to 1.0. I had already pinned
        the behaviour by hand in `test_functional.py::test_inputs_are_coerced_rather_than_rejected`,
        but I had filed it as an API-design opinion. An independent tool calling it a
        contract violation is what moves it from opinion to finding API-04, and it is the
        reason that finding is in the report at all.

    Remediation is symmetrical: when API-01, API-04 or API-07 is fixed, remove the matching
    entry from `excluded_checks` and this layer starts guarding the fix. Written down here
    so the next person does not have to reconstruct the reasoning.

    Worth being blunt about the score. Of the three exclusions, two describe defects this
    tool found without being told where to look — in a service of three equations and one
    endpoint that I had already read line by line. That is the argument for the layer.

    Exclusion rather than an explicit allow-list, so that checks Schemathesis adds in
    future versions are picked up automatically instead of being silently skipped.
    """
    assume(within_supported_envelope(case))
    response = case.call()
    case.validate_response(
        response,
        excluded_checks=[
            schemathesis.checks.not_a_server_error,          # API-01
            schemathesis.checks.status_code_conformance,     # API-07
            schemathesis.checks.negative_data_rejection,     # API-04
        ],
    )
    