"""
database.py — подключение и инициализация БД.

Структура файлов проекта:
  sql/schema.sql    — DDL: создание таблиц
  sql/queries.sql   — все SELECT-запросы приложения (без хардкода)
  data/*.csv        — начальные данные (вместо хардкода в коде или SQL)
"""
import sqlite3
import csv
import os
import re


def _sql_path(filename: str) -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "..", "sql", filename)


def _data_path(filename: str) -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "..", "data", filename)


def connect_db(path: str = "mebel.db") -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _load_csv(filepath: str) -> tuple[list[str], list[list]]:
    """Читает CSV и возвращает (заголовки, строки)."""
    with open(filepath, encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        headers = next(reader)
        rows = [row for row in reader if any(cell.strip() for cell in row)]
    return headers, rows


def _seed_table(conn: sqlite3.Connection, table: str, csv_file: str) -> None:
    """Загружает данные из CSV-файла в таблицу БД (только если она пуста)."""
    count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    if count > 0:
        return

    filepath = _data_path(csv_file)
    headers, rows = _load_csv(filepath)

    cols = ", ".join(headers)
    placeholders = ", ".join("?" for _ in headers)
    sql = f"INSERT INTO {table}({cols}) VALUES({placeholders})"

    conn.executemany(sql, rows)
    conn.commit()


def init_db(conn: sqlite3.Connection) -> None:
    """Создаёт таблицы из schema.sql и загружает начальные данные из CSV-файлов."""

    # 1. Создаём структуру БД из SQL-файла
    with open(_sql_path("schema.sql"), encoding="utf-8") as f:
        conn.executescript(f.read())

    # 2. Загружаем начальные данные из CSV — строго по порядку (FK-зависимости)
    seed_order = [
        ("СтатусыЗаказа",   "order_statuses.csv"),
        ("СпособыОплаты",   "payment_methods.csv"),
        ("СтатусыДоставки", "delivery_statuses.csv"),
        ("МестаХранения",   "storage_locations.csv"),
        ("Категории",       "categories.csv"),
        ("Поставщики",      "suppliers.csv"),
        ("Сотрудники",      "employees.csv"),
        ("Клиенты",         "clients.csv"),
        ("Товары",          "products.csv"),
        ("Заказы",          "orders.csv"),
        ("СтрокиЗаказа",    "order_items.csv"),
        ("Поставки",        "supplies.csv"),
        ("СтрокиПоставки",  "supply_items.csv"),
        ("Доставки",        "deliveries.csv"),
    ]

    for table, csv_file in seed_order:
        _seed_table(conn, table, csv_file)


# Загрузка именованных SQL-запросов из queries.sql

def load_queries() -> dict:
    """
    Читает sql/queries.sql и возвращает словарь {имя: sql_текст}.
    Метки задаются комментарием вида:  -- [имя_запроса]
    """
    with open(_sql_path("queries.sql"), encoding="utf-8") as f:
        text = f.read()

    result = {}
    parts = re.split(r'--\s*\[([^\]]+)\]', text)
    it = iter(parts[1:])
    for name, sql in zip(it, it):
        cleaned = sql.strip().rstrip(';').strip()
        if cleaned:
            result[name.strip()] = cleaned
    return result


_QUERIES: dict | None = None


def get_query(name: str) -> str:
    """Возвращает SQL-запрос по имени метки из queries.sql."""
    global _QUERIES
    if _QUERIES is None:
        _QUERIES = load_queries()
    if name not in _QUERIES:
        raise KeyError(f"Запрос '{name}' не найден в queries.sql")
    return _QUERIES[name]
