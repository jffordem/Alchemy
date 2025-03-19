import pytest
from effect import Effect, get_effect_by_name, get_effects_by_filter

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

def test_effect_data_class():
    # Test Effect instantiation and properties
    effect = Effect(
        name="Zooble Effect",
        description="Zooble someone at {mag} for {dur}",
        school="Zooble School",
        type="Zooble Type",
        cost=10.0,
        dur=30,
        mag=5,
        link="https://en.uesp.net/wiki/Skyrim:Zooble_Effect"
    )
    assert effect.name == "Zooble Effect"
    assert effect.school == "Zooble School"
    assert effect.type == "Zooble Type"
    assert effect.cost == pytest.approx(10.0)
    assert effect.dur == 30
    assert effect.mag == 5
    assert effect.verbose == "Zooble someone at 5 for 30"
    assert effect.link == "https://en.uesp.net/wiki/Skyrim:Zooble_Effect"

def test_effect_value_calculation():
    # Test value calculation with different parameters
    effects = [
        Effect(name="E1", description="D1", school="S", type="T", cost=10, dur=0, mag=1, link="https://en.uesp.net/wiki/Skyrim:E1"),  # No duration
        Effect(name="E2", description="D2", school="S", type="T", cost=10, dur=30, mag=0, link="https://en.uesp.net/wiki/Skyrim:E2"),  # No magnitude
        Effect(name="E3", description="D3", school="S", type="T", cost=10, dur=30, mag=5, link="https://en.uesp.net/wiki/Skyrim:E3"),  # Both dur and mag
    ]
    
    # Individual values
    assert effects[0].value > 0  # Basic cost and magnitude
    assert effects[1].value > 0  # Basic cost and duration
    assert effects[2].value > effects[0].value  # Combined effect should be larger
    
    # Test sum of values
    total_value = Effect.get_value(effects)
    assert total_value == sum(effect.value for effect in effects)

def test_yaml_loading():
    # Test that all effects from YAML are loaded correctly
    restore_health = get_effect_by_name("Restore Health")
    assert restore_health.school == "Restoration"
    assert restore_health.type == "Restorative"
    assert restore_health.cost == pytest.approx(0.5)
    assert restore_health.mag == 5
    assert restore_health.dur == 0
    assert restore_health.link == "https://en.uesp.net/wiki/Skyrim:Restore_Health"

def test_effect_filtering():
    # Test filtering effects by various criteria
    restoration_effects = get_effects_by_filter(lambda e: e.school == "Restoration")
    assert len(restoration_effects) > 0
    assert all(e.school == "Restoration" for e in restoration_effects)

    offensive_effects = get_effects_by_filter(lambda e: e.type == "Offensive")
    assert len(offensive_effects) > 0
    assert all(e.type == "Offensive" for e in offensive_effects)

def test_error_handling():
    # Test invalid effect name
    with pytest.raises(KeyError):
        get_effect_by_name("NonexistentEffect")

    # Test invalid effect creation
    with pytest.raises(Exception):
        Effect(
            name="Invalid",
            description="Invalid",
            school="Invalid",
            type="Invalid",
            cost="not a number",  # Invalid cost type
            dur=0,
            mag=0
        )
