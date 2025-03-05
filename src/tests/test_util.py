"""
Test integration module
"""

from utils import utilities as utils


def test_json_flat():
    """
    Test json_flat
    """
    data = {"a": 1, "b": {"c": 2, "d": 3}, "e": [{"f": 4}, {"g": 5}]}
    flat_data = utils.flatten_json(data)
    print(flat_data)
    assert flat_data["a"] == 1
    assert flat_data["b.c"] == 2
    assert flat_data["b.d"] == 3
    assert flat_data["e.0.f"] == 4
    assert flat_data["e.1.g"] == 5
