import os
import time

# Paths to the track files
script_directory = os.path.dirname(os.path.abspath(__file__))
current_track_file = os.path.join(script_directory, "current_track.txt")
last10_file = os.path.join(script_directory, "last10.txt")

# Function to get current song info from current_track.txt
def get_current_song():
    try:
        with open(current_track_file, 'r') as file:
            lines = file.readlines()
            band = ''
            track = ''
            for line in lines:
                if line.startswith('Band:'):
                    band = line.replace('Band:', '').strip()
                elif line.startswith('Track:'):
                    track = line.replace('Track:', '').strip()
            if band and track:
                return f"{band} - {track}"
    except Exception as e:
        print(f"[ERROR] Failed to read {current_track_file}: {e}")
    return None

# Function to update last10.txt with the new song (after song changes)
def update_last10(previous_song):
    if not previous_song:
        return

    # Read the current last10.txt file
    try:
        if os.path.exists(last10_file):
            with open(last10_file, 'r') as file:
                recent_songs = file.readlines()
        else:
            recent_songs = []
    except Exception as e:
        print(f"[ERROR] Failed to read {last10_file}: {e}")
        recent_songs = []

    # Clean and remove duplicates
    recent_songs = [song.strip() for song in recent_songs if song.strip()]
    if previous_song not in recent_songs:  # Avoid duplicates
        recent_songs.insert(0, previous_song)  # Add the previous song to the top

    # Keep only the last 10 songs
    recent_songs = recent_songs[:10]

    # Write the updated list back to last10.txt
    try:
        with open(last10_file, 'w') as file:
            for song in recent_songs:
                file.write(song + '\n')
    except Exception as e:
        print(f"[ERROR] Failed to write to {last10_file}: {e}")

# Function to monitor current_track.txt for changes and log previous song
def monitor_current_track():
    last_mtime = 0  # Initialize last modification time to 0
    previous_song = None  # Store the previous song in memory

    while True:
        try:
            current_mtime = os.path.getmtime(current_track_file)
            if current_mtime != last_mtime:
                last_mtime = current_mtime  # Update the modification time
                current_song = get_current_song()  # Get the current song

                # If a new song is detected (i.e., song has changed)
                if current_song != previous_song and previous_song is not None:
                    print(f"[INFO] Song changed. Logging previous song: {previous_song}")
                    update_last10(previous_song)  # Log the previous song
                previous_song = current_song  # Update the previous song to the current one

            time.sleep(2)  # Check for updates every 2 seconds
        except Exception as e:
            print(f"[ERROR] Error monitoring {current_track_file}: {e}")
            time.sleep(5)

if __name__ == "__main__":
    print("[INFO] Monitoring current_track.txt for updates...")
    monitor_current_track()
