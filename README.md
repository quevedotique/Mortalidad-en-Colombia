`<img width="1526" height="631" alt="Captura de pantalla 2026-05-16 202824" src="https://github.com/user-attachments/assets/61d73045-bcfa-4b90-a687-4e63c6290719" />
<img width="1860" height="861" alt="Captura de pantalla 2026-05-16 202814" src="https://github.com/user-attachments/assets/3f6a8a3e-2faa-41ba-b7d3-6645b1047262" />
<img width="1853" height="870" alt="Captura de pantalla 2026-05-16 203106" src="https://github.com/user-attachments/assets/08d8283e-5b99-4d1e-a2a3-1dc02f945b11" />
<img width="1852" height="881" alt="Captura de pantalla 2026-05-16 203050" src="https://github.com/user-attachments/assets/e64af6a1-b01e-4658-b0eb-9c46cfbd4785" />
<img width="1857" height="871" alt="Captura de pantalla 2026-05-16 203029" src="https://github.com/user-attachments/assets/dc6d1147-dc54-40e8-8bae-df6be8a42bfc" />
<img width="1861" height="877" alt="Captura de pantalla 2026-05-16 202954" src="https://github.com/user-attachments/assets/24db05ab-1fda-4936-a1cb-477eda4e864d" />
<img width="1855" height="889" alt="Captura de pantalla 2026-05-16 202938" src="https://github.com/user-attachments/assets/407f93c0-1c6a-49a9-8607-e3fbdbd8a583" />
<img width="1852" height="871" alt="Captura de pantalla 2026-05-16 202851" src="https://github.com/user-attachments/assets/b5494a82-2ef8-4c46-9638-be8d378fdcd9" />
<img width="1866" height="875" alt="Captura de pantalla 2026-05-16 202837" src="https://github.com/user-attachments/assets/9b5f71f8-163a-4c7e-9f49-ef7556abfdf4" />
<img width="1851" height="861" alt="Captura de pantalla 2026-05-16 203135" src="https://github.com/user-attachments/assets/5a6fbdc0-6ee4-4f58-b09f-0ffc6364395f" />
<img width="1856" height="864" alt="Captura de pantalla 2026-05-16 203123" src="https://github.com/user-attachments/assets/94221cd4-c182-4609-9943-5858bbcab15c" />
<img width="1864" height="869" alt="Captura de pantalla 2026-05-16 202722" src="https://github.com/user-attachments/assets/42c5edea-acdd-4ff3-bda9-2a4e64e66d84" />
<img width="1859" height="858" alt="Captura de pantalla 2026-05-16 202755" src="https://github.com/user-attachments/assets/1d814cd4-4137-45a0-9ec2-1cc9fc2408ce" />
`# 🏥 Mortalidad en Colombia 2019
### Análisis interactivo mediante aplicación web en Streamlit

> **Proyecto Final — Herramientas Computacionales para la Interpretación de Resultados**  
> Universidad Cooperativa de Colombia · Docente: Cristian Duney Bermúdez Quintero · Mayo 2026

---

## 8.1 Introducción del proyecto

Esta aplicación web interactiva permite explorar, visualizar e interpretar los datos de mortalidad no fetal en Colombia para el año 2019, publicados por el DANE (Estadísticas Vitales). Integra tres fuentes de datos oficiales y combina visualizaciones dinámicas con un módulo de Inteligencia Artificial (Google Antigravity / Gemini 1.5 Flash) que actúa como **epidemiólogo virtual**, generando hipótesis, predicciones de tendencias y clasificaciones de riesgo automáticas, ademas viene con voz integrada para una lectura mas rapida y dinamica.

---

## 8.2 Objetivo

Desarrollar una plataforma que permita:

- Analizar **244,355 registros** de defunciones no fetales del año 2019.
- Identificar patrones por **departamento, municipio, mes, causa, sexo y grupo de edad**.
- Enriquecer el análisis con **IA generativa** para traducir hallazgos estadísticos en lenguaje comprensible.
- Ofrecer una **experiencia de usuario profesional** con filtros interactivos y gráficos dinámicos.

---

## 8.3 Estructura del proyecto

```
mortalidad/
│
├── datos/                         # Archivos CSV procesados (DANE)
│   ├── No_Fetales_2019.csv        # 244,355 registros de mortalidad
│   ├── CodigosDeMuerte_CE.csv     # Catálogo CIE-10 (12,568 códigos)
│   └── Divipola_CE.csv            # División político-administrativa (1,123 municipios)
│
├── src/                           # Lógica del sistema
│   ├── __init__.py
│   ├── procesador_datos.py        # Carga, limpieza, cruces y funciones de agregación
│   └── ia_antigravity.py          # Integración con Google Antigravity (Gemini)
│
├── vistas/                        # Interfaz de usuario (UI) por secciones
│   ├── __init__.py
│   ├── inicio.py                  # KPIs globales y mapa de Colombia
│   ├── analisis_grafico.py        # Gráficos: líneas, barras, circular, tabla, apilado, histograma
│   └── analisis_ia.py             # 4 funciones de IA: hipótesis, predicción, CIE-10, riesgo
│
├── .gitignore
├── main.py                        # Punto de entrada Streamlit (orquestador)
├── requirements.txt               # Dependencias
├── startup.sh                     # Script de inicio para Azure App Service
└── README.md
```

---

## 8.4 Requisitos

```
streamlit==1.35.0
pandas==2.2.2
plotly==5.22.0
openpyxl==3.1.2
google-generativeai==0.7.2
```

---

## 8.5 Despliegue en Azure App Service

### Pasos realizados:

1. **Crear el App Service en Azure Portal**
   - Ir a [portal.azure.com](https://portal.azure.com)
   - Crear recurso → App Service → Python 3.11 → Linux
   - Nombre: `mortalidad-colombia-2019`

2. **Configurar las variables de entorno**
   - En el App Service → Configuration → Application settings
   - Agregar: `GEMINI_API_KEY` = tu API key de Google Antigravity
   - Agregar: `AZURE_SPEECH_KEY` = tu clave de Azure Speech
   - Agregar: `AZURE_SPEECH_REGION` = la región de tu recurso Speech (por ejemplo, `eastus`)

3. **Configurar el comando de inicio**
   - En Configuration → General settings → Startup Command:
   ```
   bash startup.sh
   ```

4. **Desplegar desde GitHub** (recomendado)
   - Deployment Center → GitHub → seleccionar repositorio y rama `main`
   - Azure genera automáticamente un workflow de GitHub Actions
   - Alternativa: usar el workflow de GitHub Actions incluido en `.github/workflows/azure-deploy.yml`

5. **URL pública generada:**
   ```
   https://<tu-app>.azurewebsites.net
   ```
   Reemplaza `<tu-app>` por el nombre de tu App Service en Azure.

---

## 8.6 Software utilizado

| Herramienta | Uso |
|---|---|
| **Python 3.11** | Lenguaje principal de programación |
| **Streamlit 1.35** | Framework de aplicación web interactiva |
| **Plotly 5.22** | Gráficos dinámicos e interactivos |
| **Pandas 2.2** | Manipulación y análisis de datos |
| **Google Antigravity (Gemini)** | IA generativa para análisis epidemiológico |
| **Visual Studio Code** | Entorno de desarrollo |
| **GitHub** | Control de versiones y CI/CD |
| **Azure App Service** | Despliegue en la nube |

| **Azure App Service** | Para voz implementada en la web |

---

## 8.7 Visualizaciones e interpretación de resultados

### 🗺️ Mapa de distribución departamental
Muestra la concentración geográfica de muertes. **Antioquia, Bogotá y Valle del Cauca** concentran el mayor volumen, reflejando tanto su tamaño poblacional como factores socioeconómicos y de violencia.

### 📈 Gráfico de líneas — Muertes por mes
Permite identificar estacionalidad. Los meses de **enero y marzo** suelen mostrar picos asociados a enfermedades respiratorias en temporadas frías en las regiones andinas.

### 🔴 Gráfico de barras — Ciudades más violentas
Filtra registros con código X95 (agresión con arma de fuego). **Medellín, Cali y Bogotá** lideran, aunque ciudades intermedias como Cúcuta y Buenaventura destacan proporcionalmente a su población.

### 🟢 Gráfico circular — Municipios con menor mortalidad
Ilustra que los municipios de menor tamaño y mayor ruralidad reportan menos defunciones en términos absolutos, aunque el acceso limitado a servicios de salud puede subestimar la mortalidad real.

### 📋 Tabla — Top 10 causas de muerte
Las enfermedades del sistema circulatorio (I219, I251) y las enfermedades crónicas no transmisibles dominan el perfil epidemiológico colombiano en 2019.

### ⚧ Barras apiladas — Muertes por sexo y departamento
La mortalidad masculina supera sistemáticamente a la femenina en todos los departamentos, especialmente por causas externas (homicidios, accidentes de tránsito).

### 👶👴 Distribución por grupo de edad
La **adultez intermedia (50-69 años) y la vejez (70+)** concentran la mayor mortalidad. Sin embargo, la mortalidad neonatal en regiones como Chocó y Guainía refleja desigualdades en atención materno-infantil.

### 🤖 Módulo de IA (Google Antigravity)
- **Hipótesis epidemiológica**: diagnóstico automático por segmento demográfico
- **Predicción de tendencias**: análisis de estacionalidad mensual
- **Traductor CIE-10**: convierte códigos médicos a lenguaje ciudadano
- **Mapa de riesgo**: clasifica municipios en Alto / Medio / Bajo riesgo

---

## Ejecutar localmente

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/mortalidad-colombia-2019.git
cd mortalidad-colombia-2019

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar API key (opcional, para funciones de IA)
export GEMINI_API_KEY="tu_api_key_aqui"   # Linux/Mac
set GEMINI_API_KEY=tu_api_key_aqui        # Windows

# 5. Ejecutar
streamlit run main.py
```

---

## Fuentes de datos

- DANE. (2019). *Estadísticas Vitales – Mortalidad No Fetal 2019*. [microdatos.dane.gov.co](https://microdatos.dane.gov.co/index.php/catalog/696)
- DANE. *Divipola – División Político-Administrativa de Colombia.*
- DANE. *Catálogo de patologías CIE-10 (actualización 2021).*
