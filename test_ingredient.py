import pytest
from ingredient import Ingredient, ActiveEffect, get_ingredient_by_name, get_ingredients_by_filter

ingredient_effect_cases = [
    # ingredient_name, effect_name, expected_has_effect
    ("Wheat", "Restore Health", True),
    ("Wheat", "Restore Magicka", False),
    ("Wheat", "Fortify Health", True),
    ("Wheat", "Fortify Magicka", False),
    ("Blue Mountain Flower", "Restore Health", True),
    ("Blue Mountain Flower", "Restore Magicka", False),
    ("Blue Mountain Flower", "Fortify Health", True),
    ("Blue Mountain Flower", "Fortify Magicka", False),
    ("Hagraven Feathers", "Restore Health", False),
    ("Hagraven Feathers", "Restore Magicka", False),
    ("Hagraven Feathers", "Fortify Health", False),
    ("Hagraven Feathers", "Fortify Magicka", False),
    ("Hagraven Feathers", "Fortify Conjuration", True),
    ("Hagraven Feathers", "Fortify Enchanting", False),
]

@pytest.mark.parametrize("ingredient_name, effect_name, expected_has_effect", ingredient_effect_cases)
def test_ingredient(ingredient_name, effect_name, expected_has_effect):
    ingredient = get_ingredient_by_name(ingredient_name)
    assert ingredient.has_effect(effect_name) == expected_has_effect

def test_ingredient_data_class():
    # Test Ingredient instantiation and properties
    effects = [
        ActiveEffect(name="Test Effect 1", power=1.0, value=1.0),
        ActiveEffect(name="Test Effect 2", power=1.5, value=2.0)
    ]
    ingredient = Ingredient(
        name="Test Ingredient",
        effects=effects,
        farmable=True,
        link_url="https://test.com",
        value=10,
        weight=0.5,
        thumbnail_url="https://test.com/thumbnail.png",
        image_url="https://test.com/image.png"
    )
    
    assert ingredient.name == "Test Ingredient"
    assert len(ingredient.effects) == 2
    assert ingredient.farmable is True
    assert ingredient.link_url == "https://test.com"
    assert ingredient.value == 10
    assert ingredient.weight == pytest.approx(0.5)
    assert ingredient.thumbnail_url == "https://test.com/thumbnail.png"
    assert ingredient.image_url == "https://test.com/image.png"

def test_active_effect_combine():
    # Test combining multiple ActiveEffects
    effects = [
        ActiveEffect(name="Restore Health", power=1.0, value=1.0),
        ActiveEffect(name="Restore Health", power=1.5, value=2.0),
        ActiveEffect(name="Restore Health", power=2.0, value=1.5)
    ]
    
    combined = ActiveEffect.combine(effects)
    assert combined.name == "Restore Health"
    assert combined.power == pytest.approx(3.0)  # 1.0 * 1.5 * 2.0
    assert combined.value == pytest.approx(3.0)  # 1.0 * 2.0 * 1.5

    # Test combining different effects (should raise error)
    with pytest.raises(ValueError):
        ActiveEffect.combine([
            ActiveEffect(name="Restore Health", power=1.0, value=1.0),
            ActiveEffect(name="Damage Health", power=1.0, value=1.0)
        ])

def test_ingredient_buff_nerf_status():
    # Test buffed and nerfed properties
    normal_effects = [ActiveEffect(name="Normal", power=1.0, value=1.0)]
    buffed_effects = [ActiveEffect(name="Buffed", power=1.5, value=1.0)]
    nerfed_effects = [ActiveEffect(name="Nerfed", power=0.5, value=1.0)]
    
    normal_ingredient = Ingredient(name="Normal", effects=normal_effects, farmable=True, link_url="", thumbnail_url="", image_url="", value=1, weight=1.0)
    buffed_ingredient = Ingredient(name="Buffed", effects=buffed_effects, farmable=True, link_url="", thumbnail_url="", image_url="", value=1, weight=1.0)
    nerfed_ingredient = Ingredient(name="Nerfed", effects=nerfed_effects, farmable=True, link_url="", thumbnail_url="", image_url="", value=1, weight=1.0)
    
    assert not normal_ingredient.buffed and not normal_ingredient.nerfed
    assert buffed_ingredient.buffed and not buffed_ingredient.nerfed
    assert not nerfed_ingredient.buffed and nerfed_ingredient.nerfed

combine_ingredient_cases = [
    # ingredient_names, expected_active_effects
    ([], []),
    (["Wheat"], []),
    (["Wheat", "Blue Mountain Flower"], ["Restore Health", "Fortify Health"]),
    (["Wheat", "Blue Mountain Flower", "Hagraven Feathers"], ["Restore Health", "Fortify Health", "Fortify Conjuration"]),
    (["Wheat", "Hagraven Feathers"], []),
    (["Blue Mountain Flower", "Hagraven Feathers"], ["Fortify Conjuration"]),
]

@pytest.mark.parametrize("ingredient_names, expected_active_effects", combine_ingredient_cases)
def test_combine_ingredient(ingredient_names, expected_active_effects):
    ingredients = [get_ingredient_by_name(name) for name in ingredient_names]
    active_effects = Ingredient.combine(ingredients)
    assert {effect.name for effect in active_effects} == set(expected_active_effects)

def test_yaml_loading():
    # Test specific ingredient properties from YAML
    nirnroot = get_ingredient_by_name("Nirnroot")
    assert nirnroot.name == "Nirnroot"
    assert len(nirnroot.effects) == 4
    assert not nirnroot.farmable
    assert nirnroot.value == 10
    assert nirnroot.weight == pytest.approx(0.2)
    assert nirnroot.thumbnail_url == "https://images.uesp.net/thumb/4/46/SR-icon-ingredient-Nirnroot.png/48px-SR-icon-ingredient-Nirnroot.png"
    assert nirnroot.image_url == "https://images.uesp.net/thumb/4/4a/SR-flora-Nirnroot.jpg/1200px-SR-flora-Nirnroot.jpg"
    assert any(effect.name == "Damage Health" and effect.value == pytest.approx(12.6) for effect in nirnroot.effects)

    # Test ingredient filtering
    farmable = get_ingredients_by_filter(lambda i: i.farmable)
    assert len(farmable) > 0
    assert all(i.farmable for i in farmable)

    valuable = get_ingredients_by_filter(lambda i: i.value >= 25)
    assert len(valuable) > 0
    assert all(i.value >= 25 for i in valuable)

def test_error_handling():
    # Test getting non-existent ingredient
    with pytest.raises(ValueError):
        get_ingredient_by_name("NonexistentIngredient")

    # Test invalid ingredient creation
    with pytest.raises(Exception):
        Ingredient(
            name="Invalid",
            effects=[],
            farmable="not a boolean",  # Invalid boolean
            link_url="",
            value="not a number",  # Invalid value type
            weight="not a number"  # Invalid weight type
        )
