Core Radio Client
Core Radio Client is a Python-based project that dynamically scrapes song metadata and album art from a radio stream and serves it via a lightweight web page. It automatically updates song information and album art in real-time.

Features
Dynamic Album Art: Scrapes album art from a web page and dynamically updates based on the most recent file.
Song Metadata: Fetches band and track info from current_track.txt.
Web Server: Serves a simple web page showing the current song and band with the latest album art.
Real-time Updates: Automatically detects updates to the current_track.txt file and updates the web page.
Project Structure
albumart.py: Scrapes album art from a webpage, downloads it, and monitors current_track.txt for changes.
metadata.py: Handles fetching song metadata (band and track) from current_track.txt.
app.js: Fetches song data and dynamically updates the album art (supports .jpg, .png, .gif, etc.).
index.html: Displays the current song, band, and album art in a web page.
run_client.py: Runs both albumart.py and metadata.py concurrently while serving the web app via a local HTTP server.
styles.css: Styles the web page layout and visual design.
Requirements
Python 3.x
Google Chrome or Chromium browser
Python Libraries:
selenium
requests
Install the necessary dependencies using:

bash
Copy code
pip install -r requirements.txt
Setup & Usage
Clone the Repository:

bash
Copy code
git clone https://github.com/yourusername/coreradioclient.git
cd coreradioclient
Install Dependencies: Install Python dependencies via the requirements.txt file:

bash
Copy code
pip install -r requirements.txt
Ensure ChromeDriver is Installed:

Download and install ChromeDriver from here.
Make sure it's accessible via your system's PATH.
Run the Application: Use the run_client.py script to start both album art scraping and metadata fetching, and to serve the web app:

bash
Copy code
python run_client.py
Access the Web Page:

Open your browser and navigate to http://localhost:8080 to see the current song, band, and album art.
Customization
Album Art Format:

The script supports multiple album art formats (.jpg, .png, .gif, etc.).
Ensure that art.* files are updated in your project directory, and the script will automatically choose the most recent one.
Web Server Port:

The default port for the local web server is 8080. You can change this by modifying the PORT variable in run_client.py.
Troubleshooting
Error: Selenium ChromeDriver not found:

Ensure that ChromeDriver is installed and correctly set in your system’s PATH.
Album Art Not Updating:

Verify that the correct file extensions are being used for the album art (.jpg, .png, etc.).
Ensure the current_track.txt file is being updated as expected.
License
This project is licensed under the MIT License.

Feel free to modify this README.md to suit any additional details you'd like to include, such as links to your project or further customization options. Let me know if you need any other tweaks!