import pytest
import numpy as np
from qa_simulation_api import Model

def test_model_simulation_mathematical_invariants():
    """TC-UNIT-001: Validate core numerical formulas independent of HTTP transport layers."""
    # Enforce known target inputs and variables
    a_param = 1.5
    b_param = 0.5
    i1_input = 2.0
    i2_input = 3.0
    
    # Initialize the model instance directly
    test_model = Model(a=a_param, b=b_param)
    results = test_model.simulate(i1=i1_input, i2=i2_input)
    
    # Invariant 1: Validate o1 calculation -> a * i1 + b * i2
    # 1.5 * 2.0 + 0.5 * 3.0 = 3.0 + 1.5 = 4.5
    assert results["o1"] == pytest.approx(4.5)
    
    # Invariant 2: Validate o2 calculation -> sin(a * i1) + cos(b * i2)
    expected_o2 = np.sin(a_param * i1_input) + np.cos(b_param * i2_input)
    assert results["o2"] == pytest.approx(expected_o2)
    
    # Invariant 3: Validate o3 safety -> ensure no unhandled NaN bounds occur
    assert not np.isnan(results["o3"])
    assert np.isfinite(results["o3"])

def test_model_neutral_zero_bounds():
    """TC-UNIT-002: Verify stability when values hit perfect zero boundaries."""
    test_model = Model(a=1.0, b=1.0)
    results = test_model.simulate(i1=0.0, i2=0.0)
    
    # o1 should equal exactly 0.0
    assert results["o1"] == 0.0
    assert not np.isnan(results["o3"])
