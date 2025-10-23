import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Resumen Estadístico - Serie A",
                   layout="wide",
                   initial_sidebar_state="expanded")
st.title("Resumen Estadístico - Serie A")
st.subheader("Análisis interactivo de equipos basado en datos de las ultimas 5 tempoadas")

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

# Métricas clave    
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Partidos Mostrados", f"{len(df_filtered):,}")
with col2:
    st.metric("Goles Totales", f"{int(df_filtered['GF'].sum()):,}")
with col3:
    avg_goals = df_filtered["GF"].mean() if len(df_filtered) > 0 else 0
    st.metric("Promedio goles por partido", f"{avg_goals:.2f}")
with col4:
    total_teams = df_filtered["Team"].nunique()
    st.metric("Equipos", f"{total_teams}")

st.markdown("___")

# Grafico de goles totales y en promedio
agg_choice = st.radio("Goles por Equipo:", options=["Totales", "En Promedio por Partido"], index=0, horizontal=True)
if agg_choice == "Totales":
    df_bars = df_filtered.groupby("Team", as_index=False)["GF"].sum().sort_values("GF", ascending=False)
    fig_bars = px.bar(df_bars, x="Team", y="GF", title="Goles Totales",labels={"GF": "Goles Totales", "Team": "Equipo"})
else:
    df_bars = df_filtered.groupby("Team", as_index=False)[["GF"]].mean().sort_values("GF", ascending=False)
    fig_bars = px.bar(df_bars, x="Team", y="GF", title="Goles Promedio por Partido", labels={"GF": "Goles Promedio por Partido", "Team": "Equipo"})

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

# Linea de tiempo del promedio de goles por mes
time_teams = st.multiselect("Equipos para la Serie Temporal", options=selected_teams, default=selected_teams[:3])

timeline = df_filtered[df_filtered["Team"].isin(time_teams)]
timeline["YearMonth"] = pd.to_datetime(timeline["YearMonth"], errors="coerce")
df_time = timeline.groupby(["YearMonth", "Team"], as_index=False)["GF"].mean()
fig_time = px.line(df_time, x="YearMonth", y="GF", color="Team", markers=True, title="Evolución del Promedio de Goles", labels={"GF": "Goles Promedio", "YearMonth": "Mes"})
fig_time.update_layout(
    title_x=0.4, 
    height=450,
    title={'font': {'size': 26}, 'x': 0.5, 'xanchor': 'center'},
    xaxis_title_font={'size': 18},
    yaxis_title_font={'size': 18},
    font=dict(size=14))

st.plotly_chart(fig_time, use_container_width=True)

st.markdown("___")

# Gráfico de barras de posesion promedio
avg_poss = df_filtered.groupby("Team")["Poss"].mean().reset_index()
avg_poss = avg_poss.sort_values(by="Poss", ascending=False)

fig_poss = px.bar(avg_poss, x="Poss", y="Team", orientation='h', color="Poss", color_continuous_scale="Blues",
              title="Posesión Promedio (%)", labels={"Poss": "Posesión Promedio (%)", "Team": "Equipo"}
)

fig_poss.update_layout(
    height=450, 
    title_x=0.4, 
    title={'font': {'size': 26}, 'x': 0.5, 'xanchor': 'center'},
    xaxis_title_font={'size': 18},
    yaxis_title_font={'size': 18},
    font=dict(size=14),
    coloraxis_colorbar=dict(title="Posesión (%)")
)
st.plotly_chart(fig_poss, use_container_width=True)

st.markdown("___")

# Tabla resumen por equipo
st.subheader("Tabla resumen")
summary = (df_filtered
           .groupby("Team", as_index=True)
           .agg(Partidos=("GF", "count"),
                Total_Goles =("GF", "sum"),
                Goles_Promedio=("GF", "mean"),
                Victorias=("Result", lambda x: (x == "Victoria").sum()),
                Empates=("Result", lambda x: (x == "Empate").sum()),
                Derrotas=("Result", lambda x: (x == "Derrota").sum()))
           .sort_values("Total_Goles", ascending=False)
           .reset_index())
st.dataframe(summary)

# CSS para personalizar estetica
st.markdown("""
<style>

    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #2c3e50 0%, #3498db 100%);
        color: white;
    }
    .css-1d391kg {
        background-color: #2c3e50;
    }
    /* Botones */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    }
    /* Radio buttons */
    .stRadio > div {
        flex-direction: row;
        align-items: center;
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .stRadio > label {
        font-weight: 600;
        margin-bottom: 0.5rem;
        color: #2c3e50;
    }
    /* Select boxes */
    .stMultiSelect [data-baseweb="select"] {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
    }
    .stMultiSelect [data-baseweb="select"]:hover {
        border-color: #667eea;
    }
    /* Separadores */
    .stMarkdown hr {
        margin: 3rem 0;
        border: none;
        height: 3px;
        background: linear-gradient(90deg, transparent, #667eea, transparent);
    }
    /* Dataframes */
    .dataframe {
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    /* Colores coordinados para gráficos */
    .metric-card {
        background: linear-gradient(135deg, #f8f9ff 0%, #e8eeff 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
    }
    /* Sidebar con fondo oscuro */
    [data-testid="stSidebar"] {
        background-color: #2f2c79;
    }
        [data-testid="stSidebar"] * {
        color: white !important;
    }
    /* Labels y textos específicos del sidebar */
    [data-testid="stSidebar"] label {
        color: white !important;
        font-weight: 600;
    }
    [data-testid="stSidebar"] .stMultiSelect, 
    [data-testid="stSidebar"] .stSlider,  {
        color: white !important;
    }
        [data-testid="stSidebar"] .stDateInput input {
        color: black !important;
        background-color: white !important;
    }
    [data-testid="stSidebar"] .stDateInput label {
        color: white !important;
    }
            </style>
""", unsafe_allow_html=True)
