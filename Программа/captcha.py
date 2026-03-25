import tkinter as tk
from PIL import Image, ImageTk, ImageDraw, ImageFont
import random, os

COLS, ROWS = 2, 2
PW, PH = 140, 120
PNG_DIR = os.path.join(os.path.dirname(__file__), "png")
from ui_theme import BG2, BG3, MUTED_FG, ACCENT, FONT_SMALL

def _make_selected(img: Image.Image, number: int) -> ImageTk.PhotoImage:
    result = img.convert("RGBA")
    overlay = Image.new("RGBA", result.size, (255, 255, 255, 100))
    result = Image.alpha_composite(result, overlay)
    draw = ImageDraw.Draw(result)
    text = str(number)
    
    w, h = result.size
    font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (w - tw) // 2
    y = (h - th) // 2

    draw.text((x + 1, y + 1), text, fill=(0, 0, 0, 180), font=font)
    draw.text((x, y), text, fill=ACCENT, font=font)
    return ImageTk.PhotoImage(result.convert("RGB"))

class PuzzleCaptcha(tk.Frame):  
    def __init__(self, master, on_solved, on_failed, **kwargs):
        kwargs.setdefault("bg", BG2)
        super().__init__(master, **kwargs)
        self.on_solved = on_solved
        self.on_failed = on_failed
        self.fails = 0
        self.clicks = []
        self.title = tk.Label(
            self,
            text="Капча — подтвердите, что вы не робот.\n"
                 "Нажмите фрагменты по порядку: слева-направо, сверху-вниз",
            bg=BG2,
            fg=MUTED_FG,
            font=FONT_SMALL,
            justify="center"
        )
        self.title.pack(pady=(0, 6))
        self.grid_frame = tk.Frame(self, bg=BG2)
        self.grid_frame.pack()
        self.status = tk.Label(self, bg=BG2, font=("Segoe UI", 8, "bold"))
        self.status.pack(pady=2)
        tk.Button(
            self,
            text="Другое изображение",
            bg=BG3,
            fg=MUTED_FG,
            relief="flat",
            font=("Segoe UI", 8),
            cursor="hand2",
            command=self.shuffle
        ).pack(pady=(0, 4))
        self.shuffle()

    def shuffle(self):
        for w in self.grid_frame.winfo_children():
            w.destroy()
        self.clicks.clear()
        files = ["1.png", "2.png", "3.png", "4.png"]
        self.pieces = []
        for f in files:
            img = Image.open(os.path.join(PNG_DIR, f)).convert("RGB")
            img.thumbnail((PW, PH), Image.LANCZOS)
            canvas = Image.new("RGB", (PW, PH), BG2)
            x = (PW - img.width) // 2
            y = (PH - img.height) // 2
            canvas.paste(img, (x, y))
            self.pieces.append(canvas)

        order = list(range(COLS * ROWS))
        random.shuffle(order)

        self.btns = []
        for pos, idx in enumerate(order):
            tk_img = ImageTk.PhotoImage(self.pieces[idx])
            r, c = divmod(pos, COLS)
            btn = tk.Button(self.grid_frame, image=tk_img, relief="flat", bg="#0f3460", cursor="hand2")
            btn.image = tk_img
            btn.grid(row=r, column=c, padx=2, pady=2)
            btn.config(command=lambda i=idx, b=btn: self._click(i, b))
            self.btns.append((idx, btn))

    def _click(self, idx, btn):
        if idx in self.clicks:
            self.clicks.remove(idx)
            original = ImageTk.PhotoImage(self.pieces[idx])
            btn.config(image=original, bg=BG3)
            btn.image = original
            return
        
        number = idx + 1
        selected_img = _make_selected(self.pieces[idx], number)
        btn.config(image=selected_img, bg=BG2)
        btn.image = selected_img
        self.clicks.append(idx)
        if len(self.clicks) == COLS * ROWS:
            if self.clicks == list(range(COLS * ROWS)):
                self.status.config(text="")
                self.after(300, self._hide)  
            else:
                self.fails += 1
                self.status.config(text=f"Неверно. Попытка {self.fails}/3", fg=ACCENT)
                self.after(800, self._reset_board)
                if self.fails >= 3:
                    self.after(800, self.on_failed)

    def _hide(self):
        self.grid_remove()   
        self.on_solved()    

    def _reset_board(self):
        self.clicks.clear()
        for idx, btn in self.btns:
            tk_img = ImageTk.PhotoImage(self.pieces[idx])
            btn.config(image=tk_img, bg=BG3)
            btn.image = tk_img

    def reset_fails(self):
        self.fails = 0

    @property
    def fail_count(self):
        return self.fails