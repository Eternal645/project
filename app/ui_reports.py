"""
Окно аналитики и отчётов.

SQL-запросы хранятся в sql/queries.sql, а этот модуль содержит только
описания экранов, параметры и отображаемые колонки.
"""

import tkinter as tk
from tkinter import ttk

from app.database import get_query


REPORTS = {
    "Выручка по месяцам": {
        "desc": "Сумма выполненных заказов, сгруппированная по году и месяцу",
        "query_name": "report_выручка_по_месяцам",
        "columns": ["Период", "Кол-во заказов", "Выручка (руб.)"],
    },
    "ТОП-10 товаров по продажам": {
        "desc": "Самые продаваемые позиции: количество, выручка, доля в общей выручке",
        "query_name": "report_топ10_товаров",
        "columns": ["Товар", "Категория", "Продано (шт.)", "Выручка (руб.)", "Доля"],
    },
    "Местонахождение товаров": {
        "desc": "Где хранится каждый товар: склад/секция, остаток",
        "query_name": "report_местонахождение_товаров",
        "columns": ["Товар", "Категория", "Место хранения", "Описание места", "Остаток (шт.)"],
    },
    "VIP-клиенты (сумма > 50 000)": {
        "desc": "Клиенты с суммарной стоимостью заказов свыше 50 000 руб.",
        "query_name": "report_vip_клиенты",
        "columns": ["ФИО клиента", "Телефон", "Заказов", "Сумма (руб.)"],
    },
    "Остатки на складе": {
        "desc": "Текущее количество товаров на складе по категориям",
        "query_name": "report_остатки_на_складе",
        "columns": ["Категория", "Товар", "Место", "Остаток (шт.)", "Цена", "Стоимость запаса"],
    },
    "Критически малый остаток (< 4 шт.)": {
        "desc": "Товары, которые нужно срочно дозаказать",
        "query_name": "report_малый_остаток",
        "columns": ["Категория", "Товар", "Место", "Остаток (шт.)", "Цена"],
    },
    "Заказы по сотрудникам": {
        "desc": "Количество и сумма заказов, оформленных каждым менеджером",
        "query_name": "report_заказы_по_сотрудникам",
        "columns": ["Сотрудник", "Должность", "Заказов", "Выручка (руб.)"],
    },
    "Статусы доставок": {
        "desc": "Распределение заказов по статусам доставки",
        "query_name": "report_статусы_доставок",
        "columns": ["Статус", "Кол-во", "№ заказов"],
    },
    "Поставки по поставщикам": {
        "desc": "Итоги поставок в разрезе поставщиков",
        "query_name": "report_поставки_по_поставщикам",
        "columns": ["Поставщик", "Кол-во поставок", "Итого (руб.)"],
    },
}


PARAM_QUERIES = [
    {
        "name": "Товары по категории",
        "desc": "Все товары выбранной категории с местом хранения",
        "params": [("Название категории:", "text")],
        "query_name": "param_товары_по_категории",
        "columns": ["ID", "Наименование", "Производитель", "Цена", "Остаток", "Место хранения"],
    },
    {
        "name": "Заказы в диапазоне дат",
        "desc": "Заказы за указанный период (формат: ГГГГ-ММ-ДД)",
        "params": [("Дата с (ГГГГ-ММ-ДД):", "text"), ("Дата по (ГГГГ-ММ-ДД):", "text")],
        "query_name": "param_заказы_по_датам",
        "columns": ["ID", "Клиент", "Дата", "Статус", "Итого", "Оплата"],
    },
    {
        "name": "Товары по цене (диапазон)",
        "desc": "Товары в заданном ценовом диапазоне с местом хранения",
        "params": [("Цена от (руб.):", "number"), ("Цена до (руб.):", "number")],
        "query_name": "param_товары_по_цене",
        "columns": ["Наименование", "Производитель", "Цена", "Остаток", "Место"],
    },
    {
        "name": "Поиск клиента по телефону",
        "desc": "Найти клиента по номеру телефона",
        "params": [("Телефон:", "text")],
        "query_name": "param_клиент_по_телефону",
        "columns": ["ID", "ФИО", "Телефон", "Email", "Адрес", "Дата регистрации"],
    },
    {
        "name": "Заказы клиента по ID",
        "desc": "Все заказы конкретного клиента",
        "params": [("ID клиента:", "number")],
        "query_name": "param_заказы_клиента",
        "columns": ["ID заказа", "Дата", "Статус", "Итого", "Оплата"],
    },
    {
        "name": "Местонахождение конкретного товара",
        "desc": "Найти, где хранится товар (по части названия)",
        "params": [("Часть названия товара:", "text")],
        "query_name": "param_поиск_товара",
        "columns": ["Наименование", "Категория", "Место хранения", "Описание места", "Остаток"],
    },
]


PROFIT_QUERIES = {
    "Неделя": {
        "income_query_name": "profit_доход_неделя",
        "expense_query_name": "profit_расход_неделя",
    },
    "Месяц": {
        "income_query_name": "profit_доход_месяц",
        "expense_query_name": "profit_расход_месяц",
    },
    "Год": {
        "income_query_name": "profit_доход_год",
        "expense_query_name": "profit_расход_год",
    },
}


def _make_result_tree(parent):
    frame = ttk.Frame(parent)
    frame.pack(fill="both", expand=True)

    tree = ttk.Treeview(frame, show="headings", selectmode="browse")
    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")
    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)

    return tree


def _fill_tree(tree, columns, rows):
    tree.configure(columns=columns)
    width = max(90, 860 // max(len(columns), 1))

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=width, minwidth=55)

    tree.delete(*tree.get_children())
    for row in rows:
        tree.insert("", "end", values=[str(value) if value is not None else "" for value in row])

    return len(rows)


def _parse_param(value, kind):
    if kind != "number":
        return value
    try:
        return float(value) if "." in value else int(value)
    except ValueError:
        return value


def build_profit_tab(nb, conn):
    tab = ttk.Frame(nb)
    nb.add(tab, text="  Прибыль по периодам  ")

    top = ttk.Frame(tab)
    top.pack(fill="x", padx=8, pady=8)

    ttk.Label(top, text="Группировка:", font=("Arial", 10, "bold")).pack(side="left")
    period_var = tk.StringVar(value="Месяц")

    for period in PROFIT_QUERIES:
        ttk.Radiobutton(
            top,
            text=period,
            variable=period_var,
            value=period,
            command=lambda: _run_profit(),
        ).pack(side="left", padx=6)

    summary_frame = ttk.LabelFrame(tab, text="Итого за все периоды", padding=(8, 4))
    summary_frame.pack(fill="x", padx=8, pady=(0, 6))

    lbl_income = ttk.Label(summary_frame, text="Доход:    -", font=("Arial", 10))
    lbl_expense = ttk.Label(summary_frame, text="Расход:   -", font=("Arial", 10))
    lbl_profit = ttk.Label(summary_frame, text="Прибыль:  -", font=("Arial", 10, "bold"))
    lbl_income.grid(row=0, column=0, padx=20, sticky="w")
    lbl_expense.grid(row=0, column=1, padx=20, sticky="w")
    lbl_profit.grid(row=0, column=2, padx=20, sticky="w")

    columns = ["Период", "Доход (руб.)", "Расход (руб.)", "Прибыль (руб.)"]
    tree = _make_result_tree(tab)
    status_var = tk.StringVar()
    ttk.Label(tab, textvariable=status_var, font=("Arial", 9)).pack(anchor="e", padx=8, pady=(2, 4))

    def _run_profit():
        meta = PROFIT_QUERIES[period_var.get()]
        try:
            income_rows = {
                row["период"]: row["доход"]
                for row in conn.execute(get_query(meta["income_query_name"])).fetchall()
            }
            expense_rows = {
                row["период"]: row["расход"]
                for row in conn.execute(get_query(meta["expense_query_name"])).fetchall()
            }
            periods = sorted(set(income_rows) | set(expense_rows))

            rows = []
            total_income = 0.0
            total_expense = 0.0
            for period in periods:
                income = income_rows.get(period, 0.0) or 0.0
                expense = expense_rows.get(period, 0.0) or 0.0
                profit = income - expense
                total_income += income
                total_expense += expense
                rows.append((period, f"{income:,.2f}", f"{expense:,.2f}", f"{profit:,.2f}"))

            _fill_tree(tree, columns, rows)
            total_profit = total_income - total_expense
            lbl_income.configure(text=f"Доход:    {total_income:,.2f} руб.")
            lbl_expense.configure(text=f"Расход:   {total_expense:,.2f} руб.")
            lbl_profit.configure(
                text=f"Прибыль:  {total_profit:,.2f} руб.",
                foreground="#2a6e2a" if total_profit >= 0 else "#8a1a1a",
            )
            status_var.set(f"Периодов: {len(rows)}")
        except Exception as exc:
            status_var.set(f"Ошибка: {exc}")

    _run_profit()


def build_reports_tab(nb, conn):
    tab = ttk.Frame(nb)
    nb.add(tab, text="  Готовые отчёты  ")

    left = ttk.Frame(tab, width=240)
    left.pack(side="left", fill="y", padx=(8, 0), pady=8)
    left.pack_propagate(False)
    ttk.Label(left, text="Отчёты", font=("Arial", 11, "bold")).pack(pady=(4, 6))

    listbox = tk.Listbox(left, selectmode="browse", activestyle="none", font=("Arial", 10), relief="flat")
    listbox.pack(fill="both", expand=True)
    for name in REPORTS:
        listbox.insert("end", "  " + name)

    right = ttk.Frame(tab)
    right.pack(side="left", fill="both", expand=True, padx=8, pady=8)

    desc_var = tk.StringVar(value="Выберите отчёт из списка слева")
    ttk.Label(right, textvariable=desc_var, wraplength=700, foreground="#555").pack(anchor="w", pady=(0, 6))

    tree = _make_result_tree(right)
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
            rows = conn.execute(get_query(meta["query_name"])).fetchall()
            count = _fill_tree(tree, meta["columns"], rows)
            status_var.set(f"Записей: {count}")
        except Exception as exc:
            status_var.set(f"Ошибка: {exc}")

    listbox.bind("<<ListboxSelect>>", run_report)
    listbox.selection_set(0)
    run_report()


def build_params_tab(nb, conn):
    tab = ttk.Frame(nb)
    nb.add(tab, text="  Запросы с параметрами  ")

    left = ttk.Frame(tab, width=240)
    left.pack(side="left", fill="y", padx=(8, 0), pady=8)
    left.pack_propagate(False)
    ttk.Label(left, text="Запросы", font=("Arial", 11, "bold")).pack(pady=(4, 6))

    listbox = tk.Listbox(left, selectmode="browse", activestyle="none", font=("Arial", 10), relief="flat")
    listbox.pack(fill="both", expand=True)
    for query in PARAM_QUERIES:
        listbox.insert("end", "  " + query["name"])

    right = ttk.Frame(tab)
    right.pack(side="left", fill="both", expand=True, padx=8, pady=8)

    desc_var = tk.StringVar(value="Выберите запрос из списка слева")
    ttk.Label(right, textvariable=desc_var, wraplength=680, foreground="#555").pack(anchor="w", pady=(0, 4))

    params_frame = ttk.LabelFrame(right, text="Параметры", padding=(8, 4))
    params_frame.pack(fill="x", pady=(0, 6))

    tree = _make_result_tree(right)
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

        for row_number, (label, kind) in enumerate(meta["params"]):
            ttk.Label(params_frame, text=label).grid(row=row_number, column=0, sticky="w", padx=(0, 8), pady=3)
            entry = ttk.Entry(params_frame, width=30)
            entry.grid(row=row_number, column=1, sticky="ew", pady=3)
            param_entries.append((entry, kind))

        params_frame.columnconfigure(1, weight=1)
        ttk.Button(params_frame, text="Выполнить", command=run_query).grid(
            row=len(meta["params"]),
            column=0,
            columnspan=2,
            pady=(6, 2),
        )
        tree.delete(*tree.get_children())
        status_var.set("")

    def run_query():
        sel = listbox.curselection()
        if not sel:
            return

        meta = PARAM_QUERIES[sel[0]]
        raw_params = [entry.get().strip() for entry, _ in param_entries]
        if any(param == "" for param in raw_params):
            status_var.set("Заполните все поля параметров")
            return

        typed_params = [
            _parse_param(entry.get().strip(), kind)
            for entry, kind in param_entries
        ]

        try:
            rows = conn.execute(get_query(meta["query_name"]), typed_params).fetchall()
            count = _fill_tree(tree, meta["columns"], rows)
            status_var.set(f"Найдено записей: {count}")
        except Exception as exc:
            status_var.set(f"Ошибка: {exc}")

    listbox.bind("<<ListboxSelect>>", on_select)
    listbox.selection_set(0)
    on_select()


def open_reports_window(conn, parent):
    win = tk.Toplevel(parent)
    win.title("Аналитика и отчёты")
    win.geometry("1100x640")
    win.minsize(900, 520)

    notebook = ttk.Notebook(win)
    notebook.pack(fill="both", expand=True, padx=6, pady=6)

    build_profit_tab(notebook, conn)
    build_reports_tab(notebook, conn)
    build_params_tab(notebook, conn)
