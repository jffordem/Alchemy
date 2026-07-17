"""
Potions are created by combining ingredients.  Each ingredient has a list of effects
that it can produce when combined with other ingredients.  The value of a potion is
calculated based on the effects it produces.  The brew method takes a list of
ingredients and returns a list of potions that can be created from those ingredients.

Usage:
    from potion import Potion
    potions = Potion.brew(["Wheat", "Garlic"])
    print(potions)
"""

from pydantic import BaseModel
from typing import Callable, Iterator, TypeVar, Any
from effect import Effect
from ingredient import Ingredient, ActiveEffect, get_ingredient_by_name
from itertools import combinations as itertools_combinations
from math import comb
from rich.progress import track as iterate

def iterate(items, **kwargs):
    """This is the 'non-progress bar' iterator.  Useful for embedded behavior (like web server)."""
    return items

T = TypeVar('T')
Predicate = Callable[[T], bool]

def combinations(items: list[Any]) -> Iterator[tuple[Any, ...]]:
    """Get all combinations of size 2 and 3 from the given items."""
    for r in range(2, min(4, len(items) + 1)):
        yield from itertools_combinations(items, r)

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
    cost: float = 0.0  # The total cost of ingredients used

    def __hash__(self):
        return hash(str(self))

    def __str__(self):
        effect_names = sorted([effect.name for effect in self.active_effects])
        return f"Potion of {' and '.join(effect_names)}"
    
    def __eq__(self, other):
        return str(self) == str(other)
    
    def ingredients_key(self) -> str:
        """Create a unique key based on sorted ingredient names."""
        return ",".join(sorted(ingredient.name for ingredient in self.ingredients))
    
    @property
    def efficiency(self) -> float:
        """Calculate the efficiency ratio (value/cost) of the potion.
        Higher efficiency means better value for the cost."""
        if self.cost == 0:
            return 0.0  # Avoid division by zero
        return self.value / self.cost

    @staticmethod
    def find_duplicates(potions: list['Potion']) -> Iterator['Potion']:
        """Find potions that use the same ingredients in different orders."""
        seen = set()
        for potion in potions:
            key = potion.ingredients_key()
            if key in seen:
                yield potion
            seen.add(key)

    @staticmethod
    def unique_potions(potions: list['Potion']) -> list['Potion']:
        """Return a list of potions with duplicate ingredient combinations removed."""
        unique = {}
        for potion in potions:
            key = potion.ingredients_key()
            unique[key] = potion
        return list(unique.values())

    @staticmethod
    def filter_potions(potions: list['Potion'], pred: Predicate['Potion']) -> Iterator['Potion']:
        """Filter potions using a predicate function."""
        return (potion for potion in potions if pred(potion))

    @staticmethod
    def match_num_effects(n: int) -> Predicate['Potion']:
        """Create a predicate that matches potions with exactly n effects."""
        return lambda potion: len(potion.active_effects) == n

    @staticmethod
    def match_farmable() -> Predicate['Potion']:
        """Create a predicate that matches potions made only from farmable ingredients."""
        return lambda potion: all(ingredient.farmable for ingredient in potion.ingredients)

    @staticmethod
    def match_not(pred: Predicate[T]) -> Predicate[T]:
        """Create a predicate that negates another predicate."""
        return lambda x: not pred(x)

    @staticmethod
    def match_any(*preds: Predicate[T]) -> Predicate[T]:
        """Create a predicate that matches if any of the given predicates match."""
        return lambda item: any(pred(item) for pred in preds)

    @staticmethod
    def match_all(*preds: Predicate[T]) -> Predicate[T]:
        """Create a predicate that matches if all of the given predicates match."""
        return lambda item: all(pred(item) for pred in preds)

    @staticmethod
    def is_valid_ingredient(ingredient: Ingredient) -> bool:
        """Check if an ingredient is valid for potion making (excludes special ingredients)."""
        return ingredient.name not in {"Jarrin Root"}

    @staticmethod
    def brew(ingredients: list[Ingredient | str], track=iterate) -> list['Potion']:
        """Brew potions from a list of ingredients.  The brew method takes a list of
        ingredients and returns a list of potions that can be created from those
        ingredients.  The track parameter is a function that takes an iterable and
        returns an iterator that can be used to track progress.  By default, it
        returns the original iterable unchanged.  You can use the track parameter
        to provide a progress bar or other tracking mechanism.
        """
        if ingredients is None:
            raise TypeError("ingredients cannot be None")
        
        if not isinstance(ingredients, list):
            raise TypeError("ingredients must be a list")
            
        processed_ingredients = []
        for item in ingredients:
            if isinstance(item, str):
                processed_ingredients.append(get_ingredient_by_name(item))
            elif isinstance(item, Ingredient):
                processed_ingredients.append(item)
            else:
                raise ValueError(f"Invalid ingredient type: {type(item)}. Must be string or Ingredient.")
                
        # Filter out invalid ingredients
        processed_ingredients = [i for i in processed_ingredients if Potion.is_valid_ingredient(i)]
                
        potions: list['Potion'] = list()
        n = len(processed_ingredients)
        
        # Try 2 and 3 ingredients with separate progress bars
        for active_ingredients in track(combinations(processed_ingredients), 
                                         total=comb(n, 2) + comb(n, 3),
                                         description=f"Brewing potions"):
            active_effects: list[ActiveEffect] = Ingredient.combine(active_ingredients)
            if len(active_effects) > 0:
                value = Effect.get_value(active_effects)
                cost = sum(ingredient.value for ingredient in active_ingredients)
                potions.append(Potion(active_effects=active_effects, ingredients=active_ingredients, value=value, cost=cost))
        
        potions.sort(key=lambda potion: potion.value, reverse=True)
        return potions
