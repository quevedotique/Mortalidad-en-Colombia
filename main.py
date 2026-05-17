import streamlit as st
from vistas import inicio, analisis_grafico, analisis_ia
from src.procesador_datos import cargar_datos

st.set_page_config(
    page_title="Mortalidad Colombia 2019",
    page_icon="🏥",
    layout="wide"
)

st.markdown("""
<style>
/* Fondo principal */
.stApp {
    background-color: #0f1f3d;
}
/* Texto general */
.stApp, .stApp p, .stApp label,
.stMarkdown, .stCaption {
    color: #c8d8f0 !important;
}
/* Tabs */
.stTabs [data-baseweb="tab"] {
    color: #8ab4d4 !important;
}
.stTabs [aria-selected="true"] {
    color: #ffffff !important;
}
/* Métricas */
[data-testid="metric-container"] {
    background-color: #1e3a5f;
    border-radius: 10px;
    padding: 0.5rem;
    border-left: 4px solid #5ab4ff;
}
[data-testid="metric-container"] label,
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #ffffff !important;
}
/* Info / alert box */
.stAlert {
    background-color: #1e3a5f !important;
    color: #c8d8f0 !important;
}
/* Expander */
details summary {
    color: #c8d8f0 !important;
}
/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #0a1628;
}
[data-testid="stSidebar"] * {
    color: #c8d8f0 !important;
}
/* Selectbox y multiselect */
[data-testid="stSelectbox"] label,
[data-testid="stMultiSelect"] label {
    color: #c8d8f0 !important;
}
/* Divider */
hr {
    border-color: #1e3a5f;
}
</style>
""", unsafe_allow_html=True)

# ── Cargar datos ──────────────────────────────────────────────────────────
@st.cache_data
def get_data():
    return cargar_datos()

df, _, _ = get_data()  # cargar_datos() retorna (df, div, cod)

# ── Sidebar de navegación ─────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Mortalidad")
    st.markdown("#### Colombia 2019")
    st.divider()

    st.markdown("### Navegación")
    pagina = st.radio(
        "",
        ["🏠 Inicio & Mapa", "📊 Análisis Gráfico", "🤖 Análisis con IA"],
        label_visibility="collapsed"
    )
    st.divider()

    st.markdown("### Filtros globales")
    maneras = ["Todas"] + sorted(df["MANERA_MUERTE"].dropna().unique().tolist())
    manera_sel = st.selectbox("Manera de muerte", maneras)

    deptos = ["Todos"] + sorted(df["DEPARTAMENTO"].dropna().unique().tolist())
    depto_sel = st.selectbox("Departamento", deptos)

    meses = ["Todos"] + sorted(df["NOMBRE_MES"].dropna().unique().tolist())
    mes_sel = st.selectbox("Mes", meses)

# ── Aplicar filtros globales ──────────────────────────────────────────────
df_filtrado = df.copy()
if manera_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado["MANERA_MUERTE"] == manera_sel]
if depto_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["DEPARTAMENTO"] == depto_sel]
if mes_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["NOMBRE_MES"] == mes_sel]

# ── Renderizar vista seleccionada ─────────────────────────────────────────
if "Inicio" in pagina:
    inicio.render(df_filtrado)
elif "Gráfico" in pagina:
    analisis_grafico.render(df_filtrado)
elif "IA" in pagina:
    analisis_ia.render(df_filtrado, cod=depto_sel)