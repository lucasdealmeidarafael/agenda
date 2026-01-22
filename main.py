from tkinter import Tk
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import json
import os
import threading
import time


class AgendaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Agenda Pessoal")
        self.root.geometry("800x600")
        self.root.configure(bg="#feffff")
        self.events = {} #{data:[eventos]}
        self.categories = {
            "Trabalho": "#FF6B6B",
            "Pessoal": "#4ECDC4",
            "Saúde": "#FFD166",
            "Lazer": "#06D6A0",
        }
        self.current_date = datetime.now()
        self.load_data()
        self.setup_ui()
        self.create_month_view(self.current_date.year, self.current_date.month)
        self.notification_manager = NotificationManager(self)

        style = ttk.Style(self.root)
        style.theme_use("clam")

        # Botão de adicionar evento.
        ttk.Button(self.control_frame, text="+ Novo Evento",
                   command=lambda: self.add_event_dialog(self.current_date)).pack(side=tk.RIGHT, padx=5)

    def setup_ui(self):
        # Controles superiores.
        self.control_frame = ttk.Frame(self.root)
        self.control_frame.pack(fill=tk.X, padx=10, pady=5)

        # Botões de navegação.
        ttk.Button(self.control_frame, text="◀", command=self.prev_month).pack(side=tk.LEFT)
        ttk.Button(self.control_frame, text="Hoje", command=self.go_to_today).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.control_frame, text="▶", command=self.next_month).pack(side=tk.LEFT)

        # Label do mês/ano
        self.date_label = ttk.Label(self.control_frame, text="", font=("Arial", 12))
        self.date_label.pack(side=tk.LEFT, padx=20)

        # Abas de visualização.
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Frame mensal.
        self.month_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.month_frame, text="Mensal")

        # Frame semanal.
        self.week_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.week_frame, text="Semanal")

        # Frame diário.
        self.day_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.day_frame, text="Diário")

        # Barra lateral com listas de eventos.
        self.sidebar = ttk.Frame(self.root, width=200)
        self.sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=10)

        # Adiciona filtros na sidebar.
        self.create_category_filter()

    def update_date_label(self):
        """Atualiza o label com o mês/ano atual"""
        self.date_label.config(text=self.current_date.strftime("%B %Y"))

    def get_days_in_month(self, year, month):
        """Retornar o número de dias em um mês."""
        if month == 12:
            return 31
        d1 = datetime(year, month, 1)
        d2 = datetime(year, month + 1, 1)
        return (d2 - d1).days

    def create_month_view(self, year, month):
        # Limpa o frame antes de criar nova visualização.
        for widget in self.month_frame.winfo_children():
            widget.destroy()

        # Cabeçalho com dias da semana.
        days = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]
        for i, day in enumerate(days):
            label = ttk.Label(self.month_frame, text=day, anchor="center",
                              background="lightgray", padding=5)
            label.grid(row=0, column=i, sticky="ew")

        # Calcular primeiro dia do mês.
        first_day = datetime(year, month, 1)
        # Começar na posição correta (ajustar para domingo=0)
        start_col = (first_day.weekday() + 1) % 7

        # Criar grid 6x7.
        row = 1
        col = start_col
        days_in_month = self.get_days_in_month(year, month)

        for day in range(1, days_in_month + 1):
            date = datetime(year, month, day)
            date_str = date.strftime("%Y-%m-%d")

            # Frame para cada dia.
            day_frame = ttk.Frame(self.month_frame, relief=tk.RAISED, borderwidth=1)

            # Número do dia.
            day_label = tk.Label(day_frame, text=str(day), anchor="nw")
            day_label.pack(anchor="nw", padx=2)

            # Eventos do dia (mostrar primeiros 2-3)
            if date_str in self.events:
                for event in self.events[date_str][:2]: # Mostra apenas 2
                    event_label = ttk.Label(
                        day_frame,
                        text=f"·{event['title'][:10]}...",
                        foreground=event['color'],
                        font=("Arial", 8)
                    )
                    event_label.pack(fill=tk.X, padx=2)

                col += 1
                if col == 7:
                    col = 0
                    row += 1

            # Configurar pesos das colunas
            for i in range(7):
                self.month_frame.grid_columnconfigure(i, weight=1)
            for i in range(7): # 6 linhas + cabeçalho.
                self.month_frame.grid_rowconfigure(i, weight=1)

    def prev_month(self):
        """Navega para o mês anterior."""
        # Vai para o último dia do mês anterior.
        first_day = self.current_date.replace(day=1)
        prev_month = first_day - timedelta(days=1)
        self.current_date = prev_month.replace(day=1)
        self.update_date_label()
        self.create_month_view(self.current_date.year, self.current_date.month)
        
    def next_month(self):
        """Navega para o próximo mês."""
        if self.current_date.month == 12:
            self.current_date = self.current_date.replace(year=self.current_date.year + 1, month=1)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month + 1)
        self.update_date_label()
        self.create_month_view(self.current_date.year, self.current_date.month)

    def go_to_today(self):
        """Volta para o mês atual."""
        self.current_date = datetime.now()
        self.update_date_label()
        self.create_month_view(self.current_date.year, self.current_date.month)

    def add_event_dialog(self, date=None):
        dialog = tk.Toplevel(self.root)
        dialog.title("Novo Evento")
        dialog.geometry("400x450")

        # Formulário.
        ttk.Label(dialog, text="Título:").pack(anchor="w", padx=20, pady=(20, 5))
        title_entry = ttk.Entry(dialog, width=40)
        title_entry.pack(padx=20, pady=(0, 10))

        ttk.Label(dialog, text="Descrição:").pack(anchor="w", padx=20, pady=(10, 5))
        desc_text = tk.Text(dialog, height=5, width=40)
        desc_text.pack(padx=20, pady=(0, 10))

        # Data e hora.
        date_frame = ttk.Frame(dialog)
        date_frame.pack(fill=tk.X, padx=20, pady=10)

        ttk.Label(date_frame, text="Data:").grid(row=0, column=0, sticky="w")
        date_entry = ttk.Entry(date_frame, width=12)
        date_entry.grid(row=0, column=1, padx=(5, 20))
        if date:
            date_entry.insert(0, date.strftime("%d/%m/%Y"))

        ttk.Label(date_frame, text="Hora:").grid(row=0, column=2, sticky="w")
        time_entry = ttk.Entry(date_frame, width=8)
        time_entry.grid(row=0, column=3)
        time_entry.insert(0, "09:00")

        # Categoria (combobox com cores)
        ttk.Label(dialog, text="Categoria:").pack(anchor="w", padx=20, pady=(10, 5))
        category_var = tk.StringVar()
        category_combo = ttk.Combobox(dialog, textvariable=category_var, state="readonly")
        category_combo['values'] = list(self.categories.keys())
        category_combo.current(0)
        category_combo.pack(padx=20, pady=(0, 10))

        # Lembrete
        ttk.Label(dialog, text="Lembrete (minutos antes):").pack(anchor="w", padx=20, pady=(10, 5))
        reminder_var = tk.StringVar(value="15")
        ttk.Entry(dialog, textvariable=reminder_var, width=10).pack(anchor="w", padx=20)

        def save_event():
            # Validar e salvar.
            title = title_entry.get()
            if not title:
                messagebox.showerror("Erro", "O título é obrigatório!")
                return
            
            # Salvar no dicionário de eventos.
            date_str = datetime.strptime(date_entry.get(), "%d/%m/%Y").strftime("%Y-%m-%d")
            event_data = {
                "title": title,
                "description": desc_text.get("1.0", tk.END).strip(),
                "time": time_entry.get(),
                "category": category_var.get(),
                "color": self.categories[category_var.get()],
                "reminder": int(reminder_var.get()),
                "notified": False # Adicionado para controle de notificações.
            }

            if date_str not in self.events:
                self.events[date_str] = []
            self.events[date_str].append(event_data)

            self.save_data()
            self.refresh_views()
            dialog.destroy()

        ttk.Button(dialog, text="Salvar", command=save_event).pack(padx=20)

    def refresh_views(self):
        """Atualiza todas as visualizações."""
        self.create_month_view(self.current_date.year, self.current_date.month)

    def save_data(self):
        data = {
            "events": self.events,
            "categories": self.categories
        }
        with open("agenda_data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # Backup automático.
        backup_file = f"backup_agenda_{datetime.now().strftime('%Y%m%d')}.json"
        with open(backup_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_data(self):
        try:
            if os.path.exists("agenda_data.json"):
                with open("agenda_data.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.events = data.get("events", {})
                    self.categories = data.get("categories", self.categories)
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")

    def create_category_filter(self):
        filter_frame = ttk.LabelFrame(self.sidebar, text="Filtrar por Categoria")
        filter_frame.pack(fill=tk.X, padx=5, pady=5)

        self.filter_vars = {}
        for category, color in self.categories.items():
            var = tk.BooleanVar(value=True)
            cb = ttk.Checkbutton(
                filter_frame,
                text=category,
                variable=var,
                command=self.apply_filters
            )
            cb.pack(anchor="w", padx=5, pady=2)
            self.filter_vars[category] = var

    def apply_filters(self):
        """Aplica os filtros selecionados."""
        


class NotificationManager:
    def __init__(self, app):
        self.app = app
        self.running = True
        self.thread = threading.Thread(target=self.check_reminders, daemon=True)
        self.thread.start()

    def check_reminders(self):
        while self.running:
            now = datetime.now()
            for date_str, events in self.app.events.items():
                for event in events:
                    event_time = datetime.strptime(
                        f"{date_str} {event['time']}",
                        "%Y-%m-%d %H:%M"
                    )
                    reminder_time = event_time - timedelta(minutes=event['reminder'])

                    # Verificar se é hora do lembrete.
                    if now >= reminder_time and not event.get('notified', False):
                        self.show_notification(event)
                        event['notified'] = True

                time.sleep(60) # Verifica a cada minuto.

    def show_notification(self, event):
        # Usar messagebox ou criar uma janela personalizada.
        self.app.root.after(0, lambda:
                            messagebox.showinfo(
                                "Lembrete",
                                f"{event['title']}\nHora: {event['time']}"
                            ))
        
    def save_data(self):
        data = {
            "events": self.events,
            "last_view": self.current_view,
            "categories": self.categories
        }
        with open("agenda_data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # Backup automático.
        backup_file = f"backup_agenda_{datetime.now().strftime('%Y%m%d')}.json"
        with open(backup_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_data(self):
        try:
            if os.path.exists("agenda_data.json"):
                with open("agenda_data.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.events = data.get("events",{})
                    self.categories = data.get("categories", self.categories)
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")

    def create_category_filter(self):
        filter_frame = ttk.LabelFrame(self.sidebar, text="Filtrar por Categoria")
        filter_frame.pack(fill=tk.X, padx=5, pady=5)

        self.filter_vars = {}
        for category, color in self.categories.items():
            var = tk.BooleanVar(value=True)
            cb = ttk.Checkbutton(
                filter_frame,
                text=category,
                variable=var,
                command=self.apply_filters
            )
            cb.pack(anchor="w", padx=5, pady=2)
            self.filter_vars[category] = var


janela = Tk()
app = AgendaApp(janela)
janela.mainloop()