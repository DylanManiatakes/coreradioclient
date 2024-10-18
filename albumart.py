import os
import time
import requests
import mimetypes

# Path where album art files are saved
script_directory = os.path.dirname(os.path.abspath(__file__))
track_file = os.path.join(script_directory, "current_track.txt")

# Function to delete all existing album art files (art.jpg, art.png, etc.)
def delete_old_artwork():
    print("[INFO] Deleting old artwork...")
    art_files = ['art.jpg', 'art.png', 'art.gif', 'art.jpeg', 'art.webp']
    for art_file in art_files:
        full_path = os.path.join(script_directory, art_file)
        if os.path.exists(full_path):
            try:
                os.remove(full_path)
                print(f"[INFO] Deleted: {art_file}")
            except OSError as e:
                print(f"[ERROR] Failed to delete {art_file}: {e}")

# Function to scrape the current album art (if available)
def fetch_new_album_art(img_url):
    try:
        response = requests.get(img_url)
        content_type = response.headers['Content-Type']
        extension = mimetypes.guess_extension(content_type)
        if not extension:
            extension = '.jpg'  # Default to .jpg if type cannot be determined
        art_file_path = os.path.join(script_directory, f'art{extension}')
        with open(art_file_path, 'wb') as handler:
            handler.write(response.content)
        print(f"[INFO] New album art downloaded: art{extension}")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Error downloading image: {e}")

# Function to handle album art on startup
def handle_startup():
    print("[INFO] Handling startup album art...")
    delete_old_artwork()  # Clear any old album art files

    # Insert logic to scrape current song album art
    img_url = "URL_TO_FETCH_NEW_ART"  # Replace this with the actual URL scraping logic
    if img_url:
        fetch_new_album_art(img_url)
    else:
        print("[INFO] No new album art found on startup. Using default.")

# Monitor for song changes and update artwork
def monitor_song_changes():
    previous_song = None

    while True:
        with open(track_file, 'r') as file:
            current_song = file.readline().strip()  # Read the first line as the current song

        if current_song != previous_song:
            print(f"[INFO] Song changed to: {current_song}")
            delete_old_artwork()  # Delete old artwork when song changes

            # Insert logic to scrape new album art if available
            img_url = "URL_TO_FETCH_NEW_ART"  # Replace this with the actual URL scraping logic
            if img_url:
                fetch_new_album_art(img_url)  # Fetch the new artwork
            else:
                print("[INFO] No new album art found. Will use default.")

            previous_song = current_song  # Update previous song

        time.sleep(10)  # Check every 10 seconds for song changes

if __name__ == "__main__":
    handle_startup()  # Handle album art on startup
    monitor_song_changes()  # Start monitoring for song changes
