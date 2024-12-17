import math
from pydantic import BaseModel
import json
import yaml

__doc__ = '''
An effect is a magical property that can be applied to a potion.  Each effect 
has a name, a description, a school, a type, a cost, a duration, and a 
magnitude.  The value of an effect is calculated based on the cost, duration, 
and magnitude.  The verbose property is a human-readable version of the 
description with the duration and magnitude filled in.  The get_value method 
calculates the total value of a list of effects.

This module requires a master list of effects to be loaded from a file.  The
file can be in either JSON or YAML format.  The list of effects is stored in
a dictionary called AllEffectsByName, which maps effect names to Effect objects.
You can use the get_effect_by_name function to look up an effect by name.

YAML format for effects:
- name: "Name"
  description: "Description"
  school: "School"
  type: "Type"
  cost: 1.0
  dur: 1
  mag: 1

Example effect:
- name: "Restore Health"
  description: "Restore {mag} points of Health."
  school: "Restoration"
  type: "Beneficial"
  cost: 1.0
  dur: 1
  mag: 1

Usage:
    from effect import Effect, get_effect_by_name
    effect = get_effect_by_name("Restore Health")
    print(effect.value, effect.verbose)
'''

class Effect(BaseModel):
    name: str
    description: str
    school: str
    type: str
    cost: float
    dur: int
    mag: int

    @property
    def value(self) -> float:
        # Tunable properties to see if we can get the right values
        mag_pow = 1.1
        dur_pow = 1.1
        dur_factor = 0.0794328
        result = self.cost
        if self.mag > 0:
            result *= self.mag ** mag_pow
        if self.dur > 0:
            result *= self.dur ** dur_pow * dur_factor
        return math.floor(result)

    @property
    def verbose(self) -> str:
        return self.description.replace('{dur}', str(self.dur)).replace('{mag}', str(self.mag))

    @staticmethod
    def get_value(effects: list['Effect']) -> float:
        return sum(effect.value for effect in effects)

    @staticmethod
    def from_file(filename: str = 'effects.yaml') -> list['Effect']:
        if filename.endswith('.json'):
            with open(filename, 'r') as file:
                return [Effect(**effect) for effect in json.load(file)]
        elif filename.endswith('.yaml'):
            with open(filename, 'r') as file:
                return [Effect(**effect) for effect in yaml.safe_load(file)]
        else:
            raise ValueError('Unsupported file format')

AllEffectsByName = {
    effect.name: effect
    for effect in Effect.from_file()
}

def get_effect_by_name(name: str) -> Effect:
    return AllEffectsByName[name]

def get_effects_by_filter(predicate) -> list[Effect]:
    return [effect for effect in AllEffectsByName.values() if predicate(effect)]
