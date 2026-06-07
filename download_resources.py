import os
import urllib.request
import shutil

# Create necessary directories if they don't exist
os.makedirs('static/images', exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('static/fonts', exist_ok=True)

# Resource URLs
resources = {
    # Skyrim Logo - Updated URL
    'skyrim-logo.png': 'https://static.wikia.nocookie.net/elderscrolls/images/4/4e/Elder_Scrolls_Logo.png/revision/latest?cb=20160614211643',
    
    # UI Icons - These worked
    'potion-icon.png': 'https://game-icons.net/icons/ffffff/000000/1x1/lorc/potion-ball.png',
    'ingredient-icon.png': 'https://game-icons.net/icons/ffffff/000000/1x1/lorc/mushroom.png',
    'effect-icon.png': 'https://game-icons.net/icons/ffffff/000000/1x1/lorc/magic-swirl.png',
    
    # Background - Updated URL
    'skyrim-bg.jpg': 'https://wallpapercave.com/wp/0Lk1Rjc.jpg',
}

# Set User-Agent header to avoid 403 errors
opener = urllib.request.build_opener()
opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')]
urllib.request.install_opener(opener)

# Download all resources
for filename, url in resources.items():
    print(f"Downloading {filename}...")
    try:
        response = urllib.request.urlopen(url)
        with open(f'static/images/{filename}', 'wb') as outfile:
            shutil.copyfileobj(response, outfile)
        print(f"Downloaded {filename}")
    except Exception as e:
        print(f"Error downloading {filename}: {e}")

print("All resources downloaded!") 