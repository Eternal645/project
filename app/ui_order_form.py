"""
Форма создания / редактирования заказа с поддержкой нескольких строк товаров.
Вызывается из ui_tables.py вместо универсального _open_form для таблицы «Заказы».
"""
import tkinter as tk
from tkinter import ttk, messagebox


def _load_clients(conn):
    rows = conn.execute("SELECT id, фио FROM Клиенты ORDER BY фио").fetchall()
    return [(r["фио"], r["id"]) for r in rows]


def _load_employees(conn):
    rows = conn.execute("SELECT id, фио FROM Сотрудники ORDER BY фио").fetchall()
    return [(r["фио"], r["id"]) for r in rows]


def _load_products(conn):
    rows = conn.execute(
        "SELECT id, наименование, цена, остаток FROM Товары ORDER BY наименование"
    ).fetchall()
    return rows  # list of sqlite3.Row


def open_order_form(conn, parent, tree_refresh_cb, order_id=None):
    """
    Открыть форму заказа.
    conn             — соединение с БД
    parent           — родительское окно
    tree_refresh_cb  — функция () → None, обновляет Treeview в окне «Заказы»
    order_id         — None для нового заказа, int для редактирования
    """
    is_edit = order_id is not None
    title = "Редактировать заказ" if is_edit else "Новый заказ"

    win = tk.Toplevel(parent)
    win.title(title)
    win.geometry("780x580")
    win.minsize(680, 500)
    win.grab_set()

    # ── загрузить справочники ──────────────────────────────────────────────
    clients   = _load_clients(conn)
    employees = _load_employees(conn)
    products  = _load_products(conn)

    client_names   = [c[0] for c in clients]
    client_map     = {c[0]: c[1] for c in clients}
    employee_names = [e[0] for e in employees]
    employee_map   = {e[0]: e[1] for e in employees}
    product_names  = [p["наименование"] for p in products]
    product_by_name = {p["наименование"]: p for p in products}

    # ── шапка заказа ──────────────────────────────────────────────────────
    header = ttk.LabelFrame(win, text="Основные данные", padding=10)
    header.pack(fill="x", padx=12, pady=(10, 4))

    def _lbl_entry(parent, text, row, col_start=0, width=26):
        ttk.Label(parent, text=text, anchor="e", width=14).grid(
            row=row, column=col_start, padx=(8, 4), pady=4, sticky="e"
        )
        var = tk.StringVar()
        e = ttk.Entry(parent, textvariable=var, width=width)
        e.grid(row=row, column=col_start + 1, padx=(0, 16), pady=4, sticky="ew")
        return var

    def _lbl_combo(parent, text, values, row, col_start=0, width=26):
        ttk.Label(parent, text=text, anchor="e", width=14).grid(
            row=row, column=col_start, padx=(8, 4), pady=4, sticky="e"
        )
        var = tk.StringVar()
        cb = ttk.Combobox(parent, textvariable=var, values=values,
                          state="readonly", width=width)
        cb.grid(row=row, column=col_start + 1, padx=(0, 16), pady=4, sticky="ew")
        return var

    for c in range(4):
        header.columnconfigure(c, weight=1)

    var_client   = _lbl_combo(header, "Клиент:",      client_names,   0, 0)
    var_employee = _lbl_combo(header, "Сотрудник:",   employee_names, 0, 2)
    var_date     = _lbl_entry(header, "Дата:",        1, 0)
    var_status   = _lbl_combo(header, "Статус:",
                               ["новый", "в обработке", "доставляется", "выполнен", "отменён"],
                               1, 2)
    var_payment  = _lbl_combo(header, "Оплата:",
                               ["наличные", "карта", "онлайн"],
                               2, 0)

    # ── таблица товаров ───────────────────────────────────────────────────
    items_frame = ttk.LabelFrame(win, text="Товары в заказе", padding=6)
    items_frame.pack(fill="both", expand=True, padx=12, pady=4)

    cols_items = ("Товар", "Кол-во", "Цена ед.", "Сумма")
    items_tree = ttk.Treeview(items_frame, columns=cols_items,
                              show="headings", height=7, selectmode="browse")
    items_tree.heading("Товар",    text="Товар")
    items_tree.heading("Кол-во",   text="Кол-во")
    items_tree.heading("Цена ед.", text="Цена ед., ₽")
    items_tree.heading("Сумма",    text="Сумма, ₽")
    items_tree.column("Товар",    width=320, minwidth=160)
    items_tree.column("Кол-во",   width=70,  minwidth=50,  anchor="center")
    items_tree.column("Цена ед.", width=110, minwidth=80,  anchor="e")
    items_tree.column("Сумма",    width=110, minwidth=80,  anchor="e")

    vsb = ttk.Scrollbar(items_frame, orient="vertical", command=items_tree.yview)
    items_tree.configure(yscrollcommand=vsb.set)
    items_tree.pack(side="left", fill="both", expand=True)
    vsb.pack(side="right", fill="y")

    # строки хранятся как список словарей {id_товара, name, qty, price}
    # id_строки — None для новых, int для существующих (при редактировании)
    order_lines = []  # [{"line_id": int|None, "id_товара": int, "name": str, "qty": int, "price": float}]

    def _rebuild_tree():
        items_tree.delete(*items_tree.get_children())
        for ln in order_lines:
            s = ln["qty"] * ln["price"]
            items_tree.insert("", "end", values=(
                ln["name"],
                ln["qty"],
                f"{ln['price']:,.2f}",
                f"{s:,.2f}",
            ))
        _update_total()

    var_total = tk.StringVar(value="0.00")

    def _update_total():
        t = sum(ln["qty"] * ln["price"] for ln in order_lines)
        var_total.set(f"{t:,.2f}")

    # ── панель добавления строки ──────────────────────────────────────────
    add_frame = ttk.Frame(win)
    add_frame.pack(fill="x", padx=12, pady=(0, 2))

    ttk.Label(add_frame, text="Товар:").pack(side="left")
    var_sel_product = tk.StringVar()
    cb_product = ttk.Combobox(add_frame, textvariable=var_sel_product,
                               values=product_names, state="readonly", width=34)
    cb_product.pack(side="left", padx=(4, 10))

    ttk.Label(add_frame, text="Кол-во:").pack(side="left")
    var_sel_qty = tk.StringVar(value="1")
    sp_qty = ttk.Spinbox(add_frame, textvariable=var_sel_qty,
                         from_=1, to=9999, width=6)
    sp_qty.pack(side="left", padx=(4, 10))

    def _auto_fill_price(*_):
        name = var_sel_product.get()
        if name in product_by_name:
            p = product_by_name[name]
            var_sel_price.set(f"{p['цена']:.2f}")

    cb_product.bind("<<ComboboxSelected>>", _auto_fill_price)

    ttk.Label(add_frame, text="Цена:").pack(side="left")
    var_sel_price = tk.StringVar()
    ttk.Entry(add_frame, textvariable=var_sel_price, width=10).pack(side="left", padx=(4, 10))

    def _add_line():
        name = var_sel_product.get().strip()
        if not name:
            messagebox.showwarning("Внимание", "Выберите товар", parent=win)
            return
        try:
            qty = int(var_sel_qty.get())
            if qty < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Количество должно быть целым числом ≥ 1", parent=win)
            return
        try:
            price = float(var_sel_price.get().replace(",", "."))
            if price < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Цена должна быть числом ≥ 0", parent=win)
            return

        prod = product_by_name.get(name)
        if prod is None:
            messagebox.showerror("Ошибка", "Товар не найден", parent=win)
            return

        order_lines.append({
            "line_id":   None,
            "id_товара": prod["id"],
            "name":      name,
            "qty":       qty,
            "price":     price,
        })
        _rebuild_tree()
        var_sel_product.set("")
        var_sel_qty.set("1")
        var_sel_price.set("")

    ttk.Button(add_frame, text="＋ Добавить", command=_add_line).pack(side="left", padx=(0, 6))

    def _remove_line():
        sel = items_tree.selection()
        if not sel:
            messagebox.showinfo("Подсказка", "Выберите строку для удаления", parent=win)
            return
        idx = items_tree.index(sel[0])
        order_lines.pop(idx)
        _rebuild_tree()

    ttk.Button(add_frame, text="✕ Удалить", command=_remove_line).pack(side="left")

    # ── итого + кнопки ────────────────────────────────────────────────────
    bottom = ttk.Frame(win)
    bottom.pack(fill="x", padx=12, pady=(4, 10))

    ttk.Label(bottom, text="Итого, ₽:", font=("Arial", 10, "bold")).pack(side="left")
    ttk.Label(bottom, textvariable=var_total,
              font=("Arial", 11, "bold"), foreground="#8b4513").pack(side="left", padx=(6, 40))

    def _save():
        client_name = var_client.get().strip()
        if not client_name:
            messagebox.showwarning("Внимание", "Выберите клиента", parent=win)
            return
        if not order_lines:
            messagebox.showwarning("Внимание", "Добавьте хотя бы один товар", parent=win)
            return

        id_client   = client_map.get(client_name)
        id_employee = employee_map.get(var_employee.get().strip()) if var_employee.get().strip() else None
        date        = var_date.get().strip() or None
        status      = var_status.get() or "новый"
        payment     = var_payment.get() or "наличные"
        total       = sum(ln["qty"] * ln["price"] for ln in order_lines)

        try:
            cur = conn.cursor()
            if is_edit:
                cur.execute(
                    """UPDATE Заказы SET id_клиента=?, id_сотрудника=?,
                       дата_заказа=?, статус=?, итого=?, способ_оплаты=?
                       WHERE id=?""",
                    (id_client, id_employee, date, status,
                     round(total, 2), payment, order_id),
                )
                # удалить старые строки и вставить заново
                cur.execute("DELETE FROM СтрокиЗаказа WHERE id_заказа=?", (order_id,))
                for ln in order_lines:
                    cur.execute(
                        "INSERT INTO СтрокиЗаказа(id_заказа,id_товара,количество,цена_единицы)"
                        " VALUES(?,?,?,?)",
                        (order_id, ln["id_товара"], ln["qty"], ln["price"]),
                    )
            else:
                cur.execute(
                    """INSERT INTO Заказы(id_клиента,id_сотрудника,дата_заказа,
                       статус,итого,способ_оплаты) VALUES(?,?,?,?,?,?)""",
                    (id_client, id_employee, date, status,
                     round(total, 2), payment),
                )
                new_order_id = cur.lastrowid
                for ln in order_lines:
                    cur.execute(
                        "INSERT INTO СтрокиЗаказа(id_заказа,id_товара,количество,цена_единицы)"
                        " VALUES(?,?,?,?)",
                        (new_order_id, ln["id_товара"], ln["qty"], ln["price"]),
                    )
            conn.commit()
            tree_refresh_cb()
            win.destroy()
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Ошибка сохранения", str(e), parent=win)

    ttk.Button(bottom, text="💾 Сохранить", command=_save, width=16).pack(side="right", padx=4)
    ttk.Button(bottom, text="Отмена", command=win.destroy, width=10).pack(side="right", padx=4)

    # ── заполнить данными при редактировании ──────────────────────────────
    if is_edit:
        row = conn.execute(
            """SELECT з.*, к.фио AS клиент_фио,
                      COALESCE(с.фио,'') AS сотрудник_фио
               FROM Заказы з
               JOIN Клиенты к ON з.id_клиента = к.id
               LEFT JOIN Сотрудники с ON з.id_сотрудника = с.id
               WHERE з.id=?""",
            (order_id,),
        ).fetchone()
        if row:
            var_client.set(row["клиент_фио"])
            var_employee.set(row["сотрудник_фио"])
            var_date.set(row["дата_заказа"] or "")
            var_status.set(row["статус"] or "новый")
            var_payment.set(row["способ_оплаты"] or "наличные")

        lines = conn.execute(
            """SELECT сз.id, сз.id_товара, т.наименование, сз.количество, сз.цена_единицы
               FROM СтрокиЗаказа сз
               JOIN Товары т ON сз.id_товара = т.id
               WHERE сз.id_заказа=? ORDER BY сз.id""",
            (order_id,),
        ).fetchall()
        for ln in lines:
            order_lines.append({
                "line_id":   ln["id"],
                "id_товара": ln["id_товара"],
                "name":      ln["наименование"],
                "qty":       ln["количество"],
                "price":     ln["цена_единицы"],
            })
        _rebuild_tree()
    else:
        # дата по умолчанию — сегодня
        import datetime
        var_date.set(datetime.date.today().isoformat())
        var_status.set("новый")
        var_payment.set("наличные")
