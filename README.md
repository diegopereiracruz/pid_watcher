# Watchdog para Monitoramento de Processos

Este projeto implementa um watchdog para monitorar a execução de processos em sistemas Windows e Linux. O watchdog é responsável por iniciar um processo, monitorar seu estado e responder a eventos como o término inesperado do processo principal.

## Estrutura do Projeto

- `main.py`: Cliente que inicia o watchdog e se comunica com ele.
- `watchdog-win.py`: Implementação do watchdog para sistemas Windows.
- `watchdog-linux.py`: Implementação do watchdog para sistemas Linux.

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

### Cliente Watchdog

O cliente [WatchdogClient](http://_vscodecontentref_/1) em [main.py](http://_vscodecontentref_/2) é responsável por iniciar o watchdog e se comunicar com ele.

Exemplo de uso:
```python
from watchdog import WatchdogClient

exec_path = "caminho/para/executavel"
port = 5001

watchdog_client = WatchdogClient(exec_path, port)
watchdog_client.start_watchdog()

# Enviar comandos para o watchdog
response = watchdog_client.send_command("ping")
print(f"Resposta do watchdog: {response}")

# Fechar o cliente
watchdog_client.close()
```