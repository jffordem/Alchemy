from pydantic import BaseModel
from collections import defaultdict
from functools import reduce
import json
import yaml

__doc__ = """
Skyrim ingredients are the raw materials used to brew potions.  Each ingredient has a 
name, a list of ActiveEffects that it can produce, a value, and a weight.  Some 
ingredients are farmable, meaning they can be grown or harvested, while others 
are not.  Ingredients are combined in potion making to produce ActiveEffects.

This module requires a master list of ingredients to be loaded from a file.  The
file can be in either JSON or YAML format.  The list of ingredients is stored in
a dictionary called AllIngredientsByName, which maps ingredient names to Ingredient
objects.  You can use the get_ingredient_by_name function to look up an ingredient
by name.

YAML format for ingredients:
- name: "Name"
  effects:
    - name: "Effect"
      power: 1.0
      value: 1.0
  farmable: true
  link: "URL"
  value: 1
  weight: 1.0

Example ingredient:
- name: "Wheat"
  effects:
    - name: "Restore Health"
      power: 1.0
      value: 1.0
    - name: "Damage Stamina"
      power: 1.0
      value: 1.0
  farmable: true
  link: "https://en.uesp.net/wiki/Skyrim:Wheat"
  value: 5
  weight: 0.1

Usage:
    from ingredient import Ingredient, ActiveEffect, get_ingredient_by_name
    a = get_ingredient_by_name("Wheat")
    b = get_ingredient_by_name("Garlic")
    active_effects: list[ActiveEffect] = Ingredient.combine([a, b])
    print(active_effects)
"""


def group_by(iterable, get_key):
    groups = defaultdict(list)
    for item in iterable:
        groups[get_key(item)].append(item)
    return groups


def prod(values):
    return reduce(lambda x, y: x * y, values, 1)


class ActiveEffect(BaseModel):
    """An ActiveEffect is an Effect (like 'Fortify Health') that's been activated by
    combining ingredients.  Since each ingredient has different effects with different 
    degrees of power, the power and value of an ActiveEffect is the product of the
    power and value of the individual effects.
    """
    name: str
    power: float
    value: float

    def __hash__(self):
        return hash(self.name) + hash(self.power) + hash(self.value)

    @staticmethod
    def combine(effects: list['ActiveEffect']) -> 'ActiveEffect':
        """Combine multiple effects of the same kind.  Since several different ingredients
        can have the same effect, we need to combine them to determine the overall power
        and value of the effect.  You should only combine effects of the same kind.
        """
        if any(effect.name != effects[0].name for effect in effects):
            raise ValueError("Can't combine effects of different kinds")
        return ActiveEffect(
            name=effects[0].name,
            power=prod(effect.power for effect in effects),
            value=prod(effect.value for effect in effects),
        ) if len(effects) > 0 else None


class Ingredient(BaseModel):
    """An Ingredient is a raw material that can be used to brew potions.  Each ingredient
    has a name, a list of ActiveEffects that it can produce, a value, and a weight.  Some
    ingredients are farmable, meaning they can be grown or harvested, while others are
    not.  Ingredients can also be combined to produce new ActiveEffects.
    """
    name: str
    effects: list[ActiveEffect]
    farmable: bool
    link: str
    value: int
    weight: float

    def has_effect(self, effect_name: str) -> bool:
        """Check if this ingredient has an effect of the given name."""
        return any(effect_name == effect.name for effect in self.effects)

    def __hash__(self):
        return hash(self.name)

    @property
    def buffed(self) -> bool:
        """Check if this ingredient has any effects that are greater than normal (buffed)."""
        return any(effect.power > 1 for effect in self.effects) or any(effect.value > 1 for effect in self.effects)
    
    @property
    def nerfed(self) -> bool:
        """Check if this ingredient has any effects that are less than normal (nerfed)."""
        return any(effect.power < 1 for effect in self.effects) or any(effect.value < 1 for effect in self.effects)
    
    @staticmethod
    def combine(ingredients: list['Ingredient']) -> list['ActiveEffect']:
        """Combining ingredients will produce a list of ActiveEffects that are the result
        of the same effects being present in at least two different ingredients.
        """
        allEffects = (
            effect
            for ingredient in ingredients
            for effect in ingredient.effects
        )
        effectGroups = group_by(allEffects, lambda effect: effect.name)
        activeEffects = [
            ActiveEffect.combine(effects) 
            for effects in effectGroups.values() 
            if len(effects) > 1
        ]
        return activeEffects

    @staticmethod
    def from_file(filename: str = 'ingredients.yaml') -> list['Ingredient']:
        """Load a list of ingredients from a file.  The file can be in either JSON or YAML"""
        if filename.endswith('.json'):
            with open(filename, 'r') as file:
                return [Ingredient(**ingredient) for ingredient in json.load(file)]
        elif filename.endswith('.yaml'):
            with open(filename, 'r') as file:
                return [Ingredient(**ingredient) for ingredient in yaml.safe_load(file)]
        else:
            raise ValueError('Unsupported file format')

    def format(self, template: str = None) -> str:
        if template is None:
            template = """
            {{
                "name": "{name}",
                "value": 1,
                "farmable": {farmable},
                "effects": [ ]
            }},
        """
        return template.format(name=self.name, farmable=str(self.farmable).lower())

AllIngredientsByName = {
    ingredient.name: ingredient
    for ingredient in Ingredient.from_file()
}

def get_ingredient_by_name(name: str) -> Ingredient:
    try:
        return AllIngredientsByName[name]
    except KeyError:
        raise ValueError(f"Unknown ingredient: {name}")

def get_ingredients_by_filter(predicate):
    return [ingredient for ingredient in AllIngredientsByName.values() if predicate(ingredient)]
