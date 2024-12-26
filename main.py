import os
import time
import subprocess
import socket
import json

def wait_for_server(host, port, timeout=5):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((host, port))
            return client_socket
        except ConnectionRefusedError:
            time.sleep(0.1)
    raise ConnectionRefusedError(f"Could not connect to server at {host}:{port} within {timeout} seconds")

if __name__ == "__main__":
    main_pid = os.getpid()
    exec_path = "/home/diego/Downloads/Ravenfield Linux/Ravenfield.x86_64"
    port = 5000

    # Start the watchdog as a subprocess
    watchdog_process = subprocess.Popen(["python", "watchdog.py", exec_path, str(main_pid), str(port)])

    # Wait for the server to be ready
    client_socket = wait_for_server('localhost', port)

    # Example of sending commands
    client_socket.sendall(json.dumps("ping").encode('utf-8'))
    response = client_socket.recv(1024)
    string_response = json.loads(response.decode('utf-8'))
    print(f"Watchdog response: {string_response}")
    
    input("Ping watchdog (enter)")
    
    # Example of sending commands
    client_socket.sendall(json.dumps("ping").encode('utf-8'))
    response = client_socket.recv(1024)
    string_response = json.loads(response.decode('utf-8'))
    print(f"Watchdog response: {string_response}")

    input("Kill watchdog (enter)")
    
    # Send command to kill the watchdog
    client_socket.sendall(json.dumps("kill").encode('utf-8'))
    response = client_socket.recv(1024)
    string_response = json.loads(response.decode('utf-8'))
    print(f"Response to killing watchdog: {string_response}")

    client_socket.close()
    watchdog_process.wait()