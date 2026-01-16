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