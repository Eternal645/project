"""
ui_tables.py — универсальное окно просмотра/редактирования таблиц.

Все SQL-запросы вынесены в sql/queries.sql и загружаются через get_query().
"""

import tkinter as tk
from tkinter import ttk, messagebox
from app.ui_order_form import open_order_form
from app.database import get_query

# Мета-описания таблиц (запросы берутся из queries.sql)

TABLE_META = {
    "Категории": {
        "query_key": "table_категории",
        "columns": ["ID", "Название", "Описание"],
        "fields": [
            ("Название", "название", "entry"),
            ("Описание", "описание", "entry"),
        ],
        "table": "Категории",
        "pk": "id",
    },
    "Места хранения": {
        "query_key": "table_места_хранения",
        "columns": ["ID", "Название", "Описание"],
        "fields": [
            ("Название", "название", "entry"),
            ("Описание", "описание", "entry"),
        ],
        "table": "МестаХранения",
        "pk": "id",
    },
    "Поставщики": {
        "query_key": "table_поставщики",
        "columns": ["ID", "Название", "Контактное лицо", "Телефон", "Email"],
        "fields": [
            ("Название",        "название",        "entry"),
            ("Контактное лицо", "контактное_лицо", "entry"),
            ("Телефон",         "телефон",         "entry"),
            ("Email",           "email",           "entry"),
        ],
        "table": "Поставщики",
        "pk": "id",
    },
    "Товары": {
        "query_key": "table_товары",
        "columns": ["ID", "Категория", "Наименование", "Производитель", "Цена", "Остаток", "Место хранения", "Описание"],
        "fields": [
            ("Категория",      "id_категории",       "combo:Категории"),
            ("Наименование",   "наименование",        "entry"),
            ("Производитель",  "производитель",       "entry"),
            ("Цена",           "цена",                "entry"),
            ("Остаток",        "остаток",             "entry"),
            ("Место хранения", "id_места_хранения",  "combo:МестаХранения"),
            ("Описание",       "описание",            "entry"),
        ],
        "table": "Товары",
        "pk": "id",
    },
    "Клиенты": {
        "query_key": "table_клиенты",
        "columns": ["ID", "ФИО", "Телефон", "Email", "Адрес", "Дата регистрации"],
        "fields": [
            ("ФИО",              "фио",              "entry"),
            ("Телефон",          "телефон",          "entry"),
            ("Email",            "email",            "entry"),
            ("Адрес",            "адрес",            "entry"),
            ("Дата регистрации", "дата_регистрации", "entry"),
        ],
        "table": "Клиенты",
        "pk": "id",
    },
    "Сотрудники": {
        "query_key": "table_сотрудники",
        "columns": ["ID", "ФИО", "Должность", "Телефон", "Зарплата"],
        "fields": [
            ("ФИО",       "фио",       "entry"),
            ("Должность", "должность", "entry"),
            ("Телефон",   "телефон",   "entry"),
            ("Зарплата",  "зарплата",  "entry"),
        ],
        "table": "Сотрудники",
        "pk": "id",
    },
    "Заказы": {
        "query_key": "table_заказы",
        "columns": ["ID", "Клиент", "Сотрудник", "Дата", "Статус", "Итого", "Оплата"],
        "fields": [
            ("Клиент",        "id_клиента",        "combo:Клиенты"),
            ("Сотрудник",     "id_сотрудника",     "combo:Сотрудники"),
            ("Дата заказа",   "дата_заказа",       "entry"),
            ("Статус",        "id_статуса",        "combo:СтатусыЗаказа"),
            ("Итого",         "итого",             "entry"),
            ("Способ оплаты", "id_способа_оплаты", "combo:СпособыОплаты"),
        ],
        "table": "Заказы",
        "pk": "id",
    },
    "Строки заказа": {
        "query_key": "table_строки_заказа",
        "columns": ["ID", "№ заказа", "Товар", "Кол-во", "Цена ед.", "Сумма"],
        "fields": [
            ("№ заказа", "id_заказа",    "entry"),
            ("Товар",    "id_товара",    "combo:Товары"),
            ("Кол-во",   "количество",  "entry"),
            ("Цена ед.", "цена_единицы","entry"),
        ],
        "table": "СтрокиЗаказа",
        "pk": "id",
    },
    "Поставки": {
        "query_key": "table_поставки",
        "columns": ["ID", "Поставщик", "Дата", "Сумма"],
        "fields": [
            ("Поставщик", "id_поставщика", "combo:Поставщики"),
            ("Дата",      "дата_поставки", "entry"),
            ("Сумма",     "сумма",         "entry"),
        ],
        "table": "Поставки",
        "pk": "id",
    },
    "Доставки": {
        "query_key": "table_доставки",
        "columns": ["ID", "№ заказа", "Клиент", "Адрес", "Дата", "Курьер", "Статус"],
        "fields": [
            ("№ заказа", "id_заказа",           "entry"),
            ("Адрес",    "адрес_доставки",      "entry"),
            ("Дата",     "дата_доставки",       "entry"),
            ("Курьер",   "курьер",              "entry"),
            ("Статус",   "id_статуса_доставки", "combo:СтатусыДоставки"),
        ],
        "table": "Доставки",
        "pk": "id",
    },
}

# Соответствие combo-источника → ключу запроса в queries.sql
_COMBO_QUERY_KEYS = {
    "СтатусыЗаказа":   "combo_статусы_заказа",
    "СпособыОплаты":   "combo_способы_оплаты",
    "СтатусыДоставки": "combo_статусы_доставки",
    "МестаХранения":   "combo_места_хранения",
    "Категории":       "combo_категории",
    "Клиенты":         "combo_клиенты",
    "Сотрудники":      "combo_сотрудники",
    "Поставщики":      "combo_поставщики",
    "Товары":          "combo_товары",
}

# Загрузка значений combo из БД

def _load_combo_values(conn, kind):
    """Возвращает [(display_text, id), ...] для FK-комбобокса."""
    key = _COMBO_QUERY_KEYS.get(kind)
    if key:
        rows = conn.execute(get_query(key)).fetchall()
        return [(r[1], r[0]) for r in rows]
    return []

# Открытие окна таблицы

def open_table_window(conn, parent, table_name):
    meta = TABLE_META.get(table_name)
    if not meta:
        messagebox.showerror("Ошибка", f"Таблица '{table_name}' не найдена")
        return

    win = tk.Toplevel(parent)
    win.title(table_name)
    win.geometry("960x540")
    win.minsize(700, 400)

    toolbar = ttk.Frame(win)
    toolbar.pack(fill="x", padx=8, pady=(8, 0))

    search_var = tk.StringVar()
    ttk.Label(toolbar, text="Поиск:").pack(side="left")
    ttk.Entry(toolbar, textvariable=search_var, width=28).pack(side="left", padx=(4, 12))

    if table_name == "Заказы":
        def _refresh_orders():
            _refresh(conn, meta, tree, search_var.get())
        ttk.Button(toolbar, text="➕ Добавить",
                   command=lambda: open_order_form(conn, win, _refresh_orders, None)
                   ).pack(side="left", padx=2)
        ttk.Button(toolbar, text="✏️ Изменить",
                   command=lambda: _edit_order_selected(conn, win, tree, _refresh_orders)
                   ).pack(side="left", padx=2)
    else:
        ttk.Button(toolbar, text="➕ Добавить",
                   command=lambda: _open_form(conn, win, meta, tree, None)).pack(side="left", padx=2)
        ttk.Button(toolbar, text="✏️ Изменить",
                   command=lambda: _edit_selected(conn, win, meta, tree)).pack(side="left", padx=2)

    ttk.Button(toolbar, text="🗑 Удалить",  command=lambda: _delete_selected(conn, win, meta, tree)).pack(side="left", padx=2)
    ttk.Button(toolbar, text="🔄 Обновить", command=lambda: _refresh(conn, meta, tree, search_var.get())).pack(side="left", padx=2)

    frame = ttk.Frame(win)
    frame.pack(fill="both", expand=True, padx=8, pady=8)

    cols = meta["columns"]
    tree = ttk.Treeview(frame, columns=cols, show="headings", selectmode="browse")
    col_width = max(70, 920 // len(cols))
    for col in cols:
        tree.heading(col, text=col, command=lambda c=col: _sort_tree(tree, c))
        tree.column(col, width=col_width, minwidth=50)

    vsb = ttk.Scrollbar(frame, orient="vertical",   command=tree.yview)
    hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")
    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)

    if table_name == "Заказы":
        tree.bind("<Double-1>", lambda e: _edit_order_selected(conn, win, tree, _refresh_orders))
    else:
        tree.bind("<Double-1>", lambda e: _edit_selected(conn, win, meta, tree))

    search_var.trace_add("write", lambda *_: _refresh(conn, meta, tree, search_var.get()))
    _refresh(conn, meta, tree, "")


def _refresh(conn, meta, tree, search=""):
    tree.delete(*tree.get_children())
    rows = conn.execute(get_query(meta["query_key"])).fetchall()
    q = search.strip().lower()
    for row in rows:
        vals = [str(v) if v is not None else "" for v in row]
        if q and not any(q in v.lower() for v in vals):
            continue
        tree.insert("", "end", values=vals)


def _sort_tree(tree, col):
    data = [(tree.set(k, col), k) for k in tree.get_children("")]
    try:
        data.sort(key=lambda t: float(t[0].replace(" ", "").replace(",", ".")))
    except ValueError:
        data.sort(key=lambda t: t[0].lower())
    for i, (_, k) in enumerate(data):
        tree.move(k, "", i)


def _edit_selected(conn, win, meta, tree):
    sel = tree.selection()
    if not sel:
        messagebox.showinfo("Подсказка", "Выберите строку для редактирования")
        return
    row_id = tree.item(sel[0])["values"][0]
    _open_form(conn, win, meta, tree, row_id)


def _delete_selected(conn, win, meta, tree):
    sel = tree.selection()
    if not sel:
        messagebox.showinfo("Подсказка", "Выберите строку для удаления")
        return
    row_id = tree.item(sel[0])["values"][0]
    if not messagebox.askyesno("Удаление", f"Удалить запись #{row_id}?"):
        return
    try:
        conn.execute(f"DELETE FROM {meta['table']} WHERE {meta['pk']}=?", (row_id,))
        conn.commit()
        _refresh(conn, meta, tree, "")
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))


def _open_form(conn, parent, meta, tree, row_id):
    """Универсальная форма добавления/редактирования."""
    is_edit = row_id is not None
    title = f"{'Редактировать' if is_edit else 'Добавить'} — {meta['table']}"

    form = tk.Toplevel(parent)
    form.title(title)
    form.resizable(False, False)
    form.grab_set()

    existing = {}
    if is_edit:
        row = conn.execute(
            f"SELECT * FROM {meta['table']} WHERE {meta['pk']}=?", (row_id,)
        ).fetchone()
        if row:
            existing = dict(row)

    widgets = {}

    for i, (label, field, kind) in enumerate(meta["fields"]):
        ttk.Label(form, text=label + ":", anchor="e", width=18).grid(
            row=i, column=0, padx=(12, 4), pady=6, sticky="e"
        )
        val = existing.get(field, "")

        if kind.startswith("combo:"):
            source = kind.split(":", 1)[1]
            options_raw = _load_combo_values(conn, source)
            display_vals = [o[0] for o in options_raw]
            cmap     = {o[0]: o[1] for o in options_raw}
            rev_map  = {str(o[1]): o[0] for o in options_raw}

            var = tk.StringVar(value=rev_map.get(str(val), str(val) if val else ""))
            cb = ttk.Combobox(form, textvariable=var, values=display_vals,
                              state="readonly", width=32)
            cb.grid(row=i, column=1, padx=(0, 12), pady=6, sticky="ew")
            widgets[field] = (var, cmap)
        else:
            var = tk.StringVar(value=str(val) if val is not None else "")
            ttk.Entry(form, textvariable=var, width=34).grid(
                row=i, column=1, padx=(0, 12), pady=6, sticky="ew"
            )
            widgets[field] = (var, None)

    def save():
        values = {}
        for field, (var, cmap) in widgets.items():
            raw = var.get().strip()
            values[field] = cmap.get(raw, raw) if cmap else (raw or None)

        cols = list(values.keys())
        vals = [values[c] for c in cols]
        try:
            if is_edit:
                set_clause = ", ".join(f"{c}=?" for c in cols)
                conn.execute(
                    f"UPDATE {meta['table']} SET {set_clause} WHERE {meta['pk']}=?",
                    vals + [row_id],
                )
            else:
                placeholders = ", ".join("?" for _ in cols)
                conn.execute(
                    f"INSERT INTO {meta['table']}({', '.join(cols)}) VALUES({placeholders})",
                    vals,
                )

            # Если сохраняем доставку со статусом is_delivered=1 - ставим заказу статус «выполнен»
            if meta["table"] == "Доставки":
                new_delivery_status_id = values.get("id_статуса_доставки")
                if new_delivery_status_id:
                    ds = conn.execute(
                        "SELECT is_delivered FROM СтатусыДоставки WHERE id=?",
                        (new_delivery_status_id,)
                    ).fetchone()
                    if ds and ds["is_delivered"]:
                        # Получаем id_заказа из текущей записи доставки
                        if is_edit:
                            d_row = conn.execute(
                                "SELECT id_заказа FROM Доставки WHERE id=?", (row_id,)
                            ).fetchone()
                        else:
                            d_row = conn.execute(
                                "SELECT id_заказа FROM Доставки WHERE id=last_insert_rowid()"
                            ).fetchone()
                        if d_row:
                            final = conn.execute(
                                "SELECT id FROM СтатусыЗаказа WHERE is_final=1 LIMIT 1"
                            ).fetchone()
                            if final:
                                conn.execute(
                                    "UPDATE Заказы SET id_статуса=? WHERE id=?",
                                    (final["id"], d_row["id_заказа"]),
                                )

            conn.commit()
            _refresh(conn, meta, tree, "")
            form.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", str(e))

    n = len(meta["fields"])
    btn_frame = ttk.Frame(form)
    btn_frame.grid(row=n, column=0, columnspan=2, pady=12)
    ttk.Button(btn_frame, text="💾 Сохранить", command=save, width=16).pack(side="left", padx=6)
    ttk.Button(btn_frame, text="Отмена",       command=form.destroy, width=10).pack(side="left", padx=6)


def _edit_order_selected(conn, win, tree, refresh_cb):
    sel = tree.selection()
    if not sel:
        messagebox.showinfo("Подсказка", "Выберите строку для редактирования", parent=win)
        return
    order_id = int(tree.item(sel[0])["values"][0])
    open_order_form(conn, win, refresh_cb, order_id)
