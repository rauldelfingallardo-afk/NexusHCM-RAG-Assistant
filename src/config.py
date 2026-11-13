import os
from dotenv import load_dotenv

# Cargar las variables del archivo .env
load_dotenv()

class Settings:
    OCI_COMPARTMENT_ID = os.getenv("OCI_COMPARTMENT_ID")
    OCI_BUCKET_NAME = os.getenv("OCI_BUCKET_NAME")
    OCI_NAMESPACE = os.getenv("OCI_NAMESPACE")
    OCI_CONFIG_PROFILE = os.getenv("OCI_CONFIG_PROFILE", "DEFAULT")
    
    # Ruta local donde se descargarán temporalmente los PDFs
    LOCAL_DATA_DIR = os.path.join(os.getcwd(), "data")

settings = Settings()
