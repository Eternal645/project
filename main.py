import tkinter as tk
from tkinter import ttk

from app.database import connect_db, init_db
from app.ui_tables import open_table_window
from app.ui_reports import open_reports_window

conn = connect_db("db/mebel.db")
try:
    init_db(conn)
except Exception as e:
    import sys
    print("Ошибка инициализации БД:", e)
    sys.exit(1)

def on_close():
    conn.close()
    root.destroy()

BG        = "#f0ece4"
SIDEBAR   = "#4a3728"
SB_ACTIVE = "#6b5242"
SB_FG     = "#f5ede3"
ACCENT    = "#c9873a"
CARD_BG   = "#faf7f2"
CARD_BD   = "#ddd4c4"
BTN_BG    = "#c9873a"
BTN_FG    = "white"
BTN_HOV   = "#a86a28"

root = tk.Tk()
root.title("Мебельный магазин")
root.geometry("780x520")
root.resizable(False, False)
root.configure(bg=BG)
root.protocol("WM_DELETE_WINDOW", on_close)

style = ttk.Style(root)
style.theme_use("clam")
style.configure("Treeview", rowheight=24, font=("Arial", 10))
style.configure("Treeview.Heading", font=("Arial", 10, "bold"))

sidebar = tk.Frame(root, bg=SIDEBAR, width=190)
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

logo_frame = tk.Frame(sidebar, bg=ACCENT, height=80)
logo_frame.pack(fill="x")
logo_frame.pack_propagate(False)
tk.Label(logo_frame, text="🛋", font=("Arial", 28),
         bg=ACCENT, fg="white").pack(pady=(10, 0))
tk.Label(logo_frame, text="Мебель", font=("Arial", 11, "bold"),
         bg=ACCENT, fg="white").pack()

tk.Frame(sidebar, bg=ACCENT, height=2).pack(fill="x")

NAV_ITEMS = [
    ("  Товары",         lambda: show_section("Товары")),
    ("  Категории",      lambda: show_section("Категории")),
    ("  Поставщики",     lambda: show_section("Поставщики")),
    ("  Поставки",       lambda: show_section("Поставки")),
    ("  Заказы",         lambda: show_section("Заказы")),
    ("  Строки заказа",  lambda: show_section("Строки заказа")),
    ("  Доставки",       lambda: show_section("Доставки")),
    ("  Клиенты",        lambda: show_section("Клиенты")),
    ("  Сотрудники",     lambda: show_section("Сотрудники")),
    ("  Отчёты",         lambda: open_reports_window(conn, root)),
]

nav_buttons = []

def make_nav_btn(parent, text, cmd):
    btn = tk.Label(parent, text=text, bg=SIDEBAR, fg=SB_FG,
                   font=("Arial", 10), anchor="w", cursor="hand2",
                   padx=16, pady=9)
    btn.pack(fill="x")
    btn.bind("<Button-1>", lambda e: cmd())
    btn.bind("<Enter>",    lambda e: btn.configure(bg=SB_ACTIVE))
    btn.bind("<Leave>",    lambda e: btn.configure(bg=SIDEBAR))
    return btn

for text, cmd in NAV_ITEMS:
    b = make_nav_btn(sidebar, text, cmd)
    nav_buttons.append(b)

tk.Label(sidebar, text="v1.0", bg=SIDEBAR, fg="#7a6555",
         font=("Arial", 8)).pack(side="bottom", pady=6)

main_area = tk.Frame(root, bg=BG)
main_area.pack(side="left", fill="both", expand=True)

title_bar = tk.Frame(main_area, bg=BG, height=48)
title_bar.pack(fill="x", padx=20, pady=(16, 0))
title_bar.pack_propagate(False)

page_title = tk.Label(title_bar, text="Добро пожаловать",
                      font=("Arial", 16, "bold"), bg=BG, fg="#3a2a1a")
page_title.pack(side="left", anchor="w")

tk.Frame(main_area, bg=CARD_BD, height=1).pack(fill="x", padx=20, pady=(8, 12))

cards_frame = tk.Frame(main_area, bg=BG)
cards_frame.pack(fill="both", expand=True, padx=20)

def _count(table):
    return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

CARDS = [
    ("Товары",      f"{_count('Товары')} позиций",      ACCENT,   "Товары"),
    ("Клиенты",     f"{_count('Клиенты')} клиентов",    "#5a8a5a","Клиенты"),
    ("Заказы",      f"{_count('Заказы')} заказов",       "#5a6a8a","Заказы"),
    ("Поставщики",  f"{_count('Поставщики')} партнёров", "#8a5a6a","Поставщики"),
]

def make_card(parent, title, subtitle, color, table, row, col):
    card = tk.Frame(parent, bg=CARD_BG, relief="flat",
                    highlightbackground=CARD_BD, highlightthickness=1,
                    cursor="hand2")
    card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

    accent_bar = tk.Frame(card, bg=color, height=4)
    accent_bar.pack(fill="x")

    tk.Label(card, text=title, font=("Arial", 13, "bold"),
             bg=CARD_BG, fg="#3a2a1a").pack(anchor="w", padx=14, pady=(10, 2))
    tk.Label(card, text=subtitle, font=("Arial", 10),
             bg=CARD_BG, fg="#7a6a5a").pack(anchor="w", padx=14, pady=(0, 6))

    open_btn = tk.Label(card, text="Открыть →", font=("Arial", 9),
                        bg=CARD_BG, fg=color, cursor="hand2")
    open_btn.pack(anchor="e", padx=14, pady=(0, 10))

    for widget in (card, accent_bar, open_btn):
        widget.bind("<Button-1>", lambda e, t=table: show_section(t))

for c in range(2):
    cards_frame.columnconfigure(c, weight=1)
for r in range(2):
    cards_frame.rowconfigure(r, weight=1)

for i, (title, subtitle, color, table) in enumerate(CARDS):
    make_card(cards_frame, title, subtitle, color, table, i // 2, i % 2)

status_bar = tk.Frame(main_area, bg="#e8e0d4", height=26)
status_bar.pack(fill="x", side="bottom")
status_bar.pack_propagate(False)
tk.Label(status_bar,
         text=f"Товаров: {_count('Товары')}  │  Клиентов: {_count('Клиенты')}  │  Заказов: {_count('Заказы')}",
         bg="#e8e0d4", fg="#7a6a5a", font=("Arial", 8), anchor="w"
         ).pack(side="left", padx=12)

def show_section(name):
    page_title.configure(text=name)
    open_table_window(conn, root, name)

root.mainloop()
