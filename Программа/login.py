import tkinter as tk
from tkinter import messagebox
import db
from captcha import PuzzleCaptcha

from ui_theme import (
    BG,
    BG2,
    BG3,
    ACCENT,
    FG,
    MUTED_FG,
    FONT_TITLE,
    FONT_LABEL,
    FONT_BTN,
    FONT_SMALL,
)

class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("OWNOSH — Авторизация")
        self.configure(bg=BG)
        self.resizable(True, True)
        self.minsize(400, 620)
        try:
            db.init_users_table()
        except Exception as e:
            messagebox.showerror("Ошибка БД",
                f"Не удалось подключиться к базе данных.\n{e}\n\n"
                "Проверьте настройки в файле db.py (пароль, имя БД).")

        self._puzzle_solved = False
        self._fail_count = 0   # общий счётчик неудачных попыток 
        self._build_ui()
        self._center()

    def _build_ui(self):
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", pady=(30, 10))
        tk.Label(header, text="OWNOSH", font=FONT_TITLE, bg=BG, fg=ACCENT).pack()
        tk.Label(
            header,
            text="Система управления производством",
            font=("Segoe UI", 10),
            bg=BG,
            fg=MUTED_FG,
        ).pack()

        card = tk.Frame(self, bg=BG2, bd=0)
        card.pack(padx=40, fill="x")
        card.columnconfigure(0, weight=1)

        tk.Label(
            card,
            text="Вход в систему",
            font=("Segoe UI", 13, "bold"),
            bg=BG2,
            fg=FG,
        ).grid(row=0, column=0, pady=(16, 12))

        self._add_field(card, "Логин", row=1)
        self._login_var = tk.StringVar()
        self._login_entry = self._styled_entry(card, self._login_var)
        self._login_entry.grid(row=2, column=0, padx=20, sticky="ew", pady=(0, 10))

        self._add_field(card, "Пароль", row=3)
        self._pass_var = tk.StringVar()
        self._pass_entry = self._styled_entry(card, self._pass_var, show="●")
        self._pass_entry.grid(row=4, column=0, padx=20, sticky="ew", pady=(0, 16))

        cap_frame = tk.LabelFrame(self, bg=BG, fg=BG2,
                                  font=FONT_SMALL,
                                  bd=1, relief="groove")
        cap_frame.pack(padx=40, fill="x", pady=(10, 0))

        self._captcha = PuzzleCaptcha(
            cap_frame,
            on_solved=self._on_puzzle_solved,
            on_failed=self._on_puzzle_failed,
            bg=BG
        )
        self._captcha.pack(padx=4, pady=4)

        self._login_btn = tk.Button(
            self, text="ВОЙТИ",
            font=FONT_BTN, bg=ACCENT, fg="#ffffff",
            activebackground=BG3, activeforeground=FG,
            relief="flat", cursor="hand2",
            pady=10,
            command=self._on_login
        )
        self._login_btn.pack(padx=40, fill="x", pady=16)

        self._status_lbl = tk.Label(self, text="", font=FONT_SMALL,
                                    bg=BG, fg=ACCENT, wraplength=340)
        self._status_lbl.pack(padx=40)

        # Привязки клавиш
        self.bind("<Return>", lambda e: self._on_login())
        self._login_entry.bind("<Tab>", lambda e: (self._pass_entry.focus(), "break"))

    def _add_field(self, parent, text, row):
        tk.Label(parent, text=text, font=FONT_LABEL,
                 bg=BG2, fg=MUTED_FG, anchor="w").grid(
            row=row, column=0, padx=20, sticky="w")

    def _styled_entry(self, parent, var, show=None):
        e = tk.Entry(parent, textvariable=var,
                     font=FONT_LABEL,
                     bg=BG3, fg=FG,
                     insertbackground=FG,
                     relief="flat",
                     bd=0,
                     highlightthickness=1,
                     highlightbackground=BG3,
                     highlightcolor=ACCENT)
        if show:
            e.config(show=show)
        e.config({"font": ("Segoe UI", 11)})
        return e

    def _center(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"+{(sw - w) // 2}+{(sh - h) // 2}")

    def _on_puzzle_solved(self):
        self._puzzle_solved = True
        self._captcha.reset_fails()
        self._captcha.master.pack_forget()  
        self._set_status("Капча пройдена", ACCENT)

    def _on_puzzle_failed(self):
        self._fail_count += self._captcha.fail_count
        self._check_total_fails()

    def _on_login(self):
        login = self._login_var.get().strip()
        parol = self._pass_var.get().strip()

        # Валидация полей
        if not login:
            messagebox.showwarning("Предупреждение", "Поле «Логин» обязательно для заполнения.")
            self._login_entry.focus()
            return
        if not parol:
            messagebox.showwarning("Предупреждение", "Поле «Пароль» обязательно для заполнения.")
            self._pass_entry.focus()
            return
        if not self._puzzle_solved:
            messagebox.showwarning("Капча", "Пожалуйста, сначала соберите пазл.")
            return

        # Проверка в БД
        try:
            user = db.get_user(login)
        except Exception as e:
            messagebox.showerror("Ошибка БД", f"Ошибка при обращении к базе данных:\n{e}")
            return

        if user is None:
            self._fail_count += 1
            self._set_status(
                "Вы ввели неверный логин или пароль. Пожалуйста проверьте ещё раз введенные данные.",
                ACCENT)
            self._check_total_fails()
            return

        if user["zablokirovan"]:
            messagebox.showerror("Заблокировано",
                "Вы заблокированы. Обратитесь к администратору.")
            return

        if user["parol"] != parol:
            self._fail_count += 1
            try:
                db.increment_attempts(login)
            except Exception:
                pass
            self._set_status(
                "Вы ввели неверный логин или пароль. Пожалуйста проверьте ещё раз введенные данные.",
                ACCENT)
            self._check_total_fails(login)
            return
        try:
            db.reset_attempts(login)
        except Exception:
            pass

        messagebox.showinfo("Добро пожаловать", "Вы успешно авторизовались!")
        self._open_main(user)

    def _check_total_fails(self, login=None):
        if self._fail_count >= 3:
            if login:
                try:
                    db.increment_attempts(login)
                except Exception:
                    pass
            messagebox.showerror("Заблокировано",
                "Вы заблокированы. Обратитесь к администратору.")
            self._login_btn.config(state="disabled")
            self._set_status("Учётная запись заблокирована.", ACCENT)

    def _set_status(self, text, color=MUTED_FG):
        self._status_lbl.config(text=text, fg=color)

    def _open_main(self, user):
        self.withdraw()
        if user["rol"] == "Администратор":
            from admin import AdminWindow
            win = AdminWindow(self, user)
        else:
            from user_window import UserWindow
            win = UserWindow(self, user)
        win.protocol("WM_DELETE_WINDOW", lambda: (win.destroy(), self.destroy()))
