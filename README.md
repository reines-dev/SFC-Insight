# SFC RAG Project

Este proyecto implementa un sistema de **Retrieval-Augmented Generation (RAG)** local para consultar la normativa de la **Superfinanciera de Colombia (SFC)**.

Permite descargar automáticamente Circulares y Resoluciones, procesarlas, almacenarlas en una base de datos vectorial y realizar consultas utilizando un LLM local (vía LM Studio).

## Características

*   **Web Scraping Automático**: Descarga documentos PDF desde la web de la SFC (años configurables, por defecto 2024-2025).
*   **Procesamiento Inteligente**: Convierte PDFs y DOCX a Markdown limpio antes de la vectorización.
*   **RAG Local**: Utiliza ChromaDB para almacenamiento vectorial y LM Studio para generación, asegurando privacidad y ejecución offline.
*   **Modular**: Arquitectura separada en scripts de descarga, parseo y embedding.

## Estructura del Proyecto

```
SFC_RAG_PROJECT/
├── data/
│   ├── 1_raw/                # Documentos originales (PDF, Word, Excel)
│   ├── 2_processed/          
│   │   ├── markdown/         # Contenido para RAG
│   │   └── json_tables/      # Tablas de Excel en JSON
│   └── 3_vector_db/          # Base de datos vectorial (ChromaDB)
├── scripts/
│   ├── scraper_sfc.py        # Descarga normatividad de la web
│   ├── parser_docs.py        # Convierte DOCX/PDF a Markdown
│   └── embedder.py           # Genera vectores y los guarda en DB
├── .env                      # Configuración de entorno
├── main.py                   # Orquestador del pipeline
├── query.py                  # Script para consultar al sistema
└── requirements.txt          # (Opcional) Lista de dependencias
```

## Requisitos

*   **Python 3.10+**
*   **LM Studio** corriendo localmente con un servidor compatible con OpenAI API.
    *   Modelo de Embedding recomendado: `nomic-embed-text-v1.5`
    *   Modelo de Chat: Cualquiera (e.g., Llama 3, Mistral)

## Instalación

1.  **Clonar el repositorio** y navegar a la carpeta.
2.  **Crear un entorno virtual**:
    ```powershell
    python -m venv .venv
    .\.venv\Scripts\Activate
    ```
3.  **Instalar dependencias**:
    ```powershell
    pip install langchain langchain-community langchain-chroma langchain-openai python-docx unstructured pypdf chromadb selenium webdriver-manager requests
    ```
4.  **Configurar `.env`**:
    Asegúrese de que el archivo `.env` apunte a su instancia de LM Studio:
    ```ini
    LM_STUDIO_URL=http://localhost:1234/v1
    EMBEDDING_MODEL=nomic-embed-text-v1.5
    ```

## Uso

El proyecto se gestiona principalmente a través de `main.py`.

### 1. Descargar Normatividad
Descarga los documentos de los años configurados (por defecto 2024-2025).
```powershell
python main.py scrape
```

### 2. Procesar Documentos
Convierte los archivos descargados a formato Markdown para mejor indexación.
```powershell
python main.py parse
```

### 3. Crear Base de Datos Vectorial (Embeddings)
Genera los embeddings y los guarda en ChromaDB.
```powershell
python main.py embed
```

> **Nota**: Puede ejecutar todo el flujo con `python main.py all`.

### 4. Consultar (RAG)
Realice preguntas sobre la normativa descargada:
```powershell
python query.py "¿Qué dice la normativa sobre el riesgo climático?"
```

## Personalización
*   **Años de descarga**: Modifique la lista `YEARS_TO_SCRAPE` en `scripts/scraper_sfc.py`.
*   **Modelos**: Cambie el modelo de embedding en `.env` y asegúrese de cargar el mismo en LM Studio.
