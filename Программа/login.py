import tkinter as tk
from tkinter import ttk, messagebox
import db
from captcha import PuzzleCaptcha

from ui_theme import (
    BG,
    BG2,
    BG3,
    ACCENT,
    FG,
    FG2,
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

        self._build_ui()
        self._center()

    # ------------------------------------------------------------------ UI ---

    def _build_ui(self):
        # Заголовок
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", pady=(30, 10))
        tk.Label(header, text="OWNOSH", font=FONT_TITLE,
                 bg=BG, fg=ACCENT).pack()
        tk.Label(
            header,
            text="Система управления производством",
            font=("Segoe UI", 10),
            bg=BG,
            fg=MUTED_FG,
        ).pack()

        # Разделитель
        sep = tk.Frame(self, height=1, bg=BG3)
        sep.pack(fill="x", padx=40, pady=(0, 20))

        # Карточка формы
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

        # Логин
        self._add_field(card, "Логин", row=1)
        self._login_var = tk.StringVar()
        self._login_entry = self._styled_entry(card, self._login_var)
        self._login_entry.grid(row=2, column=0, padx=20, sticky="ew", pady=(0, 10))

        # Пароль
        self._add_field(card, "Пароль", row=3)
        self._pass_var = tk.StringVar()
        self._pass_entry = self._styled_entry(card, self._pass_var, show="●")
        self._pass_entry.grid(row=4, column=0, padx=20, sticky="ew", pady=(0, 16))

        # Капча
        self._cap_frame = tk.LabelFrame(self, text=" Капча — подтвердите, что вы не робот ",
                                  bg=BG, fg=FG2,
                                  font=FONT_SMALL,
                                  bd=1, relief="groove")

        self._captcha = PuzzleCaptcha(
            self._cap_frame,
            on_solved=self._on_puzzle_solved,
            on_failed=self._on_puzzle_failed,
            bg=BG
        )
        self._captcha.pack(padx=4, pady=4)
        self._cap_visible = False

        # Кнопка входа
        self._login_btn = tk.Button(
            self, text="ВОЙТИ",
            font=FONT_BTN, bg=ACCENT, fg="#ffffff",
            activebackground="#c73652", activeforeground="#ffffff",
            relief="flat", cursor="hand2",
            pady=10,
            command=self._on_login
        )
        self._login_btn.pack(padx=40, fill="x", pady=16)

        # Статус
        self._status_lbl = tk.Label(self, text="", font=FONT_SMALL,
                                    bg=BG, fg=ACCENT, wraplength=340)
        self._status_lbl.pack(padx=40)


        # Привязки клавиш
        self.bind("<Return>", lambda e: self._on_login())
        self._login_entry.bind("<Tab>", lambda e: (self._pass_entry.focus(), "break"))
        self._login_var.trace_add("write", lambda *_: self._maybe_toggle_captcha())
        self._pass_var.trace_add("write", lambda *_: self._maybe_toggle_captcha())

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

    # --------------------------------------------------------------- Logic ---

    def _maybe_toggle_captcha(self):
        login = self._login_var.get().strip()
        parol = self._pass_var.get().strip()
        should_show = bool(login and parol)

        if should_show and not self._cap_visible:
            self._cap_frame.pack(padx=40, fill="x", pady=(10, 0))
            self._cap_visible = True
            self._puzzle_solved = False
            self._captcha.reset_fails()
            self._set_status("Соберите капчу и нажмите «ВОЙТИ».", MUTED_FG)
        elif (not should_show) and self._cap_visible:
            self._cap_frame.pack_forget()
            self._cap_visible = False
            self._puzzle_solved = False
            self._captcha.reset_fails()
            self._set_status("", MUTED_FG)

    def _on_puzzle_solved(self):
        self._puzzle_solved = True
        self._captcha.reset_fails()
        self._set_status("✓ Капча пройдена", ACCENT)

    def _on_puzzle_failed(self):
        messagebox.showerror("Капча", "Слишком много неверных попыток капчи. Попробуйте ещё раз.")
        self._puzzle_solved = False
        self._captcha.shuffle()

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
        if not self._cap_visible:
            self._maybe_toggle_captcha()
            messagebox.showwarning("Капча", "Теперь пройдите капчу и нажмите «ВОЙТИ».")
            return
        if not self._puzzle_solved:
            messagebox.showwarning("Капча", "Пожалуйста, сначала пройдите капчу.")
            return

        # Проверка в БД
        try:
            user = db.get_user(login)
        except Exception as e:
            messagebox.showerror("Ошибка БД", f"Ошибка при обращении к базе данных:\n{e}")
            return

        if user is None:
            self._set_status(
                "Вы ввели неверный логин или пароль. Пожалуйста проверьте ещё раз введенные данные.",
                ACCENT)
            return

        if user["zablokirovan"]:
            messagebox.showerror("Заблокировано",
                "Вы заблокированы. Обратитесь к администратору.")
            return

        if user["parol"] != parol:
            try:
                db.increment_attempts(login)
            except Exception:
                pass
            try:
                user = db.get_user(login)
            except Exception:
                user = None

            if user and user.get("zablokirovan"):
                messagebox.showerror("Заблокировано", "Вы заблокированы. Обратитесь к администратору.")
                self._set_status("Учётная запись заблокирована.", ACCENT)
            elif user:
                self._set_status(
                    f"Неверный пароль. Попыток: {user.get('popytki', 0)}/3",
                    ACCENT,
                )
            else:
                self._set_status(
                    "Неверный пароль. Попробуйте ещё раз.",
                    ACCENT,
                )
            return

        # Успех
        try:
            db.reset_attempts(login)
        except Exception:
            pass

        messagebox.showinfo("Добро пожаловать", "Вы успешно авторизовались!")
        self._open_main(user)

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
