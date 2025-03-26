import os
from flask import Flask, request, send_from_directory, render_template
import random
import json

from madlibs import AllMadlibsByName
from ingredient import AllIngredientsByName, Ingredient, get_best_ingredients, get_ingredients_by_filter, get_ingredient_by_name
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
    predicate = pred_true
    
    # Farmable filter
    if 'farmable' in request.args:
        farmable = { "True":True, "true":True }.get(request.args.get("farmable"), False)
        predicate = pred_and(predicate, lambda ingredient: ingredient.farmable == farmable)

    # Add search functionality
    if 'search' in request.args:
        search_terms = [term.strip().lower() for term in request.args.get('search').split(' ')]
        predicate = pred_and(predicate, lambda ingredient: any(term in ingredient.name.lower() for term in search_terms))

    # Add category filter functionality
    if 'category' in request.args:
        category = request.args.get('category')
        predicate = pred_and(predicate, lambda ingredient: ingredient.category == category)
    
    # Add category prefix filter functionality
    elif 'category_prefix' in request.args:
        prefix = request.args.get('category_prefix')
        predicate = pred_and(predicate, lambda ingredient: ingredient.category and ingredient.category.startswith(prefix))

    # Get sort parameters
    sortby = request.args.get('sortby', 'name')
    direction = request.args.get('direction', 'asc')
    reverse = direction == 'desc'

    # Set sort function based on sortby
    if sortby == 'name':
        sort = lambda ingredient: ingredient.name
    elif sortby == 'category':
        sort = lambda ingredient: ingredient.category or ""  # Handle None values when sorting
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
    search_query = request.args.get('search', '').lower()
    effect_type = request.args.get('type', '').lower()
    school = request.args.get('school', '').lower()
    pred = pred_true
    
    # Set a default title
    page_title = "EFFECTS"

    if search_query:
        search_terms = [term.strip().lower() for term in search_query.split(' ')]
        pred = pred_and(pred, lambda effect: any(term in effect.name.lower() for term in search_terms) or any(term in effect.description.lower() for term in search_terms))

    if effect_type:
        pred = pred_and(pred, lambda effect: effect.type.lower() == effect_type)
        # Update title for type filter
        page_title = f"{effect_type.upper()} EFFECTS"

    if school:
        pred = pred_and(pred, lambda effect: effect.school.lower() == school)
        # School filter takes precedence over type filter for the title
        page_title = f"{school.upper()} EFFECTS"

    effects = sorted(get_effects_by_filter(pred), key=lambda e: getattr(e, sortby), reverse=reverse)

    return render_template('effects.html', effects=effects, sortby=sortby, direction=direction, page_title=page_title)


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
    # Get query parameters with defaults
    ingredients_filter = request.args.get('ingredients', 'random')
    limit = int(request.args.get('limit', 100))
    
    def get_ingredients() -> list[Ingredient]:
        if 'ingredients' in request.args:
            ingredients = request.args.get('ingredients')
            if ingredients == "all": return list(AllIngredientsByName.keys())
            if ingredients == "farmable": return [ ingredient for ingredient in AllIngredientsByName.values() if ingredient.farmable]
            if ingredients == "best": return get_best_ingredients()
            return [ get_ingredient_by_name(name) for name in ingredients.split(',') ]
        else:
            ingredients = list(AllIngredientsByName.values())
            random.shuffle(ingredients)
            return ingredients[:5]
    
    ingredients = get_ingredients()
    
    # Fetch all matching potions for pagination calculations
    all_matching_potions = Potion.brew(ingredients)
    total_potions = len(all_matching_potions)
    
    # Get the limited subset of potions for display
    potions = all_matching_potions[:limit]
    
    # Determine if results are truncated
    is_truncated = total_potions > limit
    
    # Render template with pagination variables
    return render_template('potions.html', 
                          potions=potions, 
                          ingredients=ingredients,
                          is_truncated=is_truncated,
                          total_potions=total_potions,
                          current_filter=ingredients_filter,
                          limit=limit)


@app.route('/skyrim/potions', methods=['POST'])
def skyrim_potions_post():
    ingredient_names = request.form.get('ingredients', '').split(',')
    ingredients = [get_ingredient_by_name(name) for name in ingredient_names if get_ingredient_by_name(name)]
    potions = Potion.brew(ingredients)
    return render_template('potions.html', potions=potions, ingredients=ingredients)


@app.route("/madlibs")
def all_madlibs():
    return render_template('madlibs.html', names=AllMadlibsByName.keys())


@app.route("/madlibs/<string:name>")
def madlibs(name):
    if name in AllMadlibsByName:
        item = AllMadlibsByName[name]
        return render_template('madlib.html', name=name, lines=item.render(), ref=item.ref)
    return NOT_FOUND_MESSAGE, NOT_FOUND_STATUS


@app.route("/about")
def about():
    version = os.getenv('APP_VERSION', '1.0.0')
    build_date = os.getenv('BUILD_DATE', '2023-01-01')
    
    # Determine theme based on referrer
    referrer = request.referrer
    theme = "skyrim"  # Default theme
    
    if referrer:
        if "/madlibs" in referrer:
            theme = "madlib"
        elif "/skyrim" in referrer:
            theme = "skyrim"
    
    return render_template('about.html', version=version, build_date=build_date, theme=theme)


if __name__ == '__main__':
    # Use PORT environment variable if set (e.g., in Docker), otherwise default to 5000
    port = int(os.environ.get('PORT', DEFAULT_PORT))
    app.run(host='0.0.0.0', port=port)
