import time
import ctypes
import psutil
import subprocess
import os
from multiprocessing import Process, Pipe

def watchdog(exec_path, main_pid, conn, timeout=5):
    """Função principal do watchdog que monitora a execução do processo do jogo."""
    try:
        start_time = int(time.time())
        proc = subprocess.Popen(exec_path)
        exec_pid = proc.pid
        wd_pid = os.getpid()
        
        print(f"[Watchdog {wd_pid}] Processo {exec_pid} iniciado para {exec_path}")
        
        while proc.poll() is None:
            if not psutil.pid_exists(main_pid):
                ctypes.windll.user32.MessageBoxW(0, "Ao fechar essa janela o jogo será encerrado.\nSalve o seu progresso antes de confirmar.", "O programa principal foi encerrado!", 0)
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
                    end_time = int(time.time())
                    conn.send({
                        "status": "terminated",
                        "main_pid": main_pid,
                        "exec_pid": exec_pid,
                        "wd_pid": wd_pid,
                        "start_time": start_time,
                        "end_time": end_time,
                        "total_runtime": end_time - start_time
                    })
                    proc.terminate()
                    conn.close()
                    return
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
        conn.send({"status": "error", "message": str(e)})
    finally:
        if proc and proc.poll() is None:
            proc.terminate()
        conn.close()

class WatchdogManager:
    def __init__(self):
        self.watchdogs = {}
        self.last_ping = {}

    def _send_command(self, wd_pid, command):
        watchdog = self.watchdogs.get(wd_pid)
        if not watchdog:
            self._handle_disconnected_watchdog(wd_pid)
            return {"status": "not_found", "message": f"Watchdog {wd_pid} não está mais ativo"}
        
        conn = watchdog["connection"]
        if conn.closed:
            self._cleanup_watchdog(wd_pid)
            self._handle_disconnected_watchdog(wd_pid)
            return {"status": "not_found", "message": f"Watchdog {wd_pid} não está mais ativo"}
        
        try:
            conn.send(command)
            start = time.time()
            while not conn.poll() and time.time() - start < 5:  # Timeout de 5 segundos
                time.sleep(0.1)
            return conn.recv() if conn.poll() else {"status": "timeout", "message": "No response from watchdog"}
        except BrokenPipeError:
            self._handle_disconnected_watchdog(wd_pid)
            self._cleanup_watchdog(wd_pid)
            return {"status": "error", "message": "Conexão com o watchdog encerrada"}

    def _cleanup_watchdog(self, wd_pid):
        if wd_pid in self.watchdogs:
            watchdog = self.watchdogs.pop(wd_pid)
            conn = watchdog["connection"]
            conn.close()
            print(f"[Manager] Watchdog {wd_pid} finalizado e conexão fechada.")
        self.last_ping.pop(wd_pid, None)

    def _handle_disconnected_watchdog(self, wd_pid):
        last_ping = self.last_ping.get(wd_pid)
        if last_ping and psutil.pid_exists(last_ping.get("exec_pid", 0)):
            ctypes.windll.user32.MessageBoxW(
                0,
                "O tempo de execução e outros dados de desempenho coletados não poderão ser salvos, "
                "além de recursos adicionais que não estarão disponíveis durante o jogo.",
                "A conexão com o monitoramento do jogo foi perdida!",
                0
            )
            print(f"[Manager] O programa está executando sem o watchdog responsável")
        self.watchdogs.pop(wd_pid, None)
        self.last_ping.pop(wd_pid, None)

    def start_watchdog(self, main_pid, exec_path):
        parent_conn, child_conn = Pipe()
        wd = Process(target=watchdog, args=(exec_path, main_pid, child_conn))
        wd.start()
        self.watchdogs[wd.pid] = {"process": wd, "connection": parent_conn, "exec_path": exec_path}
        print(f"[Manager] Watchdog {wd.pid} iniciado para {exec_path}")
        return wd.pid

    def ping_watchdog(self, wd_pid):
        response = self._send_command(wd_pid, "ping")
        if response.get("status") != "not_found":
            self.last_ping[wd_pid] = response
        else:
            self._handle_disconnected_watchdog(wd_pid)
        return response

    def kill_watchdog(self, wd_pid):
        response = self._send_command(wd_pid, "kill")
        if response.get("status") == "not_found":
            self._handle_disconnected_watchdog(wd_pid)
        return response

    def ping_all_watchdogs(self):
        results = {}
        for wd_pid in list(self.watchdogs.keys()):
            response = self.ping_watchdog(wd_pid)
            results[wd_pid] = response
        return results

    def kill_all_watchdogs(self):
        results = {}
        for wd_pid in list(self.watchdogs.keys()):
            response = self.kill_watchdog(wd_pid)
            results[wd_pid] = response
        return results

    def stop_all_watchdogs(self):
        for wd_pid in list(self.watchdogs.keys()):
            self.kill_watchdog(wd_pid)
        print("[Manager] Todos os watchdogs foram finalizados.")
