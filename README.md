# NexusHCM - RAG Assistant 🤖💼

**NexusHCM RAG Assistant** is an intelligent virtual assistant powered by a **RAG (Retrieval-Augmented Generation)** architecture. Its primary purpose is to resolve employee inquiries by accurately analyzing internal Human Resources policies and corporate handbooks hosted in PDF format.

This project is designed to centralize Human Capital information, ensuring consistent, secure, and contextualized answers while significantly reducing the administrative workload of HR teams.

---

## 🏗️ System Architecture

The project implements an optimized data pipeline combining the robustness of **Oracle Cloud Infrastructure (OCI)** with the flexibility of **LangChain**:

1. **Storage (OCI Object Storage):** Official HR documents (.pdf) are securely managed within an OCI Bucket.
2. **Ingestion Pipeline (ETL & LangChain):** A Python script connects to the OCI bucket, downloads the files, and utilizes `PyMuPDF` for high-fidelity text extraction, segmenting it into text chunks using smart splitting strategies.
3. **Vector Processing (Embeddings):** Text chunks are transformed into high-dimensional vectors and indexed into a vector database for rapid semantic search.
4. **RAG Orchestration (LangChain + LLM):** The AI engine retrieves the most relevant context matching the user's query and generates a precise answer using a Large Language Model (LLM).
5. **User Interface (Streamlit):** An intuitive chat frontend that enables seamless, real-time interactions for end-users.

---

## 🛠️ Tech Stack & Tools

*   **Core Language:** Python 3.11+
*   **Cloud Infrastructure:** Oracle Cloud Infrastructure (OCI) - Object Storage & IAM.
*   **AI Orchestration:** LangChain (RecursiveCharacterTextSplitter, RetrievalQA).
*   **PDF Processing:** PyMuPDF (Fitz).
*   **Graphical Interface:** Streamlit.
*   **Security:** Python-dotenv for environment variables management.
*   **Version Control:** Git & GitHub.

---

## 📁 Project Structure

```text
NexusHCM-RAG-Assistant/
├── .github/workflows/    # Automated deployment pipelines (CI/CD)
├── data/                 # Temporary local folder for PDF processing (Git excluded)
├── src/
│   ├── __init__.py
│   ├── ingesta.py        # OCI Object Storage connection and document processing
│   ├── motor_rag.py      # Vector store configuration and LLM chain setup
│   └── config.py         # Environment variables loading and validation
├── app.py                # User interface built with Streamlit
├── .env.example          # Public environment variables template
├── .gitignore            # Excluded files from version control
├── requirements.txt      # Project dependencies
└── README.md             # Main documentation
```

---

## 🚀 Local Setup & Installation

Follow these steps to clone the project and run it locally using Visual Studio Code:

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
Copy the `.env.example` file, rename it to `.env`, and fill in the fields with your OCI credentials and your LLM provider keys:
```bash
cp .env.example .env
```

The `.env` file must include the following base structure:
```text
# OCI Configuration
OCI_COMPARTMENT_ID=ocid1.compartment.oc1..xxxxxx
OCI_BUCKET_NAME=your-hr-bucket
OCI_NAMESPACE=your-oci-namespace
OCI_CONFIG_PROFILE=DEFAULT

# LLM Deployment Credentials
# (Configure your OCI Generative AI, OpenAI, or other provider keys here)
LLM_API_KEY=your_api_key_here
```

### 5. Run the application
To launch the virtual assistant locally, run the following command in your terminal:
```bash
streamlit run app.py
```
Open the provided address in your browser (usually `http://localhost:8501`).

---

## 🔒 Security & Best Practices
This repository follows strict security guidelines. Cloud access credentials, OCI private keys, `.env` files, and downloaded PDF documents are explicitly configured in the `.gitignore` file to prevent accidental leaks of confidential data into public repositories.
