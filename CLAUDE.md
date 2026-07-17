# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Alchemy is a Skyrim potion simulator: a Flask web app (plus a CLI tool and a JSON API) for exploring
the game's alchemy system — ingredients, effects, and the potions they brew into. It was originally
built for two reasons: to learn front-end technologies, and to answer a real gameplay question —
which farmable ingredient combos are most profitable (the author's favorite: Imp Stool + Mora
Tapinella + Swamp Fungal Pod). The lasting value today is mostly as a sandbox for
front-end/Flask experimentation built on a working domain model.

## Commands

All Python must run via Poetry (either `poetry run python` or inside `poetry shell`). A
`requirements.txt` also exists purely for the Docker image (plain `pip install`) — keep it in sync
with `pyproject.toml` if dependencies change.

```bash
# Install dependencies
poetry install

# Run dev server (localhost:5000)
invoke start

# Run with debugger and hot reload
invoke start-debug

# Run all tests
invoke test

# Run tests with options
invoke test --verbose          # -v output
invoke test --failfast         # stop on first failure
invoke test --markers="not webtest"

# Docker
invoke docker-build
invoke docker-run              # runs on port 8080
invoke docker-stop
invoke docker-push

# Equivalent raw commands
flask run
pytest                                    # run all tests
pytest test_potion.py                     # single test file
pytest test_potion.py::test_brew          # single test function
pytest test_potion.py -k "brew"           # by keyword
```

The app also runs directly via `python app.py` (reads the `PORT` env var, defaults to 5000; Docker
sets `PORT=8080`).

Tests (`test_potion.py`, `test_ingredient.py`, `test_effect.py`) run at the project root, alongside
source files, directly against the real `ingredients.yaml`/`effects.yaml` data — there are no
mocks/fixtures standing in for that data, so changing ingredient/effect data can change test
outcomes.

## Architecture

### Domain Model

Three Pydantic models form the core, all loaded from YAML at import time into module-level
singletons:

- **Effect** ([effect.py](effect.py)) — magical effect with school, type (Beneficial/Offensive),
  cost, magnitude, duration. `value` formula: `cost * mag^1.1 * dur^1.1 * 0.0794328`. Loaded from
  [effects.yaml](effects.yaml) into `AllEffectsByName`.
- **Ingredient** ([ingredient.py](ingredient.py)) — has a list of `ActiveEffect`s (each with
  power/value multipliers; in practice every ingredient has 4), plus a farmable flag, category, and
  image URLs. Loaded from [ingredients.yaml](ingredients.yaml) into `AllIngredientsByName`.
  `Ingredient.combine(ingredients)` is the core game-rule implementation: it groups all effects
  across the given ingredients by name and only produces an `ActiveEffect` for effects shared by
  **2 or more** ingredients — this mirrors the actual Skyrim alchemy rule. Power and value for a
  combined effect are the *product* (not sum) across contributing ingredients.
- **Potion** ([potion.py](potion.py)) — result of combining 2–3 ingredients (Skyrim's max mixture
  size). Not loaded from a file. `Potion.brew(ingredients)` generates every combination via
  `combinations()`, calls `Ingredient.combine` on each, and keeps only combinations producing at
  least one active effect. Potions have no name — `str(potion)` derives one from its sorted effect
  names (`"Potion of X and Y"`), which is also used for `__eq__`. `ingredients_key()` gives an
  order-independent dedup key for a recipe (used by the also-available but currently unused
  `find_duplicates`/`unique_potions` helpers). `brew()` accepts either `Ingredient` objects or name
  strings, and filters out ingredients invalid for potion-making (currently just `"Jarrin Root"`, a
  special quest item).

Because both `AllEffectsByName` and `AllIngredientsByName` are populated as a side effect of
importing `effect.py`/`ingredient.py`, importing either module (directly or transitively) triggers a
YAML parse — there's no lazy-load path.

### Flask App

[app.py](app.py) is a single flat module of routes (no blueprints), a thin view layer over the
domain model — routes filter/sort/paginate using composable predicate functions
(`pred_true`, `pred_and`, `pred_or`) and hand data to Jinja templates in `templates/`. Feature areas:

- `/skyrim/ingredients` — list/filter/sort (`search`, `category`/`category_prefix`, `farmable`,
  `sortby`, `direction`); `/<name>` for detail.
- `/skyrim/effects` — list/filter/sort (`search`, `type`, `school`, `sortby`, `direction`);
  `/<name>` for detail plus which ingredients provide it.
- `/skyrim/potions` — `ingredients` query param accepts `all`, `farmable`, `best` (a curated
  high-value list via `get_best_ingredients()`), a comma-separated ingredient list, or is omitted for
  a random 5-ingredient sample; supports `limit` for pagination. Also accepts POST from a form.
  `GET /api/skyrim/potions` returns the JSON equivalent (`ingredients` required, comma-separated).
- `/madlibs`, `/madlibs/<name>` — an unrelated bundled feature (see [madlibs.py](madlibs.py)): a
  mad-libs-style text generator driven by [madlibs.yaml](madlibs.yaml), where alternate clauses are
  written as parenthesized, `|`-separated options and expanded via the recursive `_all`/`_any`
  functions.

`app/models/` and `app/routes/` exist but are currently **empty** — they read as a planned
blueprint-style refactor that hasn't happened; don't assume code lives there.

### CLI

[skyrimPotions.py](skyrimPotions.py) is a standalone Rich-table CLI over the same domain model
(`python skyrimPotions.py -i Wheat Garlic`, `-i Farmable`, `-s effects|value|ingredients`,
`-f ingredients.txt`) — useful for exploring brew results without the web UI.

### Data files

- `ingredients.yaml`, `effects.yaml` — the live data consumed by the app. Both are YAML lists of
  objects (not name-keyed maps) — see actual formats below. `Ingredient`/`Effect` also support a JSON
  loading path (`from_file` dispatches on extension) but no `.json` file is currently wired up as the
  default.
- `alchemyData.json`, `alchemyData2.json`, `ingredients.csv`, `effects.csv` — older/alternate data
  snapshots, not read by the running app.
- `parseNew.py`, `fixlinks.py`, `alchemyData.py`, `download_resources.py`, `get_ingredient_images.py`
  — one-off/legacy data-wrangling scripts historically used to scrape and reshape ingredient/effect
  data from the UESP wiki into the YAML files (e.g. `fixlinks.py` backfills `link_url` into
  `alchemyData.json`). Not imported by `app.py` and not part of the runtime request path;
  `alchemyData.py` is fully commented out (dead code kept for reference).

### Unrelated bundled content

`CastSpell.c` and `WoodChopper.c` are Arduino Leonardo sketches for automating in-game grinding
(documented in `readme.md`) — no relationship to the Flask app or Python code, not part of the build.

## Conventions

- snake_case for variables/functions, PascalCase for classes.
- Alchemy domain terminology in variable/function names (e.g. `active_effects`, `brew`, `farmable`).
- Predicate functions (lambdas or plain functions of one item → bool) passed as filters, composed
  with `pred_and`/`pred_or`/`pred_not`-style combinators — see ingredient/effect/potion filtering.
- Static factory methods: `Ingredient.from_file()`, `Effect.from_file()`, `Potion.brew()`.

## YAML Data Format

**Ingredients** ([ingredients.yaml](ingredients.yaml)) — a list of objects:
```yaml
- name: "Nirnroot"
  category: "Flora/Roots"
  effects:
    - name: "Damage Health"
      power: 1.0
      value: 12.6
    - name: "Damage Stamina"
      power: 1.0
      value: 1.0
  farmable: false
  value: 10
  weight: 0.2
  link_url: "https://en.uesp.net/wiki/Skyrim:Nirnroot"
  image_url: "https://images.uesp.net/..."
  thumbnail_url: "https://images.uesp.net/..."
```

**Effects** ([effects.yaml](effects.yaml)) — a list of objects:
```yaml
- name: "Fortify Marksman"
  description: "Bows do {mag}% more damage for {dur} seconds."
  school: "Restoration"
  type: "Offensive"
  cost: 0.5
  dur: 60
  mag: 4
  link_url: "https://en.uesp.net/wiki/Skyrim:Fortify_Marksman"
```
