# Watchdog

Watchdog é um agente de monitoramento de processos desenvolvido para gerenciar o ciclo de vida de um processo específico, monitorando seu estado em tempo real e respondendo a comandos essenciais, como `start`, `ping`, e `kill`.

Ele fornece dados relevantes, incluindo PIDs e tempos de execução, além de notificar automaticamente sobre mudanças no status do processo.
Recursos

- **Início e monitoramento do processo:** O Watchdog inicia e acompanha o processo especificado, retornando dados atualizados com o comando `ping_watchdog`.

- **Detecção de encerramento:** Quando o processo monitorado é encerrado, o Watchdog registra e retorna os dados automaticamente.

- **Monitoramento do processo pai:** O Watchdog detecta quando o processo pai (aquele que o iniciou) é encerrado. Nesse caso, ele exibe uma notificação para alertar o usuário e, em seguida, encerra o processo monitorado para evitar que ele continue rodando sem supervisão.

- **Notificação de encerramento do Watchdog:** O processo pai detecta quando o Watchdog é encerrado enquanto o processo monitorado ainda está ativo. Nessa situação, uma janela de notificação é exibida, informando que o processo monitorado continua em execução sem supervisão.

Este projeto é ideal para cenários que exigem supervisão constante de processos, garantindo que qualquer encerramento inesperado seja identificado e tratado de maneira eficaz, com alertas e interrupções controladas.