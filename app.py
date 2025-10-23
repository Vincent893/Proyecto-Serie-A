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

# Filtros en la barra lateral
st.sidebar.header("Filtros")

all_teams = sorted(df["Team"].dropna().unique())
selected_teams = st.sidebar.multiselect("Equipos", options=all_teams, default=all_teams)

all_seasons = sorted(df["Season"].dropna().unique())
selected_seasons = st.sidebar.multiselect("Temporadas", options=all_seasons, default=all_seasons)

all_results = sorted(df["Result"].dropna().unique())
selected_results = st.sidebar.multiselect("Resultados", options=all_results, default=all_results)

all_venues = sorted(df["Venue"].dropna().unique())
selected_venues = st.sidebar.multiselect("Localía", options=all_venues, default=all_venues)

min_goals = int(df["GF"].min())
max_goals = int(df["GF"].max())
selected_goals = st.sidebar.slider("Rango de goles", min_value=min_goals, max_value=max_goals, value=(min_goals, max_goals))

min_date = df["Date"].min()
max_date = df["Date"].max()
selected_dates = st.sidebar.date_input("Rango de fechas", min_value=min_date, max_value=max_date, value=(min_date, max_date))

# Boton para eliminar filtros
if st.sidebar.button("Restablecer filtros"):
    st.experimental_rerun()

# Aplicar filtros al dataframe
def apply_filters(df: pd.DataFrame,
                  teams: list[str],
                  seasons: list,
                  results: list[str],
                  venues: list[str],
                  goals_range: tuple,
                  date_range: tuple) -> pd.DataFrame:
    df_f = df.copy()
    if teams:
        df_f = df_f[df_f["Team"].isin(teams)]
    if seasons:
        df_f = df_f[df_f["Season"].isin(seasons)]
    if results:
        df_f = df_f[df_f["Result"].isin(results)]
    if venues:
        df_f = df_f[df_f["Venue"].isin(venues)]
    if goals_range:
        df_f = df_f[(df_f["GF"] >= goals_range[0]) & (df_f["GF"] <= goals_range[1])]

    if date_range and len(date_range) == 2:
        start_dt = pd.to_datetime(date_range[0])
        end_dt = pd.to_datetime(date_range[1])
        df_f = df_f[(df_f["Date"] >= start_dt) & (df_f["Date"] <= end_dt)]
    return df_f

df_filtered = apply_filters(df, selected_teams, selected_seasons, selected_results, selected_venues, selected_goals, selected_dates)

st.markdown(f"Mostrando: **{len(df_filtered)}** de {len(df)} partidos")
st.markdown("___")

# Grafico de goles totales y en promedio
st.subheader("Goles por Equipo")

agg_choice = st.radio("Mostrar:", options=["Totales", "En Promedio por Partido"], index=0, horizontal=True)
if agg_choice == "Totales":
    df_bars = df_filtered.groupby("Team", as_index=False)["GF"].sum().sort_values("GF", ascending=False)
    fig_bars = px.bar(df_bars, x="Team", y="GF", title="Goles Totales por Equipo",labels={"GF": "Goles Totales", "Team": "Equipo"})
else:
    df_bars = df_filtered.groupby("Team", as_index=False)[["GF"]].mean().sort_values("GF", ascending=False)
    fig_bars = px.bar(df_bars, x="Team", y="GF", title="Goles Promedio por Partido y Equipo", labels={"GF": "Goles Promedio por Partido", "Team": "Equipo"})

fig_bars.update_layout(
    xaxis_tickangle=-45,
    height=450, 
    title_x=0.4, 
    title={'font': {'size': 26}, 'x': 0.5, 'xanchor': 'center'},
    xaxis_title_font={'size': 18},
    yaxis_title_font={'size': 18},
    font=dict(size=14))

st.plotly_chart(fig_bars, use_container_width=True)
st.markdown("___")

