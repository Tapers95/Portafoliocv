import streamlit as st
import difflib

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Sinergia-Metrix", layout="wide")

def calcular_similitud(texto1, texto2):
    # Mide qué tanto cambió el texto (Ratio de Levenshtein aproximado)
    return difflib.SequenceMatcher(None, texto1, texto2).ratio()

def contar_palabras(texto):
    return len(texto.split())

# --- INTERFAZ DE USUARIO ---
st.title("🚀 Sinergia-Metrix: Cuantificador de Colaboración IA")
st.markdown("""
Esta app mide el impacto de la IA en tu CV. 
Compara tu borrador inicial con la versión mejorada por la IA.
""")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Borrador Humano (Original)")
    texto_original = st.text_area("Pega aquí tu versión inicial...", height=300)

with col2:
    st.subheader("Versión Colaborativa (IA + Tú)")
    texto_final = st.text_area("Pega aquí la versión final...", height=300)

if st.button("📊 Analizar Impacto"):
    if texto_original and texto_final:
        # Cálculos de métricas
        similitud = calcular_similitud(texto_original, texto_final)
        cambio_porcentaje = (1 - similitud) * 100
        
        palabras_orig = contar_palabras(texto_original)
        palabras_fin = contar_palabras(texto_final)
        
        # --- MOSTRAR RESULTADOS ---
        st.divider()
        st.header("Resultados de la Sinergia")
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Índice de Cambio", f"{cambio_porcentaje:.1f}%", help="Qué tanto transformó la IA tu texto original")
        m2.metric("Expansión de Contenido", f"{palabras_fin - palabras_orig} palabras", help="Diferencia de volumen de información")
        m3.metric("Fidelidad de Voz", f"{similitud*100:.1f}%", help="Qué tanto se conservó de tu esencia original")

        ### Visualización del impacto (Disruptivo)
        st.subheader("Análisis de Influencia")
        if cambio_porcentaje > 50:
            st.warning("⚠️ **Alta Influencia de IA:** El contenido ha cambiado radicalmente. Asegúrate de que los datos sigan siendo 100% reales.")
        else:
            st.success("✅ **Colaboración Equilibrada:** Has mantenido tu base personal con optimización externa.")
            
        # Comparativa visual de diferencias
        st.subheader("Mapa de Calor de Cambios")
        diff = difflib.ndiff(texto_original.split(), texto_final.split())
        st.text(" ".join(diff))
    else:
        st.error("Por favor, llena ambos campos para analizar.")
