import os
import shutil
import streamlit as st
from src.config import settings
from src.ingesta import descargar_pdfs_de_oci, procesar_documentos
from src.motor_rag import crear_o_cargar_vectorstore, construir_cadena_rag

# 1. Configuración inicial de la página
st.set_page_config(
    page_title="NexusHCM - RAG Assistant",
    page_icon="🤖",
    layout="wide"
)

# 2. Diccionario de traducciones (Español / Inglés)
TEXTOS = {
    "es": {
        "titulo": "🤖 NexusHCM - Asistente Virtual de RRHH",
        "subtitulo": "Consulta políticas corporativas, beneficios y normativas internas al instante.",
        "sidebar_titulo": "⚙️ Configuración y Datos",
        "selector_idioma": "Idioma / Language",
        "btn_sincronizar": "🔄 Sincronizar documentos desde OCI",
        "sync_proceso": "Descargando PDFs desde Oracle Cloud y actualizando memoria...",
        "sync_exito": "¡Base de conocimientos actualizada con éxito!",
        "sync_error": "No se encontraron documentos PDF en el bucket de OCI.",
        "placeholder_chat": "Escribe tu pregunta sobre políticas de RRHH aquí...",
        "pensando": "Analizando políticas de la empresa...",
        "fuentes": "📄 Documentos consultados:",
        "bienvenida": "¡Hola! Soy **NexusHCM**, tu asistente de Recursos Humanos. ¿En qué política o normativa te puedo ayudar hoy?",
        "btn_limpiar": "🗑️ Limpiar conversación"
    },
    "en": {
        "titulo": "🤖 NexusHCM - HR Virtual Assistant",
        "subtitulo": "Query corporate policies, benefits, and internal regulations instantly.",
        "sidebar_titulo": "⚙️ Settings & Data",
        "selector_idioma": "Language / Idioma",
        "btn_sincronizar": "🔄 Sync documents from OCI",
        "sync_proceso": "Downloading PDFs from Oracle Cloud and updating memory...",
        "sync_exito": "Knowledge base updated successfully!",
        "sync_error": "No PDF documents found in the OCI bucket.",
        "placeholder_chat": "Type your HR policy question here...",
        "pensando": "Analyzing company policies...",
        "fuentes": "📄 Referenced documents:",
        "bienvenida": "Hello! I am **NexusHCM**, your Human Resources assistant. Which policy or regulation can I help you with today?",
        "btn_limpiar": "🗑️ Clear chat"
    }
}

# 3. Barra lateral (Sidebar)
with st.sidebar:
    # Selector de idioma
    opcion_idioma = st.radio(
        "🌐 Idioma / Language",
        options=["Español", "English"],
        horizontal=True
    )
    lang = "es" if opcion_idioma == "Español" else "en"
    t = TEXTOS[lang]

    st.divider()
    st.header(t["sidebar_titulo"])

    # Botón para forzar la actualización desde el Bucket de OCI
    if st.button(t["btn_sincronizar"], use_container_width=True):
        with st.spinner(t["sync_proceso"]):
            # Borrar base vectorial anterior para reconstruirla limpia
            if os.path.exists(settings.VECTOR_DB_DIR):
                shutil.rmtree(settings.VECTOR_DB_DIR)
            
            pdfs = descargar_pdfs_de_oci()
            if pdfs:
                chunks = procesar_documentos(pdfs)
                crear_o_cargar_vectorstore(chunks)
                # Limpiar caché de Streamlit para recargar el motor
                st.cache_resource.clear()
                st.success(t["sync_exito"])
            else:
                st.error(t["sync_error"])

    # Botón para reiniciar el historial visual del chat
    if st.button(t["btn_limpiar"], use_container_width=True):
        st.session_state.mensajes = []
        st.rerun()

    st.divider()
    st.caption("Powered by Oracle Cloud Infrastructure (OCI) & Cohere")

# 4. Cargar el motor RAG en caché (para que sea instantáneo entre preguntas)
@st.cache_resource
def inicializar_asistente():
    if not os.path.exists(settings.VECTOR_DB_DIR):
        pdfs = descargar_pdfs_de_oci()
        chunks = procesar_documentos(pdfs)
        vector_db = crear_o_cargar_vectorstore(chunks)
    else:
        vector_db = crear_o_cargar_vectorstore()
    return construir_cadena_rag(vector_db)

asistente_rag = inicializar_asistente()

# 5. Interfaz Principal del Chat
st.title(t["titulo"])
st.markdown(t["subtitulo"])
st.divider()

# Inicializar el historial de mensajes en la sesión
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

# Mostrar mensaje de bienvenida fijo
with st.chat_message("assistant"):
    st.markdown(t["bienvenida"])

# Dibujar los mensajes anteriores del historial
for msg in st.session_state.mensajes:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 6. Caja de entrada de texto del usuario
if prompt_usuario := st.chat_input(t["placeholder_chat"]):
    # Guardar y mostrar pregunta del usuario
    st.session_state.mensajes.append({"role": "user", "content": prompt_usuario})
    with st.chat_message("user"):
        st.markdown(prompt_usuario)

    # Generar y mostrar respuesta del asistente
    with st.chat_message("assistant"):
        with st.spinner(t["pensando"]):
            # Le indicamos al modelo en qué idioma debe responder según la interfaz
            instruccion_idioma = "Responde en Español." if lang == "es" else "Answer in English."
            consulta_completa = f"{prompt_usuario}\n\n({instruccion_idioma})"
            
            resultado = asistente_rag.invoke({"input": consulta_completa})
            respuesta_texto = resultado["answer"]
            
            # Extraer los nombres de los archivos PDF consultados (sin duplicados)
            documentos_usados = set()
            if "context" in resultado:
                for doc in resultado["context"]:
                    ruta_fuente = doc.metadata.get("source", "")
                    if ruta_fuente:
                        documentos_usados.add(os.path.basename(ruta_fuente))
            
            # Armar el texto final con las fuentes al pie
            texto_final = respuesta_texto
            if documentos_usados:
                lista_fuentes = "\n".join([f"- *{doc}*" for doc in documentos_usados])
                texto_final += f"\n\n---\n**{t['fuentes']}**\n{lista_fuentes}"
                
            st.markdown(texto_final)
            st.session_state.mensajes.append({"role": "assistant", "content": texto_final})
