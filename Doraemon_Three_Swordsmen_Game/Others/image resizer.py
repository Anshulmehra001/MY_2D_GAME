from PIL import Image
import os

try:
    resample = Image.Resampling.LANCZOS  # Pillow ≥10
except AttributeError:
    resample = Image.ANTIALIAS
# Define target sizes for each image by filename
dimensions = {
    "nobita.png": (64, 64),
    "enemy_knight.png": (64, 64),
    "background_forest.png": (800, 480),
    "scene1.png": (800, 480),
    "scene2.png": (800, 480),
    "title_logo.png": (600, 100),
    "sword_slash.png": (64, 64)
}
# Folder where assets are stored
assets_folder = "assets"

# Resize loop
for filename, size in dimensions.items():
    path = os.path.join(assets_folder, filename)
    if os.path.exists(path):
        try:
            img = Image.open(path)
            resized = img.resize(size, resample)
            resized.save(path)
            print(f"✅ Resized {filename} to {size}")
        except Exception as e:
            print(f"❌ Error resizing {filename}: {e}")
    else:
        print(f"⚠️ {filename} not found in assets folder.")
