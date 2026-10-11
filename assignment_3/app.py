"""Dashboard de lluvias y declaratorias de emergencia por departamento.

Correr en local (desde la carpeta assignment_3/):
    uv run streamlit run app.py
"""

from pathlib import Path

import pandas as pd
import streamlit as st

# ---------------------------------------------------------------- configuracion
st.set_page_config(page_title="Lluvias y emergencias en el Perú", page_icon="🌧️", layout="wide")

# Ruta relativa a este archivo: Streamlit Cloud corre la app desde la raiz del
# repo, asi que "datos/dataset.csv" a secas no encontraria el archivo.
RUTA_DATOS = Path(__file__).parent / "datos" / "dataset.csv"


# ------------------------------------------------------------------ carga datos
# @st.cache_data guarda el resultado: sin esto, el archivo se lee otra vez
# cada vez que alguien mueve un filtro y la app va lentísima.
@st.cache_data
def cargar():
    # utf-8-sig quita el BOM del CSV; ubigeo como texto para no perder el 0
    datos = pd.read_csv(RUTA_DATOS, encoding="utf-8-sig", dtype={"ubigeo": str})
    datos["total_decretos"] = datos["declaratorias"] + datos["prorrogas"]
    return datos


datos = cargar()

# ----------------------------------------------------------------------- filtros
st.sidebar.header("Filtros")

departamentos = sorted(datos["departamento"].unique())
elegidos = st.sidebar.multiselect(
    "Departamento", departamentos, default=departamentos
)

minimo = st.sidebar.slider(
    "Lluvia mínima en la temporada (mm)",
    0, int(datos["lluvia_total_mm"].max()), 0, step=50,
)

filtrado = datos[
    datos["departamento"].isin(elegidos) & (datos["lluvia_total_mm"] >= minimo)
]

# ------------------------------------------------------------------------ titulo
st.title("🌧️ Lluvias y declaratorias de emergencia en el Perú")
st.caption(
    "Temporada de lluvias enero-mayo 2024 por departamento · "
    "Fuentes: decretos de la PCM (gob.pe), lluvia diaria de Open-Meteo, ubigeos del INEI"
)

if filtrado.empty:
    st.warning("No hay departamentos que cumplan los filtros. Ajusta la selección.")
    st.stop()

# ---------------------------------------------------------------------- metricas
c1, c2, c3, c4 = st.columns(4)
c1.metric("Departamentos", f"{len(filtrado):,}")
c2.metric("Declaratorias", f"{int(filtrado['declaratorias'].sum()):,}")
c3.metric("Prórrogas", f"{int(filtrado['prorrogas'].sum()):,}")
c4.metric("Lluvia promedio (mm)", f"{filtrado['lluvia_total_mm'].mean():,.1f}")

st.divider()
