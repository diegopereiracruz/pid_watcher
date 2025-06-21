# PID_watcher para Monitoramento de Processos

Este projeto implementa um monitorador para monitorar a execução de processos em sistemas Windows e Linux. O watcher é responsável por iniciar um processo, monitorar seu estado e responder a eventos como o término inesperado do processo principal.

## Estrutura do Projeto

- `pid_watcher.py`: Cliente que inicia o watcher e se comunica com ele.
- `pw_win.py`: Implementação do watcher para sistemas Windows.
- `pw_linux.py`: Implementação do watcher para sistemas Linux.

## Requisitos

- Python 3.6 ou superior
- Bibliotecas adicionais: `psutil`, `tkinter` (para Linux), `ctypes` (para Windows)

## Instalação

1. Clone o repositório:
    ```sh
    git clone <URL_DO_REPOSITORIO>
    cd <NOME_DO_REPOSITORIO>
    ```

2. Crie um ambiente virtual e ative-o:
    ```sh
    python -m venv venv
    source venv/bin/activate  # Linux
    .\venv\Scripts\activate  # Windows
    ```

3. Instale as dependências:
    ```sh
    pip install psutil
    ```

## Uso

### Cliente watcher

O cliente `PID_Watcher` em `pid_watcher.py` é responsável por iniciar o watcher e se comunicar com ele.

Exemplo de uso:
```python
from pid_watcher import PID_Watcher

if __name__ == "__main__":
    watcher_client = PID_Watcher(exec_path="C:\\Windows\\system32\\notepad.exe", port=5001)

    watcher_client.start_watcher()
    print("watcher_pid: ", watcher_client.watcher_process.pid)

    # Example of sending commands
    response = watcher_client.send_command("ping")
    print(f"Watcher response: {response}")

    input("Ping watcher (enter)")

    # Example of sending commands
    response = watcher_client.send_command("ping")
    print(f"Watcher response: {response}")

    input("Kill watcher (enter)")

    # Send command to kill the watcher
    response = watcher_client.send_command("kill")
    print(f"Response to killing watcher 1: {response}")

    watcher_client.close()
```