import tkinter as tk
from tkinter import ttk, messagebox
from app.ui_order_form import open_order_form

TABLE_META = {
    "Категории": {
        "query": "SELECT id, название, описание FROM Категории ORDER BY название",
        "columns": ["ID", "Название", "Описание"],
        "fields": [
            ("Название",  "название",  "entry"),
            ("Описание",  "описание",  "entry"),
        ],
        "table": "Категории",
        "pk": "id",
    },
    "Поставщики": {
        "query": "SELECT id, название, контактное_лицо, телефон, email FROM Поставщики ORDER BY название",
        "columns": ["ID", "Название", "Контактное лицо", "Телефон", "Email"],
        "fields": [
            ("Название",          "название",          "entry"),
            ("Контактное лицо",   "контактное_лицо",   "entry"),
            ("Телефон",           "телефон",           "entry"),
            ("Email",             "email",             "entry"),
        ],
        "table": "Поставщики",
        "pk": "id",
    },
    "Товары": {
        "query": """
            SELECT т.id, к.название, т.наименование, т.производитель,
                   т.цена, т.остаток, т.описание
            FROM Товары т
            JOIN Категории к ON т.id_категории = к.id
            ORDER BY к.название, т.наименование
        """,
        "columns": ["ID", "Категория", "Наименование", "Производитель", "Цена", "Остаток", "Описание"],
        "fields": [
            ("Категория",     "id_категории",  "combo:Категории"),
            ("Наименование",  "наименование",  "entry"),
            ("Производитель", "производитель", "entry"),
            ("Цена",          "цена",          "entry"),
            ("Остаток",       "остаток",       "entry"),
            ("Описание",      "описание",      "entry"),
        ],
        "table": "Товары",
        "pk": "id",
    },
    "Клиенты": {
        "query": "SELECT id, фио, телефон, email, адрес, дата_регистрации FROM Клиенты ORDER BY фио",
        "columns": ["ID", "ФИО", "Телефон", "Email", "Адрес", "Дата регистрации"],
        "fields": [
            ("ФИО",               "фио",               "entry"),
            ("Телефон",           "телефон",           "entry"),
            ("Email",             "email",             "entry"),
            ("Адрес",             "адрес",             "entry"),
            ("Дата регистрации",  "дата_регистрации",  "entry"),
        ],
        "table": "Клиенты",
        "pk": "id",
    },
    "Сотрудники": {
        "query": "SELECT id, фио, должность, телефон, зарплата FROM Сотрудники ORDER BY фио",
        "columns": ["ID", "ФИО", "Должность", "Телефон", "Зарплата"],
        "fields": [
            ("ФИО",        "фио",        "entry"),
            ("Должность",  "должность",  "entry"),
            ("Телефон",    "телефон",    "entry"),
            ("Зарплата",   "зарплата",   "entry"),
        ],
        "table": "Сотрудники",
        "pk": "id",
    },
    "Заказы": {
        "query": """
            SELECT з.id, к.фио, с.фио, з.дата_заказа,
                   з.статус, з.итого, з.способ_оплаты
            FROM Заказы з
            JOIN Клиенты к ON з.id_клиента = к.id
            LEFT JOIN Сотрудники с ON з.id_сотрудника = с.id
            ORDER BY з.дата_заказа DESC
        """,
        "columns": ["ID", "Клиент", "Сотрудник", "Дата", "Статус", "Итого", "Оплата"],
        "fields": [
            ("Клиент",         "id_клиента",    "combo:Клиенты"),
            ("Сотрудник",      "id_сотрудника", "combo:Сотрудники"),
            ("Дата заказа",    "дата_заказа",   "entry"),
            ("Статус",         "статус",        "combo:статус_заказа"),
            ("Итого",          "итого",         "entry"),
            ("Способ оплаты",  "способ_оплаты", "combo:способ_оплаты"),
        ],
        "table": "Заказы",
        "pk": "id",
    },
    "Строки заказа": {
        "query": """
            SELECT сз.id, з.id, т.наименование, сз.количество, сз.цена_единицы,
                   (сз.количество * сз.цена_единицы) AS сумма
            FROM СтрокиЗаказа сз
            JOIN Заказы з ON сз.id_заказа = з.id
            JOIN Товары т ON сз.id_товара = т.id
            ORDER BY з.id, сз.id
        """,
        "columns": ["ID", "№ заказа", "Товар", "Кол-во", "Цена ед.", "Сумма"],
        "fields": [
            ("№ заказа",   "id_заказа",    "entry"),
            ("Товар",      "id_товара",    "combo:Товары"),
            ("Кол-во",     "количество",   "entry"),
            ("Цена ед.",   "цена_единицы", "entry"),
        ],
        "table": "СтрокиЗаказа",
        "pk": "id",
    },
    "Поставки": {
        "query": """
            SELECT п.id, пост.название, п.дата_поставки, п.сумма
            FROM Поставки п
            JOIN Поставщики пост ON п.id_поставщика = пост.id
            ORDER BY п.дата_поставки DESC
        """,
        "columns": ["ID", "Поставщик", "Дата", "Сумма"],
        "fields": [
            ("Поставщик",   "id_поставщика",  "combo:Поставщики"),
            ("Дата",        "дата_поставки",  "entry"),
            ("Сумма",       "сумма",          "entry"),
        ],
        "table": "Поставки",
        "pk": "id",
    },
    "Доставки": {
        "query": """
            SELECT д.id, д.id_заказа, к.фио, д.адрес_доставки,
                   д.дата_доставки, д.курьер, д.статус
            FROM Доставки д
            JOIN Заказы з ON д.id_заказа = з.id
            JOIN Клиенты к ON з.id_клиента = к.id
            ORDER BY д.дата_доставки DESC
        """,
        "columns": ["ID", "№ заказа", "Клиент", "Адрес", "Дата", "Курьер", "Статус"],
        "fields": [
            ("№ заказа",  "id_заказа",       "entry"),
            ("Адрес",     "адрес_доставки",  "entry"),
            ("Дата",      "дата_доставки",   "entry"),
            ("Курьер",    "курьер",          "entry"),
            ("Статус",    "статус",          "combo:статус_доставки"),
        ],
        "table": "Доставки",
        "pk": "id",
    },
}

STATIC_COMBOS = {
    "статус_заказа":  ["новый", "в обработке", "доставляется", "выполнен", "отменён"],
    "способ_оплаты":  ["наличные", "карта", "онлайн"],
    "статус_доставки":["запланирована", "в пути", "доставлена"],
}

def _load_combo_values(conn, kind):
    """Return list of (display_text, id) for a FK combo."""
    if kind in STATIC_COMBOS:
        return [(v, v) for v in STATIC_COMBOS[kind]]
    table = kind
    if table == "Товары":
        rows = conn.execute("SELECT id, наименование FROM Товары ORDER BY наименование").fetchall()
        return [(r["наименование"], r["id"]) for r in rows]
    if table == "Категории":
        rows = conn.execute("SELECT id, название FROM Категории ORDER BY название").fetchall()
        return [(r["название"], r["id"]) for r in rows]
    if table == "Клиенты":
        rows = conn.execute("SELECT id, фио FROM Клиенты ORDER BY фио").fetchall()
        return [(r["фио"], r["id"]) for r in rows]
    if table == "Сотрудники":
        rows = conn.execute("SELECT id, фио FROM Сотрудники ORDER BY фио").fetchall()
        return [(r["фио"], r["id"]) for r in rows]
    if table == "Поставщики":
        rows = conn.execute("SELECT id, название FROM Поставщики ORDER BY название").fetchall()
        return [(r["название"], r["id"]) for r in rows]
    return []

def open_table_window(conn, parent, table_name):
    meta = TABLE_META.get(table_name)
    if not meta:
        messagebox.showerror("Ошибка", f"Таблица '{table_name}' не найдена")
        return

    win = tk.Toplevel(parent)
    win.title(table_name)
    win.geometry("900x520")
    win.minsize(700, 400)

    toolbar = ttk.Frame(win)
    toolbar.pack(fill="x", padx=8, pady=(8, 0))

    search_var = tk.StringVar()
    ttk.Label(toolbar, text="Поиск:").pack(side="left")
    search_entry = ttk.Entry(toolbar, textvariable=search_var, width=28)
    search_entry.pack(side="left", padx=(4, 12))

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
        ttk.Button(toolbar, text="➕ Добавить",   command=lambda: _open_form(conn, win, meta, tree, None)).pack(side="left", padx=2)
        ttk.Button(toolbar, text="✏️ Изменить",   command=lambda: _edit_selected(conn, win, meta, tree)).pack(side="left", padx=2)
    ttk.Button(toolbar, text="🗑 Удалить",    command=lambda: _delete_selected(conn, win, meta, tree)).pack(side="left", padx=2)
    ttk.Button(toolbar, text="🔄 Обновить",   command=lambda: _refresh(conn, meta, tree, search_var.get())).pack(side="left", padx=2)

    frame = ttk.Frame(win)
    frame.pack(fill="both", expand=True, padx=8, pady=8)

    cols = meta["columns"]
    tree = ttk.Treeview(frame, columns=cols, show="headings", selectmode="browse")

    col_width = max(70, 860 // len(cols))
    for col in cols:
        tree.heading(col, text=col, command=lambda c=col: _sort_tree(tree, c))
        tree.column(col, width=col_width, minwidth=50)

    vsb = ttk.Scrollbar(frame, orient="vertical",   command=tree.yview)
    hsb = ttk.Scrollbar(frame, orient="horizontal",  command=tree.xview)
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

    def on_search(*_):
        _refresh(conn, meta, tree, search_var.get())
    search_var.trace_add("write", on_search)

    _refresh(conn, meta, tree, "")

def _refresh(conn, meta, tree, search=""):
    tree.delete(*tree.get_children())
    rows = conn.execute(meta["query"]).fetchall()
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
    if not messagebox.askyesno("Удаление", f"Удалить запись "):
        return
    try:
        conn.execute(f"DELETE FROM {meta['table']} WHERE {meta['pk']}=?", (row_id,))
        conn.commit()
        _refresh(conn, meta, tree, "")
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

def _open_form(conn, parent, meta, tree, row_id):
    """Universal add/edit form."""
    is_edit = row_id is not None
    title = f"{'Редактировать' if is_edit else 'Добавить'} — {meta['table']}"

    form = tk.Toplevel(parent)
    form.title(title)
    form.resizable(False, False)
    form.grab_set()

    existing = {}
    if is_edit:
        pk_col = meta["pk"]
        row = conn.execute(
            f"SELECT * FROM {meta['table']} WHERE {pk_col}=?", (row_id,)
        ).fetchone()
        if row:
            existing = dict(row)

    widgets = {}
    combo_maps = {}

    for i, (label, field, kind) in enumerate(meta["fields"]):
        ttk.Label(form, text=label + ":", anchor="e", width=18).grid(
            row=i, column=0, padx=(12, 4), pady=6, sticky="e"
        )
        val = existing.get(field, "")

        if kind.startswith("combo:"):
            source = kind.split(":", 1)[1]
            options_raw = _load_combo_values(conn, source)
            display_vals = [o[0] for o in options_raw]
            cmap = {o[0]: o[1] for o in options_raw}
            rev_map = {str(o[1]): o[0] for o in options_raw}

            var = tk.StringVar(value=rev_map.get(str(val), str(val) if val else ""))
            cb = ttk.Combobox(form, textvariable=var, values=display_vals,
                              state="readonly", width=32)
            cb.grid(row=i, column=1, padx=(0, 12), pady=6, sticky="ew")
            widgets[field] = (var, cmap)
            combo_maps[field] = cmap
        else:
            var = tk.StringVar(value=str(val) if val is not None else "")
            entry = ttk.Entry(form, textvariable=var, width=34)
            entry.grid(row=i, column=1, padx=(0, 12), pady=6, sticky="ew")
            widgets[field] = (var, None)

    def save():
        values = {}
        for field, (var, cmap) in widgets.items():
            raw = var.get().strip()
            if cmap:
                values[field] = cmap.get(raw, raw)
            else:
                values[field] = raw if raw != "" else None

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
                col_clause = ", ".join(cols)
                conn.execute(
                    f"INSERT INTO {meta['table']}({col_clause}) VALUES({placeholders})",
                    vals,
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
    ttk.Button(btn_frame, text="Отмена",        command=form.destroy, width=10).pack(side="left", padx=6)


def _edit_order_selected(conn, win, tree, refresh_cb):
    """Открыть форму заказа для редактирования выбранной строки."""
    from tkinter import messagebox
    sel = tree.selection()
    if not sel:
        messagebox.showinfo("Подсказка", "Выберите строку для редактирования", parent=win)
        return
    order_id = int(tree.item(sel[0])["values"][0])
    open_order_form(conn, win, refresh_cb, order_id)
