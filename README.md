# Seguimiento 1 - Análisis de algoritmos

Este proyecto implementa los requerimientos funcionales del PDF del curso:

- ETL automatizado por HTTP para datos históricos diarios de 20 activos y mínimo 5 años.
- Limpieza de datos, tratamiento de faltantes y unificación de calendario bursátil.
- Comparación de 12 algoritmos de ordenamiento sobre datos enteros.
- Ordenamiento ascendente de registros por fecha y precio de cierre.
- Gráfica de barras de tiempos y generación del top 15 por volumen.

## Restricciones cumplidas

- No se usa `yfinance`, `pandas_datareader` ni librerías equivalentes para descarga principal.
- La descarga se realiza con solicitudes HTTP directas (`requests`) a una API pública de series históricas.
- Los algoritmos de ordenamiento solicitados se implementan explícitamente.

## Estructura de salida

- `data/raw/`: CSV descargados por activo.
- `data/processed/dataset_unificado.csv`: dataset maestro unificado y ordenado.
- `outputs/tabla1_tiempos.csv`: tabla de tiempos de la comparación.
- `outputs/tabla1_tiempos.md`: tabla en formato Markdown.
- `outputs/barras_tiempos_ordenamiento.png`: gráfico de barras ascendente.
- `outputs/top15_mayor_volumen_asc.csv`: quince días con mayor volumen, listados en ascendente.
- `outputs/metadata.json`: metadatos de ejecución y parámetros.

## Estructura del código (Opción A)

- `main.py`: punto de entrada CLI.
- `src/app.py`: orquestación del pipeline completo.
- `src/config.py`: configuración global y constantes.
- `src/domain/models.py`: entidades de dominio (`PriceRow`).
- `src/etl/downloader.py`: descarga HTTP y reintentos.
- `src/etl/cleaner.py`: limpieza e imputación de datos.
- `src/etl/unifier.py`: alineación de calendario y ordenación.
- `src/sorting/algorithms.py`: implementación explícita de los 12 algoritmos.
- `src/sorting/benchmark.py`: medición de tiempos y validación de orden.
- `src/reporting/writers.py`: generación de CSV, Markdown y metadata.
- `src/reporting/plots.py`: gráfica de barras.

## Ejecución

1. Instalar dependencias:

```powershell
pip install -r requirements.txt
```

2. Ejecutar pipeline completo:

```powershell
python main.py
```

## Parámetros opcionales

- `--years`: años históricos a descargar (por defecto `5`).
- `--benchmark-size`: tamaño de muestra de enteros para benchmark (por defecto `1200`).

Ejemplo:

```powershell
python main.py --years 6 --benchmark-size 1500
```

## Nota metodológica

Para los algoritmos cuadráticos, se usa un subconjunto de enteros del dataset unificado al medir tiempos para mantener viabilidad computacional y comparar los 12 métodos en condiciones equivalentes.

