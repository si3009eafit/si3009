# Guía del profesor — Unidad Optimización BD Relacionales (3 semanas) — Caso EAFITShop (RDS PostgreSQL)

## Propósito didáctico
Este caso está diseñado para que el estudiante:
- Lea planes reales (`EXPLAIN (ANALYZE, BUFFERS)`) y diagnostique cuellos de botella.
- Aplique optimizaciones incrementales (índices, estadísticas, reescritura) y mida impacto.
- Entienda trade-offs lectura vs escritura (TPS/latencias).
- Compare decisiones del optimizador (cost-based) y el rol de estadísticas.
- (Semana 3) Use particionamiento para “podar” datos históricos (partition pruning).

---

# 1) Preparación (antes de la clase)
## 1.1 Instancia RDS y observabilidad
- Performance Insights habilitado (ideal).
- Parameter Group con `pg_stat_statements` en `shared_preload_libraries`.
- Extensiones en DB: `pg_stat_statements`, `pg_trgm`, `aws_s3`.
- Dataset cargado (escala class para todos; stress para 1–2 grupos).

## 1.2 Recomendación de escala para clase
- 200k customers, 20k products, 1M orders, 4M order_items, 800k payments.
Esto ya produce:
- scans grandes
- hash joins
- agregaciones masivas
- mejoras visibles con índices

---

# 2) “Lo que deberías ver” en los planes (expectativas típicas)

> Nota: los planes exactos dependen de versión, recursos, cache y estadísticas.
> El objetivo es que los estudiantes **justifiquen** con evidencia.

## Q1 Ventas por ciudad en 2023 (join + filtro por rango)
**Antes**:
- `Seq Scan` en `orders` o `Bitmap Heap Scan` sin soporte eficiente.
- Join probablemente `Hash Join` (sin índices).
- Buffers: muchos `shared read` (IO).

**Después (idx_orders_order_date + idx_orders_customer_id)**:
- Filtrado por rango con índice (`Index Scan` o `Bitmap Index Scan`).
- Menos filas entrando al join.
- Tiempo y buffers bajan notablemente.

Discusión:
- selectividad del rango
- rol de estadísticas (ANALYZE) para estimar filas correctas

## Q2 Top productos vendidos (aggregate masivo)
**Antes**:
- `HashAggregate` sobre millones de filas en `order_item`.
- Join grande.
- Puede aparecer “Disk spill” si memoria no alcanza (depende de work_mem).

**Después (idx_order_item_product_id)**:
- Puede mejorar join, pero la agregación seguirá siendo pesada (porque hay que contar todo).
- Enseñanza clave: no todo se arregla con índices; a veces se requiere:
  - pre-aggregación (materialized view)
  - ETL a tabla resumen
  - particiones
  - límites/filters adicionales

## Q3 Dashboard (customer_id + ORDER BY + LIMIT)
**Antes**:
- `Seq Scan` con filtro o `Bitmap Heap Scan` y luego `Sort` costoso.

**Después (idx_orders_customer_date_desc)**:
- Idealmente `Index Scan` que ya retorna ordenado.
- El `LIMIT 20` se vuelve muy eficiente.

## Q4 ILIKE '%..%' (substring)
**Antes**:
- Scan casi inevitable (B-tree no ayuda).
**Después (pg_trgm + GIN)**:
- `Bitmap Index Scan` sobre índice trigram.
- Mejora muy evidente (gran “wow moment”).

## Q5 date_trunc(order_date)=...
**Antes**:
- Función sobre columna evita uso directo de índice por fecha (anti-pattern).
**Después**:
- Si usan índice por expresión, mejora.
- Si reescriben a rango (recomendado), también mejora y es más portable.

## Q6 Join orders+payment + filtro por payment_status
**Antes**:
- Join masivo
**Después**:
- índices en `payment(order_id)` y (opcional) `payment(payment_status)` ayudan.
- Discusión de selectividad: si ‘APPROVED’ es 90% no ayuda tanto.

---

# 3) Guion de clase por semana (3 semanas)

## Semana 1 — Diagnóstico y fundamentos (EXPLAIN / CBO)
**Clase 1**
- Introducción a optimización y “por qué el motor no es magia”
- Lectura guiada de EXPLAIN (ANALYZE, BUFFERS)
- Ejecutar Q1–Q3 antes de optimizar

**Clase 2**
- Índices: B-tree, compuestos, selectividad, sargabilidad
- Aplicar bloque B1 (índices FKs) y B2 (fecha)
- Re-ejecutar Q1, Q6 y comparar

Evidencia esperada:
- estudiantes describen al menos 3 cambios significativos de plan.

## Semana 2 — Índices avanzados + trade-off
- Bloque B3 (compuesto dashboard), B4 (expresión o reescritura), B5 (trgm+GIN)
- Medición de escritura: workload_runner (TPS/lat)
- Discusión: “índices mínimos para OLTP” vs “índices especializados”

Evidencia esperada:
- tabla TPS/latencias en 3 escenarios

## Semana 3 — Caso OLTP degradado + particionamiento
- Presentar “incidente”: reportes históricos afectan OLTP
- Opción A: particionamiento de orders por año/mes
- Opción B: materialized views para reportes (sugerido como extensión conceptual)
- Comparación de Q1 con pruning

Evidencia esperada:
- estudiantes muestran pruning y reducción de buffers.

---

# 4) Criterios de evaluación (recomendaciones)
- Penaliza “optimización por ensayo y error” sin hipótesis.
- Premia:
  - interpretación correcta del plan
  - justificación por selectividad/cardinalidad
  - control de variables (misma query, misma data, ANALYZE)
  - discusión de trade-offs

---

# 5) Troubleshooting típico
- `pg_stat_statements` no aparece:
  - falta shared_preload_libraries en parameter group o no reiniciaron.
- Import S3 falla:
  - IAM role no asociado o policy sin GetObject/ListBucket.
  - bucket/region/prefix mal escritos.
- Q2 sigue lenta:
  - es normal; es un “teachable moment” sobre agregaciones masivas.
