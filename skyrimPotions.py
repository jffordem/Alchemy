# 

import math
import json
#import urllib.request
import csv
import table
from pprint import pprint
#from ingredients import Ingredients

def indexOn(field, items):
    "Added some error handling for when there was a problem in the data."
    result = dict()
    lastKey = None
    for item in items:
        try:
            lastKey = item[field]
            result[item[field]] = item
        except:
            print("Unable to find field", field, "in", str(item))
            print("Previous item was", lastKey)
    return result

with open("skyrimPotions.json") as f:
    data = json.load(f)
AllIngredients = indexOn("name", data["ingredients"])
AllEffects = indexOn("name", data["effects"])

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
        for ingredient in potion["ingredients"]:
            if not ingredients[ingredient]["farmable"]:
                return False
        return True
    return hasFarmableIngredients

def matchNot(pred):
    return lambda x: not pred(x)

def matchAny(*preds):
    def hasAny(item):
        for pred in preds:
            if pred(item):
                return True
        return False

def matchAll(*preds):
    def hasAll(item):
        for pred in preds:
            if not pred(item):
                return False
        return True
    return hasAll

def findFiveEffectPotions(potions, ingredients):
    for potion in findPotions(potions, matchAll(matchNumIngredients(5), matchFarmableIngredients(ingredients))):
        pprint(potion)

def formatIngredients():
    for name,type in Ingredients.items():
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

def combinedEffects(*ingredients):
    result = dict()
    for i in ingredients:
        for name,effect in indexOn("name", i["effects"]).items():
            if name not in result: result[name] = [ ]
            result[name].append(effect)
    return { k:v for k,v in result.items() if len(v) > 1 }

def hasEffect(ingredient, effectName):
    effects = { effect["name"] for effect in ingredient["effects"] }
    return effectName in effects

def allCombinations(items):
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

def New_getValue(effects):
    total = 0
    for name,values in effects.items():
        effect = AllEffects[name]
        temp = getEffectValue(effect)
        for value in values:
            temp *= value["value"]
        total += temp
    return total
    
def getValue(effects):
    total = 0
    for name,values in effects.items():
        effect = AllEffects[name]
        cost = effect["cost"]
        for value in values: 
            #cost *= (value["power"] * value["value"])
            cost *= value["power"]
        total += cost
    return total

def exceptions(ingredient):
    if ingredient["name"] in { "Jarrin Root" }: 
        return False
    #return ingredient["farmable"]
    return True
    #effects = indexOn("name", ingredient["effects"])
    #return "Paralysis" in effects

def printPotionsByValue():
    header = [ "1", "2", "3", "$", "#", "@" ]
    rows = list()
    for a, b, c in allCombinations(list(filter(exceptions, data["ingredients"]))):
        effects = combinedEffects(a, b, c)
        if len(effects) > 0 and "Waterbreathing" in effects:
            value = getValue(effects)
            rows.append({ "1": a["name"], "2": b["name"], "3": c["name"], "$": value, "#": len(effects), "@": ", ".join(effects.keys()) })
    rows = sorted(rows, key=lambda item: item["$"])
    for row in rows:
        row["$"] = "{:10.4f}".format(row["$"]).strip()
    table.printTable(table.Table(header, rows))

def printIngredients(effectName):
    names = [ ingredient["name"] for ingredient in AllIngredients.values() if hasEffect(ingredient, effectName) ]
    for name in names:
        print(name)

def printIngredientsByValue():
    def getEffect(ingredient, index): 
        result = ingredient["effects"][index]["name"]
        if ingredient["effects"][index]["power"] != 1.0:
            result += "(*{:1.1f})".format(ingredient["effects"][index]["power"])
        if ingredient["effects"][index]["value"] != 1.0:
            result += "(${:1.1f})".format(ingredient["effects"][index]["value"])
        return result
    header = [ "Name", "E1", "E2", "E3", "E4", "Farmable", "Weight", "Value" ]
    rows = list()
    for i in AllIngredients.values():
        rows.append({ "Name": i["name"], "E1": getEffect(i, 0), "E2": getEffect(i, 1), "E3": getEffect(i, 2), "E4": getEffect(i, 3), "Farmable": i["farmable"], "Weight": i["weight"], "Value": i["value"] })
    rows = sorted(rows, key=lambda item: item["Farmable"])
    table.printTable(table.Table(header, rows))

e = "Waterbreathing"
print("Ingredients with", e)
printIngredients(e)
#printIngredientsByValue()
#printPotionsByValue()

# calibration
#effects = combinedEffects(AllIngredients["Nirnroot"], AllIngredients["Ectoplasm"])
#value = getValue(effects)
#print(value)

""" Calibration!
Base values: Alchemy=15, no perks or fortification
    Imp Stool + Mora Tapinella + Swamp Fungal Pod = 252
        Paralysis: 4s
        Poison damage: 4 for 10s
        Restore: 22
    Creep Cluster + More Tapinella + Scaly Pholiota = 389
        Carry Weight: 17 for 300s
        Magicka: 22
        Weakess to Magick: 9% for 30s
        Stamina Regen: 22% for 300s
        Illusion: 17% for 60s
    Giant's Toe + Wheat = 446
        Health: 17 for 300s
        Damage Stamina Regen: 100% for 22s
    Imp Stool + Wheat = 8
        Health: 13 points.
http://www.garralab.com/skyrim/alchemy.php
"""