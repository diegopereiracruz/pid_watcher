from pid_watcher import PID_Watcher

if __name__ == "__main__":
    exec_path_1 = "C:\\Windows\\system32\\notepad.exe"
    port_1 = 5001

    watcher_client_1 = PID_Watcher(exec_path=exec_path_1, port=port_1)

    watcher_client_1.start_watcher()
    print("watcher_pid: ", watcher_client_1.watcher_process.pid)

    # Example of sending commands
    response = watcher_client_1.send_command("ping")
    print(f"Watcher 1 response: {response}")

    input("Ping watcher (enter)")

    # Example of sending commands
    response = watcher_client_1.send_command("ping")
    print(f"Watcher 1 response: {response}")

    input("Kill watcher (enter)")

    # Send command to kill the watcher
    response = watcher_client_1.send_command("kill")
    print(f"Response to killing watcher 1: {response}")

    watcher_client_1.close()