from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
import mimetypes
import os

# Path where album art files are saved
script_directory = os.path.dirname(os.path.abspath(__file__))
track_file = os.path.join(script_directory, "current_track.txt")

# Set up the Selenium WebDriver (e.g., Chrome)
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode (no UI)
driver = webdriver.Chrome(options=chrome_options)

url = "https://coreradio.online/listen"  # Replace with the URL of the webpage

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

# Function to fetch the album art using Selenium
def fetch_new_album_art():
    try:
        # Open the webpage
        driver.get(url)

        # Wait until the album art image element is found
        scrape_art = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "cachecover"))
        )
        img_element = scrape_art.find_element(By.TAG_NAME, 'img')

        # Get the src attribute of the image element (URL of the album art)
        img_url = img_element.get_attribute('src')
        print(f"[INFO] Album art URL found: {img_url}")

        # Now, download the album art using the image URL
        response = requests.get(img_url)
        content_type = response.headers['Content-Type']
        extension = mimetypes.guess_extension(content_type)
        if not extension:
            extension = '.jpg'  # Default to .jpg if type cannot be determined

        # Save the image
        art_file_path = os.path.join(script_directory, f'art{extension}')
        with open(art_file_path, 'wb') as handler:
            handler.write(response.content)
        print(f"[INFO] New album art downloaded and saved as: art{extension}")
        return True

    except Exception as e:
        print(f"[ERROR] Error fetching album art with Selenium: {e}")
        return False

# Monitor for song changes and update artwork
def monitor_song_changes():
    previous_song = None
    last_mod_time = None

    while True:
        current_mod_time = os.path.getmtime(track_file)

        with open(track_file, 'r') as file:
            current_song = file.readline().strip()  # Read the first line as the current song

        # Check if the song has changed by modification time of current_track.txt
        if current_mod_time != last_mod_time:
            print(f"[INFO] Song changed to: {current_song} at {time.ctime(current_mod_time)}")

            # Delay before fetching new artwork
            time.sleep(2)

            # Delete old artwork first before attempting to fetch new art
            delete_old_artwork()

            # Fetch new album art using Selenium
            fetched = fetch_new_album_art()
            if not fetched:
                print("[INFO] No new album art found. Using default.")

            # Update previous song and modification time
            previous_song = current_song
            last_mod_time = current_mod_time

        time.sleep(10)  # Check every 10 seconds for song changes

if __name__ == "__main__":
    try:
        monitor_song_changes()  # Start monitoring for song changes
    except Exception as e:
        print(f"[ERROR] An error occurred in monitor_song_changes: {e}")
    finally:
        driver.quit()  # Make sure to quit the driver when done
