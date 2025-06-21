import os
import time
import subprocess
import psutil
import socket
import json
import tkinter
from tkinter import messagebox


def show_message_box():
    root = tkinter.Tk()
    root.withdraw()  # Esconde a janela principal
    response = messagebox.askokcancel(
        "O programa principal foi encerrado de forma inesperada!",
        "Nenhum dado de progresso será salvo.\n\nDeseja encerrar a aplicação em execução?"
    )
    return response


def send_status(conn, status, main_pid, exec_pid, watcher_pid, start_time, end_time=None):
    message = {
        "status": status,
        "main_pid": main_pid,
        "exec_pid": exec_pid,
        "watcher_pid": watcher_pid,
        "start_time": start_time,
        "end_time": end_time,
        "total_runtime": (end_time - start_time) if end_time else None
    }
    conn.sendall(json.dumps(message).encode('utf-8'))


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


def watcher(file_path, main_pid, port):
    """Função principal do watcher que monitora a execução do processo do jogo."""
    server_socket = None
    conn = None
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('localhost', port))
        server_socket.listen(1)
        conn, _ = server_socket.accept()

        start_time = int(time.time())
        proc = verify_and_execute(file_path)
        if proc == 0:
            raise Exception(f"Failed to execute '{file_path}'")
        exec_pid = proc.pid if hasattr(proc, 'pid') else None
        if exec_pid is None:
            raise Exception(f"Failed to retrieve PID for '{file_path}'")
        wd_pid = os.getpid()
        
        print(f"[Watcher {wd_pid}] Processo {exec_pid} iniciado para {file_path}")
        
        while proc.poll() is None:
            if not psutil.pid_exists(main_pid):
                response = show_message_box()
                if response:
                    proc.terminate()
                    send_status(conn, "terminated", main_pid, exec_pid, wd_pid, start_time, int(time.time()))
                else:
                    send_status(conn, "watcher_cancelled", main_pid, exec_pid, wd_pid, start_time, int(time.time()))
                break
            
            conn.settimeout(0.1)
            try:
                data = conn.recv(1024)
                if data:
                    signal = json.loads(data.decode('utf-8'))
                    if signal == "ping":
                        uptime = int(time.time()) - start_time
                        conn.sendall(json.dumps({
                            "status": "running",
                            "main_pid": main_pid,
                            "exec_pid": exec_pid,
                            "wd_pid": wd_pid,
                            "start_time": start_time,
                            "uptime": uptime
                        }).encode('utf-8'))
                    elif signal == "kill":
                        proc.terminate()
                        send_status(conn, "killed", main_pid, exec_pid, wd_pid, start_time, int(time.time()))
                        break
            except socket.timeout:
                pass
            except ConnectionResetError:
                if not psutil.pid_exists(main_pid):
                    response = show_message_box()
                    if response:
                        proc.terminate()
                    break
        print(f"[Watcher {wd_pid}] Encerrado.")
    except Exception as e:
        try:
            if conn:
                conn.sendall(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))
            else:
                print(f"Error: {e}")
        except BrokenPipeError:
            print(f"[Watcher {wd_pid}] Erro ao enviar mensagem de erro: {e}")
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass
        try:
            if server_socket:
                server_socket.close()
        except Exception:
            pass


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Watcher para monitoramento de processos.")
    parser.add_argument("exec_path", help="Caminho para o executável a ser monitorado.")
    parser.add_argument("main_pid", type=int, help="PID do processo principal.")
    parser.add_argument("port", type=int, help="Porta para comunicação.")
    args = parser.parse_args()

    watcher(args.exec_path, args.main_pid, args.port)