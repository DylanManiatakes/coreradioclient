import subprocess
import os
import http.server
import socketserver
import threading
import time

# Get the directory where the run_client.py script is located
script_directory = os.path.dirname(os.path.abspath(__file__))

# Define paths to the scripts
metadata_script = os.path.join(script_directory, 'metadata.py')
albumart_script = os.path.join(script_directory, 'albumart.py')
recent_songs_script = os.path.join(script_directory, 'log_recent_songs.py')  # New script to log recent songs
PORT = 8080

def run_script(script_path, name):
    try:
        print(f"[INFO] Starting {name} ({script_path})")
        process = subprocess.Popen(['python3', script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return process
    except Exception as e:
        print(f"[ERROR] Failed to run {name}: {e}")

def monitor_process(process, name):
    try:
        for line in iter(process.stdout.readline, b''):
            print(f"[{name} Output]: {line.decode().strip()}")
        process.stdout.close()

        process.wait()
        if process.returncode != 0:
            print(f"[ERROR] {name} process ended with return code {process.returncode}")
            print(f"[{name} Error Output]: {process.stderr.read().decode().strip()}")
    except Exception as e:
        print(f"[ERROR] Error monitoring {name}: {e}")

def start_web_server():
    web_dir = script_directory  # Serve files from the directory where this script is located
    os.chdir(web_dir)

    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"[INFO] Web server running on port {PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[INFO] Web server shutting down...")

def main():
    print("[INFO] Starting Core Radio Client")

    # Run metadata.py, albumart.py, and log_recent_songs.py as separate subprocesses
    metadata_process = run_script(metadata_script, "Metadata")
    albumart_process = run_script(albumart_script, "Album Art")
    recent_songs_process = run_script(recent_songs_script, "Recent Songs")

    # Start threads to monitor the output of each script
    metadata_thread = threading.Thread(target=monitor_process, args=(metadata_process, "Metadata"))
    albumart_thread = threading.Thread(target=monitor_process, args=(albumart_process, "Album Art"))
    recent_songs_thread = threading.Thread(target=monitor_process, args=(recent_songs_process, "Recent Songs"))

    metadata_thread.start()
    albumart_thread.start()
    recent_songs_thread.start()

    # Start the web server in the main thread
    try:
        start_web_server()
    except KeyboardInterrupt:
        print("\n[INFO] Shutting down web server and subprocesses...")
        metadata_process.terminate()
        albumart_process.terminate()
        recent_songs_process.terminate()

    # Wait for threads to finish
    metadata_thread.join()
    albumart_thread.join()
    recent_songs_thread.join()

    print("[INFO] Core Radio Client has been shut down")

if __name__ == "__main__":
    main()
