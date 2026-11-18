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

# 2. Diccionario de traducciones y Preguntas Frecuentes (Español / Inglés)
TEXTOS = {
    "es": {
        "titulo": "🤖 NexusHCM - Asistente Virtual de RRHH",
        "subtitulo": "Consulta políticas corporativas, beneficios y normativas internas al instante.",
        "sidebar_titulo": "⚙️ Configuración y Datos",
        "btn_sincronizar": "🔄 Sincronizar documentos desde OCI",
        "sync_proceso": "Descargando PDFs desde Oracle Cloud y actualizando memoria...",
        "sync_exito": "¡Base de conocimientos actualizada con éxito!",
        "sync_error": "No se encontraron documentos PDF en el bucket de OCI.",
        "placeholder_chat": "Escribe tu pregunta sobre políticas de RRHH aquí...",
        "pensando": "Analizando políticas de la empresa...",
        "fuentes": "📄 Documentos consultados:",
        "bienvenida": "¡Hola! Soy **NexusHCM**, tu asistente de Recursos Humanos. ¿En qué política o normativa te puedo ayudar hoy?",
        "btn_limpiar": "🗑️ Limpiar conversación",
        "faq_titulo": "💡 Preguntas Frecuentes",
        "faqs": [
            "¿Qué evalúa la auditoría de seguridad en el trabajo remoto?",
            "¿Cuáles son los premios por años de servicio y lealtad?",
            "¿Cuál es el resumen general de las políticas vigentes?"
        ]
    },
    "en": {
        "titulo": "🤖 NexusHCM - HR Virtual Assistant",
        "subtitulo": "Query corporate policies, benefits, and internal regulations instantly.",
        "sidebar_titulo": "⚙️ Settings & Data",
        "btn_sincronizar": "🔄 Sync documents from OCI",
        "sync_proceso": "Downloading PDFs from Oracle Cloud and updating memory...",
        "sync_exito": "Knowledge base updated successfully!",
        "sync_error": "No PDF documents found in the OCI bucket.",
        "placeholder_chat": "Type your HR policy question here...",
        "pensando": "Analyzing company policies...",
        "fuentes": "📄 Referenced documents:",
        "bienvenida": "Hello! I am **NexusHCM**, your Human Resources assistant. Which policy or regulation can I help you with today?",
        "btn_limpiar": "🗑️ Clear chat",
        "faq_titulo": "💡 Frequently Asked Questions",
        "faqs": [
            "What does the remote workplace health & safety audit evaluate?",
            "What are the years of service recognition and loyalty awards?",
            "What is the general summary of current company policies?"
        ]
    }
}

# 3. Barra lateral (Sidebar)
pregunta_seleccionada = None

with st.sidebar:
    opcion_idioma = st.radio(
        "🌐 Idioma / Language",
        options=["Español", "English"],
        horizontal=True
    )
    lang = "es" if opcion_idioma == "Español" else "en"
    t = TEXTOS[lang]

    st.divider()
    st.subheader(t["faq_titulo"])
    
    # Botones de Preguntas Frecuentes
    for faq in t["faqs"]:
        if st.button(faq, use_container_width=True):
            pregunta_seleccionada = faq

    st.divider()
    st.subheader(t["sidebar_titulo"])

    if st.button(t["btn_sincronizar"], use_container_width=True):
        with st.spinner(t["sync_proceso"]):
            if os.path.exists(settings.VECTOR_DB_DIR):
                shutil.rmtree(settings.VECTOR_DB_DIR)
            
            pdfs = descargar_pdfs_de_oci()
            if pdfs:
                chunks = procesar_documentos(pdfs)
                crear_o_cargar_vectorstore(chunks)
                st.cache_resource.clear()
                st.success(t["sync_exito"])
            else:
                st.error(t["sync_error"])

    if st.button(t["btn_limpiar"], use_container_width=True):
        st.session_state.mensajes = []
        st.rerun()

    st.divider()
    st.caption("Powered by Oracle Cloud Infrastructure (OCI) & Cohere")

# 4. Cargar el motor RAG en caché
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

if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

with st.chat_message("assistant"):
    st.markdown(t["bienvenida"])

for msg in st.session_state.mensajes:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 6. Procesar entrada (ya sea escrita por el usuario o clic en FAQ)
prompt_usuario = st.chat_input(t["placeholder_chat"]) or pregunta_seleccionada

if prompt_usuario:
    st.session_state.mensajes.append({"role": "user", "content": prompt_usuario})
    with st.chat_message("user"):
        st.markdown(prompt_usuario)

    with st.chat_message("assistant"):
        with st.spinner(t["pensando"]):
            instruccion_idioma = "Responde en Español." if lang == "es" else "Answer in English."
            consulta_completa = f"{prompt_usuario}\n\n({instruccion_idioma})"
            
            resultado = asistente_rag.invoke({"input": consulta_completa})
            respuesta_texto = resultado["answer"]
            
            documentos_usados = set()
            if "context" in resultado:
                for doc in resultado["context"]:
                    ruta_fuente = doc.metadata.get("source", "")
                    if ruta_fuente:
                        documentos_usados.add(os.path.basename(ruta_fuente))
            
            texto_final = respuesta_texto
            if documentos_usados:
                lista_fuentes = "\n".join([f"- *{doc}*" for doc in documentos_usados])
                texto_final += f"\n\n---\n**{t['fuentes']}**\n{lista_fuentes}"
                
            st.markdown(texto_final)
            st.session_state.mensajes.append({"role": "assistant", "content": texto_final})
