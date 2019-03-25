# app.py

from flask import Flask, request
from flask.cli import with_appcontext
import os
import socket
import random
from skyrimPotions import AllIngredients, AllEffects, getPotionsTable
import table

app = Flask(__name__)

@app.route("/")
def hello():
    return """<h1>Skyrim Potions</H1>
    <h2>Ingredients</h2>
    <p>GET /ingredients
    <p>Params:
    <ul>
    <li>effects={list of effects}</li>
    <li>farmable=True/False</li>
    <li>sortby={column}</li>
    </ul>
    <h2>Effects</h2>
    <p>GET /effects
    <p>Params:
    <ul>
    <li>school={school}</li>
    <li>type={type}</li>
    <li>sortby={column}</li>
    </ul>
    <h2>Potions</h2>
    <p>GET /potions
    <p>Params:
    <ul>
    <li>ingredients={list of ingredients}</li>
    <li>sortby={column}</li>
    </ul>
    """
    

@app.route("/ingredients")
def ingredients():
    def hasEffect(i, e):
        return e in [ effect["name"] for effect in i["effects"] ]
    def matchIngredient(i):
        if "effects" in request.args:
            effects = request.args.get("effects").split(",")
            for effect in effects:
                if not hasEffect(i, effect):
                    return False
        if "farmable" in request.args:
            isFarmable = { "True":True, "true":True }.get(request.args.get("farmable"), False)
            if i["farmable"] != isFarmable: return False
        return True
    headers = [ "Name", "Effect 1", "Effect 2", "Effect 3", "Effect 4", "Farmable", "Weight", "Value" ]
    rows = [ ]
    for k in sorted(AllIngredients.keys()):
        v = AllIngredients[k]
        if matchIngredient(v):
            rows.append({ 
                "Name": k, 
                "Effect 1": v["effects"][0]["name"] ,
                "Effect 2": v["effects"][1]["name"] ,
                "Effect 3": v["effects"][2]["name"] ,
                "Effect 4": v["effects"][3]["name"] ,
                "Farmable": str(v["farmable"]),
                "Weight": str(v["weight"]),
                "Value": str(v["value"]),
                })
    sortby = None
    if "sortby" in request.args:
        sortby = request.args.get("sortby")
    fmt = table.HtmlTableFormat()
    table.printTable(table.Table(headers, rows, sortby), fmt)
    return "<h1>Ingredients</h1>" + str(fmt)

@app.route("/effects")
def effects():
    def matchEffect(e):
        if "school" in request.args:
            school = request.args.get("school")
            if e["school"] != school:
                return False
        if "type" in request.args:
            type = request.args.get("type")
            if e["type"] != type:
                return False
        return True
    headers = [ "Name", "Description", "School", "Type", "Cost" ]
    rows = [ ]
    for k in sorted(AllEffects.keys()):
        v = AllEffects[k]
        if matchEffect(v):
            rows.append({ 
                "Name": k, 
                "Description": v["description"].format(**v),
                "School": v["school"],
                "Type": v["type"],
                "Cost": v["cost"],
                # "Magicka": v["mag"],
                # "Duration": v["dur"],
                })
    sortby = None
    if "sortby" in request.args:
        sortby = request.args.get("sortby")
    fmt = table.HtmlTableFormat()
    table.printTable(table.Table(headers, rows, sortby), fmt)
    return "<h1>Effects</h1>" + str(fmt)

@app.route("/potions")
def potions():
    if "ingredients" in request.args:
        ingredients = request.args.get("ingredients")
        result = getPotionsTable(ingredients.split(","))
        if "sortby" in request.args:
            result.setSortCol(request.args.get("sortby"))
        fmt = table.HtmlTableFormat()
        table.printTable(result, fmt)
        return "<h1>Potions</h1>" + str(fmt)
    else:
        return "<h1>Potions</h1><p>Provide list of ingredents as a parameter.<p>"
        

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)