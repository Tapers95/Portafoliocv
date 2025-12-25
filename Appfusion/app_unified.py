import streamlit as st
import difflib
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from PyPDF2 import PdfReader

# --- CONFIGURACIÓN GLOBAL ---
st.set_page_config(page_title="Career Forge AI", layout="wide", page_icon="🚀")

# --- FUNCIONES DE SINERGIA (COMPARACIÓN DE TEXTO) ---
def calcular_similitud_texto(texto1, texto2):
    return difflib.SequenceMatcher(None, texto1, texto2).ratio()

def contar_palabras(texto):
    return len(texto.split())

# --- FUNCIONES DE MATCHER (IA & SEMÁNTICA) ---
@st.cache_resource
def cargar_modelo():
    # Carga el modelo de IA una sola vez para optimizar velocidad
    return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def extraer_texto_pdf(archivo):
    try:
        reader = PdfReader(archivo)
        texto = ""
        for page in reader.pages:
            texto += page.extract_text() + "\n"
        return texto
    except Exception as e:
        return ""

def limpiar_texto(texto):
    if not texto: return ""
    texto = texto.lower()
    # Mantiene caracteres útiles para tech skills (ej: c++, c#, .net)
    texto = re.sub(r"[^a-z0-9áéíóúñü\s\+\#\.\-/]", " ", texto) 
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()

# Banco de palabras clave corregido y formateado para Python
def obtener_keywords():
    return {
        "desarrollo": ["python", "java", "javascript", "typescript", "react", "angular", "vue", "node", "django", "flask", "sql", "nosql", "docker", "kubernetes", "aws", "azure", "git", "ci/cd"],
        "datos": ["pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "power bi", "tableau", "sql", "etl", "big data", "spark", "hadoop"],
        "soft_skills": ["liderazgo", "comunicación", "trabajo en equipo", "agile", "scrum", "inglés", "resolución de problemas", "gestión de tiempo"]
    }

def extraer_habilidades(texto):
    texto = texto.lower()
    banco = obtener_keywords()
    detectadas = set()
    
    # Búsqueda por diccionario
    for categoria, skills in banco.items():
        for skill in skills:
            # Búsqueda simple de palabra completa
            if f" {skill} " in f" {texto} ":
                detectadas.add(skill)
    
    # Búsqueda por Regex para patrones técnicos complejos
    candidatos = re.findall(r"[a-z0-9\+\#\.\-/]{2,15}", texto)
    tech_patterns = ["js", "ai", "ml", "net", "io"]
    for c in candidatos:
        if any(p in c for p in tech_patterns) and len(c) > 2:
            detectadas.add(c)
            
    return list(detectadas)

def calcular_match_semantico(cv_text, job_text, modelo):
    if not cv_text or not job_text: return 0.0
    emb1 = modelo.encode([cv_text])
    emb2 = modelo.encode([job_text])
    return float(cosine_similarity(emb1, emb2)[0][0])

# --- INTERFAZ DE USUARIO ---

st.sidebar.title("🛠️ Menú de Herramientas")
opcion = st.sidebar.radio("Selecciona una fase:", ["1. Editor de Sinergia (Drafting)", "2. Matcher con Oferta (ATS)"])

st.sidebar.info("""
**Guía de Uso:**
1. Usa el **Editor** para comparar tu borrador original con la versión mejorada por ChatGPT/Claude.
2. Usa el **Matcher** para ver si tu CV final pasa los filtros de la oferta de trabajo.
""")

if opcion == "1. Editor de Sinergia (Drafting)":
    st.title("📝 Editor de Sinergia: Humano + IA")
    st.markdown("Analiza qué tanto ha cambiado tu texto original al ser procesado por una IA.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Tu Borrador Original")
        texto_original = st.text_area("Pega aquí tu texto inicial...", height=300, key="txt_orig")
    with col2:
        st.subheader("Versión Mejorada por IA")
        texto_final = st.text_area("Pega aquí la versión de la IA...", height=300, key="txt_final")

    if st.button("📊 Analizar Cambios"):
        if texto_original and texto_final:
            similitud = calcular_similitud_texto(texto_original, texto_final)
            cambio_pct = (1 - similitud) * 100
            diff_palabras = contar_palabras(texto_final) - contar_palabras(texto_original)
            
            st.divider()
            m1, m2, m3 = st.columns(3)
            m1.metric("Transformación", f"{cambio_pct:.1f}%", delta_color="inverse")
            m2.metric("Diferencia Palabras", f"{diff_palabras}", delta_color="off")
            m3.metric("Fidelidad Original", f"{similitud*100:.1f}%")
            
            if cambio_pct > 60:
                st.warning("⚠️ **Alerta:** El texto ha cambiado drásticamente. Verifica que la información siga siendo veraz.")
            else:
                st.success("✅ **Buen Balance:** Se mantiene tu esencia con mejoras.")

elif opcion == "2. Matcher con Oferta (ATS)":
    st.title("🎯 ATS Matcher Inteligente")
    st.markdown("Compara tu CV contra una descripción de empleo usando Inteligencia Artificial.")
    
    # Cargar modelo (con spinner para feedback visual)
    with st.spinner("Cargando cerebro de IA..."):
        modelo_ai = cargar_modelo()

    col_cv, col_job = st.columns(2)
    
    cv_texto_completo = ""
    
    with col_cv:
        st.subheader("Tu CV")
        upload_cv = st.file_uploader("Sube tu PDF", type=["pdf"])
        paste_cv = st.text_area("O pega el texto del CV", height=200)
        
        if upload_cv:
            cv_texto_completo = extraer_texto_pdf(upload_cv)
        elif paste_cv:
            cv_texto_completo = paste_cv

    with col_job:
        st.subheader("La Oferta de Trabajo")
        job_texto = st.text_area("Pega la descripción del puesto aquí...", height=270)

    if st.button("🔍 Analizar Compatibilidad"):
        if cv_texto_completo and job_texto:
            # Limpieza
            cv_clean = limpiar_texto(cv_texto_completo)
            job_clean = limpiar_texto(job_texto)
            
            # Análisis Semántico
            match_score = calcular_match_semantico(cv_clean, job_clean, modelo_ai)
            match_pct = round(match_score * 100, 1)
            
            # Análisis de Keywords (Gap Analysis)
            skills_cv = set(extraer_habilidades(cv_clean))
            skills_job = set(extraer_habilidades(job_clean))
            missing_skills = skills_job - skills_cv
            matched_skills = skills_job.intersection(skills_cv)
            
            # Mostrar Resultados
            st.divider()
            st.header(f"Resultado del Match: {match_pct}%")
            st.progress(match_pct / 100)
            
            c1, c2 = st.columns(2)
            
            with c1:
                st.success(f"✅ Habilidades Encontradas ({len(matched_skills)})")
                st.write(", ".join(list(matched_skills)) if matched_skills else "No se detectaron coincidencias exactas de keywords.")
                
            with c2:
                if missing_skills:
                    st.error(f"⚠️ Habilidades Faltantes en CV ({len(missing_skills)})")
                    st.write(", ".join(list(missing_skills)))
                    st.caption("Considera agregar estas palabras clave si tienes la experiencia.")
                else:
                    st.success("¡Excelente! Cubres todas las keywords detectadas.")
            
            # Recomendación final
            st.subheader("💡 Recomendación de IA")
            if match_pct > 75:
                st.write("Tu perfil está **altamente alineado**. ¡Postula ahora!")
            elif match_pct > 50:
                st.write("Tienes un perfil **competitivo**, pero intenta agregar las habilidades faltantes antes de enviar.")
            else:
                st.write("La alineación es **baja**. Adapta tu CV más específicamente para este puesto.")
                
        else:
            st.warning("Por favor sube un CV y la descripción del trabajo.")

