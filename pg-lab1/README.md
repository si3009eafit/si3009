# pg-lab init scripts (PostgreSQL)
Carpeta `init/` para usar con `docker compose` montada en `/docker-entrypoint-initdb.d`.

## Orden recomendado
1. `01_schema.sql` -> crea tablas (sin índices secundarios a propósito)
2. `02_seed_small.sql` -> datos pequeños (rápido) + ANALYZE
   - (Opcional) luego ejecuta `03_seed_big.sql` en vez del small si vas por millones
3. `06_measurement_helpers.sql` -> extensiones/ayudas (pg_stat_statements si está habilitada)
4. `04_bad_queries.sql` -> consultas base con EXPLAIN ANALYZE
5. `05_optimizations.sql` -> aplica optimizaciones incrementalmente y vuelve a ejecutar `04_bad_queries.sql`

## Consejos
- Para el informe: captura (copiar/pegar) el plan y tiempos antes/después.
- En Postgres, prueba `EXPLAIN (ANALYZE, BUFFERS)` para ver IO.
- Si usas dataset grande, considera ejecutar por bloques y medir impacto de:
  - índices simples vs compuestos
  - estadísticas (ANALYZE)
  - índices por expresión (date_trunc)
  - GIN + pg_trgm para búsquedas por substring
