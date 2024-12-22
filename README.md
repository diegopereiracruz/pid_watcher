# Watchdog

This repository contains a simple implementation of a watchdog in Python. The `watchdog.py` script monitors a specified directory for any changes and logs these events.

## Features

- Monitor a directory for file system changes
- Log events such as file creation, modification, and deletion

## Installation

To install the required dependencies, run:

```bash
pip install -r requirements.txt
```

## /Usage

Here is an example of how to use the `watchdog.py` script:

```python
import os
import time
import subprocess
import socket
import json

if __name__ == "__main__":
    main_pid = os.getpid()
    exec_path = "path\\to\\exe"
    port = 5000

    # Start the watchdog as a subprocess
    watchdog_process = subprocess.Popen(["python", "watchdog.py", exec_path, str(main_pid), str(port)])

    # Socket configuration for communication
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', port))

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
```

In this example, replace `"path\\to\\exe"` with the path to the executable you want to monitor. The script starts the watchdog as a subprocess and communicates with it using a socket.

## Note

The `main.py` file is not included in the repository. The example above demonstrates how to use the `watchdog.py` script.