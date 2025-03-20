import argparse
import yaml
import requests
from bs4 import BeautifulSoup
import time
import re
from rich.progress import Progress
from rich.console import Console
from urllib.parse import urljoin

__doc__ = '''
This script loads the UESP page from each ingredient and adds the url for the thumbnail image, and the full-sized image.

For each ingredient in the AllIngredientsByName dictionary, it fetches the UESP page and extracts the thumbnail image and the full-sized image.
'''

console = Console()

def fetch_images(ingredient_name, url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the image element
        thumbnail_url = soup.find('img', {'alt': ingredient_name})['src']
        full_image_url = soup.find('meta', {'property': 'og:image'})['content']

        # Resolve relative URLs to absolute URLs
        thumbnail_url = urljoin(url, thumbnail_url)
        full_image_url = urljoin(url, full_image_url)

        return thumbnail_url, full_image_url
    except Exception as e:
        console.print(f"Error fetching images for {ingredient_name}: {e}")
        return None, None

def main(args):
    with open('ingredients.yaml', 'r') as file:
        ingredients = yaml.safe_load(file)

    updated_ingredients = list()

    with Progress() as progress:
        track = progress.add_task("Fetching ingredient images...", total=len(ingredients))
        for ingredient in ingredients:
            ingredient_name = ingredient['name']
            progress.update(track, advance=1, description=f"Fetching images for {ingredient_name}...")
            #console.print(f"Fetching images for {ingredient_name}...")
            uesp_url = ingredient.get('link_url')
            if not uesp_url:
                console.print(f"[red]No UESP URL for {ingredient_name}, skipping...[/red]")
                continue

            thumbnail_url, full_image_url = fetch_images(ingredient_name, uesp_url)
            ingredient['thumbnail_url'] = thumbnail_url
            ingredient['image'] = full_image_url
            updated_ingredients.append(ingredient)
            if not thumbnail_url or not full_image_url:
                console.print(f"[red]Error fetching images for {ingredient_name}[/red]")

            if args.testing:
                console.print(f"\nFetched images for {ingredient_name}: \n{thumbnail_url} \n{full_image_url}")
                break # just do one for now

            # Respectful delay to avoid overwhelming the server
            time.sleep(args.sleep)

    # Save updated ingredients to a new YAML file
    if not args.testing:
        with open('NEW_ingredients.yaml', 'w') as file:
            yaml.dump(updated_ingredients, file)
        console.print("Updated ingredient data saved to NEW_ingredients.yaml.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-t', '--testing', action='store_true', help="Run in testing mode (only fetch one ingredient)")
    parser.add_argument('-s', '--sleep', type=float, default=0.5, help="Number of seconds to sleep between requests")
    args = parser.parse_args()
    main(args)
