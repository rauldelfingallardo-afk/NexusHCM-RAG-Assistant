import os
from unittest.mock import MagicMock, patch
from langchain_core.documents import Document
from src.config import settings
from src.ingesta import procesar_documentos

def test_configuracion_cargada():
    """Verifica que las variables críticas de OCI y modelos estén definidas."""
    assert settings.OCI_BUCKET_NAME is not None
    assert settings.OCI_LLM_MODEL_ID is not None
    assert settings.OCI_EMBEDDING_MODEL_ID is not None
    assert "http" in settings.OCI_GENAI_ENDPOINT

def test_fragmentacion_documentos():
    """Verifica que el divisor de texto genere chunks válidos manteniendo la fuente."""
    with patch("src.ingesta.PyMuPDFLoader") as mock_loader:
        mock_instance = MagicMock()
        mock_instance.load.return_value = [
            Document(
                page_content="Política de vacaciones NexusHCM. " * 100,
                metadata={"source": "politica_vacaciones.pdf", "page": 0}
            )
        ]
        mock_loader.return_value = mock_instance

        chunks = procesar_documentos(["ruta/falsa/politica_vacaciones.pdf"])
        
        assert len(chunks) > 1, "El texto largo debería dividirse en múltiples fragmentos"
        assert chunks[0].metadata["source"] == "politica_vacaciones.pdf"

def test_integridad_app_streamlit():
    """Verifica que el archivo principal app.py exista y no tenga errores de sintaxis."""
    assert os.path.exists("app.py")
    with open("app.py", "r", encoding="utf-8") as f:
        codigo = f.read()
    compile(codigo, "app.py", "exec")
