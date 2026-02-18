import argparse
import sys
import os

# Añadir carpeta actual al path para importar scripts si fuera necesario
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts import scraper_sfc
from scripts import parser_docs
from scripts import embedder

def run_scraper():
    print("\n=== EJECUTANDO SCRAPER ===")
    scraper_sfc.run_scraper()

def run_parser():
    print("\n=== EJECUTANDO PARSER (RAW -> MARKDOWN) ===")
    parser_docs.main()

def run_embedder():
    print("\n=== EJECUTANDO EMBEDDER (MARKDOWN -> VECTOR DB) ===")
    embedder.main()

def main():
    parser = argparse.ArgumentParser(description="Pipeline RAG SFC")
    parser.add_argument("step", choices=["scrape", "parse", "embed", "all"], help="Paso a ejecutar")
    
    args = parser.parse_args()
    
    if args.step == "scrape":
        run_scraper()
    elif args.step == "parse":
        run_parser()
    elif args.step == "embed":
        run_embedder()
    elif args.step == "all":
        run_scraper()
        run_parser()
        run_embedder()

if __name__ == "__main__":
    main()
