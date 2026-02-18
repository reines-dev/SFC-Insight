import os
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# --- CONFIGURACIÓN ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "2_processed", "markdown")
CHROMA_PATH = os.path.join(BASE_DIR, "data", "3_vector_db")

# Ajustar según tu configuración de LM Studio
LM_STUDIO_URL = "http://localhost:1234/v1" 
EMBEDDING_MODEL = "nomic-embed-text-v1.5" 

def load_markdown_docs():
    documents = []
    print(f"Buscando archivos MD en: {PROCESSED_DIR}")
    
    for root, dirs, files in os.walk(PROCESSED_DIR):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        text = f.read()
                        
                    # Crear objeto Document de Langchain
                    rel_path = os.path.relpath(file_path, PROCESSED_DIR)
                    doc = Document(page_content=text, metadata={"source": rel_path})
                    documents.append(doc)
                    
                except Exception as e:
                    print(f"Error leyendo {file_path}: {e}")
                    
    print(f"Total documentos cargados: {len(documents)}")
    return documents

def main():
    # 1. Cargar documentos
    docs = load_markdown_docs()
    if not docs:
        print("No se encontraron documentos procesados.")
        return

    # 2. Dividir texto (Splitting)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True
    )
    chunks = text_splitter.split_documents(docs)
    print(f"Documentos divididos en {len(chunks)} chunks.")

    # 3. Inicializar Embeddings
    embeddings = OpenAIEmbeddings(
        base_url=LM_STUDIO_URL,
        api_key="lm-studio",
        model=EMBEDDING_MODEL,
        check_embedding_ctx_length=False
    )

    # 4. Crear/Actualizar Vector Store (Chroma)
    print("Creando/Actualizando base de datos vectorial...")
    db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PATH
    )
    print(f"Base de datos guardada en {CHROMA_PATH}")

if __name__ == "__main__":
    main()
