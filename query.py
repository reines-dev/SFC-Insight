import argparse
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# --- CONFIGURACIÓN ---
CHROMA_PATH = "data/3_vector_db"
LM_STUDIO_URL = "http://localhost:1234/v1"
EMBEDDING_MODEL = "nomic-embed-text-v1.5" # Asegúrate de que coincida con el usado en ingest.py
# Nombre del modelo de chat en LM Studio (puede ser cualquiera si LM Studio solo carga uno)
CHAT_MODEL = "local-model" 

PROMPT_TEMPLATE = """
Responde la pregunta basándote únicamente en el siguiente contexto:

{context}

---

Pregunta: {question}
"""

def main():
    # 1. Parsear argumentos
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="La pregunta para el RAG")
    args = parser.parse_args()
    query_text = args.query_text

    # 2. Inicializar Vector Store y Embeddings
    embedding_function = OpenAIEmbeddings(
        base_url=LM_STUDIO_URL,
        api_key="lm-studio",
        model=EMBEDDING_MODEL,
        check_embedding_ctx_length=False
    )
    
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # 3. Buscar en la base de datos (Retrieval)
    results = db.similarity_search_with_score(query_text, k=5)
    
    if len(results) == 0:
        print("No se encontraron resultados relevantes.")
        return

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    
    # 4. Generar respuesta con LLM (Generation)
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    
    print(f"\n--- Contexto Recuperado (ejemplo) ---\n{results[0][0].page_content[:200]}...\n")

    model = ChatOpenAI(
        base_url=LM_STUDIO_URL,
        api_key="lm-studio",
        model=CHAT_MODEL,
        temperature=0.7
    )
    
    print("--- Generando respuesta... ---")
    try:
        response = model.invoke(prompt)
        print("\nRespuesta:\n")
        print(response.content)
    except Exception as e:
        print(f"\nError generando respuesta: {e}")
        print("\nSUGERENCIA: Asegúrate de tener cargado un modelo de CHAT (ej. Llama 3, Mistral) en LM Studio, no solo el de embeddings.")
        print("El modelo actual detectado en LM Studio parece ser solo de embeddings o no compatible con chat.")

if __name__ == "__main__":
    main()
