"""Dashboard de lluvias y declaratorias de emergencia por departamento.

Correr en local (desde la carpeta assignment_3/):
    uv run streamlit run app.py
"""

import unicodedata
from pathlib import Path

import pandas as pd
import plotly.express as px
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


def sin_tildes(texto):
    # Para ordenar: sorted() a secas manda "Áncash" al final de la lista
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()


departamentos = sorted(datos["departamento"].unique(), key=sin_tildes)
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

# ---------------------------------------------------------------------- graficos
izq, der = st.columns(2)

# Misma altura para los dos graficos; crece con el numero de departamentos
alto = max(350, 24 * len(filtrado))

with izq:
    st.subheader("Decretos por departamento")
    por_depto = (
        filtrado.sort_values("total_decretos")
        .rename(columns={"declaratorias": "Declaratorias", "prorrogas": "Prórrogas"})
    )
    fig = px.bar(
        por_depto, x=["Declaratorias", "Prórrogas"], y="departamento", orientation="h",
        color_discrete_map={"Declaratorias": "#a50f15", "Prórrogas": "#fc9272"},
        labels={"value": "Decretos", "departamento": "", "variable": ""},
    )
    fig.update_layout(
        template="plotly_white", height=alto,
        legend=dict(orientation="h", yanchor="bottom", y=1.0, x=0),
    )
    st.plotly_chart(fig, width="stretch")

with der:
    st.subheader("¿Más lluvia, más declaratorias?")
    fig = px.scatter(
        filtrado, x="lluvia_total_mm", y="declaratorias",
        hover_name="departamento",
        hover_data={"capital": True, "prorrogas": True, "dias_lluvia_fuerte": True},
        labels={
            "lluvia_total_mm": "Lluvia acumulada ene-may 2024 (mm)",
            "declaratorias": "Declaratorias",
            "prorrogas": "Prórrogas",
            "capital": "Capital",
            "dias_lluvia_fuerte": "Días con 20 mm o más",
        },
    )
    fig.update_traces(marker=dict(size=11, color="#a50f15", line=dict(width=1.5, color="white")))
    fig.update_layout(template="plotly_white", height=alto)
    st.plotly_chart(fig, width="stretch")

# -------------------------------------------------------------------------- mapa
st.subheader("Mapa por capital de departamento")
st.caption("Tamaño del punto: lluvia acumulada · Color: número de declaratorias")

fig = px.scatter_map(
    filtrado,
    lat="latitud",
    lon="longitud",
    color="declaratorias",
    size="lluvia_total_mm",
    color_continuous_scale="YlOrRd",
    # Escala de color fija: un departamento no cambia de color al filtrar
    range_color=[0, datos["declaratorias"].max()],
    size_max=30,
    map_style="carto-positron",
    zoom=4.3,
    center={"lat": -9.2, "lon": -75.0},
    hover_name="departamento",
    hover_data={
        "capital": True, "declaratorias": True, "prorrogas": True,
        "lluvia_total_mm": True, "latitud": False, "longitud": False,
    },
    labels={
        "declaratorias": "Declaratorias", "prorrogas": "Prórrogas",
        "lluvia_total_mm": "Lluvia (mm)", "capital": "Capital",
    },
    height=550,
)
# Tamano fijo respecto a todo el dataset (no solo al filtro) y minimo visible
fig.update_traces(marker=dict(sizeref=2 * datos["lluvia_total_mm"].max() / 30**2, sizemin=5))
fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
st.plotly_chart(fig, width="stretch")

# ------------------------------------------------------------------------- tabla
st.subheader("Datos por departamento")

tabla = filtrado.sort_values(["total_decretos", "lluvia_total_mm"], ascending=False)[
    ["ubigeo", "departamento", "capital", "declaratorias", "prorrogas",
     "total_decretos", "lluvia_total_mm", "dias_lluvia_fuerte"]
]

st.dataframe(
    tabla.rename(columns={
        "ubigeo": "Ubigeo", "departamento": "Departamento", "capital": "Capital",
        "declaratorias": "Declaratorias", "prorrogas": "Prórrogas",
        "total_decretos": "Total decretos", "lluvia_total_mm": "Lluvia (mm)",
        "dias_lluvia_fuerte": "Días con 20 mm o más",
    }),
    width="stretch",
    hide_index=True,
)
st.caption("1 mm de lluvia equivale a 1 litro de agua por metro cuadrado.")

st.download_button(
    "Descargar datos filtrados (CSV)",
    tabla.to_csv(index=False).encode("utf-8-sig"),
    "lluvias_emergencias_filtrado.csv",
    "text/csv",
)
