# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Alchemy is a Flask web application for exploring the Skyrim alchemy system — ingredients, effects, and brewed potions. It also exposes a CLI tool and a JSON API.

## Commands

All Python must run via Poetry (either `poetry run python` or inside `poetry shell`).

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
invoke docker-run              # runs on port 8088
invoke docker-stop
invoke docker-push
```

## Architecture

### Domain Model

Three Pydantic models form the core, all loaded from YAML at import time:

- **Effect** ([effect.py](effect.py)) — magical effect with school, type (Beneficial/Offensive), cost, magnitude, duration. Value formula: `cost * mag^1.1 * dur^1.1 * 0.0794328`. Loaded from [effects.yaml](effects.yaml).
- **Ingredient** ([ingredient.py](ingredient.py)) — has exactly 4 `ActiveEffect` slots (each with power/value multipliers), plus farmable flag, category, and image URLs. Loaded from [ingredients.yaml](ingredients.yaml).
- **Potion** ([potion.py](potion.py)) — result of combining 2–3 ingredients. An effect appears in a potion only if **at least 2 ingredients share it**. `Potion.brew()` generates all combinations; `ingredients_key()` deduplicates order-independent recipes.

### Flask App

[app.py](app.py) has 14 routes across four feature areas:
- `/skyrim/ingredients` — list/filter/sort; `/<name>` for detail
- `/skyrim/effects` — list/filter/sort; `/<name>` for detail + which ingredients provide it
- `/skyrim/potions` — POST form to generate potions (random/all/farmable/best/custom sets); `GET /api/skyrim/potions` returns JSON
- `/madlibs` — standalone fill-in-the-blanks game from [madlibs.yaml](madlibs.yaml)

Data is loaded into module-level singletons at import time: `AllIngredientsByName`, `AllEffectsByName`, `AllMadlibsByName`.

### CLI

[skyrimPotions.py](skyrimPotions.py) is a standalone Rich-formatted table tool for potion generation with ingredient selection flags (specific, farmable, from-file) and sorting options.

## Conventions

- snake_case for variables/functions, PascalCase for classes
- Alchemy domain terminology in variable names (e.g., `active_effects`, `brew`, `farmable`)
- Predicate functions (lambdas/functions) passed as filters — see ingredient and potion filtering patterns
- Static factory methods: `Ingredient.from_file()`, `Effect.from_file()`, `Potion.brew()`
- Tests live at the project root alongside source files (`test_*.py`)

## YAML Data Format

**Ingredients** ([ingredients.yaml](ingredients.yaml)):
```yaml
ingredient_name:
  effects:
    - effect_name_1
    - effect_name_2
    - effect_name_3
    - effect_name_4
  value: <gold>
  weight: <units>
  farmable: true   # optional
  dlc: <name>      # optional
```

**Effects** ([effects.yaml](effects.yaml)):
```yaml
effect_name:
  type: beneficial/harmful/neutral
  description: <text>
  base_magnitude: <number>
  base_duration: <seconds>
  cost: <number>
  school: <Restoration|Destruction|...>
```
