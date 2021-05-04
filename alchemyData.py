import json

def indexOn(field, items):
    return { item[field]: item for item in items }

with open("alchemyData.json") as f:
    data = json.load(f)
    AllIngredients = indexOn("name", data["ingredients"])
    AllEffects = indexOn("name", data["effects"])
