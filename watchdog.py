import os
import time
import subprocess
import psutil
import ctypes
import socket
import json

def watchdog(exec_path, main_pid, port, timeout=5):
    """Função principal do watchdog que monitora a execução do processo do jogo."""
    try:
        start_time = int(time.time())
        proc = subprocess.Popen(exec_path)
        exec_pid = proc.pid
        wd_pid = os.getpid()
        
        print(f"[Watchdog {wd_pid}] Processo {exec_pid} iniciado para {exec_path}")
        
        # Configuração do socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('localhost', port))
        server_socket.listen(1)
        conn, _ = server_socket.accept()
        
        while proc.poll() is None:
            if not psutil.pid_exists(main_pid):
                response = ctypes.windll.user32.MessageBoxW(
                    0,
                    "Nenhum dado de progresso será salvo.\n\nDeseja encerrar a aplicação em execução?",
                    "O programa principal foi encerrado de forma inesperada!",
                    1 | 0x30 | 0x1  # MB_OKCANCEL | MB_ICONWARNING | MB_DEFBUTTON1
                )
                if response == 1:  # IDOK
                    proc.terminate()
                    conn.sendall(json.dumps({
                        "status": "terminated",
                        "main_pid": main_pid,
                        "exec_pid": exec_pid,
                        "wd_pid": wd_pid,
                        "start_time": start_time,
                        "end_time": int(time.time()),
                        "total_runtime": int(time.time()) - start_time
                    }).encode('utf-8'))
                elif response == 2:  # IDCANCEL
                    conn.sendall(json.dumps({
                        "status": "watchdog_cancelled",
                        "main_pid": main_pid,
                        "exec_pid": exec_pid,
                        "wd_pid": wd_pid,
                        "start_time": start_time,
                        "end_time": int(time.time()),
                        "total_runtime": int(time.time()) - start_time
                    }).encode('utf-8'))
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
                        conn.sendall(json.dumps({
                            "status": "killed",
                            "main_pid": main_pid,
                            "exec_pid": exec_pid,
                            "wd_pid": wd_pid,
                            "start_time": start_time,
                            "end_time": int(time.time()),
                            "total_runtime": int(time.time()) - start_time
                        }).encode('utf-8'))
                        break
            except socket.timeout:
                pass
            except ConnectionResetError:
                if not psutil.pid_exists(main_pid):
                    response = ctypes.windll.user32.MessageBoxW(
                        0,
                        "Nenhum dado de progresso será salvo.\n\nEscolha uma opção:",
                        "O programa principal foi encerrado de forma inesperada!",
                        1 | 0x30 | 0x1  # MB_OKCANCEL | MB_ICONWARNING | MB_DEFBUTTON1
                    )
                    if response == 1:  # IDOK
                        proc.terminate()
                    break
        print(f"[Watchdog {wd_pid}] Encerrado.")
    except Exception as e:
        try:
            conn.sendall(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))
        except BrokenPipeError:
            print(f"[Watchdog {wd_pid}] Erro ao enviar mensagem de erro: {e}")
    finally:
        conn.close()
        server_socket.close()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Watchdog para monitoramento de processos.")
    parser.add_argument("exec_path", help="Caminho para o executável a ser monitorado.")
    parser.add_argument("main_pid", type=int, help="PID do processo principal.")
    parser.add_argument("port", type=int, help="Porta para comunicação.")
    args = parser.parse_args()

    watchdog(args.exec_path, args.main_pid, args.port)