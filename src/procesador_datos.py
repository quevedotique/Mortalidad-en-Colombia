import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'datos')

MESES = {
    1:'Enero', 2:'Febrero', 3:'Marzo', 4:'Abril',
    5:'Mayo', 6:'Junio', 7:'Julio', 8:'Agosto',
    9:'Septiembre', 10:'Octubre', 11:'Noviembre', 12:'Diciembre'
}

SEXO_MAP = {1: 'Masculino', 2: 'Femenino', 3: 'Indeterminado'}

GRUPO_EDAD_MAP = {
    **{i: 'Mortalidad neonatal' for i in range(0, 5)},
    **{i: 'Mortalidad infantil' for i in range(5, 7)},
    **{i: 'Primera infancia' for i in range(7, 9)},
    **{i: 'Niñez' for i in range(9, 11)},
    11: 'Adolescencia',
    **{i: 'Juventud' for i in range(12, 14)},
    **{i: 'Adultez temprana' for i in range(14, 17)},
    **{i: 'Adultez intermedia' for i in range(17, 20)},
    **{i: 'Vejez' for i in range(20, 25)},
    **{i: 'Longevidad / Centenarios' for i in range(25, 29)},
    29: 'Edad desconocida'
}

try:
    import streamlit as st
    st_cache = st.cache_data
except Exception:
    def st_cache(fn):
        return fn

@st_cache
def cargar_datos():
    """Carga y cruza todos los datasets."""
    df = pd.read_csv(os.path.join(DATA_DIR, 'No_Fetales_2019.csv'), dtype={'COD_MUERTE': str, 'COD_DANE': str})
    div = pd.read_csv(os.path.join(DATA_DIR, 'Divipola_CE.csv'), dtype={'COD_DANE': str})
    cod = pd.read_csv(os.path.join(DATA_DIR, 'CodigosDeMuerte_CE.csv'), dtype={'COD_MUERTE': str})

    div['COD_DANE'] = div['COD_DANE'].astype(str).str.zfill(5)
    df['COD_DANE'] = df['COD_DANE'].astype(str).str.zfill(5)
    df['COD_MUERTE'] = df['COD_MUERTE'].astype(str).str.strip()
    cod['COD_MUERTE'] = cod['COD_MUERTE'].astype(str).str.strip()

    df = df.merge(div[['COD_DANE', 'DEPARTAMENTO', 'MUNICIPIO', 'COD_DEPARTAMENTO']], on='COD_DANE', how='left')
    df = df.merge(cod[['COD_MUERTE', 'DESCRIPCION']], on='COD_MUERTE', how='left')

    df['NOMBRE_MES'] = df['MES'].map(MESES)
    df['NOMBRE_SEXO'] = df['SEXO'].map(SEXO_MAP)
    df['CATEGORIA_EDAD'] = df['GRUPO_EDAD1'].map(GRUPO_EDAD_MAP)
    df['DESCRIPCION'] = df['DESCRIPCION'].fillna('Sin clasificar')
    df['MUNICIPIO'] = df['MUNICIPIO'].fillna('Sin dato')
    df['DEPARTAMENTO'] = df['DEPARTAMENTO'].fillna('Sin dato')

    return df, div, cod


def muertes_por_departamento(df):
    return df.groupby('DEPARTAMENTO').size().reset_index(name='TOTAL_MUERTES').sort_values('TOTAL_MUERTES', ascending=False)


def muertes_por_mes(df):
    g = df.groupby(['MES', 'NOMBRE_MES']).size().reset_index(name='TOTAL')
    return g.sort_values('MES')


def ciudades_mas_violentas(df, top=5):
    hom = df[df['COD_MUERTE'].str.startswith('X95', na=False)]
    g = hom.groupby('MUNICIPIO').size().reset_index(name='HOMICIDIOS')
    return g.sort_values('HOMICIDIOS', ascending=False).head(top)


def ciudades_menor_mortalidad(df, top=10):
    g = df.groupby('MUNICIPIO').size().reset_index(name='TOTAL_MUERTES')
    g = g[g['MUNICIPIO'] != 'Sin dato']
    return g.sort_values('TOTAL_MUERTES').head(top)


def top_causas_muerte(df, top=10):
    g = df.groupby(['COD_MUERTE', 'DESCRIPCION']).size().reset_index(name='TOTAL')
    return g.sort_values('TOTAL', ascending=False).head(top)


def muertes_sexo_departamento(df):
    g = df.groupby(['DEPARTAMENTO', 'NOMBRE_SEXO']).size().reset_index(name='TOTAL')
    return g


def distribucion_edad(df):
    orden = ['Mortalidad neonatal','Mortalidad infantil','Primera infancia','Niñez',
             'Adolescencia','Juventud','Adultez temprana','Adultez intermedia',
             'Vejez','Longevidad / Centenarios','Edad desconocida']
    g = df.groupby('CATEGORIA_EDAD').size().reset_index(name='TOTAL')
    g['orden'] = g['CATEGORIA_EDAD'].map({v: i for i, v in enumerate(orden)})
    return g.sort_values('orden')


def stats_globales(df):
    return {
        'total': len(df),
        'departamentos': df['DEPARTAMENTO'].nunique(),
        'causas': df['COD_MUERTE'].nunique(),
        'mes_pico': df.groupby('NOMBRE_MES').size().idxmax(),
        'depto_mas': df.groupby('DEPARTAMENTO').size().idxmax(),
    }
