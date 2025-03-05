from potion import Potion
from ingredient import AllIngredientsByName, get_ingredient_by_name, get_ingredients_by_filter
from rich.console import Console
from rich.table import Table
from rich.progress import track
import argparse
from enum import Enum

__doc__ = '''
Utility script for displaying potion information in a tabular format.
All core potion functionality has been moved to the Potion class.

Usage:
    python skyrimPotions.py                     # Use all ingredients, sort by value
    python skyrimPotions.py -i Wheat Garlic     # Specific ingredients
    python skyrimPotions.py -i Farmable         # Use all farmable ingredients
    python skyrimPotions.py -s effects          # Sort by number of effects
    python skyrimPotions.py -f ingredients.txt   # Read ingredients from file
'''

class SortColumn(str, Enum):
    """Sort columns for potion display."""
    VALUE = "value"
    EFFECTS = "effects"
    INGREDIENTS = "ingredients"

    def __str__(self):
        return self.value

def get_sort_key(sort_by: SortColumn):
    """Get the sort key function for a given column."""
    sort_keys = {
        SortColumn.VALUE: lambda p: p.value,
        SortColumn.EFFECTS: lambda p: len(p.active_effects),
        SortColumn.INGREDIENTS: lambda p: len(p.ingredients)
    }
    return sort_keys[sort_by]

def print_potions(ingredients, *, sort_by: SortColumn = SortColumn.VALUE, limit: int = 10):
    """Print a table of potions sorted by the specified column.
    
    Args:
        ingredients: List of ingredients to brew potions from.
        sort_by: Column to sort by (value, effects, or ingredients)
        limit: Maximum number of potions to show. Use -1 to show all potions.
    """
    ingredients = list(filter(Potion.is_valid_ingredient, ingredients))
    potions = Potion.brew(ingredients, track=track)
    table = Table(
        title=f"Potions (Sorted by {sort_by.value})", 
        show_header=True, 
        header_style="bold magenta",
        padding=(0,1,0,1),  # top, right, bottom, left padding
        show_lines=True     # Show lines between rows
    )

    # Add columns with proper widths
    table.add_column("Ingredient 1", width=16, no_wrap=True)
    table.add_column("Ingredient 2", width=16, no_wrap=True)
    table.add_column("Ingredient 3", width=16, no_wrap=True)
    table.add_column("$ Value", justify="right", width=8, no_wrap=True)
    table.add_column("#", justify="right", width=3, no_wrap=True)
    table.add_column("Effects", min_width=40, no_wrap=False)

    # Sort potions by specified column
    potions = sorted(potions, key=get_sort_key(sort_by), reverse=True)
    
    # Show all potions if limit is -1, otherwise show top N
    potions_to_show = potions if limit == -1 else potions[:limit]
    for potion in potions_to_show:
        ingredients = list(potion.ingredients)
        while len(ingredients) < 3:
            ingredients.append(None)
            
        table.add_row(
            ingredients[0].name if ingredients[0] else "",
            ingredients[1].name if ingredients[1] else "",
            ingredients[2].name if ingredients[2] else "",
            f"{potion.value:8.2f}".strip(),  # Format value with 2 decimal places
            str(len(potion.active_effects)),
            ", ".join(effect.name for effect in potion.active_effects)
        )

    console = Console()
    console.print(table)

def get_ingredients_from_file(filepath):
    """Read ingredients from a file, one per line.
    
    Args:
        filepath: Path to ingredients file
        
    Returns:
        List of ingredients
        
    Example file format:
        Wheat
        Garlic
        Blue Mountain Flower
    """
    try:
        with open(filepath, 'r') as f:
            names = [line.strip() for line in f if line.strip()]
        
        ingredients = []
        for name in names:
            try:
                ingredient = get_ingredient_by_name(name)
                ingredients.append(ingredient)
            except ValueError as e:
                print(f"Warning: {e}")
        return ingredients
    except FileNotFoundError:
        print(f"Error: Ingredients file '{filepath}' not found")
        return []
    except Exception as e:
        print(f"Error reading ingredients file: {e}")
        return []

def get_ingredients_from_args(args):
    """Get list of ingredients based on command line arguments.
    
    Special keywords:
    - Farmable: Use all farmable ingredients
    - @filename: Read ingredients from file
    """
    if not args.ingredients:
        return list(AllIngredientsByName.values())
    
    if len(args.ingredients) == 1:
        if args.ingredients[0].lower() == "farmable":
            return get_ingredients_by_filter(lambda i: i.farmable)
        if args.file:
            return get_ingredients_from_file(args.file)
    
    ingredients = []
    for name in args.ingredients:
        try:
            ingredient = get_ingredient_by_name(name)
            ingredients.append(ingredient)
        except ValueError as e:
            print(f"Warning: {e}")
    return ingredients

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Display potion combinations and their values in a table format.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s                      # Use all ingredients, sort by value
    %(prog)s -i Wheat Garlic     # Use specific ingredients
    %(prog)s -i Farmable         # Use all farmable ingredients
    %(prog)s -s effects          # Sort by number of effects
    %(prog)s -f ingredients.txt   # Read ingredients from file
    %(prog)s --ingredients "Blue Mountain Flower" "Dragon's Tongue"  # Ingredients with spaces
        """
    )
    parser.add_argument(
        '-i', '--ingredients',
        nargs='*',
        help='List of ingredients to use. Use "Farmable" to select all farmable ingredients. If not specified, all ingredients will be used.',
        metavar='INGREDIENT'
    )
    parser.add_argument(
        '-f', '--file',
        help='Read ingredients from file (one ingredient name per line)'
    )
    parser.add_argument(
        '-s', '--sort',
        type=lambda x: SortColumn(x.lower()),
        choices=[e.value for e in SortColumn],
        default=SortColumn.VALUE,
        help='Column to sort by (default: value)'
    )
    parser.add_argument(
        '-n', '--limit',
        type=int,
        default=10,
        help='Maximum number of potions to show (default: 10, use -1 to show all)'
    )
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    ingredients = get_ingredients_from_args(args)
    
    if not ingredients:
        print("No valid ingredients specified. Please check ingredient names and try again.")
    else:
        print_potions(ingredients, sort_by=args.sort, limit=args.limit)
