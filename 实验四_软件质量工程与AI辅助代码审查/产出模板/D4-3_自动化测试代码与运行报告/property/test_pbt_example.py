from hypothesis import given, strategies as st

@given(st.integers(), st.integers())
def test_commutative(a, b):
    assert a + b == b + a
