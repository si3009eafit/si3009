# Informe técnico — Optimización de consultas (EAFITShop)

**Curso:** Bases de Datos Avanzadas — EAFIT  
**Unidad:** Optimización de BD Relacionales  
**Equipo:** [Nombres]  
**Motor:** PostgreSQL (RDS)  
**Dataset:** [class / stress] — (volúmenes)  
**Fecha:** [YYYY-MM-DD]

---

## 1. Resumen ejecutivo (½ página)
- Problema principal observado
- Optimización con mayor impacto
- Trade-off lectura vs escritura (en 1 frase con métrica)

---

## 2. Contexto del sistema y carga
- Descripción breve del sistema (OLTP e-commerce)
- Tamaños de tablas (pegar salida de `08_evidence_queries.sql`)

Tabla sugerida:

| Tabla | Tamaño total | Comentario |
|---|---:|---|
| orders | | |
| order_item | | |
| payment | | |

---

## 3. Metodología experimental
- Herramientas: EXPLAIN (ANALYZE, BUFFERS), pg_stat_statements, Performance Insights (si aplica)
- Control de variables:
  - misma consulta, mismos parámetros
  - ANALYZE ejecutado en puntos clave
  - entorno (instancia RDS, storage)

---

## 4. Diagnóstico inicial (antes de optimizar)
### 4.1 Consulta Q1 — Ventas por ciudad
- SQL (o referencia)
- Plan (pegar extracto relevante)
- Métricas: tiempo total, buffers, filas estimadas vs reales
- Interpretación: ¿cuál es el cuello?

### 4.2 Consulta Q2 — Top productos
(igual)

### 4.3 Consulta Q3 — Dashboard
(igual)

*(Opcional: Q4/Q5/Q6)*

---

## 5. Optimización incremental (antes/después)
> Presenta por etapas (B1..B5). Cada etapa debe tener hipótesis, cambio y evidencia.

### B1. Índices para FKs / joins
- Hipótesis:
- Cambio aplicado (SQL):
- Evidencia: diferencia de plan + tiempos

### B2. Índice por fecha
...

### B3. Índice compuesto dashboard
...

### B4. Reescritura o índice por expresión
...

### B5. GIN + trigram para substring
...

---

## 6. Trade-off: índice vs escritura (OLTP)
Describe el experimento (workload_runner):
- N operaciones:
- Concurrencia:
- 3 escenarios de índices:

Tabla sugerida:

| Escenario | TPS | Latencia media (ms) | p95 (ms) |
|---|---:|---:|---:|
| Sin índices extra | | | |
| Índices FKs | | | |
| Todos | | | |

Conclusión: ¿cuál conjunto de índices recomendarías para OLTP?

---

## 7. Conclusiones y recomendaciones
- 3 hallazgos principales (con evidencia)
- Recomendación final de índices “mínimos” vs “especializados”
- Qué mejorarías en esquema / consultas (refactor SQL, vistas materializadas, particionamiento, etc.)

---

## Anexos
- Scripts SQL (link o pegado)
- Capturas de Performance Insights (si aplica)
- Salidas completas de EXPLAIN (si no caben en cuerpo)
