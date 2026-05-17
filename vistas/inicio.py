import streamlit as st
import plotly.express as px
from src.procesador_datos import (
    muertes_por_departamento, stats_globales
)

COORDS_DEPTO = {
    'AMAZONAS': (-1.443, -71.572), 'ANTIOQUIA': (7.198, -75.344),
    'ARAUCA': (6.547, -71.003), 'ATLANTICO': (10.696, -74.996),
    'BOGOTA': (4.711, -74.072), 'BOLIVAR': (8.671, -74.033),
    'BOYACA': (5.454, -73.362), 'CALDAS': (5.298, -75.248),
    'CAQUETA': (1.614, -75.613), 'CASANARE': (5.759, -71.575),
    'CAUCA': (2.536, -76.627), 'CESAR': (9.337, -73.653),
    'CHOCO': (5.691, -76.658), 'CORDOBA': (8.049, -75.574),
    'CUNDINAMARCA': (4.867, -74.044), 'GUAINIA': (2.585, -68.525),
    'GUAVIARE': (2.044, -72.333), 'HUILA': (2.536, -75.528),
    'LA GUAJIRA': (11.354, -72.525), 'MAGDALENA': (10.41, -74.406),
    'META': (3.993, -73.561), 'NARIÑO': (1.287, -77.358),
    'NORTE DE SANTANDER': (7.944, -72.498), 'PUTUMAYO': (0.436, -75.523),
    'QUINDIO': (4.461, -75.667), 'RISARALDA': (5.315, -76.155),
    'SAN ANDRES': (12.544, -81.720), 'SANTANDER': (6.644, -73.653),
    'SUCRE': (8.814, -75.394), 'TOLIMA': (4.09, -75.152),
    'VALLE DEL CAUCA': (3.802, -76.512), 'VAUPES': (0.855, -70.813),
    'VICHADA': (4.423, -69.287),
}

BG = '#0f1f3d'
FONT_COLOR = "#f0f0f0"


def render(df):
    st.markdown("""
    <style>
    .st-expander { border-color: #2d6a9f !important; }
    .st-expander summary { color: #c8d8f0 !important; }
    </style>
    <div style='background: linear-gradient(135deg, #1e3a5f 0%, #2d6a9f 100%);
         padding: 2rem; border-radius: 12px; margin-bottom: 1.5rem;'>
        <h1 style='color:white; margin:0; font-size:2rem;'>🏥 Mortalidad en Colombia 2019</h1>
        <p style='color:#b8d4f0; margin:0.5rem 0 0 0; font-size:1rem;'>
        Análisis interactivo de 244,355 registros del DANE · Herramientas Computacionales
        </p>
    </div>
    """, unsafe_allow_html=True)

    stats = stats_globales(df)

    col1, col2, col3, col4, col5 = st.columns(5)
    kpis = [
        ("💀", "Total muertes", f"{stats['total']:,}"),
        ("🗺️", "Departamentos", str(stats['departamentos'])),
        ("🧬", "Causas únicas", str(stats['causas'])),
        ("📅", "Mes pico", stats['mes_pico']),
        ("🏙️", "Depto. más afectado", stats['depto_mas'].title()),
    ]
    for col, (icon, label, val) in zip([col1, col2, col3, col4, col5], kpis):
        col.markdown(f"""
        <div style='background:#1e3a5f; border-radius:10px; padding:1rem; text-align:center;
             border-left: 4px solid #5ab4ff;'>
            <div style='font-size:1.8rem;'>{icon}</div>
            <div style='font-size:0.75rem; color:#8ab4d4; font-weight:600; text-transform:uppercase;'>{label}</div>
            <div style='font-size:1.2rem; font-weight:700; color:#ffffff;'>{val}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.subheader("🗺️ Distribución de muertes por departamento")
    depto_df = muertes_por_departamento(df)
    depto_df['LAT'] = depto_df['DEPARTAMENTO'].map(lambda x: COORDS_DEPTO.get(x.upper(), (4.5, -74.0))[0])
    depto_df['LON'] = depto_df['DEPARTAMENTO'].map(lambda x: COORDS_DEPTO.get(x.upper(), (4.5, -74.0))[1])

    fig_mapa = px.scatter_mapbox(
        depto_df, lat='LAT', lon='LON',
        size='TOTAL_MUERTES', color='TOTAL_MUERTES',
        hover_name='DEPARTAMENTO',
        hover_data={'TOTAL_MUERTES': True, 'LAT': False, 'LON': False},
        color_continuous_scale='Reds',
        size_max=60,
        zoom=4.5,
        center={'lat': 4.5, 'lon': -74.0},
        mapbox_style='carto-positron',   # ← mapa claro, más legible
        title='Total de muertes por departamento - Colombia 2019'
    )
    fig_mapa.update_layout(
        height=520,
        margin={'r': 0, 't': 40, 'l': 0, 'b': 0},
        paper_bgcolor=BG,
        font=dict(color=FONT_COLOR),
        title_font=dict(color=FONT_COLOR),
        coloraxis_colorbar=dict(
            title='Muertes',
            tickfont=dict(color=FONT_COLOR),
            titlefont=dict(color=FONT_COLOR)
        )
    )
    st.plotly_chart(fig_mapa, use_container_width=True)

    with st.expander("📊 Ver tabla de datos por departamento"):
        st.dataframe(
            depto_df[['DEPARTAMENTO', 'TOTAL_MUERTES']].rename(
                columns={'DEPARTAMENTO': 'Departamento', 'TOTAL_MUERTES': 'Total Muertes'}
            ),
            use_container_width=True, hide_index=True
        )