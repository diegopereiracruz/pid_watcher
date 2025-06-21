import os
import time
import subprocess
import socket
import json

class PID_Watcher:
    def __init__(self, exec_path, port, timeout=5):
        self.exec_path = exec_path
        self.port = port
        self.timeout = timeout
        self.main_pid = os.getpid()
        self.watcher_process = None
        self.client_socket = None


    def start_watcher(self):
        try:
            file_path = os.path.dirname(__file__)
            script_name = "pw_win.py" if os.name == 'nt' else "pw_linux.py"
            script_path = os.path.join(file_path, script_name)
            self.watcher_process = subprocess.Popen(["python", script_path, self.exec_path, str(self.main_pid), str(self.port)])
            self.client_socket = self.wait_for_server('localhost', self.port)
        except Exception as e:
            raise RuntimeError(f"Failed to start watcher: {e}")


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
        if self.watcher_process:
            self.watcher_process.terminate()
            self.watcher_process.wait()