from flask import Flask, request, send_from_directory, render_template
import random
import json, os

from madlibs import AllMadlibsByName
from ingredient import AllIngredientsByName, get_ingredients_by_filter, get_ingredient_by_name
from effect import AllEffectsByName, get_effect_by_name, get_effects_by_filter
from potion import Potion

__doc__ = """
Then configure Flask.

C:> set FLASK_APP=app
C:> set FLASK_ENV=development

Then you can start the service.  It will be at http://localhost:5000 by default.

C:> flask run
"""

# better place for these predicate functions?
def pred_true(_):
    return True

def pred_and(*predicates):
    return lambda x: all(predicate(x) for predicate in predicates)

def pred_or(*predicates):
    return lambda x: any(predicate(x) for predicate in predicates)

app = Flask(__name__)


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
def skyrim_ingredients():
    if 'farmable' in request.args:
        farmable = { "True":True, "true":True }.get(request.args.get("farmable"), False)
        predicate = lambda ingredient: ingredient.farmable == farmable
    else:
        predicate = pred_true
    # sort = { 'field': 'value', 'reverse': True }
    # if 'sortby' in request.args:
    #     sort = { 'field': request.args.get('sortby'), 'reverse': False }
    ingredients = get_ingredients_by_filter(predicate)
    #ingredients.sort(key=lambda ingredient: ingredient[sort['field']], reverse=sort['reverse'])
    return render_template('ingredients.html', ingredients=ingredients)


@app.route("/skyrim/ingredients/<name>")
def skyrim_ingredient(name):
    item = get_ingredient_by_name(name)
    if item:
        return render_template('ingredient.html', ingredient=item)
    else:
        return "Not Found", 404


@app.route("/skyrim/effects")
def skyrim_effects():
    if 'school' in request.args:
        school = request.args.get('school')
        match_school = lambda effect: effect.school == school
    else:
        match_school = pred_true
    if 'type' in request.args:
        effect_type = request.args.get('type')
        match_type = lambda effect: effect.type == effect_type
    else:
        match_type = pred_true
    effects = get_effects_by_filter(pred_and(match_school, match_type))
    #effects.sort(key=lambda effect: effect.cost, reverse=True)
    return render_template('effects.html', effects=effects)


@app.route("/skyrim/effects/<name>")
def skyrim_effect(name):
    item = get_effect_by_name(name)
    if item:
        return render_template('effect.html', effect=item)
    else:
        return "Not Found", 404


@app.route('/api/skyrim/potions', methods=['GET'])
def skyrim_potions_api():
    ingredients = request.args.get('ingredients').split(',')
    potions = Potion.brew(ingredients)
    return json.dumps({'potions': potions, 'ingredients': ingredients})


@app.route('/skyrim/potions')
def skyrim_potions():
    def getIngredients():
        if 'ingredients' in request.args:
            ingredients = request.args.get('ingredients')
            if ingredients == "all": return list(AllIngredientsByName.keys())
            if ingredients == "farmable": return [ ingredient.name for ingredient in AllIngredientsByName.values() if ingredient.farmable]
            return ingredients.split(',')
        else:
            ingredients = list(AllIngredientsByName.keys())
            random.shuffle(ingredients)
            return ingredients[:5]
    limit = 100
    ingredients = getIngredients()
    potions = Potion.brew(ingredients)
    return render_template('potions.html', potions=potions[:limit], ingredients=ingredients)


@app.route("/madlibs")
def all_madlibs():
    return render_template('madlibs.html', names=AllMadlibsByName.keys())


@app.route("/madlibs/<name>")
def madlibs(name):
    if name in AllMadlibsByName:
        item = AllMadlibsByName[name]
        return render_template('madlib.html', name=name, lines=item.render(), ref=item.ref)
    return "Not Found", 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
