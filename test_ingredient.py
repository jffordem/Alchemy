import pytest
from ingredient import Ingredient, get_ingredient_by_name

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
