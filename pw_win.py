import os
import time
import subprocess
import psutil
import ctypes
import socket
import json


def show_message_box():
    response = ctypes.windll.user32.MessageBoxW(
        0,
        "Nenhum dado de progresso será salvo.\n\nDeseja encerrar a aplicação em execução?",
        "O programa principal foi encerrado de forma inesperada!",
        1 | 0x30 | 0x1  # MB_OKCANCEL | MB_ICONWARNING | MB_DEFBUTTON1
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


def watcher(exec_path, main_pid, port):
    """Função principal do watcher que monitora a execução do processo do jogo."""
    try:
        if not os.path.isfile(exec_path):
            conn.sendall(json.dumps({
                "status": "error",
                "message": f"Failed to execute '{exec_path}'"
            }).encode('utf-8'))
            return
        
        # Configuração do socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('localhost', port))
        server_socket.listen(1)
        conn, _ = server_socket.accept()
        
        start_time = int(time.time())
        proc = subprocess.Popen(exec_path)
        exec_pid = proc.pid
        watcher_pid = os.getpid()

        print(f"[Watcher {watcher_pid}] Processo {exec_pid} iniciado para {exec_path}")

        while proc.poll() is None:
            if not psutil.pid_exists(main_pid):
                response = show_message_box()
                if response == 1:  # IDOK
                    proc.terminate()
                    send_status(conn, "terminated", main_pid, exec_pid, watcher_pid, start_time, int(time.time()))
                else:  # IDCANCEL
                    send_status(conn, "watcher_cancelled", main_pid, exec_pid, watcher_pid, start_time, int(time.time()))
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
                            "watcher_pid": watcher_pid,
                            "start_time": start_time,
                            "uptime": uptime
                        }).encode('utf-8'))
                    elif signal == "kill":
                        proc.terminate()
                        send_status(conn, "killed", main_pid, exec_pid, watcher_pid, start_time, int(time.time()))
                        break
            except socket.timeout:
                pass
            except ConnectionResetError:
                if not psutil.pid_exists(main_pid):
                    response = show_message_box()
                    if response == 1:  # IDOK
                        proc.terminate()
                    break
        print(f"[Watcher {watcher_pid}] Encerrado.")
    except Exception as e:
        try:
            conn.sendall(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))
        except BrokenPipeError:
            print(f"[Watcher {watcher_pid}] Erro ao enviar mensagem de erro: {e}")
    finally:
        conn.close()
        server_socket.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Watcher para monitoramento de processos.")
    parser.add_argument("exec_path", help="Caminho para o executável a ser monitorado.")
    parser.add_argument("main_pid", type=int, help="PID do processo principal.")
    parser.add_argument("port", type=int, help="Porta para comunicação.")
    args = parser.parse_args()

    watcher(args.exec_path, args.main_pid, args.port)