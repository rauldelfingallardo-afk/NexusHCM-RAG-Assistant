# NexusHCM - RAG Assistant 🤖💼

[![Live Demo](https://shields.io)](https://nip.io)
[![Python](https://shields.io)](https://python.org)
[![Oracle Cloud](https://shields.io)](https://oracle.com)
[![Streamlit](https://shields.io)](https://streamlit.io)

**NexusHCM RAG Assistant** is an intelligent, bilingual (English/Spanish) virtual assistant powered by a **RAG (Retrieval-Augmented Generation)** architecture. Its primary purpose is to resolve employee inquiries by accurately analyzing internal Human Resources policies and corporate handbooks hosted in PDF format.

This project centralizes Human Capital information on **Oracle Cloud Infrastructure (OCI)**, ensuring consistent, secure, and source-cited answers while significantly reducing the administrative workload of HR teams.

---

## 🌐 Live Deployment

The application is deployed and running 24/7 on an **Oracle Cloud Compute (Ubuntu)** instance secured with **Nginx** and **Let's Encrypt SSL**:

👉 **[Access NexusHCM Live Assistant](https://https://nexushcm.144.22.231.88.nip.io)**

---

## 🏗️ System Architecture

The project implements an end-to-end cloud-native data pipeline combining **Oracle Cloud Infrastructure (OCI)** services with **LangChain**:

1. **Storage (OCI Object Storage):** Official HR policy documents (`.pdf`) are securely stored and versioned within a private OCI Bucket.
2. **Ingestion Pipeline (ETL & PyMuPDF):** A Python pipeline connects via the OCI SDK to download documents, extracts text with `PyMuPDF`, and splits content into semantic chunks (`RecursiveCharacterTextSplitter`).
3. **Vector Processing (OCI GenAI Embeddings + FAISS):** Text chunks are transformed into dense vector representations using **Cohere Embed v4 (`cohere.embed-v4.0`)** on OCI Generative AI and indexed locally in **FAISS** for low-latency semantic retrieval.
4. **RAG Orchestration (LangChain + Cohere Command-A):** The retrieval chain fetches the top relevant policy fragments and generates grounded, context-aware answers using **Cohere Command-A (`cohere.command-a-03-2025`)**, citing the exact source PDFs.
5. **Bilingual Frontend (Streamlit):** An interactive chat interface featuring real-time **English/Spanish** switching, one-click FAQ prompts, and an on-demand **OCI Bucket Sync** button.

---

## 🛠️ Tech Stack & Cloud Services

* **Core Language:** Python 3.11+
* **Cloud Infrastructure (OCI):**
  * **OCI Generative AI:** `cohere.command-a-03-2025` (LLM) & `cohere.embed-v4.0` (Embeddings).
  * **OCI Object Storage & IAM:** Secure document repository and API key authentication.
  * **OCI Compute & VCN:** Ubuntu 22.04 VM, Virtual Cloud Network, and Security Lists.
* **AI & Vector Search:** LangChain, `langchain-oci`, FAISS (`faiss-cpu`).
* **PDF Processing:** PyMuPDF (`fitz`).
* **Frontend & Web Server:** Streamlit, Nginx (Reverse Proxy), Certbot (HTTPS/TLS via `nip.io`).
* **Quality Assurance:** Pytest (Unit & integration tests with mocking).

---

## 📁 Project Structure

```text
NexusHCM-RAG-Assistant/
├── data/                     # Temporary local folder for PDF processing (Git excluded)
├── vectorstore_faiss/        # Persisted FAISS vector index (Git excluded)
├── src/
│   ├── __init__.py           # Package initializer
│   ├── config.py             # Environment variables loading and validation
│   ├── ingesta.py            # OCI Object Storage connection and PDF chunking
│   └── motor_rag.py          # FAISS vector store and OCI GenAI RAG chain setup
├── tests/
│   ├── __init__.py
│   └── test_rag_pipeline.py  # Automated pytest QA suite
├── app.py                    # Bilingual Streamlit UI with FAQ buttons & OCI sync
├── .env.example              # Public environment variables template
├── .gitignore                # Security exclusions (.env, keys, data, vectorstore)
├── requirements.txt          # Project dependencies
└── README.md                 # Project documentation
```

---

## 🚀 Local Setup & Installation

Follow these steps to clone the project and run it locally:

### 1. Clone the repository
```bash
git clone https://github.com
cd NexusHCM-RAG-Assistant
```

### 2. Create and activate the virtual environment
```bash
# On Windows:
python -m venv venv
venv\Scripts\activate

# On macOS/Linux:
python3 -m venv venv
source venv/bin/activate
```


### 3. Install dependencies
```bash
pip install -r requirements.txt
```


### 4. Configure environment variables
Copy `.env.example` to `.env` and fill in your OCI credentials and model endpoints:
```bash
cp .env.example .env
```

```ini
# OCI Object Storage Configuration
OCI_COMPARTMENT_ID=ocid1.compartment.oc1..xxxxxx
OCI_BUCKET_NAME=nexushcm-documents
OCI_NAMESPACE=your-oci-namespace
OCI_CONFIG_PROFILE=DEFAULT

# OCI Generative AI Configuration
OCI_GENAI_ENDPOINT=https://oraclecloud.com
OCI_LLM_MODEL_ID=cohere.command-a-03-2025
OCI_EMBEDDING_MODEL_ID=cohere.embed-v4.0
```

### 5. Run automated tests (QA)
```bash
pytest -v -W ignore::DeprecationWarning
```

### 6. Run the application locally
```bash
streamlit run app.py
```
Open `http://localhost:8501` in your browser.

---

## 🔒 Security & Best Practices

This repository follows strict cloud security guidelines:
* **Credential Isolation:** OCI API keys (`~/.oci/oci_api_key.pem`), `.env` files, downloaded PDFs, and local vector indexes are excluded via `.gitignore`.
* **Encrypted Traffic:** Production deployment enforces HTTPS via Let's Encrypt TLS certificates and reverse proxying through Nginx.
* **Service Resilience:** Managed as a background `systemd` daemon (`nexushcm.service`) with automatic restart policies.
