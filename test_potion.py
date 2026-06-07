import pytest
from potion import Potion, combinations
from ingredient import get_ingredient_by_name

brew_test_cases = [
    # ingredient_names, potion_names
    (["Wheat", "Blue Mountain Flower"], [
        "Potion of Fortify Health and Restore Health"
        ]),
    (["Wheat", "Blue Mountain Flower", "Hagraven Feathers"], [
        "Potion of Fortify Health and Restore Health", 
        "Potion of Fortify Conjuration", 
        "Potion of Fortify Conjuration and Fortify Health and Restore Health"
        ]),
    (["Wheat", "Giant's Toe"], ["Potion of Damage Stamina Regen and Fortify Health"]),
    (["Wheat", "NOT AN INGREDIENT"], None),
]

@pytest.mark.parametrize("ingredient_names, potion_names", brew_test_cases)
def test_brew(ingredient_names, potion_names):
    if potion_names is None:
        with pytest.raises(ValueError):
            potions = Potion.brew(ingredient_names)
            assert False, "Should have raised an exception"
    else:
        potions = Potion.brew(ingredient_names)
        assert len(potions) == len(potion_names), f"Expected {len(potion_names)} potions, but got {len(potions)}"
        assert { str(potion) for potion in potions } == set(potion_names)

def test_equals():
    p1 = Potion.brew(["Wheat", "Blue Mountain Flower"])[0]
    p2 = Potion.brew(["Blue Mountain Flower", "Wheat"])[0]
    assert p1 == p2
    assert hash(p1) == hash(p2)
    assert str(p1) == str(p2)
    potions = set([p1, p2])
    assert len(potions) == 1

def test_combinations():
    # Test the combinations helper function
    items = [1, 2, 3, 4]
    # Get all combinations
    combs = list(combinations(items))
    
    # Test two-item combinations
    two_item = [(1,2), (1,3), (1,4), (2,3), (2,4), (3,4)]
    # Test three-item combinations
    three_item = [(1,2,3), (1,2,4), (1,3,4), (2,3,4)]
    
    assert all(c in combs for c in two_item)
    assert all(c in combs for c in three_item)
    assert len(combs) == len(two_item) + len(three_item)

def test_basic_potion_creation():
    # Test creating a simple potion with two ingredients
    ingredients = ["Wheat", "Blue Mountain Flower"]
    potions = Potion.brew(ingredients)
    
    assert len(potions) > 0
    # Should have Restore Health and Fortify Health effects
    first_potion = potions[0]
    effect_names = {effect.name for effect in first_potion.active_effects}
    assert "Restore Health" in effect_names
    assert "Fortify Health" in effect_names
    assert len(first_potion.ingredients) == 2

def test_potion_value_sorting():
    # Test that potions are sorted by value
    ingredients = ["Nirnroot", "Deathbell", "Emperor Parasol Moss"]
    potions = Potion.brew(ingredients)
    
    # Verify potions are sorted by value in descending order
    assert len(potions) > 0
    values = [p.value for p in potions]
    assert values == sorted(values, reverse=True)

def test_potion_string_representation():
    # Test the string representation of potions
    ingredients = ["Wheat", "Blue Mountain Flower"]
    potions = Potion.brew(ingredients)
    
    # The effects should be alphabetically ordered in the string
    potion_str = str(potions[0])
    assert potion_str == "Potion of Fortify Health and Restore Health"

def test_potion_equality():
    # Test that potions with the same effects are considered equal
    ingredients1 = ["Wheat", "Blue Mountain Flower"]
    ingredients2 = ["Blue Mountain Flower", "Wheat"]  # Same ingredients, different order
    
    potions1 = Potion.brew(ingredients1)
    potions2 = Potion.brew(ingredients2)
    
    assert potions1[0] == potions2[0]

def test_complex_potion_brewing():
    # Test creating potions with three ingredients
    ingredients = ["Nirnroot", "Deathbell", "Emperor Parasol Moss"]
    potions = Potion.brew(ingredients)
    
    # Verify we get both 2-ingredient and 3-ingredient potions
    ingredient_counts = {len(p.ingredients) for p in potions}
    assert 2 in ingredient_counts
    assert 3 in ingredient_counts

def test_ingredient_flexibility():
    # Test that brew accepts both strings and Ingredient objects
    wheat_str = "Wheat"
    wheat_obj = get_ingredient_by_name("Wheat")
    blue_mtn = "Blue Mountain Flower"
    
    # Mix of string and Ingredient object
    potions1 = Potion.brew([wheat_str, blue_mtn])
    potions2 = Potion.brew([wheat_obj, blue_mtn])
    
    assert potions1[0] == potions2[0]

def test_edge_cases():
    # Test empty ingredient list
    assert len(Potion.brew([])) == 0
    
    # Test single ingredient (should produce no potions)
    assert len(Potion.brew(["Wheat"])) == 0
    
    # Test ingredients with no matching effects
    ingredients = ["Wheat", "Hagraven Feathers"]  # These have no common effects
    potions = Potion.brew(ingredients)
    assert len(potions) == 0

def test_error_handling():
    # Test with invalid ingredient name
    with pytest.raises(ValueError):
        Potion.brew(["NonexistentIngredient"])
    
    # Test with invalid ingredient type
    with pytest.raises(ValueError):
        Potion.brew([123])  # Not a string or Ingredient
        
    # Test with None value
    with pytest.raises(TypeError):
        Potion.brew(None)  # None is not a list
