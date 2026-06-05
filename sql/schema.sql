--  СХЕМА БД «Мебельный магазин»
-- Lookup-таблицы (справочники статусов/способов)

CREATE TABLE IF NOT EXISTS СтатусыЗаказа (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    название      TEXT    NOT NULL UNIQUE,
    is_final      INTEGER NOT NULL DEFAULT 0,  -- 1 = заказ выполнен
    is_delivering INTEGER NOT NULL DEFAULT 0,  -- 1 = доставляется (списать склад + создать доставку)
    is_cancelled  INTEGER NOT NULL DEFAULT 0   -- 1 = отменён (вернуть товар на склад)
);

CREATE TABLE IF NOT EXISTS СпособыОплаты (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    название TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS СтатусыДоставки (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    название     TEXT    NOT NULL UNIQUE,
    is_transit   INTEGER NOT NULL DEFAULT 0,  -- 1 = товар в пути, списать со склада
    is_delivered INTEGER NOT NULL DEFAULT 0   -- 1 = доставлено, заказ → выполнен
);

CREATE TABLE IF NOT EXISTS МестаХранения (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    название    TEXT NOT NULL UNIQUE,
    описание    TEXT
);

-- Основные справочники

CREATE TABLE IF NOT EXISTS Категории (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    название    TEXT NOT NULL UNIQUE,
    описание    TEXT
);

CREATE TABLE IF NOT EXISTS Поставщики (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    название           TEXT NOT NULL,
    контактное_лицо    TEXT,
    телефон            TEXT,
    email              TEXT
);

CREATE TABLE IF NOT EXISTS Товары (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    id_категории       INTEGER NOT NULL REFERENCES Категории(id),
    наименование       TEXT    NOT NULL,
    производитель      TEXT,
    цена               REAL    NOT NULL CHECK(цена >= 0),
    остаток            INTEGER NOT NULL DEFAULT 0 CHECK(остаток >= 0),
    описание           TEXT,
    id_места_хранения  INTEGER REFERENCES МестаХранения(id)
);

CREATE TABLE IF NOT EXISTS Сотрудники (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    фио         TEXT NOT NULL,
    должность   TEXT,
    телефон     TEXT,
    зарплата    REAL CHECK(зарплата >= 0)
);

CREATE TABLE IF NOT EXISTS Клиенты (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    фио                TEXT NOT NULL,
    телефон            TEXT,
    email              TEXT,
    адрес              TEXT,
    дата_регистрации   TEXT DEFAULT (date('now'))
);

-- Транзакционные таблицы

CREATE TABLE IF NOT EXISTS Заказы (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    id_клиента          INTEGER NOT NULL REFERENCES Клиенты(id),
    id_сотрудника       INTEGER REFERENCES Сотрудники(id),
    дата_заказа         TEXT    DEFAULT (date('now')),
    id_статуса          INTEGER NOT NULL DEFAULT 1 REFERENCES СтатусыЗаказа(id),
    итого               REAL    DEFAULT 0,
    id_способа_оплаты   INTEGER DEFAULT 1 REFERENCES СпособыОплаты(id)
);

CREATE TABLE IF NOT EXISTS СтрокиЗаказа (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    id_заказа       INTEGER NOT NULL REFERENCES Заказы(id) ON DELETE CASCADE,
    id_товара       INTEGER NOT NULL REFERENCES Товары(id),
    количество      INTEGER NOT NULL DEFAULT 1 CHECK(количество > 0),
    цена_единицы    REAL    NOT NULL CHECK(цена_единицы >= 0)
);

CREATE TABLE IF NOT EXISTS Поставки (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    id_поставщика   INTEGER NOT NULL REFERENCES Поставщики(id),
    дата_поставки   TEXT    DEFAULT (date('now')),
    сумма           REAL    DEFAULT 0
);

CREATE TABLE IF NOT EXISTS СтрокиПоставки (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    id_поставки     INTEGER NOT NULL REFERENCES Поставки(id) ON DELETE CASCADE,
    id_товара       INTEGER NOT NULL REFERENCES Товары(id),
    количество      INTEGER NOT NULL DEFAULT 1 CHECK(количество > 0),
    закупочная_цена REAL    NOT NULL CHECK(закупочная_цена >= 0)
);

CREATE TABLE IF NOT EXISTS Доставки (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    id_заказа             INTEGER NOT NULL REFERENCES Заказы(id),
    адрес_доставки        TEXT,
    дата_доставки         TEXT,
    курьер                TEXT,
    id_статуса_доставки   INTEGER DEFAULT 1 REFERENCES СтатусыДоставки(id)
);
