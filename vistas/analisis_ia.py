import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from src.procesador_datos import (
    muertes_por_departamento, stats_globales, top_causas_muerte
)
from src.ia_antigravity import (
    generar_hipotesis, predecir_tendencia_mensual,
    traducir_cie10, clasificar_riesgo_municipios
)
from src.agente_azure import sintetizar_texto_azure, azure_voice_available

BG = '#0f1f3d'
GRID = '#1e3a5f'
FONT_COLOR = '#c8d8f0'


def render(df, cod):
    st.markdown("""
    <div style='background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
         padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem;'>
        <h2 style='color:white; margin:0;'>🤖 Análisis con Inteligencia Artificial</h2>
        <p style='color:#90caf9; margin:0.3rem 0 0 0;'>
        Powered by Google Antigravity (Gemini 1.5 Flash) — Epidemiólogo virtual, predicciones y más
        </p>
    </div>
    """, unsafe_allow_html=True)

    use_azure_voice = st.checkbox("🔊 Reproducir IA con voz Azure", value=True)
    if use_azure_voice and not azure_voice_available():
        st.warning("Azure Speech no está configurado. Configure AZURE_SPEECH_KEY y AZURE_SPEECH_REGION.")

    tab1, tab2, tab3, tab4 = st.tabs([
        "🧠 Hipótesis Epidemiológica",
        "🔮 Predicción de Tendencias",
        "💬 Traductor CIE-10",
        "🗺️ Mapa de Riesgo Municipal"
    ])

    # ── TAB 1: Generador de hipótesis ─────────────────────────────────────
    with tab1:
        st.markdown("### 🧠 Epidemiólogo virtual")
        st.caption("El asistente IA usa los filtros seleccionados para sugerir hipótesis y factores de riesgo.")

        c1, c2, c3 = st.columns(3)
        with c1:
            deptos = ['Todos'] + sorted(df['DEPARTAMENTO'].dropna().unique().tolist())
            depto_sel = st.selectbox("Departamento", deptos, key='ia_depto')
        with c2:
            sexos = ['Todos'] + sorted(df['NOMBRE_SEXO'].dropna().unique().tolist())
            sexo_sel = st.selectbox("Sexo", sexos, key='ia_sexo')
        with c3:
            edades = ['Todos'] + sorted(df['CATEGORIA_EDAD'].dropna().unique().tolist())
            edad_sel = st.selectbox("Grupo de edad", edades, key='ia_edad')

        df_filt = df.copy()
        if depto_sel != 'Todos':
            df_filt = df_filt[df_filt['DEPARTAMENTO'] == depto_sel]
        if sexo_sel != 'Todos':
            df_filt = df_filt[df_filt['NOMBRE_SEXO'] == sexo_sel]
        if edad_sel != 'Todos':
            df_filt = df_filt[df_filt['CATEGORIA_EDAD'] == edad_sel]

        top3 = top_causas_muerte(df_filt, top=3)
        top3_list = top3[['COD_MUERTE', 'DESCRIPCION', 'TOTAL']].to_dict('records')
        causas_externas = df_filt[df_filt['MANERA_MUERTE'].isin(['Homicidio', 'Accidente'])]
        pct_ext = len(causas_externas) / len(df_filt) * 100 if len(df_filt) > 0 else 0
        media_nac = len(df) / df['DEPARTAMENTO'].nunique()

        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Muertes en segmento", f"{len(df_filt):,}")
        col_m2.metric("% Causas externas", f"{pct_ext:.1f}%")
        col_m3.metric("Media nacional/depto", f"{media_nac:,.0f}")

        if st.button("Generar diagnóstico IA", type='primary', key='btn_hipotesis'):
            resumen = {
                'departamento': depto_sel,
                'sexo': sexo_sel,
                'edad': edad_sel,
                'total_muertes': len(df_filt),
                'top_causas': top3_list,
                'media_nacional': media_nac,
                'pct_externas': pct_ext
            }
            with st.spinner("Analizando datos con IA..."):
                texto = generar_hipotesis(resumen)

            # ── Cuadro diagnóstico: azul cian profundo ──────────────────
            st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, #0d2137 0%, #0a3d62 60%, #1a1a4e 100%);
                border: 1px solid #1e6fa8;
                border-left: 5px solid #00d4ff;
                border-radius: 12px;
                padding: 1.5rem 1.8rem;
                margin-top: 1.2rem;
                box-shadow: 0 4px 24px rgba(0, 212, 255, 0.12);
            '>
                <div style='display:flex; align-items:center; gap:0.6rem; margin-bottom:1rem;'>
                    <span style='font-size:1.4rem;'>🤖</span>
                    <span style='color:#00d4ff; font-weight:700; font-size:0.85rem;
                                 text-transform:uppercase; letter-spacing:0.1em;'>
                        Diagnóstico IA · Antigravity / Gemini
                    </span>
                </div>
                <div style='color:#d0eaff; font-size:1rem; line-height:1.75;
                            border-top:1px solid #1e4a6e; padding-top:1rem;'>
                    {texto.replace(chr(10), '<br>')}
                </div>
            </div>
            """, unsafe_allow_html=True)

            if use_azure_voice:
                audio = sintetizar_texto_azure(texto)
                if audio:
                    st.audio(audio, format='audio/wav')
                else:
                    st.info("No se pudo reproducir el audio Azure. Revise las variables AZURE_SPEECH_KEY y AZURE_SPEECH_REGION.")

    # ── TAB 2: Predicción tendencia mensual ───────────────────────────────
    with tab2:
        st.markdown("### 🔮 Predicción de tendencias")
        st.caption("La IA detecta patrones estacionales y proyecta la tendencia mensual de mortalidad.")

        mes_agg = df.groupby(['MES', 'NOMBRE_MES']).size().reset_index(name='TOTAL').sort_values('MES')
        fig_pred = px.area(
            mes_agg, x='NOMBRE_MES', y='TOTAL',
            color_discrete_sequence=['#5ab4ff'],
            labels={'NOMBRE_MES': 'Mes', 'TOTAL': 'Total de muertes'},
            title='Serie mensual de mortalidad · Colombia 2019'
        )
        fig_pred.update_layout(
            plot_bgcolor=BG,
            paper_bgcolor=BG,
            font=dict(color=FONT_COLOR),
            yaxis=dict(gridcolor=GRID),
            xaxis_showgrid=False,
            xaxis={'categoryorder': 'array', 'categoryarray': mes_agg['NOMBRE_MES'].tolist()},
            height=350
        )
        st.plotly_chart(fig_pred, use_container_width=True)

        if st.button("Predecir tendencias con IA", type='primary', key='btn_pred'):
            datos_ia = [{'mes': r['NOMBRE_MES'], 'total': int(r['TOTAL'])} for _, r in mes_agg.iterrows()]
            with st.spinner("Calculando patrones estacionales..."):
                texto = predecir_tendencia_mensual(datos_ia)

            # ── Cuadro predicción: verde esmeralda oscuro ───────────────
            st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, #0a2e1a 0%, #0d4a2a 60%, #0a3322 100%);
                border: 1px solid #1a7a40;
                border-left: 5px solid #00e676;
                border-radius: 12px;
                padding: 1.5rem 1.8rem;
                margin-top: 1rem;
                box-shadow: 0 4px 24px rgba(0, 230, 118, 0.10);
            '>
                <div style='display:flex; align-items:center; gap:0.6rem; margin-bottom:1rem;'>
                    <span style='font-size:1.4rem;'>🔮</span>
                    <span style='color:#00e676; font-weight:700; font-size:0.85rem;
                                 text-transform:uppercase; letter-spacing:0.1em;'>
                        Análisis de Tendencias · Antigravity / Gemini
                    </span>
                </div>
                <div style='color:#c8f0d8; font-size:1rem; line-height:1.75;
                            border-top:1px solid #1a5a30; padding-top:1rem;'>
                    {texto.replace(chr(10), '<br>')}
                </div>
            </div>
            """, unsafe_allow_html=True)

            if use_azure_voice:
                audio = sintetizar_texto_azure(texto)
                if audio:
                    st.audio(audio, format='audio/wav')
                else:
                    st.info("No se pudo reproducir el audio Azure. Revise las variables AZURE_SPEECH_KEY y AZURE_SPEECH_REGION.")

    # ── TAB 3: Traductor CIE-10 ───────────────────────────────────────────
    with tab3:
        st.markdown("### 💬 Traductor de CIE-10")
        st.caption("Convierte el lenguaje técnico de la clasificación médica a términos más claros.")

        top_causas_df = top_causas_muerte(df, top=50)

        opciones = {
            f"{r['COD_MUERTE']} — {r['DESCRIPCION'][:60]}": (r['COD_MUERTE'], r['DESCRIPCION'])
            for _, r in top_causas_df.iterrows()
        }
        seleccion = st.selectbox("Selecciona un código de muerte:", list(opciones.keys()), key='cie_sel')
        cod_sel, desc_sel = opciones[seleccion]

        col_a, col_b = st.columns(2)
        with col_a:
            # ── Cuadro CIE-10 técnico: ámbar oscuro ─────────────────────
            st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, #2a1a00 0%, #3d2800 100%);
                border: 1px solid #7a5500;
                border-left: 5px solid #ffc107;
                border-radius: 12px;
                padding: 1.2rem 1.5rem;
            '>
                <div style='color:#ffc107; font-weight:700; font-size:0.8rem;
                             text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.8rem;'>
                    📋 Código CIE-10
                </div>
                <code style='background:#1a1000; color:#ffe082; padding:0.2rem 0.5rem;
                              border-radius:4px; font-size:1rem;'>{cod_sel}</code>
                <div style='color:#c8a800; margin-top:0.8rem; font-size:0.85rem;
                             text-transform:uppercase; letter-spacing:0.05em;'>Descripción técnica</div>
                <div style='color:#ffe4a0; margin-top:0.3rem; line-height:1.5;'>{desc_sel}</div>
            </div>
            """, unsafe_allow_html=True)

        if st.button("Traducir con IA", type='primary', key='btn_cie'):
            with st.spinner("Traduciendo..."):
                traduccion = traducir_cie10(cod_sel, desc_sel)
            with col_b:
                # ── Cuadro traducción: violeta oscuro ───────────────────
                st.markdown(f"""
                <div style='
                    background: linear-gradient(135deg, #1a0a2e 0%, #2d1060 100%);
                    border: 1px solid #6a35b0;
                    border-left: 5px solid #b388ff;
                    border-radius: 12px;
                    padding: 1.2rem 1.5rem;
                    box-shadow: 0 4px 20px rgba(179, 136, 255, 0.12);
                '>
                    <div style='color:#b388ff; font-weight:700; font-size:0.8rem;
                                 text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.8rem;'>
                        💬 En términos simples
                    </div>
                    <div style='color:#e8d5ff; font-size:1.15rem; font-weight:700; line-height:1.5;'>
                        {traduccion}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            if use_azure_voice:
                audio = sintetizar_texto_azure(traduccion)
                if audio:
                    st.audio(audio, format='audio/wav')
                else:
                    st.info("No se pudo reproducir el audio Azure. Revise las variables AZURE_SPEECH_KEY y AZURE_SPEECH_REGION.")

    # ── TAB 4: Mapa de riesgo por municipio ───────────────────────────────
    with tab4:
        st.markdown("### 🗺️ Clasificación de riesgo municipal")
        st.caption("Clasifica los municipios según niveles de riesgo y visualiza el patrón de mortalidad.")

        mun_df = df.groupby('MUNICIPIO').size().reset_index(name='total_muertes')
        mun_df = mun_df[mun_df['MUNICIPIO'] != 'Sin dato']
        top_causa_mun = df.groupby('MUNICIPIO').apply(
            lambda x: x['DESCRIPCION'].mode()[0] if len(x) > 0 else 'Sin dato'
        ).reset_index(name='top_causa')
        mun_df = mun_df.merge(top_causa_mun, on='MUNICIPIO')
        mun_data = mun_df.rename(columns={'MUNICIPIO': 'municipio'}).to_dict('records')

        if st.button("Clasificar con IA", type='primary', key='btn_riesgo'):
            with st.spinner("Clasificando municipios..."):
                clasificados = clasificar_riesgo_municipios(mun_data)

            clas_df = pd.DataFrame(clasificados)
            if use_azure_voice:
                texto = "La clasificación de municipios por riesgo ha sido generada. Revisa la tabla y el gráfico para ver los resultados."
                audio = sintetizar_texto_azure(texto)
                if audio:
                    st.audio(audio, format='audio/wav')
                else:
                    st.info("No se pudo reproducir el audio Azure. Revise las variables AZURE_SPEECH_KEY y AZURE_SPEECH_REGION.")

            color_map = {'Alto': '#dc3545', 'Medio': '#ffc107', 'Bajo': '#28a745'}

            col_r1, col_r2, col_r3 = st.columns(3)
            for nivel, col in [('Alto', col_r1), ('Medio', col_r2), ('Bajo', col_r3)]:
                n = len(clas_df[clas_df.get('nivel_riesgo', pd.Series()) == nivel]) if 'nivel_riesgo' in clas_df.columns else 0
                col.metric(f"Municipios {nivel}", n)

            if 'nivel_riesgo' in clas_df.columns:
                fig_risk = px.bar(
                    clas_df.sort_values('total_muertes', ascending=False).head(30),
                    x='municipio', y='total_muertes',
                    color='nivel_riesgo',
                    color_discrete_map=color_map,
                    labels={'municipio': 'Municipio', 'total_muertes': 'Total muertes', 'nivel_riesgo': 'Nivel de riesgo'},
                    title='Top 30 municipios clasificados por nivel de riesgo'
                )
                fig_risk.update_layout(
                    xaxis_tickangle=-45,
                    height=420,
                    plot_bgcolor=BG,
                    paper_bgcolor=BG,
                    font=dict(color=FONT_COLOR),
                    yaxis=dict(gridcolor=GRID),
                    xaxis_showgrid=False
                )
                st.plotly_chart(fig_risk, use_container_width=True)

                with st.expander("Ver tabla completa de clasificación"):
                    st.dataframe(
                        clas_df[['municipio', 'total_muertes', 'top_causa', 'nivel_riesgo']].sort_values('total_muertes', ascending=False),
                        use_container_width=True, hide_index=True
                    )
        else:
            st.info("Presione el botón para activar la clasificación de riesgo municipal.")
