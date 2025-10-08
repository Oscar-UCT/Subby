# Modelo relacional - Detalle

## Entidad Suscripción
Columnas:
* id_plan - NOT NULL
* id_recordatorio - NULLABLE
* nombre - NOT NULL - string
* fecha_pago - NOT NULL - datetime
* monto_pago - NOT NULL - number
* medio_pago - NOT NULL - string

## Entidad Pago
Columnas: 
* id_suscripcion - NOT NULL
* fecha - NOT NULL - datetime
* monto - NOT NULL - number

## Entidad Plan
Columnas:
* nombre - NOT NULL - string
* días - NOT NULL - number

## Entidad Recordatorio
Columnas:
* horas_antes - NOT NULL - number
* nota - NOT NULL - string