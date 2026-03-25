import tkinter as tk
from tkinter import ttk, messagebox
import db
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
FONT_TABLE = ("Segoe UI", 9)

class AdminWindow(tk.Toplevel):
    def __init__(self, parent, user):
        super().__init__(parent)
        self.title(f"Администратор ({user['login']})")
        self.configure(bg=BG)
        self.minsize(700, 500)
        self.resizable(True, True)
        self._selected_id = None
        self._selected_parol = None  
        self._build_ui()
        self._load_users()
        self._center()

    def _build_ui(self):
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=20, pady=(16, 0))
        tk.Label(hdr, text="Панель администратора", font=FONT_TITLE,
                 bg=BG, fg=ACCENT).pack(side="left")
        tk.Button(hdr, text="Выход ", font=FONT_SMALL,
                  bg=BG3, fg=MUTED_FG, relief="flat", cursor="hand2",
                  command=self.destroy).pack(side="right")

        sep = tk.Frame(self, height=1, bg=BG2)
        sep.pack(fill="x", padx=20, pady=8)

        # Таблица пользователей
        tbl_frame = tk.Frame(self, bg=BG2)
        tbl_frame.pack(fill="both", expand=True, padx=20, pady=(0, 8))
        cols = ("ID", "Логин", "Роль", "Заблокирован", "Попытки")
        self._tree = ttk.Treeview(tbl_frame, columns=cols, show="headings", selectmode="browse")
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                         background=BG2, foreground=FG,
                         fieldbackground=BG2, rowheight=24,
                         font=FONT_TABLE)
        style.configure("Treeview.Heading",
                         background=BG3, foreground=MUTED_FG,
                         font=("Segoe UI", 9, "bold"), relief="flat")
        style.map("Treeview", background=[("selected", BG3)],
                  foreground=[("selected", ACCENT)])

        widths = [40, 160, 130, 110, 70]
        for col, w in zip(cols, widths):
            self._tree.heading(col, text=col)
            self._tree.column(col, width=w, anchor="center")

        vsb = ttk.Scrollbar(tbl_frame, orient="vertical",
                             command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        self._tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self._tree.bind("<<TreeviewSelect>>", self._on_select)

        # Форма редактирования/добавления
        form_frame = tk.Frame(self, bg=BG)
        form_frame.pack(fill="x", padx=20, pady=(0, 8))

        tk.Label(
            form_frame,
            text="Данные пользователя",
            font=FONT_SMALL,
            bg=BG,
            fg=MUTED_FG,
        ).pack(anchor="w", padx=12, pady=(0, 4))

        fields = tk.Frame(form_frame, bg=BG)
        fields.pack(fill="x", padx=12, pady=8)
        fields.columnconfigure(1, weight=1)
        fields.columnconfigure(3, weight=1)

        tk.Label(fields, text="Логин:", font=FONT_LABEL,
                 bg=BG, fg=MUTED_FG).grid(row=0, column=0, sticky="w", padx=(0, 6))
        self._f_login = tk.StringVar()
        tk.Entry(fields, textvariable=self._f_login, font=FONT_LABEL,
                 bg=BG3, fg=FG, insertbackground=FG, relief="flat",
                 highlightthickness=1, highlightbackground=BG3,
                 highlightcolor=ACCENT).grid(row=0, column=1, sticky="ew", padx=(0, 16))

        tk.Label(fields, text="Пароль:", font=FONT_LABEL,
                 bg=BG, fg=MUTED_FG).grid(row=0, column=2, sticky="w", padx=(0, 6))
        self._f_pass = tk.StringVar()
        tk.Entry(fields, textvariable=self._f_pass, font=FONT_LABEL,
                 bg=BG3, fg=FG, insertbackground=FG, relief="flat",
                 highlightthickness=1, highlightbackground=BG3,
                 highlightcolor=ACCENT).grid(row=0, column=3, sticky="ew")

        tk.Label(fields, text="Роль:", font=FONT_LABEL,
                 bg=BG, fg=MUTED_FG).grid(row=1, column=0, sticky="w", padx=(0, 6), pady=(8, 0))
        self._f_rol = tk.StringVar(value="Пользователь")
        rol_cb = ttk.Combobox(fields, textvariable=self._f_rol,
                               values=["Администратор", "Пользователь"],
                               state="readonly", font=FONT_LABEL)
        rol_cb.grid(row=1, column=1, sticky="ew", padx=(0, 16), pady=(8, 0))

        self._f_blocked = tk.BooleanVar(value=False)
        tk.Checkbutton(fields, text="Заблокирован", variable=self._f_blocked,
                       bg=BG, fg=MUTED_FG, selectcolor=BG3,
                       activebackground=BG, activeforeground=FG,
                       font=FONT_LABEL).grid(row=1, column=2, columnspan=2,
                                              sticky="w", pady=(8, 0))

        btn_frame = tk.Frame(self, bg=BG)
        btn_frame.pack(fill="x", padx=20, pady=(0, 16))

        btns = [
            ("Добавить", BG3, FG, self._add_user),
            ("Сохранить", BG3, FG, self._save_user),
            ("Обновить", BG3, MUTED_FG, self._load_users),
            ("Очистить", BG3, MUTED_FG, self._clear_form),
        ]
        for text, bg, fg, cmd in btns:
            tk.Button(btn_frame, text=text, font=FONT_BTN,
                      bg=bg, fg=fg, activebackground=bg,
                      relief="flat", cursor="hand2",
                      padx=14, pady=6, command=cmd).pack(side="left", padx=(0, 8))

    def _center(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"+{(sw - w) // 2}+{(sh - h) // 2}")

    def _load_users(self):
        for row in self._tree.get_children():
            self._tree.delete(row)
        try:
            users = db.get_all_users()
            for u in users:
                uid, login, rol, blocked, attempts = u
                self._tree.insert("", "end", iid=str(uid),
                                  values=(uid, login, rol,
                                          "Да" if blocked else "Нет",
                                          attempts))
        except Exception as e:
            messagebox.showerror("Ошибка БД", f"Не удалось загрузить пользователей:\n{e}")

    def _on_select(self, _event=None):
        sel = self._tree.selection()
        if not sel:
            return
        iid = sel[0]
        values = self._tree.item(iid, "values")
        self._selected_id = int(values[0])
        self._f_login.set(values[1])
        self._f_rol.set(values[2])
        self._f_blocked.set(values[3] == "Да")
        self._f_pass.set("")   
        try:
            u = db.get_user(values[1])
            self._selected_parol = u["parol"] if u else None
        except Exception:
            self._selected_parol = None

    def _clear_form(self):
        self._selected_id = None
        self._selected_parol = None
        self._f_login.set("")
        self._f_pass.set("")
        self._f_rol.set("Пользователь")
        self._f_blocked.set(False)
        self._tree.selection_remove(self._tree.selection())

    def _add_user(self):
        login = self._f_login.get().strip()
        parol = self._f_pass.get().strip()
        rol   = self._f_rol.get()
        if not login or not parol:
            messagebox.showwarning("Предупреждение",
                                   "Логин и пароль обязательны для заполнения.")
            return
        ok, msg = db.add_user(login, parol, rol)
        if ok:
            messagebox.showinfo("Успех", msg)
            self._load_users()
            self._clear_form()
        else:
            messagebox.showerror("Ошибка", msg)

    def _save_user(self):
        if self._selected_id is None:
            messagebox.showwarning("Предупреждение",
                                   "Выберите пользователя в таблице для редактирования.")
            return
        login   = self._f_login.get().strip()
        parol   = self._f_pass.get().strip()
        rol     = self._f_rol.get()
        blocked = self._f_blocked.get()
        if not login:
            messagebox.showwarning("Предупреждение", "Логин не может быть пустым.")
            return
        if not parol:
            if self._selected_parol:
                parol = self._selected_parol
            else:
                messagebox.showwarning(
                    "Предупреждение",
                    "Введите пароль, чтобы сохранить изменения.",
                )
                return
        try:
            db.update_user(self._selected_id, login, parol, rol, blocked)
            messagebox.showinfo("Успех", "Данные пользователя обновлены.")
            self._load_users()
            self._clear_form()
        except Exception as e:
            messagebox.showerror("Ошибка БД", f"Не удалось сохранить изменения:\n{e}")
