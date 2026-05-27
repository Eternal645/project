import tkinter as tk
from tkinter import ttk

REPORTS = {
    "Выручка по месяцам": {
        "desc": "Сумма выполненных заказов, сгруппированная по году и месяцу",
        "query": """
            SELECT substr(дата_заказа,1,7) AS период,
                   COUNT(*) AS заказов,
                   printf('%.2f', SUM(итого)) AS выручка
            FROM Заказы WHERE статус = 'выполнен'
            GROUP BY substr(дата_заказа,1,7) ORDER BY период
        """,
        "columns": ["Период", "Кол-во заказов", "Выручка (руб.)"],
    },
    "ТОП-10 товаров по продажам": {
        "desc": "Самые продаваемые позиции по количеству штук",
        "query": """
            SELECT т.наименование,
                   SUM(сз.количество) AS продано_шт,
                   printf('%.2f', SUM(сз.количество * сз.цена_единицы)) AS выручка
            FROM СтрокиЗаказа сз
            JOIN Товары т ON сз.id_товара = т.id
            JOIN Заказы з ON сз.id_заказа = з.id
            WHERE з.статус != 'отменён'
            GROUP BY т.id ORDER BY продано_шт DESC LIMIT 10
        """,
        "columns": ["Товар", "Продано (шт.)", "Выручка (руб.)"],
    },
    "VIP-клиенты (сумма > 50 000)": {
        "desc": "Клиенты с суммарной стоимостью невозвращённых заказов свыше 50 000 руб.",
        "query": """
            SELECT к.фио, к.телефон, COUNT(з.id) AS заказов,
                   printf('%.2f', SUM(з.итого)) AS сумма
            FROM Клиенты к
            JOIN Заказы з ON к.id = з.id_клиента
            WHERE з.статус != 'отменён'
            GROUP BY к.id HAVING SUM(з.итого) > 50000
            ORDER BY SUM(з.итого) DESC
        """,
        "columns": ["ФИО клиента", "Телефон", "Заказов", "Сумма (руб.)"],
    },
    "Остатки на складе": {
        "desc": "Текущее количество товаров на складе по категориям",
        "query": """
            SELECT к.название AS категория, т.наименование,
                   т.остаток AS шт,
                   printf('%.2f', т.цена) AS цена,
                   printf('%.2f', т.остаток * т.цена) AS стоимость_запаса
            FROM Товары т
            JOIN Категории к ON т.id_категории = к.id
            ORDER BY к.название, т.наименование
        """,
        "columns": ["Категория", "Товар", "Остаток (шт.)", "Цена", "Стоимость запаса"],
    },
    "Критически малый остаток (< 4 шт.)": {
        "desc": "Товары, которые нужно срочно дозаказать",
        "query": """
            SELECT к.название AS категория, т.наименование,
                   т.остаток, printf('%.2f', т.цена) AS цена
            FROM Товары т
            JOIN Категории к ON т.id_категории = к.id
            WHERE т.остаток < 4 ORDER BY т.остаток
        """,
        "columns": ["Категория", "Товар", "Остаток (шт.)", "Цена"],
    },
    "Заказы по сотрудникам": {
        "desc": "Количество и сумма заказов, оформленных каждым менеджером",
        "query": """
            SELECT COALESCE(с.фио, '(не указан)') AS сотрудник,
                   с.должность, COUNT(з.id) AS заказов,
                   printf('%.2f', SUM(з.итого)) AS выручка
            FROM Заказы з
            LEFT JOIN Сотрудники с ON з.id_сотрудника = с.id
            WHERE з.статус != 'отменён'
            GROUP BY з.id_сотрудника ORDER BY SUM(з.итого) DESC
        """,
        "columns": ["Сотрудник", "Должность", "Заказов", "Выручка (руб.)"],
    },
    "Статусы доставок": {
        "desc": "Распределение заказов по статусам доставки",
        "query": """
            SELECT д.статус, COUNT(*) AS кол_во,
                   GROUP_CONCAT(д.id_заказа, ', ') AS номера_заказов
            FROM Доставки д GROUP BY д.статус ORDER BY д.статус
        """,
        "columns": ["Статус", "Кол-во", "№ заказов"],
    },
    "Поставки по поставщикам": {
        "desc": "Итоги поставок в разрезе поставщиков",
        "query": """
            SELECT пост.название, COUNT(п.id) AS поставок,
                   printf('%.2f', SUM(п.сумма)) AS итого
            FROM Поставки п
            JOIN Поставщики пост ON п.id_поставщика = пост.id
            GROUP BY пост.id ORDER BY SUM(п.сумма) DESC
        """,
        "columns": ["Поставщик", "Кол-во поставок", "Итого (руб.)"],
    },
}

PARAM_QUERIES = [
    {
        "name": "Товары по категории",
        "desc": "Все товары выбранной категории",
        "params": [("Название категории:", "text", None)],
        "query": """
            SELECT т.id, т.наименование, т.производитель,
                   printf('%.2f', т.цена) AS цена, т.остаток
            FROM Товары т
            JOIN Категории к ON т.id_категории = к.id
            WHERE к.название = ?
            ORDER BY т.наименование
        """,
        "columns": ["ID", "Наименование", "Производитель", "Цена", "Остаток"],
    },
    {
        "name": "Заказы в диапазоне дат",
        "desc": "Заказы за указанный период (формат: ГГГГ-ММ-ДД)",
        "params": [
            ("Дата с (ГГГГ-ММ-ДД):", "text", None),
            ("Дата по (ГГГГ-ММ-ДД):", "text", None),
        ],
        "query": """
            SELECT з.id, к.фио AS клиент, з.дата_заказа,
                   з.статус, printf('%.2f', з.итого) AS итого, з.способ_оплаты
            FROM Заказы з
            JOIN Клиенты к ON з.id_клиента = к.id
            WHERE з.дата_заказа BETWEEN ? AND ?
            ORDER BY з.дата_заказа DESC
        """,
        "columns": ["ID", "Клиент", "Дата", "Статус", "Итого", "Оплата"],
    },
    {
        "name": "Товары по цене (диапазон)",
        "desc": "Товары в заданном ценовом диапазоне",
        "params": [
            ("Цена от (руб.):", "text", None),
            ("Цена до (руб.):", "text", None),
        ],
        "query": """
            SELECT наименование, производитель,
                   printf('%.2f', цена) AS цена, остаток
            FROM Товары
            WHERE цена BETWEEN ? AND ?
            ORDER BY цена
        """,
        "columns": ["Наименование", "Производитель", "Цена", "Остаток"],
    },
    {
        "name": "Поиск клиента по телефону",
        "desc": "Найти клиента по номеру телефона",
        "params": [("Телефон:", "text", None)],
        "query": """
            SELECT id, фио, телефон, email, адрес, дата_регистрации
            FROM Клиенты WHERE телефон = ?
        """,
        "columns": ["ID", "ФИО", "Телефон", "Email", "Адрес", "Дата регистрации"],
    },
    {
        "name": "Заказы клиента по ID",
        "desc": "Все заказы конкретного клиента",
        "params": [("ID клиента:", "text", None)],
        "query": """
            SELECT з.id, з.дата_заказа, з.статус,
                   printf('%.2f', з.итого) AS итого, з.способ_оплаты
            FROM Заказы з
            WHERE з.id_клиента = ?
            ORDER BY з.дата_заказа DESC
        """,
        "columns": ["ID заказа", "Дата", "Статус", "Итого", "Оплата"],
    },
]

def make_result_tree(parent):
    frame = ttk.Frame(parent)
    frame.pack(fill="both", expand=True)
    tree = ttk.Treeview(frame, show="headings", selectmode="browse")
    vsb = ttk.Scrollbar(frame, orient="vertical",   command=tree.yview)
    hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")
    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)
    return tree

def fill_tree(tree, columns, rows):
    tree.configure(columns=columns)
    for col in columns:
        w = max(90, 860 // len(columns))
        tree.heading(col, text=col)
        tree.column(col, width=w, minwidth=55)
    tree.delete(*tree.get_children())
    for row in rows:
        tree.insert("", "end", values=[str(v) if v is not None else "" for v in row])
    return len(rows)

def build_reports_tab(nb, conn):
    tab = ttk.Frame(nb)
    nb.add(tab, text="  📊 Готовые отчёты  ")

    left = ttk.Frame(tab, width=230)
    left.pack(side="left", fill="y", padx=(8, 0), pady=8)
    left.pack_propagate(False)
    ttk.Label(left, text="Отчёты", font=("Arial", 11, "bold")).pack(pady=(4, 6))

    listbox = tk.Listbox(left, selectmode="browse", activestyle="none",
                         font=("Arial", 10), relief="flat", borderwidth=1)
    listbox.pack(fill="both", expand=True)
    for name in REPORTS:
        listbox.insert("end", "  " + name)

    right = ttk.Frame(tab)
    right.pack(side="left", fill="both", expand=True, padx=8, pady=8)

    desc_var = tk.StringVar(value="Выберите отчёт из списка слева")
    ttk.Label(right, textvariable=desc_var, wraplength=700,
              foreground="#555", font=("Arial", 9, "italic")).pack(anchor="w", pady=(0, 6))

    tree = make_result_tree(right)

    status_var = tk.StringVar()
    ttk.Label(right, textvariable=status_var, font=("Arial", 9)).pack(anchor="e", pady=(4, 0))

    def run_report(event=None):
        sel = listbox.curselection()
        if not sel:
            return
        name = list(REPORTS.keys())[sel[0]]
        meta = REPORTS[name]
        desc_var.set(meta["desc"])
        try:
            rows = conn.execute(meta["query"]).fetchall()
            n = fill_tree(tree, meta["columns"], rows)
            status_var.set(f"Записей: {n}")
        except Exception as e:
            status_var.set(f"Ошибка: {e}")

    listbox.bind("<<ListboxSelect>>", run_report)
    listbox.selection_set(0)
    run_report()

def build_params_tab(nb, conn):
    tab = ttk.Frame(nb)
    nb.add(tab, text="  🔍 Запросы с параметрами  ")

    left = ttk.Frame(tab, width=230)
    left.pack(side="left", fill="y", padx=(8, 0), pady=8)
    left.pack_propagate(False)
    ttk.Label(left, text="Запросы", font=("Arial", 11, "bold")).pack(pady=(4, 6))

    listbox = tk.Listbox(left, selectmode="browse", activestyle="none",
                         font=("Arial", 10), relief="flat", borderwidth=1)
    listbox.pack(fill="both", expand=True)
    for q in PARAM_QUERIES:
        listbox.insert("end", "  " + q["name"])

    right = ttk.Frame(tab)
    right.pack(side="left", fill="both", expand=True, padx=8, pady=8)

    desc_var = tk.StringVar(value="Выберите запрос из списка слева")
    ttk.Label(right, textvariable=desc_var, wraplength=680,
              foreground="#555", font=("Arial", 9, "italic")).pack(anchor="w", pady=(0, 4))

    params_frame = ttk.LabelFrame(right, text="Параметры", padding=(8, 4))
    params_frame.pack(fill="x", pady=(0, 6))

    tree = make_result_tree(right)
    status_var = tk.StringVar()
    ttk.Label(right, textvariable=status_var, font=("Arial", 9)).pack(anchor="e", pady=(4, 0))

    param_entries = []

    def on_select(event=None):
        sel = listbox.curselection()
        if not sel:
            return
        meta = PARAM_QUERIES[sel[0]]
        desc_var.set(meta["desc"])

        for widget in params_frame.winfo_children():
            widget.destroy()
        param_entries.clear()

        for i, (label, kind, _) in enumerate(meta["params"]):
            ttk.Label(params_frame, text=label).grid(
                row=i, column=0, sticky="w", padx=(0, 8), pady=3)
            e = ttk.Entry(params_frame, width=30)
            e.grid(row=i, column=1, sticky="ew", pady=3)
            param_entries.append(e)
        params_frame.columnconfigure(1, weight=1)

        btn_row = len(meta["params"])
        ttk.Button(params_frame, text="▶  Выполнить", command=run_query).grid(
            row=btn_row, column=0, columnspan=2, pady=(6, 2))

        tree.delete(*tree.get_children())
        status_var.set("")

    def run_query():
        sel = listbox.curselection()
        if not sel:
            return
        meta = PARAM_QUERIES[sel[0]]
        params = [e.get().strip() for e in param_entries]
        if any(p == "" for p in params):
            status_var.set("⚠  Заполните все поля параметров")
            return
        try:
            typed = []
            for p in params:
                try:
                    typed.append(float(p) if "." in p else int(p))
                except ValueError:
                    typed.append(p)
            rows = conn.execute(meta["query"], typed).fetchall()
            n = fill_tree(tree, meta["columns"], rows)
            status_var.set(f"Найдено записей: {n}")
        except Exception as e:
            status_var.set(f"Ошибка: {e}")

    listbox.bind("<<ListboxSelect>>", on_select)
    listbox.selection_set(0)
    on_select()

def open_reports_window(conn, parent):
    win = tk.Toplevel(parent)
    win.title("Аналитика и запросы")
    win.geometry("1050x600")
    win.minsize(850, 480)

    nb = ttk.Notebook(win)
    nb.pack(fill="both", expand=True, padx=6, pady=6)

    build_reports_tab(nb, conn)
    build_params_tab(nb, conn)
