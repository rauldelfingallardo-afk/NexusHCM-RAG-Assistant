import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OCIGenAIEmbeddings
from langchain_community.chat_models import ChatOCIGenAI
from langchain_openai import ChatOpenAI
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

from src.config import settings
from src.ingesta import descargar_pdfs_de_oci, procesar_documentos

def obtener_embeddings():
    """Inicializa el modelo de Embeddings de Cohere en OCI."""
    return OCIGenAIEmbeddings(
        model_id=settings.OCI_EMBEDDING_MODEL_ID,
        service_endpoint=settings.OCI_GENAI_ENDPOINT,
        compartment_id=settings.OCI_COMPARTMENT_ID,
        auth_profile=settings.OCI_CONFIG_PROFILE
    )

def crear_o_cargar_vectorstore(chunks=None):
    """Crea la base de datos vectorial FAISS o la carga si ya existe en disco."""
    embeddings = obtener_embeddings()
    
    if os.path.exists(settings.VECTOR_DB_DIR) and chunks is None:
        print("📂 Cargando base de datos vectorial existente desde disco...")
        return FAISS.load_local(
            settings.VECTOR_DB_DIR, 
            embeddings, 
            allow_dangerous_deserialization=True
        )
    
    print("🧠 Vectorizando fragmentos con Cohere en OCI (esto puede tomar unos segundos)...")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(settings.VECTOR_DB_DIR)
    print(f"💾 Base de datos vectorial guardada en: {settings.VECTOR_DB_DIR}")
    return vectorstore

def obtener_llm():
    """Intenta conectar con OCI Cohere; si falla, activa el modelo de respaldo (Fallback)."""
    try:
        print(f"🤖 Conectando con OCI Generative AI ({settings.OCI_LLM_MODEL_ID})...")
        llm = ChatOCIGenAI(
            model_id=settings.OCI_LLM_MODEL_ID,
            service_endpoint=settings.OCI_GENAI_ENDPOINT,
            compartment_id=settings.OCI_COMPARTMENT_ID,
            auth_profile=settings.OCI_CONFIG_PROFILE,
            model_kwargs={"temperature": 0.2, "max_tokens": 800}
        )
        return llm
    except Exception as e:
        print(f"⚠️ Error al conectar con OCI GenAI: {e}")
        print("🔄 Activando modelo de respaldo (Fallback - OpenAI)...")
        return ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_MODEL_NAME,
            temperature=0.2
        )

def construir_cadena_rag(vectorstore):
    """Une el buscador de documentos con el LLM mediante un Prompt de RRHH."""
    llm = obtener_llm()
    
    # Configurar el buscador para que traiga los 4 fragmentos más relevantes
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    
    # Instrucciones estrictas para el asistente
    system_prompt = (
        "Eres NexusHCM, un asistente virtual experto en Recursos Humanos. "
        "Utiliza ÚNICAMENTE los siguientes fragmentos de las políticas de la empresa para responder a la pregunta del colaborador. "
        "Si la respuesta no se encuentra en el contexto proporcionado, di amablemente que no tienes esa información en las políticas actuales y sugiere contactar a Recursos Humanos. "
        "Responde en el mismo idioma en el que te hagan la pregunta (Español o Inglés).\n\n"
        "Contexto:\n{context}"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])
    
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    return rag_chain

# Bloque de prueba directa en consola
if __name__ == "__main__":
    # 1. Ejecutar ingesta si aún no hemos creado los vectores
    if not os.path.exists(settings.VECTOR_DB_DIR):
        pdfs = descargar_pdfs_de_oci()
        chunks = procesar_documentos(pdfs)
        vector_db = crear_o_cargar_vectorstore(chunks)
    else:
        vector_db = crear_o_cargar_vectorstore()
        
    # 2. Construir el asistente
    asistente = construir_cadena_rag(vector_db)
    
    # 3. Hacer una pregunta de prueba
    pregunta = "¿De qué tratan estos documentos o cuál es la política principal?"
    print(f"\n🙋 Pregunta: {pregunta}")
    
    respuesta = asistente.invoke({"input": pregunta})
    print(f"\n🤖 Respuesta de NexusHCM:\n{respuesta['answer']}")
