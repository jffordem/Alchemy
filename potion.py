from pydantic import BaseModel
from effect import Effect
from ingredient import Ingredient, ActiveEffect, get_ingredient_by_name

__doc__ = """
Potions are created by combining ingredients.  Each ingredient has a list of effects
that it can produce when combined with other ingredients.  The value of a potion is
calculated based on the effects it produces.  The brew method takes a list of
ingredients and returns a list of potions that can be created from those ingredients.

Usage:
    from potion import Potion
    potions = Potion.brew(["Wheat", "Garlic"])
    print(potions)
"""

def combinations(items):
    """Return all the two-item and three-item combinations of a list of items."""
    for i in range(len(items)-1):
        for j in range(i+1, len(items)):
            yield (items[i], items[j])
    for i in range(len(items)-2):
        for j in range(i+1, len(items)-1):
            for k in range(j+1, len(items)):
                yield (items[i], items[j], items[k])

def iterate(items, **kwargs):
    """This is the 'non-progress bar' iterator.  Useful for embedded behavior (like web server)."""
    return items

class Potion(BaseModel):
    """A Potion is a magical elixir that can be created by combining ingredients.  Each
    potion has a list of ActiveEffects that it produces, a list of ingredients used to
    create it, and a value based on the effects it produces.  Potions can be sorted by
    value to find the most valuable.

    Potions don't actually have names.  They're described by their effects.  For example,
    a potion that restores health and fortifies health would be called a 'Potion of Restore
    Health and Fortify Health'.  The __str__ method returns a human-readable version of
    the potion's effects.
    """
    active_effects: list[ActiveEffect]
    ingredients: list[Ingredient]
    value: float

    def __hash__(self):
        return sum(hash(ingredient) for ingredient in self.ingredients)

    def __str__(self):
        effect_names = sorted([effect.name for effect in self.active_effects])
        return f"Potion of {' and '.join(effect_names)}"
    
    def __eq__(self, other):
        return str(self) == str(other)

    @staticmethod
    def brew(ingredients: list[Ingredient | str], track=iterate) -> list['Potion']:
        """Brew potions from a list of ingredients.  The brew method takes a list of
        ingredients and returns a list of potions that can be created from those
        ingredients.  The track parameter is a function that takes an iterable and
        returns an iterator that can be used to track progress.  By default, it
        returns the original iterable unchanged.  You can use the track parameter
        to provide a progress bar or other tracking mechanism.
        """
        ingredients: list[Ingredient] = [get_ingredient_by_name(name) if isinstance(name, str) else name for name in ingredients]
        potions: list['Potion'] = list()
        total = (len(ingredients) - 1) ** 2 + (len(ingredients) - 2) ** 3
        for active_ingredients in track(combinations(ingredients), total=total, description="Brewing potions"):
            active_effects: list[ActiveEffect] = Ingredient.combine(active_ingredients)
            if len(active_effects) > 0:
                value = Effect.get_value(active_effects)
                potions.append(Potion(active_effects=active_effects, ingredients=active_ingredients, value=value))
        potions.sort(key=lambda potion: potion.value, reverse=True)
        return potions
