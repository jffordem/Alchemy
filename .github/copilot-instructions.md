## Technologies
- Python
- Flask
- YAML

## Dependencies Management
- Poetry

## Testing
- Pytest

## Instructions
Answer all questions in the style of a friendly colleague, using informal language.

This application refers to the popular computer game "The Elder Scrolls V: Skyrim".  
When I mention "Skyrim" or "the game", I'm talking about that game.

The goal of this application is to provide useful information about the Skyrim alchemy system.
In Skyrim the player collects various ingredients which are imbued with magical effects.
When those ingredients are combined at an alchemy table, they create potions which have the effects
shared by two or more of the ingredients used in the recipe.

Always consider all files that are currently open in the editor as context.
When I want to add a file for consideration I'll include its name in the prompt, such as 'and update the data in #file.txt'.

## Alchemy System Details
- Each ingredient has exactly 4 magical effects
- A potion can be created by combining 2 or 3 ingredients
- For an effect to appear in a potion, at least 2 ingredients must share that effect
- The strength (magnitude) of potion effects can be influenced by the player's skill level and perks

## Project Structure
- `/data`: YAML files containing ingredient and effect data
- `/app`: Main application code
- `/tests`: Pytest test files
- `/templates`: Flask HTML templates
- `/static`: CSS, JavaScript, and images

## Coding Conventions
- Use snake_case for variables and function names
- Use PascalCase for class names
- Use descriptive variable names that reflect alchemy terminology
- Document functions with docstrings
- Follow PEP 8 guidelines

## Data Structures
Ingredients should be structured as:
```yaml
ingredient_name:
  effects:
    - effect_name_1
    - effect_name_2
    - effect_name_3
    - effect_name_4
  value: cost_in_gold
  weight: weight_in_units
  dlc: optional_dlc_name
```

Effects should be structured as:
```yaml
effect_name:
  type: beneficial/harmful/neutral
  description: effect_description
  base_magnitude: number
  base_duration: seconds
```

## Common Queries
- Finding ingredients with specific effects
- Creating potions with desired effects
- Determining the most valuable potions that can be created from a list of ingredients
- Identifying which ingredients to gather to create specific potions
