import os
import shutil
from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader

# --- CONFIGURACIÓN ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "1_raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "2_processed", "markdown")

def process_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    full_text = ""
    
    try:
        if ext == ".docx":
            loader = Docx2txtLoader(file_path)
            docs = loader.load()
            full_text = "\n\n".join([d.page_content for d in docs])
            
        elif ext == ".pdf":
            loader = PyPDFLoader(file_path)
            docs = loader.load()
            full_text = "\n\n".join([d.page_content for d in docs])

        elif ext in [".xls", ".xlsx"]:
            import pandas as pd
            import json
            
            try:
                xls = pd.ExcelFile(file_path)
                text_parts = []
                sheets_dict = {}
                
                for sheet_name in xls.sheet_names:
                    df = pd.read_excel(xls, sheet_name=sheet_name)
                    # Limpiar columnas vacías
                    df = df.dropna(how='all').dropna(axis=1, how='all')
                    
                    if not df.empty:
                        # Convertir a Markdown
                        md_table = df.to_markdown(index=False)
                        text_parts.append(f"## Hoja: {sheet_name}\n\n{md_table}")
                        
                        # Guardar para JSON - convertir fechas a str para evitar error de serializacion
                        df = df.astype(str)
                        sheets_dict[sheet_name] = df.to_dict(orient="records")
                
                if text_parts:
                    full_text = "\n\n".join(text_parts)
                    
                # Guardar JSON si hay datos
                if sheets_dict:
                    # Encontrar ruta destino JSON
                    abs_path = os.path.abspath(file_path)
                    raw_mark = os.path.join("data", "1_raw")
                    if raw_mark in abs_path:
                        rel = abs_path.split(raw_mark)[1].lstrip(os.sep)
                        json_dest = os.path.join(BASE_DIR, "data", "2_processed", "json_tables", os.path.splitext(rel)[0] + ".json")
                        
                        os.makedirs(os.path.dirname(json_dest), exist_ok=True)
                        with open(json_dest, "w", encoding="utf-8") as f:
                            json.dump(sheets_dict, f, ensure_ascii=False, indent=4)
                    
            except Exception as e:
                print(f"Error leyendo Excel {file_path}: {e}")
                return None

        else:
            return None
            
        if not full_text:
            return None
        
        # Añadir metadatos simples al inicio
        source = os.path.basename(file_path)
        md_content = f"# DOCUMENTO: {source}\n\n{full_text}"
        return md_content

    except Exception as e:
        print(f"Error procesando {file_path}: {e}")
        return None

def main():
    print(f"Iniciando procesamiento desde: {RAW_DIR}")
    print(f"Destino: {PROCESSED_DIR}")
    
    count = 0
    
    for root, dirs, files in os.walk(RAW_DIR):
        for file in files:
            if file.lower().endswith((".docx", ".pdf", ".xls", ".xlsx")):
                src_path = os.path.join(root, file)
                
                # Calcular ruta relativa para replicar estructura
                rel_path = os.path.relpath(src_path, RAW_DIR)
                dest_subpath = os.path.splitext(rel_path)[0] + ".md"
                dest_path = os.path.join(PROCESSED_DIR, dest_subpath)
                
                # Crear directorios destino
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                
                print(f"Procesando: {rel_path} -> {dest_subpath}")
                content = process_file(src_path)
                
                if content:
                    with open(dest_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    count += 1
                else:
                    print(f"  -> Advertencia: No se pudo extraer texto de {file}")

    print(f"Total documentos procesados: {count}")

if __name__ == "__main__":
    main()
