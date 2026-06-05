import sqlite3
import unittest

from app.database import get_query, init_db
from app.ui_reports import PARAM_QUERIES, PROFIT_QUERIES, REPORTS


EXPECTED_TABLES = {
    "СтатусыЗаказа",
    "СпособыОплаты",
    "СтатусыДоставки",
    "МестаХранения",
    "Категории",
    "Поставщики",
    "Товары",
    "Сотрудники",
    "Клиенты",
    "Заказы",
    "СтрокиЗаказа",
    "Поставки",
    "СтрокиПоставки",
    "Доставки",
}


def make_db():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    init_db(conn)
    return conn


class DatabaseTests(unittest.TestCase):
    def test_init_db_creates_expected_tables_and_loads_seed_data(self):
        conn = make_db()
        tables = {
            row["name"]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }

        self.assertTrue(EXPECTED_TABLES.issubset(tables))
        self.assertGreater(conn.execute("SELECT COUNT(*) FROM Товары").fetchone()[0], 0)
        self.assertGreater(conn.execute("SELECT COUNT(*) FROM Заказы").fetchone()[0], 0)

    def test_named_queries_are_available_and_executable(self):
        conn = make_db()

        report_query = get_query("report_выручка_по_месяцам")
        combo_query = get_query("combo_товары")

        self.assertIsNotNone(conn.execute(report_query).fetchall())
        self.assertTrue(conn.execute(combo_query).fetchall())

    def test_report_catalog_queries_exist(self):
        query_names = [meta["query_name"] for meta in REPORTS.values()]
        query_names += [meta["query_name"] for meta in PARAM_QUERIES]
        for meta in PROFIT_QUERIES.values():
            query_names.append(meta["income_query_name"])
            query_names.append(meta["expense_query_name"])

        for name in query_names:
            self.assertTrue(get_query(name), name)

    def test_schema_rejects_negative_stock(self):
        conn = make_db()
        product = conn.execute("SELECT * FROM Товары LIMIT 1").fetchone()

        with self.assertRaises(sqlite3.IntegrityError):
            conn.execute(
                """UPDATE Товары
                   SET остаток = -1
                   WHERE id = ?""",
                (product["id"],),
            )


if __name__ == "__main__":
    unittest.main()
