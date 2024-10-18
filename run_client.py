import subprocess
import os
import http.server
import socketserver
import threading

# Define paths to the scripts
script_directory = os.path.dirname(os.path.abspath(__file__))
metadata_script = os.path.join(script_directory, 'metadata.py')
albumart_script = os.path.join(script_directory, 'albumart.py')

# Define web server settings
PORT = 8080

def run_script(script_path):
    try:
        # Start the subprocess to run the script
        process = subprocess.Popen(['python3', script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return process
    except Exception as e:
        print(f"Failed to run {script_path}: {e}")

def monitor_process(process, name):
    try:
        # Continuously monitor the process output
        for line in iter(process.stdout.readline, b''):
            print(f"[{name} Output]: {line.decode().strip()}")
        process.stdout.close()

        # Check for errors
        process.wait()
        if process.returncode != 0:
            print(f"[{name} Error]: Process ended with return code {process.returncode}")
            print(f"[{name} Error Output]: {process.stderr.read().decode().strip()}")
    except Exception as e:
        print(f"Error monitoring {name}: {e}")

def start_web_server():
    web_dir = script_directory  # Serve files from the directory where this script is located
    os.chdir(web_dir)

    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"Serving HTTP on port {PORT}")
        httpd.serve_forever()

def main():
    print("Starting metadata.py and albumart.py...")

    # Run metadata.py and albumart.py as separate subprocesses
    metadata_process = run_script(metadata_script)
    albumart_process = run_script(albumart_script)

    # Start threads to monitor the output of both scripts
    metadata_thread = threading.Thread(target=monitor_process, args=(metadata_process, "Metadata"))
    albumart_thread = threading.Thread(target=monitor_process, args=(albumart_process, "Album Art"))
    
    metadata_thread.start()
    albumart_thread.start()

    # Start the web server in the main thread
    try:
        start_web_server()
    except KeyboardInterrupt:
        print("Shutting down web server and subprocesses...")
        metadata_process.terminate()
        albumart_process.terminate()

if __name__ == "__main__":
    main()
