# app.py

from flask import Flask, request, send_from_directory
from flask.cli import with_appcontext
import os
import socket
import random
from skyrimPotions import AllIngredients, AllEffects, getPotionsTable, getPotionsByEffects
import table
from madlibs import madlib, calendar_altText, calendar_facts, country_song

app = Flask(__name__)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.root_path, 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route("/")
def hello():
    return """<h1>Crafting Database</H1>
    <h2>Skyrim</h2>
    <p>GET /skyrim
    """

def makeUrl(path):
    return request.url_root + path.replace(" ", "%20").replace("'", "%27")

def makeAnchor(resourceType, resourceName):
    return "<a href='" + makeUrl(resourceType + "/" + resourceName) + "'>" + resourceName + "</a>"

@app.route("/skyrim")
def skyrim():
    return """<h1>Skyrim Potions</H1>
    <h2>Ingredients</h2>
    <p>GET skyrim/ingredients
    <p>Params:
    <ul>
    <li>effects={list of effects}</li>
    <li>farmable=True/False</li>
    <li>sortby={column}</li>
    </ul>
    <h2>Effects</h2>
    <p>GET skyrim/effects
    <p>Params:
    <ul>
    <li>school={school}</li>
    <li>type={type}</li>
    <li>sortby={column}</li>
    </ul>
    <h2>Potions</h2>
    <p>GET skyrim/potions
    <p>Params:
    <ul>
    <li>ingredients={list of ingredients} or all or farmable</li>
    <li>sortby={column}</li>
    </ul>
    """

@app.route("/skyrim/ingredients")
def skyrimIngredients():
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
                # TODO: How to get current hostname:port from app?
                "Name": makeAnchor("skyrim/ingredients", k),
                "Effect 1": makeAnchor("skyrim/effects", v["effects"][0]["name"]) ,
                "Effect 2": makeAnchor("skyrim/effects", v["effects"][1]["name"]) ,
                "Effect 3": makeAnchor("skyrim/effects", v["effects"][2]["name"]) ,
                "Effect 4": makeAnchor("skyrim/effects", v["effects"][3]["name"]) ,
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

@app.route("/skyrim/ingredients/<name>")
def skyrimIngredient(name):
    if name in AllIngredients:
        i = AllIngredients[name]
        result = "<table><tr><th>Name</th><td>" + makeAnchor("skyrim/ingredients", i["name"]) + "</td></tr>" + \
                      "<tr><th>Farmable</th><td>" + str(i["farmable"]) + "</td></tr>" + \
                      "<tr><th>Weight</th><td>" + str(i["weight"]) + "</td></tr>" + \
                      "<tr><th>Value</th><td>" + str(i["value"]) + "</td></tr>"
        for n in range(4):
            effect = i["effects"][n]
            result += "<tr><th>Effect %d</th><td>" % (n+1, )
            result += makeAnchor("skyrim/effects", effect["name"])
            if effect["power"] != 1.0:
                result += " (*{:1.1f})".format(effect["power"])
            if effect["value"] != 1.0:
                result += " (${:1.1f})".format(effect["value"])
            result += "</td></tr>"
        result += "</table>"
        return result
    else:
        return "Not found"

@app.route("/skyrim/effects")
def skyrimEffects():
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
                "Name": makeAnchor("skyrim/effects", k), 
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

@app.route("/skyrim/effects/<name>")
def skyrimEffect(name):
    if name in AllEffects:
        e = AllEffects[name]
        return "<table><tr><th>Name</th><td>" + makeAnchor("skyrim/effects", e["name"]) + "</td></tr>" + \
                  "<tr><th>Description</th><td>" + e["description"].format(**e) + "</td></tr>" + \
                  "<tr><th>School</th><td>" + e["school"] + "</td></tr>" + \
                  "<tr><th>Type</th><td>" + e["type"] + "</td></tr></table>"
    else:
        return "Not found"

@app.route("/skyrim/potions")
def skyrimPotions():
    if "ingredients" in request.args:
        ingredients = request.args.get("ingredients")
        if ingredients == "all": ingredients = ",".join(AllIngredients.keys())
        if ingredients == "farmable": ingredients = ",".join([ ingredient["name"] for ingredient in AllIngredients.values() if ingredient["farmable"] ])
        result = getPotionsTable(ingredients.split(","))
        if "sortby" in request.args:
            result.setSortCol(request.args.get("sortby"))
        fmt = table.HtmlTableFormat()
        table.printTable(result, fmt)
        return "<h1>Potions</h1>" + str(fmt)
    elif "effects" in request.args:
        result = getPotionsByEffects(request.args.get("effects").split(","))
        if "sortby" in request.args:
            result.setSortCol(request.args.get("sortby"))
        fmt = table.HtmlTableFormat()
        table.printTable(result, fmt)
        return "<h1>Potions</h1>" + str(fmt)
    else:
        return "<h1>Potions</h1><p>Provide list of ingredients as a parameter.<p>"

@app.route("/madlibs/<name>")
def madlibs(name):
    if name == "xkcd":
        return "<h1>xkcd</h1><p>" + madlib(calendar_facts)
    elif name == "country":
        return "<h1>Country Song</h1><p>" + madlib(country_song)
    elif name == "alt":
        return "<h1>Alt Text</h1><p>" + madlib(calendar_altText)
    else:
        return "Madlib not found"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)