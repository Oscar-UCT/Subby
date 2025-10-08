-- Tabla Plan
CREATE TABLE Plan (
    id_plan INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    dias INTEGER NOT NULL
);

-- Tabla Recordatorio
CREATE TABLE Recordatorio (
    id_recordatorio INTEGER PRIMARY KEY AUTOINCREMENT,
    horas_antes INTEGER NOT NULL,
    nota TEXT NOT NULL
);

-- Tabla Suscripcion
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
);

-- Tabla Pago
CREATE TABLE Pago (
    id_pago INTEGER PRIMARY KEY AUTOINCREMENT,
    id_suscripcion INTEGER NOT NULL,
    fecha DATETIME NOT NULL,
    monto REAL NOT NULL,
    FOREIGN KEY (id_suscripcion) REFERENCES Suscripcion(id_suscripcion)
);