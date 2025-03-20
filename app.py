import os
from flask import Flask, request, send_from_directory, render_template
import random
import json

from madlibs import AllMadlibsByName
from ingredient import AllIngredientsByName, Ingredient, get_ingredients_by_filter, get_ingredient_by_name
from effect import AllEffectsByName, get_effect_by_name, get_effects_by_filter
from potion import Potion

NOT_FOUND_MESSAGE = "Not Found"
NOT_FOUND_STATUS = 404
DEFAULT_PORT = 5000

__doc__ = """
Then configure Flask.

```cmd
$ set FLASK_APP=app
$ set FLASK_ENV=development
```

Then you can start the service.  It will be at http://localhost:5000 by default.

```cmd
$ flask run
```
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

    # Get sort parameters
    sortby = request.args.get('sortby', 'name')
    direction = request.args.get('direction', 'asc')
    reverse = direction == 'desc'

    # Set sort function based on sortby
    if sortby == 'name':
        sort = lambda ingredient: ingredient.name
    elif sortby == 'value':
        sort = lambda ingredient: ingredient.value
    elif sortby == 'weight':
        sort = lambda ingredient: ingredient.weight
    else:
        sort = lambda ingredient: ingredient.name

    ingredients = get_ingredients_by_filter(predicate)
    ingredients.sort(key=sort, reverse=reverse)
    return render_template('ingredients.html', ingredients=ingredients, sortby=sortby, direction=direction)


@app.route("/skyrim/ingredients/<string:name>")
def skyrim_ingredient(name):
    item = get_ingredient_by_name(name)
    if item:
        return render_template('ingredient.html', ingredient=item)
    else:
        return NOT_FOUND_MESSAGE, NOT_FOUND_STATUS


@app.route("/skyrim/effects")
def skyrim_effects():
    sortby = request.args.get('sortby', 'name')
    direction = request.args.get('direction', 'asc')
    reverse = direction == 'desc'
    effects = sorted(AllEffectsByName.values(), key=lambda e: getattr(e, sortby), reverse=reverse)
    return render_template('effects.html', effects=effects, sortby=sortby, direction=direction)


@app.route("/skyrim/effects/<string:name>")
def skyrim_effect(name):
    item = get_effect_by_name(name)
    if item:
        return render_template('effect.html', effect=item)
    else:
        return NOT_FOUND_MESSAGE, NOT_FOUND_STATUS


@app.route('/api/skyrim/potions', methods=['GET'])
def skyrim_potions_api():
    ingredient_names = request.args.get('ingredients').split(',')
    potions = Potion.brew(ingredient_names)
    return json.dumps({'potions': potions, 'ingredients': ingredient_names})


@app.route('/skyrim/potions')
def skyrim_potions():
    def get_ingredients() -> list[Ingredient]:
        if 'ingredients' in request.args:
            ingredients = request.args.get('ingredients')
            if ingredients == "all": return list(AllIngredientsByName.keys())
            if ingredients == "farmable": return [ ingredient for ingredient in AllIngredientsByName.values() if ingredient.farmable]
            return [ get_ingredient_by_name(name) for name in ingredients.split(',') ]
        else:
            ingredients = list(AllIngredientsByName.values())
            random.shuffle(ingredients)
            return ingredients[:5]
    limit = 100
    ingredients = get_ingredients()
    potions = Potion.brew(ingredients)
    return render_template('potions.html', potions=potions[:limit], ingredients=ingredients)


@app.route("/madlibs")
def all_madlibs():
    return render_template('madlibs.html', names=AllMadlibsByName.keys())


@app.route("/madlibs/<string:name>")
def madlibs(name):
    if name in AllMadlibsByName:
        item = AllMadlibsByName[name]
        return render_template('madlib.html', name=name, lines=item.render(), ref=item.ref)
    return NOT_FOUND_MESSAGE, 404


@app.route("/about")
def about():
    version = os.getenv('APP_VERSION', '1.0.0')
    build_date = os.getenv('BUILD_DATE', '2023-01-01')
    return render_template('about.html', version=version, build_date=build_date)


if __name__ == '__main__':
    # Use PORT environment variable if set (e.g., in Docker), otherwise default to 5000
    port = int(os.environ.get('PORT', DEFAULT_PORT))
    app.run(host='0.0.0.0', port=port)
