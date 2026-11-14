import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # OCI Base
    OCI_COMPARTMENT_ID = os.getenv("OCI_COMPARTMENT_ID")
    OCI_BUCKET_NAME = os.getenv("OCI_BUCKET_NAME")
    OCI_NAMESPACE = os.getenv("OCI_NAMESPACE")
    OCI_CONFIG_PROFILE = os.getenv("OCI_CONFIG_PROFILE", "DEFAULT")
    
    # OCI Generative AI (Cohere)
    OCI_GENAI_ENDPOINT = os.getenv("OCI_GENAI_ENDPOINT")
    OCI_LLM_MODEL_ID = os.getenv("OCI_LLM_MODEL_ID", "cohere.command-r-plus")
    OCI_EMBEDDING_MODEL_ID = os.getenv("OCI_EMBEDDING_MODEL_ID", "cohere.embed-multilingual-v3.0")
    
    # Fallback (OpenAI)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
    
    # Rutas locales
    LOCAL_DATA_DIR = os.path.join(os.getcwd(), "data")
    VECTOR_DB_DIR = os.path.join(os.getcwd(), "vectorstore_faiss")

settings = Settings()

# CODIGO ANTERIOR (COMENTADO) PARA CARGAR VARIABLES DE ENTORNO DESDE UN ARCHIVO .env
# import os
# from dotenv import load_dotenv

# # Cargar las variables del archivo .env
# load_dotenv()

# class Settings:
#     OCI_COMPARTMENT_ID = os.getenv("OCI_COMPARTMENT_ID")
#     OCI_BUCKET_NAME = os.getenv("OCI_BUCKET_NAME")
#     OCI_NAMESPACE = os.getenv("OCI_NAMESPACE")
#     OCI_CONFIG_PROFILE = os.getenv("OCI_CONFIG_PROFILE", "DEFAULT")
    
#     # Ruta local donde se descargarán temporalmente los PDFs
#     LOCAL_DATA_DIR = os.path.join(os.getcwd(), "data")

# settings = Settings()
