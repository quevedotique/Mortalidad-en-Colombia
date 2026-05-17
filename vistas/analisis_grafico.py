import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from src.procesador_datos import (
    muertes_por_mes, ciudades_mas_violentas,
    ciudades_menor_mortalidad, top_causas_muerte,
    muertes_sexo_departamento, distribucion_edad
)
from src.ia_antigravity import predecir_tendencia_mensual

COLORES = px.colors.qualitative.Bold

BG = '#0f1f3d'
GRID = '#1e3a5f'
FONT_COLOR = '#c8d8f0'


def render(df):
    st.markdown("""
    <style>
    .stPlotlyChart { background: #0f1f3d; border-radius: 10px; }
    </style>
    <div style='background: linear-gradient(135deg, #1e3a5f 15%, #2d6a9f 100%);
         padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem;'>
        <h2 style='color:white; margin:0;'>📊 Análisis Gráfico</h2>
        <p style='color:#b8d4f0; margin:0.3rem 0 0 0;'>Visualizaciones interactivas de los patrones de mortalidad</p>
    </div>
    """, unsafe_allow_html=True)

    # ── 1. Líneas: muertes por mes ──────────────────────────────────────────
    st.subheader("📈 Total de muertes por mes")
    mes_df = muertes_por_mes(df)
    fig_mes = px.line(
        mes_df, x='NOMBRE_MES', y='TOTAL',
        markers=True, line_shape='spline',
        color_discrete_sequence=['#5ab4ff'],
        labels={'NOMBRE_MES': 'Mes', 'TOTAL': 'Total de muertes'},
        title='Evolución mensual de la mortalidad · Colombia 2019'
    )
    fig_mes.update_traces(marker=dict(size=9), line=dict(width=3))
    fig_mes.update_layout(
        xaxis={'categoryorder': 'array', 'categoryarray': mes_df['NOMBRE_MES'].tolist()},
        plot_bgcolor=BG,
        paper_bgcolor=BG,
        font=dict(color=FONT_COLOR),
        yaxis=dict(gridcolor=GRID),
        xaxis_showgrid=False,
        height=380
    )
    st.plotly_chart(fig_mes, use_container_width=True)

    with st.expander("🤖 Ver análisis de IA sobre tendencia mensual"):
        datos_ia = [{'mes': r['NOMBRE_MES'], 'total': int(r['TOTAL'])} for _, r in mes_df.iterrows()]
        with st.spinner("Consultando IA..."):
            texto = predecir_tendencia_mensual(datos_ia)
        st.info(texto)

    st.divider()

    # ── 2. Barras: 5 ciudades más violentas ────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔴 5 ciudades más violentas (Homicidios X95)")
        viol_df = ciudades_mas_violentas(df)
        fig_viol = px.bar(
            viol_df, x='HOMICIDIOS', y='MUNICIPIO',
            orientation='h',
            color='HOMICIDIOS', color_continuous_scale='Reds',
            labels={'HOMICIDIOS': 'Homicidios', 'MUNICIPIO': 'Ciudad'},
            title='Ciudades con mayor número de homicidios con arma de fuego'
        )
        fig_viol.update_layout(
            plot_bgcolor=BG,
            paper_bgcolor=BG,
            font=dict(color=FONT_COLOR),
            coloraxis_showscale=False,
            yaxis={'categoryorder': 'total ascending'},
            xaxis=dict(gridcolor=GRID),
            height=350
        )
        st.plotly_chart(fig_viol, use_container_width=True)

    # ── 3. Circular: 10 ciudades menor mortalidad ──────────────────────────
    with col2:
        st.subheader("🟢 10 ciudades con menor mortalidad")
        min_df = ciudades_menor_mortalidad(df)
        fig_pie = px.pie(
            min_df, values='TOTAL_MUERTES', names='MUNICIPIO',
            color_discrete_sequence=px.colors.sequential.Greens_r,
            title='Municipios con menor índice de mortalidad'
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(
            height=350,
            showlegend=False,
            paper_bgcolor=BG,
            font=dict(color=FONT_COLOR)
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    st.divider()

    # ── 4. Tabla: 10 principales causas ───────────────────────────────────
    st.subheader("📋 Top 10 causas de muerte en Colombia 2019")
    causas_df = top_causas_muerte(df)
    causas_df = causas_df.rename(columns={
        'COD_MUERTE': 'Código CIE-10',
        'DESCRIPCION': 'Descripción',
        'TOTAL': 'Total de casos'
    })
    causas_df['Ranking'] = range(1, len(causas_df) + 1)
    causas_df['% del total'] = (causas_df['Total de casos'] / len(df) * 100).round(2).astype(str) + '%'

    st.dataframe(
        causas_df[['Ranking', 'Código CIE-10', 'Descripción', 'Total de casos', '% del total']],
        use_container_width=True, hide_index=True,
        column_config={
            'Ranking': st.column_config.NumberColumn(width='small'),
            'Total de casos': st.column_config.ProgressColumn(
                min_value=0, max_value=int(causas_df['Total de casos'].max()),
                format='%d'
            )
        }
    )

    st.divider()

    # ── 5. Barras apiladas: muertes por sexo y departamento ───────────────
    st.subheader("⚧ Muertes por sexo en cada departamento")

    deptos_disponibles = sorted(df['DEPARTAMENTO'].dropna().unique())
    deptos_sel = st.multiselect(
        "Selecciona departamentos a comparar:",
        options=deptos_disponibles,
        default=deptos_disponibles[:8],
        key='sel_deptos_sexo'
    )

    if deptos_sel:
        sexo_df = muertes_sexo_departamento(df)
        sexo_df = sexo_df[sexo_df['DEPARTAMENTO'].isin(deptos_sel)]
        fig_sexo = px.bar(
            sexo_df, x='DEPARTAMENTO', y='TOTAL',
            color='NOMBRE_SEXO',
            barmode='stack',
            color_discrete_map={'Masculino': '#5ab4ff', 'Femenino': '#e84393', 'Indeterminado': '#adb5bd'},
            labels={'TOTAL': 'Total de muertes', 'DEPARTAMENTO': 'Departamento', 'NOMBRE_SEXO': 'Sexo'},
            title='Distribución de muertes por sexo y departamento'
        )
        fig_sexo.update_layout(
            xaxis_tickangle=-30,
            plot_bgcolor=BG,
            paper_bgcolor=BG,
            font=dict(color=FONT_COLOR),
            yaxis=dict(gridcolor=GRID),
            xaxis_showgrid=False,
            height=420,
            legend_title='Sexo'
        )
        st.plotly_chart(fig_sexo, use_container_width=True)
    else:
        st.warning("Selecciona al menos un departamento.")

    st.divider()

    # ── 6. Histograma: distribución por grupo de edad ─────────────────────
    st.subheader("👶👴 Distribución de muertes por grupo de edad")
    edad_df = distribucion_edad(df)
    fig_edad = px.bar(
        edad_df, x='CATEGORIA_EDAD', y='TOTAL',
        color='TOTAL',
        color_continuous_scale='Blues',
        labels={'CATEGORIA_EDAD': 'Grupo de edad', 'TOTAL': 'Total de muertes'},
        title='Mortalidad por ciclo de vida · Colombia 2019'
    )
    fig_edad.update_layout(
        xaxis_tickangle=-35,
        plot_bgcolor=BG,
        paper_bgcolor=BG,
        font=dict(color=FONT_COLOR),
        yaxis=dict(gridcolor=GRID),
        xaxis_showgrid=False,
        coloraxis_showscale=False,
        height=400
    )
    st.plotly_chart(fig_edad, use_container_width=True)