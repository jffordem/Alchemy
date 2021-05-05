from flask import Flask, request, send_from_directory, render_template
from skyrimPotions import getPotions
from madlibs import madlib, calendar_altText, calendar_facts, country_song, whip_it
from pymongo import MongoClient
from bson.objectid import ObjectId
import random
from alchemyData import AllEffects, AllIngredients, indexOn
import json, os

__doc__ = """
Create a mongodb client, usually as a docker container.

C:> docker run -p 27017:27017 -d mongodb

Then configure Flask.

C:> set FLASK_APP=app
C:> set FLASK_ENV=development

Configure the data.

C:> flask db_load

Then you can start the service.  It will be at http://localhost:5000 by default.

C:> flask run
"""

conn = "mongodb://localhost:27017/"
eng = MongoClient(conn)
db = eng.alchemy

app = Flask(__name__)

# Good grief!  flask.jsonify doesn't support ObjectId?!
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

# No thanks, flask.  I've got this.
def jsonify(data):
    return JSONEncoder().encode(data)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/skyrim")
def skyrim():
    return render_template('skyrim.html')

@app.route("/skyrim/ingredients")
def skyrimIngredients():
    filter = {}
    if 'farmable' in request.args:
        farmable = { "True":True, "true":True }.get(request.args.get("farmable"), False)
        filter['farmable'] = farmable
    ingredients = db.ingredients.find(filter, sort=[('value', -1)])
    return render_template('ingredients.html', ingredients=ingredients)

@app.route("/skyrim/ingredients/<name>")
def skyrimIngredient(name):
    item = db.ingredients.find_one({ 'name': name })
    if item:
        return render_template('ingredient.html', ingredient=item)
    else:
        return "Not Found", 404

@app.route("/skyrim/effects")
def skyrimEffects():
    filter = {}
    if 'school' in request.args:
        school = request.args.get('school')
        filter['school'] = school
    if 'type' in request.args:
        effect_type = request.args.get('type')
        filter['type'] = effect_type
    return render_template('effects.html', effects=db.effects.find(filter, sort=[('cost', -1)]))

@app.route("/skyrim/effects/<name>")
def skyrimEffect(name):
    item = db.effects.find_one({ 'name': name })
    if item:
        return render_template('effect.html', effect=item)
    else:
        return "Not Found", 404

@app.route('/api/skyrim/potions', methods=['GET'])
def skyrimPotionsApi():
    ingredients = request.args.get('ingredients').split(',')
    ingredientsByName = indexOn('name', db.ingredients.find())
    effectsByName = indexOn('name', db.effects.find())
    potions = getPotions(ingredients, ingredientsByName, effectsByName)
    return jsonify({'potions': potions, 'ingredients': ingredients})

@app.route('/skyrim/potions')
def skyrimPotions():
    def getIngredients(ingredientsByName):
        if 'ingredients' in request.args:
            ingredients = request.args.get('ingredients')
            if ingredients == "all": return list(ingredientsByName.keys())
            if ingredients == "farmable": return [ ingredient["name"] for ingredient in ingredientsByName.values() if ingredient["farmable"] ]
            return ingredients.split(',')
        else:
            ingredients = list(ingredientsByName.keys())
            random.shuffle(ingredients)
            return ingredients[:5]
    limit = 100
    ingredientsByName = indexOn('name', db.ingredients.find())
    effectsByName = indexOn('name', db.effects.find())
    ingredients = getIngredients(ingredientsByName)
    potions = getPotions(ingredients, ingredientsByName, effectsByName)
    return render_template('potions.html', potions=potions[:limit], ingredients=ingredients)

AllMadlibs = {
    "xkcd": calendar_facts,
    "Country Song": country_song,
    "Alt Text": calendar_altText,
    "Whip It": whip_it
}

@app.route("/madlibs")
def all_madlibs():
    return render_template('madlibs.html', names=AllMadlibs.keys())

@app.route("/madlibs/<name>")
def madlibs(name):
    if name in AllMadlibs:
        return render_template('madlib.html', name=name, lines=madlib(AllMadlibs[name]))
    return "Not Found", 404

@app.cli.command('db_load')
def loadDb():
    db.ingredients.insert_many(AllIngredients.values())
    db.effects.insert_many(AllEffects.values())
    # could also create indexes
    #db.ingredients.createIndex({'name':1}, {'unique': True})
    #db.ingredients.createIndex({'farmable':1})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)