import subprocess
import time
#import pyyaml as yaml
import os
import argparse

def get_ffmpeg_metadata(stream_url, verbose=False):
    # Run ffmpeg to fetch metadata from the stream
    command = ['ffmpeg', '-i', stream_url, '-f', 'ffmetadata', '-']
    
    if verbose:
        print(f"Running command: {' '.join(command)}")

    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if verbose:
        print(f"FFmpeg output:\n{result.stdout}")
        print(f"FFmpeg error (if any):\n{result.stderr}")
    
    if result.returncode != 0:
        print("Error while running ffmpeg. Please check the stream URL and ffmpeg setup.")
    
    return result.stdout

# Function to parse and split StreamTitle into Band and Track
def extract_band_and_track(metadata, verbose=False):
    if verbose:
        print("Extracting band and track info from metadata...")

    for line in metadata.splitlines():
        if verbose:
            print(f"Processing line: {line}")

        if line.startswith("StreamTitle"):
            # Extract the track info after 'StreamTitle='
            track_info = line.split('=', 1)[1].strip()

            # Assume it's in the format "Band - Track"
            if " - " in track_info:
                band, track = track_info.split(" - ", 1)
                return band.strip(), track.strip()
            else:
                return "Unknown", "Unknown"
    
    return "No metadata available", ""

# Function to write to a .txt file
def write_to_text_file(band, track, verbose=False):
    text_file_path = os.path.expanduser("current_track.txt")
    with open(text_file_path, "w") as text_file:
        text_file.write(f"Band: {band}\n")
        text_file.write(f"Track: {track}\n")
    if verbose:
        print(f"Updated text file at: {text_file_path}")

# Function to write to a .yaml file
# def write_to_yaml_file(band, track, verbose=False):
#     yaml_file_path = os.path.expanduser("current_track.yaml")
#     data = {
#         'Band': band,
#         'Track': track
#     }
#     with open(yaml_file_path, "w") as yaml_file:
#         yaml.dump(data, yaml_file)
#     if verbose:
#         print(f"Updated YAML file at: {yaml_file_path}")


# Main function to loop and fetch metadata
def main():
    # Parse command-line arguments for verbose mode
    parser = argparse.ArgumentParser(description="Icecast Metadata Fetcher")
    parser.add_argument('-v', '--verbose', action='store_true', help="Enable verbose mode for debugging")
    args = parser.parse_args()

    stream_url = 'http://serv.coreradio.online:8000/coreradio'
    
    last_track_info = None  # To track if the song has changed
    try:
        while True:
            # Fetch metadata
            metadata = get_ffmpeg_metadata(stream_url, verbose=args.verbose)
            
            # Extract current band and track info
            band, track = extract_band_and_track(metadata, verbose=args.verbose)
            track_info = f"{band} - {track}"
            
            # Only update files if the track has changed
            if track_info != last_track_info:
                if args.verbose:
                    print(f"New track detected: Band: {band}, Track: {track}")
                
                # Write to both text and yaml files
                write_to_text_file(band, track, verbose=args.verbose)
                #write_to_yaml_file(band, track, verbose=args.verbose)
                
                last_track_info = track_info
            
            # Sleep for 10 seconds before checking again
            time.sleep(10)

    except KeyboardInterrupt:
        print("\nExiting the loop.")

if __name__ == "__main__":
    print("Current Working Directory:", os.getcwd())  # Check where the script is running
    main()
