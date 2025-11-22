import sqlite3
from datetime import datetime

def check_db():
    conn = sqlite3.connect("subscriptions.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Plan (
            id_plan INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            dias INTEGER NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Recordatorio (
            id_recordatorio INTEGER PRIMARY KEY AUTOINCREMENT,
            horas_antes INTEGER NOT NULL,
            nota TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Suscripcion (
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
        CREATE TABLE IF NOT EXISTS Pago (
            id_pago INTEGER PRIMARY KEY AUTOINCREMENT,
            id_suscripcion INTEGER NOT NULL,
            fecha DATETIME NOT NULL,
            monto REAL NOT NULL,
            FOREIGN KEY (id_suscripcion) REFERENCES Suscripcion(id_suscripcion)
        )
    """)

    default_plans = [
        ("Mensual", 30),
        ("Anual", 365),
        ("Semestral", 180),
    ]

    for nombre, dias in default_plans:
        cursor.execute("SELECT 1 FROM Plan WHERE nombre = ?", (nombre,))
        exists = cursor.fetchone()

        if not exists:
            cursor.execute(
                "INSERT INTO Plan (nombre, dias) VALUES (?, ?)",
                (nombre, dias)
            )

    conn.commit()
    conn.close()

def load_suscriptions():
    check_db()
    conn = sqlite3.connect("subscriptions.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Suscripcion")
    datos = cursor.fetchall()
    conn.close()
    return datos

def load_payments():
    conn = sqlite3.connect("subscriptions.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Pago")
    payments = cursor.fetchall()
    conn.close()
    return payments

def create_subscription(nombre, plan_id, fecha_pago, monto_pago, medio_pago):
    conn = sqlite3.connect("subscriptions.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Suscripcion (nombre, id_plan, fecha_pago, monto_pago, medio_pago)
        VALUES (?, ?, ?, ?, ?)
    """, (nombre, plan_id, fecha_pago, monto_pago, medio_pago))
    conn.commit()
    conn.close()

def delete_subscription(id):
    conn = sqlite3.connect("subscriptions.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Suscripcion WHERE id_suscripcion = ?", (id,))
    conn.commit()
    conn.close()

def edit_subscription(id, nombre=None, fecha_pago=None, monto_pago=None, medio_pago=None):
    conn = sqlite3.connect("subscriptions.db")
    cursor = conn.cursor()
    
    update_fields = []
    params = []
    
    if nombre is not None:
        update_fields.append("nombre = ?")
        params.append(nombre)
    if fecha_pago is not None:
        update_fields.append("fecha_pago = ?")
        params.append(fecha_pago)
    if monto_pago is not None:
        update_fields.append("monto_pago = ?")
        params.append(monto_pago)
    if medio_pago is not None:
        update_fields.append("medio_pago = ?")
        params.append(medio_pago)
    
    if update_fields:
        params.append(id)
        cursor.execute(f"""
            UPDATE Suscripcion 
            SET {', '.join(update_fields)} 
            WHERE id_suscripcion = ?
        """, params)
    
    conn.commit()
    conn.close()

def load_plan_by_id(id):
    conn = sqlite3.connect("subscriptions.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Plan WHERE id_plan = ?", (id,))
    plan = cursor.fetchone()
    conn.close()
    return plan

def get_plan_id_from_string(plan_name):
    conn = sqlite3.connect("subscriptions.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id_plan FROM Plan WHERE nombre = ?", (plan_name,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def create_plan(name, days):
    conn = sqlite3.connect("subscriptions.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO Plan (nombre, dias) VALUES (?, ?)", (name, days))
    conn.commit()
    conn.close()

def get_monthly_expense():
    conn = sqlite3.connect("subscriptions.db")
    cursor = conn.cursor()

    # Get subscriptions with their plan duration in one query
    cursor.execute("""
        SELECT S.monto_pago, P.dias
        FROM Suscripcion S
        JOIN Plan P ON S.id_plan = P.id_plan
    """)

    rows = cursor.fetchall()
    conn.close()

    total = 0.0

    for monto, dias in rows:
        if dias <= 0:
            continue  # safety

        # Convert price into monthly-equivalent
        # Monthly price = total_price * (30 / duration_in_days)
        monthly_cost = monto * (30 / dias)
        total += monthly_cost

    return f"${int(round(total)):,}".replace(",", ".")


def get_next_subscription():
    conn = sqlite3.connect("subscriptions.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Suscripcion")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return None

    today = datetime.now()
    closest = None
    closest_date = None

    for row in rows:
        fecha_str = row[4]

        try:
            fecha = datetime.strptime(fecha_str.strip(), "%d/%m/%Y")
        except:
            continue

        if fecha < today:
            continue

        if closest is None or fecha < closest_date:
            closest = row
            closest_date = fecha

    return closest
