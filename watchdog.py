import os
import time
import subprocess
import socket
import json

class WatchdogClient:
    def __init__(self, exec_path, port, timeout=5):
        self.exec_path = exec_path
        self.port = port
        self.timeout = timeout
        self.main_pid = os.getpid()
        self.watchdog_process = None
        self.client_socket = None

    def start_watchdog(self):
        try:
            script_name = "watchdog-win.py" if os.name == 'nt' else "watchdog-linux.py"
            self.watchdog_process = subprocess.Popen(["python", script_name, self.exec_path, str(self.main_pid), str(self.port)])
            self.client_socket = self.wait_for_server('localhost', self.port)
        except Exception as e:
            raise RuntimeError(f"Failed to start watchdog: {e}")

    def wait_for_server(self, host, port):
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect((host, port))
                return client_socket
            except ConnectionRefusedError:
                time.sleep(0.1)
            except OSError as e:
                if e.errno == 98:  # Address already in use
                    raise OSError(f"Port {port} is already in use")
                else:
                    raise e
        raise ConnectionRefusedError(f"Could not connect to server at {host}:{port} within {self.timeout} seconds")

    def send_command(self, command):
        if not self.client_socket:
            raise ConnectionError("Client socket is not connected")
        try:
            self.client_socket.sendall(json.dumps(command).encode('utf-8'))
            response = self.client_socket.recv(1024)
            return json.loads(response.decode('utf-8'))
        except Exception as e:
            raise RuntimeError(f"Failed to send command: {e}")

    def close(self):
        if self.client_socket:
            try:
                self.client_socket.close()
            except Exception:
                pass
        if self.watchdog_process:
            self.watchdog_process.terminate()
            self.watchdog_process.wait()


# if __name__ == "__main__":
#     exec_path_1 = "path/to/executable"
#     port_1 = 5001

#     watchdog_client_1 = WatchdogClient(exec_path_1, port_1)

#     watchdog_client_1.start_watchdog()
#     print("watchdog_pid: ", watchdog_client_1.watchdog_process.pid)

#     # Example of sending commands
#     response = watchdog_client_1.send_command("ping")
#     print(f"Watchdog 1 response: {response}")

#     input("Ping watchdog (enter)")

#     # Example of sending commands
#     response = watchdog_client_1.send_command("ping")
#     print(f"Watchdog 1 response: {response}")

#     input("Kill watchdog (enter)")

#     # Send command to kill the watchdog
#     response = watchdog_client_1.send_command("kill")
#     print(f"Response to killing watchdog 1: {response}")

#     watchdog_client_1.close()