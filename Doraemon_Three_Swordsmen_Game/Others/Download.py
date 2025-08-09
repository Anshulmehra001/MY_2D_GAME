import requests

# TODO: Replace this link with the real one when provided
url = "https://your-real-download-link.com/game.zip"


# Name to save the file as
file_name = "Doraemon_Three_Swordsmen_Game.zip"

print("📥 Downloading your Doraemon game... Please wait...")

try:
    response = requests.get(url, stream=True)
    response.raise_for_status()

    with open(file_name, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    print(f"✅ Download complete! File saved as: {file_name}")
    print("📂 You can now unzip the file and double-click the .exe to play.")
except requests.exceptions.RequestException as e:
    print("❌ Download failed:", e)
