from src import database
import sqlite3
from pathlib import Path

def test_db_load():
    database.check_db()
    conn = sqlite3.connect('subscriptions.db')
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {r[0] for r in cursor.fetchall()}
    assert {"Plan", "Recordatorio", "Suscripcion", "Pago"}.issubset(tables)

def test_data_load(tmp_path):
    db_file = tmp_path / "mock_subscriptions.db"

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    database.check_db()

    cursor.execute("""
        CREATE TABLE Plan (
            id_plan INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            dias INTEGER NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE Recordatorio (
            id_recordatorio INTEGER PRIMARY KEY AUTOINCREMENT,
            horas_antes INTEGER NOT NULL,
            nota TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE Suscripcion (
            id_suscripcion INTEGER PRIMARY KEY AUTOINCREMENT,
            id_plan INTEGER NOT NULL,
            id_recordatorio INTEGER,
            nombre TEXT NOT NULL,
            fecha_pago DATETIME NOT NULL,
            monto_pago REAL NOT NULL,
            medio_pago TEXT NOT NULL,
            FOREIGN KEY (id_plan) REFERENCES Plan(id_plan),
            FOREIGN KEY (id_recordatorio) REFERENCES Recordatorio(id_recordatorio)
        )
    """)
    cursor.execute("""
        CREATE TABLE Pago (
            id_pago INTEGER PRIMARY KEY AUTOINCREMENT,
            id_suscripcion INTEGER NOT NULL,
            fecha DATETIME NOT NULL,
            monto REAL NOT NULL,
            FOREIGN KEY (id_suscripcion) REFERENCES Suscripcion(id_suscripcion)
        )
    """)

    conn.commit()

    cursor.execute("INSERT INTO Plan (nombre, dias) VALUES (?, ?)", ("Básico", 30))
    cursor.execute("INSERT INTO Plan (nombre, dias) VALUES (?, ?)", ("Premium", 90))

    cursor.execute("INSERT INTO Recordatorio (horas_antes, nota) VALUES (?, ?)", (24, "Recordar pago mensual"))
    cursor.execute("INSERT INTO Recordatorio (horas_antes, nota) VALUES (?, ?)", (48, "Recordar pago trimestral"))

    cursor.execute("""
        INSERT INTO Suscripcion (id_plan, id_recordatorio, nombre, fecha_pago, monto_pago, medio_pago)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (1, 1, "Suscripción de prueba", "2025-10-20", 100.0, "Tarjeta"))

    cursor.execute("""
        INSERT INTO Pago (id_suscripcion, fecha, monto) VALUES (?, ?, ?)
    """, (1, "2025-10-21", 100.0))

    conn.commit()

    cursor.execute("SELECT nombre, dias FROM Plan ORDER BY id_plan")
    plans = cursor.fetchall()
    assert plans == [("Básico", 30), ("Premium", 90)]

    cursor.execute("SELECT horas_antes, nota FROM Recordatorio ORDER BY id_recordatorio")
    recordatorios = cursor.fetchall()
    assert recordatorios == [(24, "Recordar pago mensual"), (48, "Recordar pago trimestral")]

    cursor.execute("SELECT nombre, monto_pago, medio_pago FROM Suscripcion")
    suscripciones = cursor.fetchall()
    assert suscripciones == [("Suscripción de prueba", 100.0, "Tarjeta")]

    cursor.execute("SELECT monto FROM Pago")
    pagos = cursor.fetchall()
    assert pagos == [(100.0,)]

    conn.close()

def setup_mock_db(db_file):
    """Creates tables and inserts mock data"""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE Plan (
            id_plan INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            dias INTEGER NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE Recordatorio (
            id_recordatorio INTEGER PRIMARY KEY AUTOINCREMENT,
            horas_antes INTEGER NOT NULL,
            nota TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE Suscripcion (
            id_suscripcion INTEGER PRIMARY KEY AUTOINCREMENT,
            id_plan INTEGER NOT NULL,
            id_recordatorio INTEGER,
            nombre TEXT NOT NULL,
            fecha_pago DATETIME NOT NULL,
            monto_pago REAL NOT NULL,
            medio_pago TEXT NOT NULL,
            FOREIGN KEY (id_plan) REFERENCES Plan(id_plan),
            FOREIGN KEY (id_recordatorio) REFERENCES Recordatorio(id_recordatorio)
        )
    """)
    cursor.execute("""
        CREATE TABLE Pago (
            id_pago INTEGER PRIMARY KEY AUTOINCREMENT,
            id_suscripcion INTEGER NOT NULL,
            fecha DATETIME NOT NULL,
            monto REAL NOT NULL,
            FOREIGN KEY (id_suscripcion) REFERENCES Suscripcion(id_suscripcion)
        )
    """)

    cursor.executemany(
        "INSERT INTO Plan (nombre, dias) VALUES (?, ?)",
        [("Básico", 30), ("Premium", 90), ("VIP", 365)]
    )
    cursor.executemany(
        "INSERT INTO Recordatorio (horas_antes, nota) VALUES (?, ?)",
        [(24, "Recordar pago mensual"), (48, "Recordar pago trimestral")]
    )
    cursor.executemany(
        """
        INSERT INTO Suscripcion (id_plan, id_recordatorio, nombre, fecha_pago, monto_pago, medio_pago)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            (1, 1, "Suscripción A", "2025-10-20", 100.0, "Tarjeta"),
            (2, 2, "Suscripción B", "2025-10-21", 250.0, "Efectivo"),
        ]
    )
    cursor.executemany(
        "INSERT INTO Pago (id_suscripcion, fecha, monto) VALUES (?, ?, ?)",
        [
            (1, "2025-10-21", 100.0),
            (2, "2025-10-22", 250.0),
        ]
    )
    conn.commit()
    conn.close()


def test_querying_db(tmp_path):
    db_file = tmp_path / "mock_query.db"
    setup_mock_db(db_file)

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.nombre, p.nombre
        FROM Suscripcion s
        JOIN Plan p ON s.id_plan = p.id_plan
        ORDER BY s.id_suscripcion
    """)
    subs_with_plan = cursor.fetchall()
    assert subs_with_plan == [("Suscripción A", "Básico"), ("Suscripción B", "Premium")]

    cursor.execute("SELECT SUM(monto) FROM Pago")
    total = cursor.fetchone()[0]
    assert total == 350.0

    cursor.execute("""
        SELECT s.nombre
        FROM Suscripcion s
        JOIN Recordatorio r ON s.id_recordatorio = r.id_recordatorio
        WHERE r.horas_antes > 24
    """)
    subs_long_reminder = cursor.fetchall()
    assert subs_long_reminder == [("Suscripción B",)]


    cursor.execute("SELECT nombre FROM Plan WHERE dias > 100 ORDER BY dias, nombre")
    long_plans = cursor.fetchall()
    assert long_plans == [("VIP",)]

    conn.close()

def test_delete_row(tmp_path):
    db_file = tmp_path / "mock_delete.db"
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE Plan (
            id_plan INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            dias INTEGER NOT NULL
        )
    """)
    conn.commit()

    cursor.executemany(
        "INSERT INTO Plan (nombre, dias) VALUES (?, ?)",
        [("Básico", 30), ("Premium", 90), ("VIP", 365)]
    )
    conn.commit()

    cursor.execute("SELECT nombre FROM Plan ORDER BY id_plan")
    rows_before = cursor.fetchall()
    assert rows_before == [("Básico",), ("Premium",), ("VIP",)]

    cursor.execute("DELETE FROM Plan WHERE nombre = ?", ("Premium",))
    conn.commit()

    cursor.execute("SELECT nombre FROM Plan ORDER BY id_plan")
    rows_after = cursor.fetchall()
    assert rows_after == [("Básico",), ("VIP",)]

    conn.close()
