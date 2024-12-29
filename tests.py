import subprocess
import os
import platform

def verify_and_execute(file_path):
    if not os.path.isfile(file_path):
        print(f"'{file_path}' is not a valid file.")
        return 0

    try:
        if os.access(file_path, os.X_OK):
            proc = subprocess.Popen([file_path])
            print(f"'{file_path}' executed successfully.")
            return proc
        else:
            proc = subprocess.Popen(["xdg-open", file_path])
            print(f"'{file_path}' executed successfully via xdg-open.")
            return proc
    except subprocess.CalledProcessError as e:
        print(f"Error when processing '{file_path}': {e}")
    except FileNotFoundError:
        print("The 'xdg-open' command is not available on the system.")
    except Exception as e:
        print(f"An unexpected error has occurred: {e}")
    
    return 0

# Exemplo de uso
caminho1 = "/home/diego/Downloads/Ravenfield Linux/Ravenfield.x86_64"
caminho2 = "/home/diego/Documents/code/py/flet-apps/watchdog/example.txt"
proc = verify_and_execute(caminho1)

print("\n\nProcesso:", proc)
print("PID:", proc.pid)
