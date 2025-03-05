import pytest
from potion import Potion

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
