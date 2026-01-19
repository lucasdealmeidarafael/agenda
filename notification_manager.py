"""
Sistema de notificação e lembretes.
"""

import threading
import time
from datetime import datetime, timedelta
from plyer import notification
import winsound

class NotificationManager:
    def __init__(self, app_callback=None):
        """
        Inicializa o gerenciador de notificações.

        Args:
            app_callback: Função para atualizar interface quando notificar.
        """
        self.app_callback = app_callback
        self.running = False
        self.thread = None
        self.check_interval = 30 # Verifica a cada 30 segundos.

    def start(self):
        """Inicia o monitoramento de lembretes."""
        
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self_monitor_loop, daemon=True)
        self.thread.start()
        print("✅ Sistema de notificações iniciado")

        def stop(self):
            """Parar monitoramento."""
            self.running = False
            if self.trhead:
                self.thread.join(timeout=2)
            print("🛑 Sistema de notificações parado")

        def _monitor_loop(self):
            """Loop principal de verificação."""
            while self.running:
                try:
                    self_check_reminders()
                except Exception as e:
                    print(f"Erro no monitor: {e}")

                time.sleep(self.check_interval)

        def _check_reminder(self, events_dict):
            """Verifica se há lembretes para exibir."""
            now = datetime.now()
            