import pytest
from effect import get_effect_by_name

effect_test_cases = [
    # effect_name, verbose
    ("Restore Health", "Restore 5 points of Health."),
    ("Fortify Health", "Health is increased by 4 points for 60 seconds."),
    ("Damage Health", "Causes 2 points of poison damage."),
    ("Fortify Enchanting", "For 30 seconds items are enchanted 1% stronger."),
]

@pytest.mark.parametrize("effect_name, verbose", effect_test_cases)
def test_effect(effect_name, verbose):
    actual = get_effect_by_name(effect_name)
    assert actual.name == effect_name
    assert actual.verbose == verbose
