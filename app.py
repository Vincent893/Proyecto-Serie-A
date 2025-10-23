import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Resumen Estadístico - Serie A",
                   layout="wide",
                   initial_sidebar_state="expanded")
st.title("Resumen Estadístico - Serie A")
st.subheader("Análisis interactivo de partidos basado en datos de las ultimas 5 tempoadas")

df = pd.read_csv("matches_serie_A.csv")

# Limpieza del dataframe
df["Date"] = pd.to_datetime(df["Date"], dayfirst=False, errors="coerce")
df["Season"] = df["Season"].replace({"2021": "2020/2021", "2022": "2021/2022", "2023": "2022/2023", "2024": "2023/2024", "2025": "2024/2025"})
df["Venue"] = df["Venue"].replace({"Home": "Local", "Away": "Visitante"})
df["Result"] = df["Result"].replace({"W": "Victoria", "L": "Derrota", "D": "Empate"})
df["YearMonth"] = df["Date"].dt.to_period("M").astype(str)

