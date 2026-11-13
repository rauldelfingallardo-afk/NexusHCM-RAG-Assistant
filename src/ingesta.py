import os
import oci
from langchain_community.document_loaders import PyMuPDFLoader
# Nuevo y correcto
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.config import settings

def descargar_pdfs_de_oci():
    """Conecta a OCI Object Storage y descarga todos los PDFs del bucket."""
    print("🔄 Conectando con Oracle Cloud Infrastructure...")
    
    # 1. Cargar configuración desde ~/.oci/config
    config = oci.config.from_file(profile_name=settings.OCI_CONFIG_PROFILE)
    object_storage_client = oci.object_storage.ObjectStorageClient(config)
    
    # 2. Crear la carpeta 'data/' localmente si no existe
    os.makedirs(settings.LOCAL_DATA_DIR, exist_ok=True)
    
    # 3. Listar los archivos dentro del Bucket
    list_objects_response = object_storage_client.list_objects(
        namespace_name=settings.OCI_NAMESPACE,
        bucket_name=settings.OCI_BUCKET_NAME
    )
    
    archivos_descargados = []
    
    for obj in list_objects_response.data.objects:
        nombre_archivo = obj.name
        # Filtrar para descargar solo archivos PDF
        if nombre_archivo.lower().endswith(".pdf"):
            ruta_local = os.path.join(settings.LOCAL_DATA_DIR, nombre_archivo)
            print(f"📥 Descargando: {nombre_archivo}...")
            
            get_obj = object_storage_client.get_object(
                namespace_name=settings.OCI_NAMESPACE,
                bucket_name=settings.OCI_BUCKET_NAME,
                object_name=nombre_archivo
            )
            
            with open(ruta_local, "wb") as f:
                for chunk in get_obj.data.raw.stream(1024 * 1024, decode_content=False):
                    f.write(chunk)
                    
            archivos_descargados.append(ruta_local)
            
    print(f"✅ Descarga completada. Total de PDFs listos: {len(archivos_descargados)}")
    return archivos_descargados

def procesar_documentos(rutas_pdfs):
    """Lee los PDFs descargados y los divide en chunks de texto."""
    documentos_totales = []
    
    for ruta in rutas_pdfs:
        print(f"📄 Extrayendo texto de: {os.path.basename(ruta)}")
        loader = PyMuPDFLoader(ruta)
        documentos_totales.extend(loader.load())
        
    # Configurar el divisor de texto (chunks de 1000 caracteres con superposición de 200)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    
    chunks = text_splitter.split_documents(documentos_totales)
    print(f"🧩 Documentos divididos en {len(chunks)} fragmentos (chunks) listos para vectorizar.")
    return chunks

# Bloque de prueba directa
if __name__ == "__main__":
    pdfs = descargar_pdfs_de_oci()
    if pdfs:
        fragmentos = procesar_documentos(pdfs)
        print("\n--- Vista previa del primer fragmento ---")
        print(fragmentos[0].page_content[:300] + "...")
    else:
        print("⚠️ No se encontraron archivos PDF en el bucket de OCI.")
