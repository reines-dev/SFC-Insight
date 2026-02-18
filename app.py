import streamlit as st
import os
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

# --- CONFIGURACIÓN ---
load_dotenv()
CHROMA_PATH = "data/3_vector_db"
DEFAULT_LM_STUDIO_URL = os.getenv("LM_STUDIO_URL", "http://localhost:1234/v1")
DEFAULT_EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text-v1.5")
DEFAULT_CHAT_MODEL = "local-model"

st.set_page_config(page_title="SFC RAG - Consulta Normativa", page_icon="🏦", layout="wide")

# --- UI SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Configuración")
    lm_studio_url = st.text_input("URL LM Studio", value=DEFAULT_LM_STUDIO_URL)
    embedding_model = st.text_input("Modelo de Embedding", value=DEFAULT_EMBEDDING_MODEL)
    chat_model = st.text_input("Modelo de Chat", value=DEFAULT_CHAT_MODEL)
    st.info("Asegúrese de que LM Studio esté corriendo y con los modelos cargados.")

st.title("🏦 SFC RAG: Consulta de Normativa")
st.markdown("""
Esta aplicación permite realizar consultas sobre la normativa de la **Superfinanciera de Colombia** (Circulares, Resoluciones) 
utilizando Inteligencia Artificial local.
""")

# --- LÓGICA RAG ---
def query_rag(query_text_local):
    try:
        # 1. Inicializar Embeddings
        embedding_function = OpenAIEmbeddings(
            base_url=lm_studio_url,
            api_key="lm-studio",
            model=embedding_model,
            check_embedding_ctx_length=False
        )
        
        # 2. Conectar a Vector Store
        if not os.path.exists(CHROMA_PATH):
            return "Error: No se encontró la base de datos vectorial en `data/3_vector_db`. Ejecute `main.py embed` primero.", []
            
        db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

        # 3. Retrieval
        results = db.similarity_search_with_score(query_text_local, k=5)
        
        if len(results) == 0:
            return "No se encontraron resultados relevantes en la base de datos.", []

        # Separador explícito sin romper el literal de string
        context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
        
        # 4. Generation
        prompt_template = ChatPromptTemplate.from_template("""
        Responde la pregunta basándote únicamente en el siguiente contexto:
        {context}
        ---
        Pregunta: {question}
        """)
        prompt = prompt_template.format(context=context_text, question=query_text_local)

        model = ChatOpenAI(
            base_url=lm_studio_url,
            api_key="lm-studio",
            model=chat_model,
            temperature=0.7
        )
        
        response = model.invoke(prompt)
        return response.content, results

    except Exception as e:
        return f"Error durante la consulta: {e}", []

# --- INTERFAZ DE CONSULTA ---
query_input = st.text_input("Escriba su pregunta sobre la normativa:", placeholder="Ej: ¿Qué dice la circular sobre riesgo climático?")

if st.button("Consultar"):
    if query_input:
        with st.spinner("Buscando en la normativa y generando respuesta..."):
            answer, sources = query_rag(query_input)
            
            st.subheader("Respuesta:")
            st.write(answer)
            
            if sources:
                with st.expander("📄 Fuentes y Contexto Recuperado"):
                    for i, (doc, score) in enumerate(sources):
                        st.markdown(f"**Fuente {i+1}:** `{doc.metadata.get('source', 'Desconocido')}` (Score: {score:.4f})")
                        st.text_area(f"Fragmento {i+1}", doc.page_content, height=150, key=f"fragment_{i}")
    else:
        st.warning("Por favor, ingrese una pregunta.")

st.divider()
st.caption("Desarrollado para consulta de normativa SFC con RAG Local.")
