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

C:> flask init

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
    def hasEffect(ingredient, effectName):
        return any(effectName in effect['name'].lower() for effect in ingredient['effects'])
    def hasEffects(ingredient, effectNames):
        return any(hasEffect(ingredient, effectName.lower()) for effectName in effectNames)
    filter = {}
    if 'farmable' in request.args:
        farmable = { "True":True, "true":True }.get(request.args.get("farmable"), False)
        filter['farmable'] = farmable
    sort = ('value', -1)
    if 'sortby' in request.args:
        sort = (request.args.get('sortby'), 1)
    ingredients = list(db.ingredients.find(filter, sort=[sort]))
    buffs = { i['name']: hasBuffs(i) for i in ingredients }
    nerfs = { i['name']: hasNerfs(i) for i in ingredients }
    if 'effects' in request.args:
        effectNames = request.args.get('effects').split(',')
        ingredients = [ ingredient for ingredient in ingredients if hasEffects(ingredient, effectNames) ]
    return render_template('ingredients.html', ingredients=ingredients, buffs=buffs, nerfs=nerfs)

def hasBuffs(ingredient):
    return any(effect['power'] > 1 for effect in ingredient['effects']) or any(effect['value'] > 1 for effect in ingredient['effects'])

def hasNerfs(ingredient):
    return any(effect['power']< 1 for effect in ingredient['effects']) or any(effect['value'] < 1 for effect in ingredient['effects'])

@app.route("/skyrim/ingredients/<string:name>")
def skyrimIngredient(name: str):
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

@app.route("/skyrim/effects/<string:name>")
def skyrimEffect(name: str):
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
    def hasEffect(potion, effectName):
        return any(effectName in effect.lower() for effect in potion['effects'].keys())
    def hasEffects(potion, effectNames):
        return any(hasEffect(potion, effectName.lower()) for effectName in effectNames)
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
    ingredientsByName = indexOn('name', db.ingredients.find())
    effectsByName = indexOn('name', db.effects.find())
    ingredients = getIngredients(ingredientsByName)
    potions = getPotions(ingredients, ingredientsByName, effectsByName)
    if 'effects' in request.args:
        effectNames = request.args.get('effects').split(',')
        potions = [ potion for potion in potions if hasEffects(potion, effectNames) ]
    limit = len(potions)
    if 'limit' in request.args:
        limit = int(request.args.get('limit'))
    return render_template('potions.html', potions=potions[:limit], ingredients=ingredients)

AllMadlibs = {
    'xkcd Calendar Facts': calendar_facts,
    "Country Song": country_song,
    "Alt Text": calendar_altText,
    "Whip It": whip_it
}

MadlibRefs = {
    'xkcd Calendar Facts': 'https://xkcd.com/1930/'
}

@app.route("/madlibs")
def all_madlibs():
    return render_template('madlibs.html', names=AllMadlibs.keys())

@app.route("/madlibs/<string:name>")
def madlibs(name: str):
    if name in AllMadlibs:
        return render_template('madlib.html', name=name, lines=madlib(AllMadlibs[name]), ref=MadlibRefs.get(name, None))
    return "Not Found", 404

@app.route('/tictactoe')
def tictactoe():
    board = makeBoard()
    session['board'] = board
    return render_template('tictactoe.html', rows=boardRows(board), result=None)

@app.route('/tictactoe/move/<int:move>')
def tictactoe_move(move: int):
    board = session['board']
    result = None
    if board[move] == ' ' or board[move] == '-':
        board = makePlayerMove(board, move)
        board = makeComputerMove(board)
        session['board'] = board
        if isPlayerWin(board): result = "You win!"
        if isComputerWin(board): result = "You lose."
        if isGameOver(board): result = "Game over."
    return render_template('tictactoe.html', rows=boardRows(board), result=result)

@app.cli.command('init')
def loadDb():
    db.ingredients.insert_many(AllIngredients.values())
    db.effects.insert_many(AllEffects.values())
    # could also create indexes
    #db.ingredients.createIndex({'name':1}, {'unique': True})
    #db.ingredients.createIndex({'farmable':1})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)