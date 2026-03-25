import tkinter as tk
from ui_theme import BG, BG2, BG3, ACCENT, FG, MUTED_FG, FONT_TITLE


class UserWindow(tk.Toplevel):
    def __init__(self, parent, user):
        super().__init__(parent)
        self.title(f"Рабочий стол ({user['login']})")
        self.configure(bg=BG)
        self.minsize(500, 300)
        self.resizable(True, True)

        tk.Label(self, text=f"Добро пожаловать, {user['login']}!",
                 font=FONT_TITLE, bg=BG, fg=ACCENT).pack(pady=(30, 8))
        tk.Label(self, text=f"Роль: {user['rol']}",
                 font=("Segoe UI", 10), bg=BG, fg=MUTED_FG).pack()
        tk.Frame(self, height=1, bg=BG2).pack(fill="x", padx=40, pady=16)
        tk.Label(self, text="Раздел пользователя",
                 font=("Segoe UI", 12, "bold"), bg=BG, fg=FG).pack()
        tk.Label(self, text="Здесь будет основной функционал приложения.",
                 font=("Segoe UI", 9), bg=BG, fg=MUTED_FG).pack(pady=6)
        tk.Button(self, text="Выйти", font=("Segoe UI", 9, "bold"),
                  bg=BG3, fg=MUTED_FG, relief="flat", cursor="hand2",
                  command=self.destroy).pack(pady=20)
