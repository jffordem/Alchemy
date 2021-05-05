import math
import json
import csv
from table import Table, printTable, CsvTableFormat
from pprint import pprint
from alchemyData import indexOn

def findDuplicates(potions):
    def makeIngredientsKey(potion):
        return ",".join(sorted(list(potion["ingredients"])))
    all = dict()
    for potion in potions:
        key = makeIngredientsKey(potion)
        #print(key)
        if key in all:
            yield potion
        all[key] = potion

def uniquePotions(potions):
    def makeIngredientsKey(potion):
        return ",".join(sorted(list(potion["ingredients"])))
    all = dict()
    for potion in potions:
        key = makeIngredientsKey(potion)
        all[key] = potion
    return all.values()

def findPotions(potions, pred):
    for potion in potions:
        if pred(potion):
            yield potion

def matchNumIngredients(n):
    return lambda potion: len(potion["effects"]) == n 

def matchFarmableIngredients(ingredients):
    def hasFarmableIngredients(potion):
        return all(ingredients[ingredient]['farmable'] for ingredient in potion['ingredients'])
    return hasFarmableIngredients

def matchNot(pred):
    return lambda x: not pred(x)

def matchAny(*preds):
    return lambda item: any(pred(item) for pred in preds)

def matchAll(*preds):
    return lambda item: all(pred(item) for pred in preds)

def findFiveEffectPotions(potions, ingredients):
    for potion in findPotions(potions, matchAll(matchNumIngredients(5), matchFarmableIngredients(ingredients))):
        pprint(potion)

def formatIngredients(ingredientsByName):
    for name,type in ingredientsByName.items():
        template = """
            {{
                "name": "{name}",
                "value": 1,
                "farmable": {farmable},
                "effects": [ ]
            }},
        """
        print(template.format(name=name, farmable=str(type=="Plant").lower()))

def readIngredientsCsv(file):
    with open(file, 'r') as f:
        reader = csv.reader(f, delimiter=",")
        result = dict()
        for line in reader:
            if line == None or len(line) == 0: continue
            result[line[0]] = line[1:]
        return result

def combinedEffects(ingredients):
    result = dict()
    for i in ingredients:
        for effect in i['effects']:
            name = effect['name']
            power = effect['power']
            value = effect['value']
            if name not in result:
                result[name] = {
                    'name': name,
                    'count': 1,
                    'power': power,
                    'value': value
                }
            else:
                result[name]['count'] += 1
                result[name]['power'] *= power
                result[name]['value'] *= value
    return { name: effect for name, effect in result.items() if effect['count'] > 1 }

def hasEffect(ingredient, effectName):
    effects = { effect["name"] for effect in ingredient["effects"] }
    return effectName in effects

def allCombinations(items):
    for i in range(len(items)-1):
        for j in range(i+1, len(items)):
            yield (items[i], items[j])
    for i in range(len(items)-2):
        for j in range(i+1, len(items)-1):
            for k in range(j+1, len(items)):
                yield (items[i], items[j], items[k])

def getEffectValue(effect):
    """
    Gold_cost = floor( Base_Cost * (Magnitude^1.1) * 0.0794328 * (Duration^1.1) )
    If the magnitude or duration is zero, the corresponding term is dropped from the equation, i.e.:

    Gold_cost (When Magnitude = 0) = floor( Base_Cost * 0.0794328 * (Duration^1.1) )
    Gold_cost (When Duration = 0) = floor( Base_Cost * (Magnitude^1.1) )
    If the magnitude or duration is not displayed in game, that does not necessarily mean that the value is zero. The game still has an internal value for each parameter (based on the ingredient's Base_Mag and Base_Dur) which is used in this calculation. These internal values are listed in the following table.
    """
    result = effect["cost"]
    if effect["mag"] > 0:
        result *= effect["mag"] ** 1.1
    if effect["dur"] > 0:
        result *= effect["dur"] ** 1.1 * 0.0794328
    print("Value for", effect["name"], "is", result)
    return math.floor(result)

def New_getValue(effects, effectsByName):
    total = 0
    for name,values in effects.items():
        effect = effectsByName[name]
        temp = getEffectValue(effect)
        for value in values:
            temp *= value["value"]
        total += temp
    return total

def getValue(effects, effectsByName):
    total = 0
    for name, buffs in effects.items():
        effect = effectsByName[name]
        total += effect["cost"] * buffs['value']
    return total

def exceptions(ingredient):
    if ingredient["name"] in { "Jarrin Root" }: 
        return False
    #return ingredient["farmable"]
    return True
    #effects = indexOn("name", ingredient["effects"])
    #return "Paralysis" in effects

def getPotions(ingredient_names, ingredientsByName, effectsByName):
    ingredients = [ ingredientsByName[name] for name in ingredient_names if name in ingredientsByName.keys() ]
    rows = list()
    for these in allCombinations(ingredients):
        effects = combinedEffects(these)
        if len(effects) > 0:
            value = getValue(effects, effectsByName)
            rows.append({ "ingredients": these, "value": value, "effects": effects })
    rows = sorted(rows, key=lambda item: item["value"], reverse=True)
    for row in rows:
        row["value"] = "{:10.2f}".format(row["value"]).strip()
    return rows

#def getPotionsTable(ingredient_names):
#    rows = getPotions(ingredient_names)
#    header = [ "1", "2", "3", "$", "N", "E" ]
#    return Table(header, rows)

def printAllPotionsByValue(ingredientsByName, effectsByName):
    printPotionsByValue(ingredientsByName.values(), effectsByName)

def printPotionsByValue(ingredients, effectsByName):
    header = [ "1", "2", "3", "$", "N", "E" ]
    rows = list()
    for these in allCombinations(list(filter(exceptions, ingredients))):
        effects = combinedEffects(these)
        if len(effects) > 0:
            value = getValue(effects, effectsByName)
            a, b, c = these
            rows.append({ "1": a["name"], "2": b["name"], "3": c["name"], "$": value, "N": len(effects), "E": ", ".join(effects.keys()) })
    rows = sorted(rows, key=lambda item: item["$"])
    for row in rows:
        row["$"] = "{:10.4f}".format(row["$"]).strip()
    printTable(Table(header, rows))

def printIngredients(effectName, ingredientsByName):
    names = [ ingredient["name"] for ingredient in ingredientsByName.values() if hasEffect(ingredient, effectName) ]
    for name in names:
        print(name)

def printIngredientsByValue(ingredientsByName):
    def getEffect(ingredient, index): 
        result = ingredient["effects"][index]["name"]
        if ingredient["effects"][index]["power"] != 1.0:
            result += "(*{:1.1f})".format(ingredient["effects"][index]["power"])
        if ingredient["effects"][index]["value"] != 1.0:
            result += "(${:1.1f})".format(ingredient["effects"][index]["value"])
        return result
    header = [ "Name", "E1", "E2", "E3", "E4", "Farmable", "Weight", "Value" ]
    rows = list()
    for i in ingredientsByName.values():
        rows.append({ "Name": i["name"], "E1": getEffect(i, 0), "E2": getEffect(i, 1), "E3": getEffect(i, 2), "E4": getEffect(i, 3), "Farmable": i["farmable"], "Weight": i["weight"], "Value": i["value"] })
    rows = sorted(rows, key=lambda item: item["Farmable"])
    printTable(Table(header, rows))

def getPotionsByEffects(names, ingredientsByName, effectsByName):
    def matchEffects(ingredient):
        return len({ effect["name"] for effect in ingredient["effects"] }.intersection(names)) > 0
    names = set(names)
    ingredients = [ ingredient for ingredient in ingredientsByName.values() if matchEffects(ingredient) ]
    header = [ "1", "2", "3", "$", "N", "E" ]
    rows = list()
    for these in allCombinations(ingredients):
        effects = combinedEffects(these)
        if set(effects.keys()).issuperset(names):
            value = getValue(effects, effectsByName)
            a, b, c = these
            rows.append({ "1": a["name"], "2": b["name"], "3": c["name"], "$": value, "N": len(effects), "E": ", ".join(effects.keys()) })
    rows = sorted(rows, key=lambda item: item["$"])
    for row in rows:
        row["$"] = "{:10.4f}".format(row["$"]).strip()
    return Table(header, rows)

def printAllIngredientsCsv(ingredientsByName):
    header = [ 'name', 'value', 'weight', 'farmable', 
        'effect_1_name', 'effect_1_power', 'effect_1_value', 
        'effect_2_name', 'effect_2_power', 'effect_2_value', 
        'effect_3_name', 'effect_3_power', 'effect_3_value' ]
    rows = [ ]
    for record in ingredientsByName.values():
        row = { 'name': record['name'],
                'value': record['value'],
                'weight': record['weight'],
                'farmable': record['farmable'],
              }
        for index, effect in enumerate(record['effects']):
            row['effect_{}_name'.format(index+1)] = effect['name']
            row['effect_{}_power'.format(index+1)] = effect['power']
            row['effect_{}_value'.format(index+1)] = effect['value']
        rows.append(row)
    t = Table(header, rows)
    printTable(t, CsvTableFormat())

def printAllEffectsCsv(effectsByName):
    header = [ 'name', 'description', 'school', 'type', 'cost', 'mag', 'dur' ]
    rows = [ ]
    for record in effectsByName.values():
        rows.append({ key:record[key] for key in header })
    t = Table(header, rows)
    printTable(t, CsvTableFormat())
