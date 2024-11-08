from watchdog import WatchdogManager
import os

if __name__ == "__main__":
    wd_manager = WatchdogManager()

    wd_pid1 = wd_manager.start_watchdog(os.getpid(), "D:\\Games\\Anomaly\\AnomalyLauncher.exe")

    print(f"\n[Principal] Status do WatchDog {wd_pid1}:")
    wd_pid1_status = wd_manager.ping_watchdog(wd_pid1)
    print(wd_pid1_status)
    

    input(f"\nEnter para pingar {wd_pid1}\n")
    
    print(f"\n[Principal] Status do WatchDog {wd_pid1}:")
    wd_pid1_status = wd_manager.ping_watchdog(wd_pid1)
    print(wd_pid1_status)
    
    input(f"\nEnter para encerrar {wd_pid1}\n")
    
    print(f"\n[Principal] Status do WatchDog {wd_pid1}:")
    wd_pid1_status = wd_manager.kill_watchdog(wd_pid1)
    print(wd_pid1_status)
    
    
    

    wd_manager.stop_all_watchdogs()
    print("[Principal] Todos os watchdogs foram finalizados.")