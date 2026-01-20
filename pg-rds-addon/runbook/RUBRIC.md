# Rúbrica (Informe técnico corto) — Optimización de BD Relacionales (EAFITShop)

Puntaje total sugerido: 100 pts (convertible a escala 0.0–5.0)

## 1) Diagnóstico y análisis del problema (SO1) — 25 pts
- (10) Identifica correctamente cuellos de botella del plan (Seq Scan, joins, sort, aggregate, buffers)
- (10) Interpreta estimaciones vs reales (rows) y discute misestimations / rol de estadísticas
- (5) Usa terminología correcta (Index Scan, Bitmap, Hash Join, Nested Loop, etc.)

## 2) Diseño y justificación de optimizaciones (SO2) — 30 pts
- (10) Selección adecuada de índices (FKs, compuestos, expresión, GIN/trgm cuando aplica)
- (10) Justificación técnica clara (selectividad, orden, sargabilidad, cardinalidad)
- (10) Proceso incremental y razonado (no “probé cosas al azar”)

## 3) Evidencia experimental y reproducibilidad (SO5) — 25 pts
- (10) Métricas antes/después (tiempo total, buffers/IO, top SQL si disponible)
- (10) Código SQL documentado y ejecutable (scripts limpios, orden, comentarios)
- (5) Control de variables (mismo dataset, mismo entorno, se ejecuta ANALYZE cuando corresponde)

## 4) Comunicación técnica (SO3) — 20 pts
- (10) Informe claro (estructura, tablas/figuras, conclusiones)
- (5) Presenta planes de ejecución relevantes (no excesivos) y resaltan cambios clave
- (5) Conclusiones conectadas con evidencia (no opiniones)

### Criterios de excelencia (A)
- Explica trade-offs (lectura vs escritura) con mediciones.
- Propone índice “mínimo viable” para OLTP + índice “especializado” y su costo.
- Explica por qué ciertas consultas no son indexables con B-tree (ej. '%texto') y qué alternativa aplica.
