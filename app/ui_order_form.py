"""
Форма создания / редактирования заказа.

Бизнес-логика остатков и доставок:
  • Статус → «доставляется» : списать товары со склада + авто-создать запись в Доставки.
  • Статус «доставляется» → «отменён»  : вернуть товары на склад.
  • Статус «доставляется» → «выполнен» : ничего не трогаем (товар уже списан).
  • Статусы и способы оплаты загружаются из lookup-таблиц БД (не хардкод).
"""
import datetime
import random
import tkinter as tk
from tkinter import ttk, messagebox

from app.database import get_query


# Вспомогательные функции

def _get_status_flags(conn, status_name: str) -> dict:
    """Возвращает флаги статуса заказа из БД."""
    row = conn.execute(
        "SELECT is_final, is_delivering, is_cancelled FROM СтатусыЗаказа WHERE название=?",
        (status_name,)
    ).fetchone()
    if row is None:
        return {"is_final": 0, "is_delivering": 0, "is_cancelled": 0}
    return {"is_final": row["is_final"], "is_delivering": row["is_delivering"], "is_cancelled": row["is_cancelled"]}


def _get_cancelled_status_name(conn) -> str | None:
    """Возвращает название статуса «отменён» из БД."""
    row = conn.execute(
        "SELECT название FROM СтатусыЗаказа WHERE is_cancelled = 1 LIMIT 1"
    ).fetchone()
    return row["название"] if row else None


def _load_lookup(conn, table, id_col, name_col):
    rows = conn.execute(f"SELECT {id_col}, {name_col} FROM {table} ORDER BY {id_col}").fetchall()
    to_id   = {r[1]: r[0] for r in rows}
    to_name = {r[0]: r[1] for r in rows}
    return list(to_id.keys()), to_id, to_name


def _get_stock(conn, product_id: int) -> int:
    row = conn.execute("SELECT остаток FROM Товары WHERE id=?", (product_id,)).fetchone()
    return int(row[0]) if row else 0


def _already_in_order(order_lines, product_id: int) -> int:
    return sum(ln["qty"] for ln in order_lines if ln["id_товара"] == product_id)


def _deduct_stock(cur, order_lines):
    """Списать товары со склада."""
    for ln in order_lines:
        cur.execute(
            "UPDATE Товары SET остаток = MAX(0, остаток - ?) WHERE id=?",
            (ln["qty"], ln["id_товара"]),
        )


def _restore_stock(cur, order_id):
    """Вернуть товары на склад по строкам заказа."""
    lines = cur.execute(
        "SELECT id_товара, количество FROM СтрокиЗаказа WHERE id_заказа=?",
        (order_id,)
    ).fetchall()
    for ln in lines:
        cur.execute(
            "UPDATE Товары SET остаток = остаток + ? WHERE id=?",
            (ln["количество"], ln["id_товара"]),
        )


def _auto_create_delivery(cur, conn, order_id, order_date):
    """
    Автоматически создаёт запись в Доставки при переходе заказа в «доставляется».
    - Адрес берётся из Клиенты
    - Дата = дата заказа
    - Курьер = случайный сотрудник
    - Статус = «запланирована» (первый статус доставки)
    """
    # Адрес клиента
    client_row = cur.execute(
        """SELECT кл.адрес FROM Заказы з
           JOIN Клиенты кл ON з.id_клиента = кл.id
           WHERE з.id=?""",
        (order_id,)
    ).fetchone()
    address = client_row["адрес"] if client_row and client_row["адрес"] else ""

    # Случайный сотрудник как курьер
    employees = cur.execute("SELECT фио FROM Сотрудники").fetchall()
    courier = random.choice(employees)["фио"] if employees else "Не назначен"

    # Первый статус доставки (запланирована)
    status_row = cur.execute(
        "SELECT id FROM СтатусыДоставки ORDER BY id LIMIT 1"
    ).fetchone()
    delivery_status_id = status_row["id"] if status_row else 1

    # Проверяем - вдруг доставка уже есть для этого заказа
    existing = cur.execute(
        "SELECT id FROM Доставки WHERE id_заказа=?", (order_id,)
    ).fetchone()
    if existing:
        return  # уже создана раньше

    cur.execute(
        """INSERT INTO Доставки(id_заказа, адрес_доставки, дата_доставки, курьер, id_статуса_доставки)
           VALUES(?, ?, ?, ?, ?)""",
        (order_id, address, order_date, courier, delivery_status_id),
    )

# Главная форма

def open_order_form(conn, parent, tree_refresh_cb, order_id=None):
    is_edit = order_id is not None
    win = tk.Toplevel(parent)
    win.title("Редактировать заказ" if is_edit else "Новый заказ")
    win.geometry("780x600")
    win.minsize(680, 520)
    win.grab_set()

    # Справочники 
    clients   = [(r["фио"], r["id"]) for r in conn.execute("SELECT id, фио FROM Клиенты ORDER BY фио").fetchall()]
    employees = [(r["фио"], r["id"]) for r in conn.execute("SELECT id, фио FROM Сотрудники ORDER BY фио").fetchall()]

    products     = conn.execute("SELECT id, наименование, цена, остаток FROM Товары ORDER BY наименование").fetchall()
    prod_names   = [p["наименование"] for p in products]
    prod_by_name = {p["наименование"]: dict(p) for p in products}
    prod_by_id   = {p["id"]: dict(p) for p in products}

    client_map = {c[0]: c[1] for c in clients}
    emp_map    = {e[0]: e[1] for e in employees}

    status_names, status_to_id, status_to_name = _load_lookup(conn, "СтатусыЗаказа", "id", "название")
    pay_names,    pay_to_id,    pay_to_name    = _load_lookup(conn, "СпособыОплаты",  "id", "название")

    # Старый статус заказа
    old_status_name: str | None = None
    if is_edit:
        r = conn.execute(
            "SELECT ст.название FROM Заказы з JOIN СтатусыЗаказа ст ON з.id_статуса=ст.id WHERE з.id=?",
            (order_id,),
        ).fetchone()
        old_status_name = r[0] if r else None

    # UI-хелперы
    def _combo(parent, label, values, row, col):
        ttk.Label(parent, text=label, anchor="e", width=14).grid(row=row, column=col,   padx=(8,4), pady=4, sticky="e")
        var = tk.StringVar()
        cb  = ttk.Combobox(parent, textvariable=var, values=values, state="readonly", width=26)
        cb.grid(row=row, column=col+1, padx=(0,16), pady=4, sticky="ew")
        return var

    def _entry(parent, label, row, col):
        ttk.Label(parent, text=label, anchor="e", width=14).grid(row=row, column=col,   padx=(8,4), pady=4, sticky="e")
        var = tk.StringVar()
        ttk.Entry(parent, textvariable=var, width=28).grid(row=row, column=col+1, padx=(0,16), pady=4, sticky="ew")
        return var

    # Шапка
    header = ttk.LabelFrame(win, text="Основные данные", padding=10)
    header.pack(fill="x", padx=12, pady=(10, 4))
    for c in range(4):
        header.columnconfigure(c, weight=1)

    var_client   = _combo(header, "Клиент:",    [c[0] for c in clients], 0, 0)
    var_employee = _combo(header, "Сотрудник:", [e[0] for e in employees], 0, 2)
    var_date     = _entry(header, "Дата:", 1, 0)
    var_status   = _combo(header, "Статус:",    status_names, 1, 2)
    var_payment  = _combo(header, "Оплата:",    pay_names,    2, 0)

    # Таблица строк заказа
    items_frame = ttk.LabelFrame(win, text="Товары в заказе", padding=6)
    items_frame.pack(fill="both", expand=True, padx=12, pady=4)

    cols_items = ("Товар", "Кол-во", "Доступно", "Цена ед.", "Сумма")
    items_tree = ttk.Treeview(items_frame, columns=cols_items, show="headings", height=7)
    widths = {"Товар": 290, "Кол-во": 65, "Доступно": 75, "Цена ед.": 100, "Сумма": 100}
    for col in cols_items:
        items_tree.heading(col, text=col)
        items_tree.column(col, width=widths[col], minwidth=50,
                          anchor="w" if col == "Товар" else "e")
    vsb = ttk.Scrollbar(items_frame, orient="vertical", command=items_tree.yview)
    items_tree.configure(yscrollcommand=vsb.set)
    items_tree.pack(side="left", fill="both", expand=True)
    vsb.pack(side="right", fill="y")

    items_tree.tag_configure("over_stock", foreground="#c0392b")

    order_lines: list[dict] = []

    def _available_stock(product_id: int) -> int:
        stock = _get_stock(conn, product_id)
        old_flags = _get_status_flags(conn, old_status_name) if old_status_name else {}
        if is_edit and old_flags.get("is_delivering"):
            already_committed = 0
        else:
            already_committed = _already_in_order(order_lines, product_id)
        return max(0, stock - already_committed)

    def _rebuild_tree():
        items_tree.delete(*items_tree.get_children())
        for ln in order_lines:
            stock_now = _get_stock(conn, ln["id_товара"])
            tag = "over_stock" if ln["qty"] > stock_now else ""
            items_tree.insert("", "end",
                values=(ln["name"], ln["qty"], stock_now,
                        f"{ln['price']:,.2f}", f"{ln['qty']*ln['price']:,.2f}"),
                tags=(tag,))
        _update_total()

    var_total = tk.StringVar(value="0.00")

    def _update_total():
        var_total.set(f"{sum(ln['qty'] * ln['price'] for ln in order_lines):,.2f}")

    # Панель добавления строки 
    add_frame = ttk.Frame(win)
    add_frame.pack(fill="x", padx=12, pady=(0, 2))

    ttk.Label(add_frame, text="Товар:").pack(side="left")
    var_sel_product = tk.StringVar()
    cb_product = ttk.Combobox(add_frame, textvariable=var_sel_product,
                               values=prod_names, state="readonly", width=32)
    cb_product.pack(side="left", padx=(4, 10))

    stock_lbl_var = tk.StringVar(value="")
    ttk.Label(add_frame, textvariable=stock_lbl_var,
              foreground="#2a6e2a", font=("Arial", 9)).pack(side="left", padx=(0, 10))

    ttk.Label(add_frame, text="Кол-во:").pack(side="left")
    var_sel_qty = tk.StringVar(value="1")
    sp_qty = ttk.Spinbox(add_frame, textvariable=var_sel_qty, from_=1, to=9999, width=6)
    sp_qty.pack(side="left", padx=(4, 10))

    ttk.Label(add_frame, text="Цена:").pack(side="left")
    var_sel_price = tk.StringVar()
    ttk.Entry(add_frame, textvariable=var_sel_price, width=10).pack(side="left", padx=(4, 10))

    def _on_product_select(*_):
        name = var_sel_product.get()
        if name not in prod_by_name:
            stock_lbl_var.set("")
            return
        prod = prod_by_name[name]
        avail = _available_stock(prod["id"])
        stock_lbl_var.set(f"На складе: {avail} шт.")
        sp_qty.configure(to=max(1, avail))
        if int(var_sel_qty.get() or 1) > avail:
            var_sel_qty.set(str(max(1, avail)))
        var_sel_price.set(f"{prod['цена']:.2f}")

    cb_product.bind("<<ComboboxSelected>>", _on_product_select)

    def _add_line():
        name = var_sel_product.get().strip()
        if not name:
            messagebox.showwarning("Внимание", "Выберите товар", parent=win); return

        prod = prod_by_name.get(name)
        if prod is None:
            messagebox.showerror("Ошибка", "Товар не найден", parent=win); return

        try:
            qty = int(var_sel_qty.get())
            assert qty >= 1
        except Exception:
            messagebox.showerror("Ошибка", "Количество — целое ≥ 1", parent=win); return

        try:
            price = float(var_sel_price.get().replace(",", "."))
            assert price >= 0
        except Exception:
            messagebox.showerror("Ошибка", "Цена — число ≥ 0", parent=win); return

        avail = _available_stock(prod["id"])
        if qty > avail:
            messagebox.showerror(
                "Недостаточно товара",
                f"«{name}»\nДоступно на складе: {avail} шт.\nВы пытаетесь добавить: {qty} шт.",
                parent=win,
            )
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
        stock_lbl_var.set("")
        sp_qty.configure(to=9999)

    def _remove_line():
        sel = items_tree.selection()
        if not sel:
            messagebox.showinfo("Подсказка", "Выберите строку для удаления", parent=win); return
        order_lines.pop(items_tree.index(sel[0]))
        _rebuild_tree()

    ttk.Button(add_frame, text="＋ Добавить", command=_add_line).pack(side="left", padx=(0, 6))
    ttk.Button(add_frame, text="✕ Удалить",  command=_remove_line).pack(side="left")

    # Итого + кнопки
    bottom = ttk.Frame(win)
    bottom.pack(fill="x", padx=12, pady=(4, 10))
    ttk.Label(bottom, text="Итого, ₽:", font=("Arial", 10, "bold")).pack(side="left")
    ttk.Label(bottom, textvariable=var_total,
              font=("Arial", 11, "bold"), foreground="#8b4513").pack(side="left", padx=(6, 40))

    # Сохранение
    def _save():
        client_name = var_client.get().strip()
        if not client_name:
            messagebox.showwarning("Внимание", "Выберите клиента", parent=win); return
        if not order_lines:
            messagebox.showwarning("Внимание", "Добавьте хотя бы один товар", parent=win); return

        new_status_name = var_status.get()
        id_client   = client_map.get(client_name)
        id_employee = emp_map.get(var_employee.get().strip()) or None
        date        = var_date.get().strip() or datetime.date.today().isoformat()
        id_status   = status_to_id.get(new_status_name, 1)
        id_payment  = pay_to_id.get(var_payment.get(), 1)
        total       = round(sum(ln["qty"] * ln["price"] for ln in order_lines), 2)

        # Флаги старого и нового статуса
        old_flags = _get_status_flags(conn, old_status_name) if old_status_name else {}
        new_flags = _get_status_flags(conn, new_status_name)

        old_delivering = old_flags.get("is_delivering", 0)
        new_delivering = new_flags.get("is_delivering", 0)
        new_cancelled  = new_flags.get("is_cancelled",  0)

        try:
            cur = conn.cursor()

            if is_edit:
                # Статус менялся С «доставляется» → «отменён» : вернуть товар на склад
                if old_delivering and new_cancelled:
                    _restore_stock(cur, order_id)

                # Статус менялся НА «доставляется» (раньше не был) : списать товар
                if new_delivering and not old_delivering:
                    _deduct_stock(cur, order_lines)
                    _auto_create_delivery(cur, conn, order_id, date)

                cur.execute(
                    """UPDATE Заказы SET id_клиента=?, id_сотрудника=?,
                       дата_заказа=?, id_статуса=?, итого=?, id_способа_оплаты=?
                       WHERE id=?""",
                    (id_client, id_employee, date, id_status, total, id_payment, order_id),
                )
                cur.execute("DELETE FROM СтрокиЗаказа WHERE id_заказа=?", (order_id,))
                for ln in order_lines:
                    cur.execute(
                        "INSERT INTO СтрокиЗаказа(id_заказа,id_товара,количество,цена_единицы)"
                        " VALUES(?,?,?,?)",
                        (order_id, ln["id_товара"], ln["qty"], ln["price"]),
                    )

            else:
                # Новый заказ
                cur.execute(
                    """INSERT INTO Заказы(id_клиента,id_сотрудника,дата_заказа,
                       id_статуса,итого,id_способа_оплаты) VALUES(?,?,?,?,?,?)""",
                    (id_client, id_employee, date, id_status, total, id_payment),
                )
                new_order_id = cur.lastrowid
                for ln in order_lines:
                    cur.execute(
                        "INSERT INTO СтрокиЗаказа(id_заказа,id_товара,количество,цена_единицы)"
                        " VALUES(?,?,?,?)",
                        (new_order_id, ln["id_товара"], ln["qty"], ln["price"]),
                    )
                # Если сразу создан как «доставляется» - списать и создать доставку
                if new_delivering:
                    _deduct_stock(cur, order_lines)
                    _auto_create_delivery(cur, conn, new_order_id, date)

            conn.commit()
            tree_refresh_cb()
            win.destroy()

        except Exception as e:
            conn.rollback()
            messagebox.showerror("Ошибка сохранения", str(e), parent=win)

    ttk.Button(bottom, text="💾 Сохранить", command=_save, width=16).pack(side="right", padx=4)
    ttk.Button(bottom, text="Отмена", command=win.destroy, width=10).pack(side="right", padx=4)

    # Заполнить при редактировании
    if is_edit:
        row = conn.execute(
            """SELECT з.*, кл.фио AS клиент_фио,
                      COALESCE(с.фио,'') AS сотрудник_фио
               FROM Заказы з
               JOIN Клиенты кл ON з.id_клиента = кл.id
               LEFT JOIN Сотрудники с ON з.id_сотрудника = с.id
               WHERE з.id=?""",
            (order_id,),
        ).fetchone()
        if row:
            var_client.set(row["клиент_фио"])
            var_employee.set(row["сотрудник_фио"])
            var_date.set(row["дата_заказа"] or "")
            var_status.set(status_to_name.get(row["id_статуса"], ""))
            var_payment.set(pay_to_name.get(row["id_способа_оплаты"], ""))

        for ln in conn.execute(
            """SELECT сз.id, сз.id_товара, т.наименование, сз.количество, сз.цена_единицы
               FROM СтрокиЗаказа сз
               JOIN Товары т ON сз.id_товара = т.id
               WHERE сз.id_заказа=? ORDER BY сз.id""",
            (order_id,),
        ).fetchall():
            order_lines.append({
                "line_id":   ln["id"],
                "id_товара": ln["id_товара"],
                "name":      ln["наименование"],
                "qty":       ln["количество"],
                "price":     ln["цена_единицы"],
            })
        _rebuild_tree()
    else:
        var_date.set(datetime.date.today().isoformat())
        var_status.set(status_names[0] if status_names else "")
        var_payment.set(pay_names[0] if pay_names else "")
