# Runbook para estudiantes — Laboratorio de Optimización en RDS PostgreSQL (EAFITShop)

## Objetivo
Diagnosticar y mejorar el rendimiento de consultas y transacciones en un sistema OLTP (EAFITShop) usando:
- `EXPLAIN (ANALYZE, BUFFERS)`
- índices (simples, compuestos, por expresión, GIN+trigram)
- estadísticas (`ANALYZE`)
- (opcional) particionamiento
- métricas: tiempo, buffers/IO, top SQL

## Pre-requisitos
- Acceso a una instancia **Amazon RDS for PostgreSQL** (endpoint, usuario, password, DB).
- Cliente SQL: **DBeaver/CloudBeaver** o **pgAdmin**.
- (Opcional para carga): AWS CLI configurado si tu equipo genera CSV y sube a S3.

## Artefactos
Usa los scripts del kit:
- `sql/00_rds_setup.sql`
- `sql/01_schema.sql`
- `sql/04_bad_queries.sql`
- `sql/05_optimizations.sql`
- `sql/08_evidence_queries.sql`
- (opcional) `sql/07_partitioning_optional.sql`

---

# Parte A — Medición base (SIN optimizar)

## A1. Verificar extensiones y estadísticas
1) Ejecuta `sql/00_rds_setup.sql`
2) Ejecuta `ANALYZE;`

Evidencia (captura):
- Resultado de `SELECT extname FROM pg_extension;`

## A2. Ejecutar consultas base con plan de ejecución
Ejecuta cada query de `sql/04_bad_queries.sql`.
Para cada una, captura y guarda:
- Plan completo de `EXPLAIN (ANALYZE, BUFFERS)`
- Tiempo total
- N° de filas estimadas vs reales (líneas "rows=")
- Observación: ¿Seq Scan? ¿Hash Join? ¿Sort? ¿Aggregate masivo?

**Checklist de análisis**
- ¿Hay `Seq Scan` sobre tablas grandes?
- ¿El join es `Hash Join` porque no hay índices?
- ¿Aparece `Sort` costoso (mem/disk)?
- ¿Buffers: muchos `shared read` (IO) o más `hit` (cache)?

---

# Parte B — Optimización incremental (en etapas)

> Regla: aplica un bloque, corre de nuevo las mismas consultas (A2) y compara.

## B1. Índices para FKs (joins)
Ejecuta el bloque 1 de `sql/05_optimizations.sql` (idx en FKs).
Luego corre de nuevo Q1, Q2 y Q6.
Evidencias:
- ¿Cambió a `Index Scan` o `Bitmap Index Scan`?
- ¿Bajó el tiempo total? ¿Bajaron los buffers leídos?

## B2. Índice por rango temporal (order_date)
Ejecuta el bloque 2 (idx_orders_order_date).
Corre Q1.
Discute:
- ¿El filtro por fecha ahora usa índice?
- ¿El plan reduce filas tempranamente?

## B3. Índice compuesto para dashboard (customer_id, order_date desc)
Ejecuta bloque 3.
Corre Q3.
Discute:
- ¿Se elimina el `Sort`?
- ¿La consulta con `LIMIT` retorna rápido por el orden del índice?

## B4. Anti-pattern función sobre columna (date_trunc)
Ejecuta bloque 4 (índice por expresión).
Corre Q5.
Discute alternativas:
- Reescritura a rango (preferida) vs índice por expresión (didáctico)

## B5. Substring search (ILIKE '%..%') con trigram
Ejecuta bloque 5 (pg_trgm + GIN).
Corre Q4.
Discute:
- Por qué índices B-tree no ayudan con comodín inicial
- Por qué GIN + trigrams sí

---

# Parte C — Trade-off índice vs escritura (OLTP)

## C1. Medir inserciones antes/después
Mide tiempos de inserción de N órdenes (p.ej. 10k) en 3 escenarios:
1) Sin índices extra (solo PK)
2) Con índices de joins (B1)
3) Con todos los índices (B1..B5)

**Qué reportar**
- TPS (transacciones/seg) o tiempo total
- Observación: más índices → más costo de INSERT/UPDATE

---

# Parte D — Evidencias cuantitativas

Ejecuta `sql/08_evidence_queries.sql` y captura:
- Tamaño total por tabla (y cómo crecen índices)
- Top 10 SQL por tiempo (si `pg_stat_statements` está activo)

---

# Parte E — (Opcional) Particionamiento (semana 3)
Ejecuta `sql/07_partitioning_optional.sql` (requiere recrear orders y reinsertar).
Luego corre Q1 y observa `Partition Pruning`:
- ¿Cuántas particiones se escanean?
- ¿Se reduce IO?

---

# Plantilla de conclusiones (para el informe)
- Cuál era el cuello de botella principal (IO vs CPU vs sort vs join)
- Qué optimización produjo el mayor impacto y por qué
- Qué optimización NO ayudó (y por qué)
- Trade-off: impacto en escritura (TPS)
- Recomendaciones finales (índices “mínimos” para OLTP + índices “especializados” para casos puntuales)
