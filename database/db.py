import psycopg2
import hashlib

def get_connection():
    try:
        return psycopg2.connect(
            host="localhost", dbname="budget_db", user="postgres",
            password="1386", port="5432"
        )
    except:
        return None

def ensure_tables():
    conn = get_connection()
    if not conn:
        print("База данных недоступна, будет использован демо-режим")
        return
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY, username VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(256) NOT NULL, role VARCHAR(20) DEFAULT 'user'
        );""")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS centers (
            id SERIAL PRIMARY KEY, name VARCHAR(200) NOT NULL,
            responsible VARCHAR(150), color VARCHAR(20) DEFAULT '#3B82F6'
        );""")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id SERIAL PRIMARY KEY, code VARCHAR(20) NOT NULL,
            name VARCHAR(200) NOT NULL,
            item_type VARCHAR(20) CHECK (item_type IN ('Доход','Расход')),
            unit VARCHAR(20) DEFAULT 'руб.'
        );""")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS scenarios (
            id SERIAL PRIMARY KEY, name VARCHAR(100) NOT NULL,
            description TEXT, is_base BOOLEAN DEFAULT FALSE
        );""")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id SERIAL PRIMARY KEY,
            center_id INTEGER REFERENCES centers(id) ON DELETE CASCADE,
            item_id INTEGER REFERENCES items(id) ON DELETE CASCADE,
            period VARCHAR(7) NOT NULL, planned DECIMAL(15,2) DEFAULT 0,
            actual DECIMAL(15,2) DEFAULT 0, scenario_id INTEGER DEFAULT 1,
            UNIQUE(center_id, item_id, period, scenario_id)
        );""")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS limits (
            id SERIAL PRIMARY KEY,
            center_id INTEGER REFERENCES centers(id) ON DELETE CASCADE,
            item_id INTEGER REFERENCES items(id) ON DELETE CASCADE,
            period VARCHAR(7) NOT NULL, limit_value DECIMAL(15,2) NOT NULL,
            threshold INTEGER DEFAULT 80,
            UNIQUE(center_id, item_id, period)
        );""")

    # Дефолтный admin
    h = hashlib.sha256("admin".encode()).hexdigest()
    cur.execute("SELECT id FROM users WHERE username='admin';")
    if not cur.fetchone():
        cur.execute("INSERT INTO users (username,password,role) VALUES (%s,%s,%s);",
                    ("admin", h, "admin"))

    # Дефолтные сценарии
    cur.execute("SELECT id FROM scenarios WHERE name='Базовый';")
    if not cur.fetchone():
        cur.execute("INSERT INTO scenarios (name,description,is_base) VALUES (%s,%s,%s);",
                    ("Базовый", "Базовый план", True))
        cur.execute("INSERT INTO scenarios (name,description,is_base) VALUES (%s,%s,%s);",
                    ("Оптимистичный", "Рост доходов", False))
        cur.execute("INSERT INTO scenarios (name,description,is_base) VALUES (%s,%s,%s);",
                    ("Пессимистичный", "Снижение доходов", False))

    # Дефолтные центры
    cur.execute("SELECT id FROM centers WHERE name='Отдел продаж';")
    if not cur.fetchone():
        cur.execute("INSERT INTO centers (name,responsible,color) VALUES (%s,%s,%s);",
                    ("Отдел продаж", "Иванова А.С.", "#3B82F6"))
        cur.execute("INSERT INTO centers (name,responsible,color) VALUES (%s,%s,%s);",
                    ("Производство", "Петров Б.В.", "#10B981"))
        cur.execute("INSERT INTO centers (name,responsible,color) VALUES (%s,%s,%s);",
                    ("Администрация", "Сидорова Е.М.", "#F59E0B"))
        cur.execute("INSERT INTO centers (name,responsible,color) VALUES (%s,%s,%s);",
                    ("Маркетинг", "Козлов Д.И.", "#8B5CF6"))

    # Дефолтные статьи
    cur.execute("SELECT id FROM items WHERE code='1010';")
    if not cur.fetchone():
        data = [
            ("1010", "Выручка от продаж", "Доход"),
            ("1020", "Прочие доходы", "Доход"),
            ("2010", "Себестоимость", "Расход"),
            ("2020", "ФОТ", "Расход"),
            ("2030", "Аренда", "Расход"),
            ("2040", "Коммунальные услуги", "Расход"),
            ("2050", "Маркетинг", "Расход"),
            ("2060", "Транспорт", "Расход"),
            ("2070", "Прочие расходы", "Расход"),
        ]
        for row in data:
            cur.execute("INSERT INTO items (code,name,item_type) VALUES (%s,%s,%s);", row)

    conn.commit()
    cur.close()
    conn.close()
    print("Таблицы созданы")
