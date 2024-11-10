import time
import subprocess
import os
import ctypes
import psutil
from multiprocessing import Process, Pipe

def watchdog(exec_path, main_pid, conn, timeout=5):
    try:
        start_time = int(time.time())
        proc = subprocess.Popen(exec_path)
        exec_pid = proc.pid
        wd_pid = os.getpid()
        
        print(f"[Watchdog {wd_pid}] Processo {exec_pid} iniciado para {exec_path}")
        
        while proc.poll() is None:
            if not psutil.pid_exists(main_pid):
                ctypes.windll.user32.MessageBoxW(0, "Ao fechar essa janela o jogo será encerrado.\nSalve o seu progresso no jogo antes de fechar.", "O programa principal foi encerrado!", 0)
                proc.terminate()
                conn.close()
                return
            
            if conn.poll():
                signal = conn.recv()
                if signal == "ping":
                    uptime = int(time.time()) - start_time
                    conn.send({
                        "status": "running",
                        "main_pid": main_pid,
                        "exec_pid": exec_pid,
                        "wd_pid": wd_pid,
                        "start_time": start_time,
                        "uptime": uptime
                    })
                elif signal == "kill":
                    proc.terminate()
                    break
            time.sleep(1)

        end_time = int(time.time())
        
        print(f"[Watchdog {wd_pid}] Auto-exclusão em 5 segundos. Aguardando sinal...")
        waiting_start = time.time()
        while time.time() - waiting_start < timeout:
            if conn.poll():  # Checa se recebeu um sinal
                conn.send({
                    "status": "terminated",
                    "main_pid": main_pid,
                    "exec_pid": exec_pid,
                    "wd_pid": wd_pid,
                    "start_time": start_time,
                    "end_time": end_time,
                    "total_runtime": end_time - start_time
                })
                break
            time.sleep(0.1)
        print(f"[Watchdog {wd_pid}] Encerrado.")
    except Exception as e:
        if conn and not conn.closed:
            conn.send({"status": "error", "message": str(e)})
    finally:
        if proc and proc.poll() is None:
            proc.terminate()
        if conn and not conn.closed:
            conn.close()



class WatchdogManager:
    def __init__(self):
        self.watchdogs = {}  # Dicionário para armazenar watchdogs ativos
        self.last_ping = {}

    def start_watchdog(self, main_pid, exec_path):
        parent_conn, child_conn = Pipe()
        wd = Process(target=watchdog, args=(exec_path, main_pid, child_conn))
        wd.start()
        
        # Armazena o watchdog e a conexão no dicionário
        self.watchdogs[wd.pid] = {
            "process": wd,
            "connection": parent_conn,
            "exec_path": exec_path
        }
        
        self.last_ping[wd.pid] = {
            "wd_pid": wd.pid,
        }
        
        
        print(f"[Manager] Watchdog {wd.pid} iniciado para {exec_path}")
        return wd.pid  # Retorna o ID do watchdog (PID do processo watchdog)

    def ping_watchdog(self, wd_pid):
        watchdog = self.watchdogs.get(wd_pid)
        last_ping = self.last_ping.get(wd_pid)
        if watchdog:
            conn = watchdog["connection"]
            if not conn.closed:
                try:
                    conn.send("ping")
                    # Espera a resposta do watchdog com timeout para evitar bloqueio
                    start = int(time.time())
                    while not conn.poll() and (int(time.time()) - start) < 5:  # Timeout de 5 segundos
                        print("ping timeout...")
                        time.sleep(0.1)
                    if conn.poll():
                        response = conn.recv()
                        self.last_ping[wd_pid] = response
                        return response
                except BrokenPipeError:
                    print(f"[Manager] Conexão com o watchdog {wd_pid} encerrada.")
                    if psutil.pid_exists(last_ping["exec_pid"]):
                        print(f"[Manager] O programa está executando sem o watchdog responsável")
                        ctypes.windll.user32.MessageBoxW(0, f"O tempo de execução e outros dados de desempenho coletados não poderão ser salvos, além de recursos adicionais que não estarão disponíveis durante o jogo.", "A conexão com o monitoramento do jogo perdida!", 0)
            # Remove watchdog finalizado
            self.watchdogs.pop(wd_pid, None)
            self.last_ping.pop(wd_pid, None)
        return {"status": "not_found", "message": f"Watchdog {wd_pid} não está mais ativo"}

    def kill_watchdog(self, wd_pid):
        watchdog = self.watchdogs.get(wd_pid)
        last_ping = self.last_ping.get(wd_pid)
        if watchdog:
            conn = watchdog["connection"]
            if not conn.closed:
                try:
                    conn.send("kill")
                    # Aguarda resposta do watchdog
                    start = int(time.time())
                    while not conn.poll() and (int(time.time()) - start) < 5:
                        print("ping timeout...")
                        time.sleep(0.1)
                    if conn.poll():
                        response = conn.recv()
                        self.last_ping[wd_pid] = response
                        return response
                except BrokenPipeError:
                    print(f"[Manager] Conexão com o watchdog {wd_pid} encerrada.")
                    if psutil.pid_exists(last_ping["exec_pid"]):
                        print(f"[Manager] O programa está executando sem o watchdog responsável")
                        ctypes.windll.user32.MessageBoxW(0, f"O tempo de execução e outros dados de desempenho coletados não poderão ser salvos, além de recursos adicionais que não estarão disponíveis durante o jogo.", "A conexão com o monitoramento do jogo perdida!", 0)
            # Remove watchdog finalizado
            self.watchdogs.pop(wd_pid, None)
            self.last_ping.pop(wd_pid, None)
        return {"status": "not_found", "message": f"Watchdog {wd_pid} não está mais ativo"}

    def ping_all_watchdogs(self):
        results = {}
        for wd_pid, watchdog in list(self.watchdogs.items()):
            last_ping = self.last_ping.get(wd_pid)
            conn = watchdog["connection"]
            if not conn.closed:
                try:
                    conn.send("ping")
                    # Aguarda resposta com timeout
                    start = int(time.time())
                    while not conn.poll() and (int(time.time()) - start) < 5:
                        print("ping timeout...")
                        time.sleep(0.1)
                    if conn.poll():
                        last_ping[wd_pid] = conn.recv()
                        results[wd_pid] = conn.recv()
                except BrokenPipeError:
                    print(f"[Manager] Conexão com o watchdog {wd_pid} encerrada.")
                    if psutil.pid_exists(last_ping["exec_pid"]):
                        print(f"[Manager] O programa está executando sem o watchdog responsável")
                        ctypes.windll.user32.MessageBoxW(0, f"O tempo de execução e outros dados de desempenho coletados não poderão ser salvos, além de recursos adicionais que não estarão disponíveis durante o jogo.", "A conexão com o monitoramento do jogo perdida!", 0)
                    self.watchdogs.pop(wd_pid, None)  # Remove watchdog finalizado
                    self.last_ping.pop(wd_pid, None)
            else:
                results[wd_pid] = {"status": "not_found", "message": f"Watchdog {wd_pid} não está mais ativo"}
        return results

    def kill_all_watchdogs(self):
        results = {}
        for wd_pid, watchdog in list(self.watchdogs.items()):
            last_ping = self.last_ping.get(wd_pid)
            conn = watchdog["connection"]
            if not conn.closed:
                try:
                    conn.send("kill")
                    # Aguarda resposta com timeout
                    start = int(time.time())
                    while not conn.poll() and (int(time.time()) - start) < 5:
                        print("ping timeout...")
                        time.sleep(0.1)
                    if conn.poll():
                        last_ping[wd_pid] = conn.recv()
                        results[wd_pid] = conn.recv()
                except BrokenPipeError:
                    print(f"[Manager] Conexão com o watchdog {wd_pid} encerrada.")
                    if psutil.pid_exists(last_ping["exec_pid"]):
                        print(f"[Manager] O programa está executando sem o watchdog responsável")
                        ctypes.windll.user32.MessageBoxW(0, f"O tempo de execução e outros dados de desempenho coletados não poderão ser salvos, além de recursos adicionais que não estarão disponíveis durante o jogo.", "A conexão com o monitoramento do jogo perdida!", 0)
                    self.watchdogs.pop(wd_pid, None)  # Remove watchdog finalizado
                    self.last_ping.pop(wd_pid, None)
            else:
                results[wd_pid] = {"status": "not_found", "message": f"Watchdog {wd_pid} não está mais ativo"}
        return results

    def stop_all_watchdogs(self):
        """Finaliza todos os watchdogs e limpa o dicionário."""
        for wd_pid, watchdog in list(self.watchdogs.items()):
            conn = watchdog["connection"]
            process = watchdog["process"]
            
            if process.is_alive():  # Verifica se o processo ainda está ativo
                try:
                    if not conn.closed:
                        conn.send("kill")  # Envia sinal para finalizar o watchdog
                        
                        # Aguarda o processo responder ou encerrar
                        start = int(time.time())
                        while process.is_alive() and (int(time.time()) - start) < 5:
                            print("ping timeout...")
                            time.sleep(0.1)
                    
                    # Força o término se o processo não responder em 5 segundos
                    if process.is_alive():
                        process.terminate()
                        print(f"[Manager] Watchdog {wd_pid} forçado a encerrar.")

                except BrokenPipeError:
                    print(f"[Manager] Conexão com o watchdog {wd_pid} já encerrada.")
                finally:
                    # Garante que o processo terminou
                    process.join()
                    conn.close()
                    print(f"[Manager] Watchdog {wd_pid} finalizado e conexão fechada.")

            # Remove o watchdog finalizado do dicionário
            self.watchdogs.pop(wd_pid, None)
            self.last_ping.pop(wd_pid, None)

        print("[Manager] Todos os watchdogs foram finalizados.")