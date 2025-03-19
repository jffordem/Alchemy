import yaml
import requests
from bs4 import BeautifulSoup
import time
import re
from rich.progress import track

def get_image_url(name, link, is_effect=False):
    """Get the full-sized image URL from the UESP wiki page."""
    try:
        # Add a small delay to be nice to the server
        time.sleep(0.25)
        
        response = requests.get(link)
        if response.status_code != 200:
            print(f"Failed to fetch {link}")
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # First try to find the full image in the infobox
        infobox = soup.find('table', {'class': 'infobox'})
        if infobox:
            img = infobox.find('img')
            if img and 'src' in img.attrs:
                # Convert thumbnail URL to full image URL
                src = img['src']
                if 'thumb' in src:
                    # Remove the thumbnail parameters to get the full image
                    full_url = src.split('/thumb/')[0] + '/' + src.split('/thumb/')[1].split('/')[0]
                    return full_url
        
        # If not found in infobox, try finding any image with the name
        for img in soup.find_all('img'):
            if 'src' in img.attrs and name.lower() in img['src'].lower():
                src = img['src']
                if 'thumb' in src:
                    # Remove the thumbnail parameters to get the full image
                    full_url = src.split('/thumb/')[0] + '/' + src.split('/thumb/')[1].split('/')[0]
                    return full_url
                
        return None
    except Exception as e:
        print(f"Error processing {name}: {str(e)}")
        return None

def update_ingredients():
    """Update ingredient thumbnails."""
    print("Updating ingredient thumbnails...")
    # Read the current YAML file
    with open('ingredients.yaml', 'r') as f:
        data = yaml.safe_load(f)

    # Process each ingredient
    for ingredient in track(data, description="Processing ingredients..."):
        name = ingredient['name']
        link = ingredient['link']
        
        # Get the full image URL
        image_url = get_image_url(name, link)
        
        if image_url:
            # Update the image URL
            ingredient['thumbnail'] = image_url
        else:
            ingredient['thumbnail'] = f"Could not find image for {name}"

    # Write back to the YAML file
    with open('ingredients.yaml', 'w') as f:
        yaml.dump(data, f, sort_keys=False, allow_unicode=True)
    
    print("Finished updating ingredient images!")

def update_effects():
    """Update effect thumbnails."""
    print("Updating effect thumbnails...")
    # Read the current YAML file
    with open('effects.yaml', 'r') as f:
        data = yaml.safe_load(f)

    # Process each effect
    for effect in track(data, description="Processing effects..."):
        name = effect['name']
        link = effect['link']
        
        # Get the full image URL
        image_url = get_image_url(name, link, is_effect=True)
        
        if image_url:
            # Update the image URL
            effect['thumbnail'] = image_url
        else:
            effect['thumbnail'] = f"Could not find image for {name}"

    # Write back to the YAML file
    with open('NEW_effects.yaml', 'w') as f:
        yaml.dump(data, f, sort_keys=False, allow_unicode=True)
    
    print("Finished updating effect images!")

if __name__ == "__main__":
    #update_ingredients()
    update_effects() 