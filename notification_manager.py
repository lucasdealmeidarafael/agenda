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
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
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
                    self._check_reminders()
                except Exception as e:
                    print(f"Erro no monitor: {e}")

                time.sleep(self.check_interval)

        def _check_reminder(self, events_dict):
            """Verifica se há lembretes para exibir."""
            now = datetime.now()

            for date_str, events in events_dict.items():
                for event in events:
                    # Verificar se evento tem lembrete e ainda não foi notificado.
                    if (event.get('reminder') and
                        not event.get('notified', False)):

                        event_time = datetime.strptime(
                            f"{date_str} {event['time']}",
                            "%y-%m-%d %H:%M"
                        )

                        reminder_time = event_time-timedelta(
                            minutes=event['reminder']
                        )

                        # Se é hora do lembrete.
                        if now >= reminder_time:
                            self._show_notification(event)
                            event['notified'] = True

        def _show_notification(self, event):
            """Exibe a notificação."""
            title = f'🔔 Lembrete: {event['title']}'
            message = f"Hora: {event['time']}\n{event.get('description', '')}"

            # Notificação do sistema (Window/Linux/Mac)
            try:
                notification.notify(
                    title = title,
                    message = message,
                    timeout = 10,
                    app_name = "Agenda Pessoal"
                )
            except:
                # Fallback para messagebox se plyer não funcionar.
                if self.app_callback:
                    self.app_callback("show_reminder", event)

                # Som de notificação (Windows).
                try:
                    winsound.Beep(1000, 300) # Frequência 1000Hz, 300ms
                except:
                    pass

        def reset_notifications(self, events_dict, date_filter=None):
            """Reseta status de notificações para eventos futuros."""
            now = datetime.now()

            for date_str, events in events_dict.items():
                event_date = datetime.strptime(date_str, "%Y-%m-%d")

                for event in events:
                    # Se o evento é futuro, reseta a notificação.
                    if event_date >= now:
                        event['notified'] = False
