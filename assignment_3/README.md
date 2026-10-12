# Lluvias y declaratorias de emergencia en el Perú

Dashboard en Streamlit que cruza, por departamento, **cuánto llovió en la temporada
de lluvias enero-mayo 2024** con **cuántos decretos de estado de emergencia por lluvias**
(declaratorias y prórrogas) publicó la PCM en ese mismo periodo. La pregunta que guía
la app es: *¿los departamentos donde más llovió son los que más declaratorias recibieron?*

**App desplegada:** https://lluvias-emergencias-peru-grupo11.streamlit.app

## Qué muestra

- **Filtros** en la barra lateral: departamentos y lluvia mínima acumulada (mm).
- **Métricas** que se actualizan con los filtros: departamentos, declaratorias,
  prórrogas y lluvia promedio.
- **Gráficos** (Plotly): decretos por departamento (barras) y lluvia vs. declaratorias
  (dispersión).
- **Mapa** con un punto en la capital de cada departamento: tamaño = lluvia acumulada,
  color = número de declaratorias.
- **Tabla** con los datos filtrados y botón para descargarlos en CSV.

## De dónde vienen los datos

La app lee un solo archivo, `datos/dataset.csv` (25 departamentos), que armamos en el
Assignment 2 cruzando tres fuentes por ubigeo:

| Fuente | Qué aporta |
|---|---|
| [Normas legales de la PCM en gob.pe](https://www.gob.pe/busquedas?contenido[]=normas&institucion[]=pcm) (scraping con Selenium) | Decretos supremos de declaratoria y prórroga de estado de emergencia por lluvias, enero-mayo 2024 |
| [Open-Meteo](https://open-meteo.com/): API histórica (`archive-api`) y API de geocodificación | Lluvia diaria (`precipitation_sum`) en la capital de cada departamento y sus coordenadas |
| INEI y [Wikipedia: Departamentos del Perú](https://es.wikipedia.org/wiki/Departamentos_del_Per%C3%BA) | Códigos de ubigeo y capital de cada departamento |

Columnas principales: `declaratorias`, `prorrogas`, `lluvia_total_mm` (lluvia acumulada
del 1 de enero al 31 de mayo de 2024) y `dias_lluvia_fuerte` (días con 20 mm o más).
La lluvia se mide en la capital, así que es una aproximación del departamento.

## Correr en local

Desde la carpeta `assignment_3/`:

```bash
uv venv
uv pip install -r requirements.txt
uv run streamlit run app.py
```
