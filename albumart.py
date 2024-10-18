import os
import time
import requests
import mimetypes
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up the WebDriver (e.g., Chrome)
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode for background execution
chrome_options.add_argument('--no-sandbox')  # Necessary for some environments
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=chrome_options)  # Make sure ChromeDriver is installed and in your PATH

url = "https://coreradio.online/listen"  # Replace with the URL of the webpage

# Get the directory where the script is located
script_directory = os.path.dirname(os.path.abspath(__file__))

# Set the path to `current_track.txt` in the same directory as the script
track_file = os.path.join(script_directory, "current_track.txt")

# Function to get the modification time of the track file
def get_file_mtime(filepath):
    try:
        return os.path.getmtime(filepath)
    except OSError:
        print(f"Error: Cannot access {filepath}")
        return 0  # Return 0 if the file doesn't exist or can't be accessed

# Function to scrape the latest album art immediately
def scrape_album_art():
    try:
        print("Locating album art on the page...")
        scrape_art = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "cachecover"))
        )
        img_element = scrape_art.find_element(By.TAG_NAME, 'img')

        # Wait until the img src is not empty
        img_url = WebDriverWait(driver, 10).until(
            lambda driver: img_element.get_attribute('src') if img_element.get_attribute('src') else None
        )
        print(f"Scraped image URL: {img_url}")

        return img_url

    except Exception as e:
        print(f"Error finding image element or downloading image: {e}")
        return None

# Function to download and save the album art
def download_album_art(img_url):
    if img_url:
        try:
            response = requests.get(img_url)
            content_type = response.headers['Content-Type']
            extension = mimetypes.guess_extension(content_type)
            if not extension:
                extension = '.jpg'  # Default to .jpg if type cannot be determined
            # Save the image as "art.file_extension"
            img_filename = os.path.join(script_directory, f'art{extension}')
            with open(img_filename, 'wb') as handler:
                handler.write(response.content)
            print(f"Album art saved as {img_filename}")
        except requests.exceptions.RequestException as e:
            print(f"Error downloading image: {e}")
    else:
        print("No image URL provided, skipping download.")

try:
    # Open the webpage
    print("Opening the webpage...")
    driver.get(url)
    
    # Scrape album art immediately on script start
    print("Scraping latest album art on startup...")
    previous_img_url = scrape_album_art()
    download_album_art(previous_img_url)

    # Store the previous image URL and file modification time
    previous_mtime = get_file_mtime(track_file)

    print(f"Initial file modification time: {previous_mtime}")
    print(f"Monitoring {track_file} for changes...")

    while True:
        # Get the current modification time of current_track.txt
        current_mtime = get_file_mtime(track_file)

        # Check if the track file has been updated
        if current_mtime != previous_mtime:
            print(f"Detected change in {track_file} (mtime: {current_mtime}), checking for new album art...")
            previous_mtime = current_mtime

            # Scrape and download new album art if the track file has been updated
            img_url = scrape_album_art()
            if img_url != previous_img_url:
                previous_img_url = img_url
                download_album_art(img_url)
            else:
                print("Album art has not changed.")

        # Sleep for 2 seconds before checking the content again
        time.sleep(2)

except Exception as e:
    print(f"An error occurred: {e}")
finally:
    driver.quit()
