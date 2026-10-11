"""
Dashboard: Lluvias y declaratorias de emergencia por departamento (Peru)

Correr en local, desde la carpeta assignment_3/:
    uv run streamlit run app.py
"""

from pathlib import Path

import pandas as pd
import streamlit as st

# --- Configuracion de la pagina ---------------------------------------------
st.set_page_config(
    page_title="Lluvias y emergencias en el Peru",
    page_icon="🌧️",
    layout="wide",
)

# Ruta al CSV relativa a este archivo: funciona en local y en Streamlit Cloud
RUTA_DATOS = Path(__file__).parent / "datos" / "dataset.csv"


# --- Carga de datos ---------------------------------------------------------
@st.cache_data
def cargar_datos(ruta):
    # utf-8-sig quita el BOM del CSV; ubigeo como texto para conservar el 0 inicial
    df = pd.read_csv(ruta, encoding="utf-8-sig", dtype={"ubigeo": str})
    df["total_decretos"] = df["declaratorias"] + df["prorrogas"]
    return df


df = cargar_datos(RUTA_DATOS)

# --- Encabezado -------------------------------------------------------------
st.title("🌧️ Lluvias y declaratorias de emergencia en el Peru")
st.markdown(
    "Cruce entre los **decretos de estado de emergencia por lluvias** "
    "(declaratorias y prorrogas) y la **lluvia acumulada** registrada en la "
    "capital de cada departamento."
)
