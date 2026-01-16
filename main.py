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

    