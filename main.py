import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import json
import os

class AgendaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Agenda Pessoal")
        self.events = {} #{data:[eventos]}
        self.categories = {
            "Trabalho": "#FF6B6B",
            "Pessoal": "#4ECDC4",
            "Saúde": "#FFD166",
            "Lazer": "#06D6AD",
        }
        self.load_data()
        self.setup_ui()

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

    def create_month_view(self, year, month):
        # Cabeçalho com dias da semana.
        days = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]
        for i, day in enumerate(days):
            label = ttk.Label(self.month_frame, text=day, anchor="center",
                              background="lightray", padding=5)
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
                        text=f"·{event["title"][:10]}...",
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
            for i in range(6): # 6 linhas.
                self.month_frame.grid_rowconfigure(i+1, weight=1)

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
                "reminder": int(reminder_var.get())
            }

            if date_str not in self.events:
                self.events[date_str] = []
            self.events[date_str].append(event_data)

            self.save_data()
            self.refresh_views()
            dialog.destroy()

        ttk.Button(dialog, text="Salvar", command=save_event).pack(padx=20)