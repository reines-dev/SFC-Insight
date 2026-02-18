import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlparse, parse_qs

# --- CONFIGURACIÓN ---
YEARS_TO_SCRAPE = ["2024", "2025", "2026"] 
# BASE_DIR adjustment relative to script location or absolute
BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "1_raw", "pdf")
MAIN_URL = "https://www.superfinanciera.gov.co/publicaciones/20149/normativanormativa-generalcirculares-externas-cartas-circulares-y-resoluciones-desde-el-ano-20149/"

# --- SETUP SELENIUM ---
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--ignore-certificate-errors")

# Suppress logging
chrome_options.add_argument("--log-level=3")

def setup_driver():
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def download_file(url, folder):
    try:
        response = requests.get(url, verify=False, stream=True)
        response.raise_for_status()
        
        filename = ""
        if "content-disposition" in response.headers:
            cd = response.headers["content-disposition"]
            if "filename=" in cd:
                filename = cd.split("filename=")[1].strip('"')
        
        if not filename:
            query = urlparse(url).query
            params = parse_qs(query)
            if "idFile" in params:
                 filename = f"doc_{params['idFile'][0]}.pdf"
            else:
                 filename = os.path.basename(urlparse(url).path)
                 if not filename or "." not in filename:
                     filename = f"doc_unknown_{int(time.time())}.pdf"

        filepath = os.path.join(folder, filename)
        
        if os.path.exists(filepath):
            print(f"  [SKIP] Ya existe: {filename}")
            return

        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"  [OK] Descargado: {filename}")
        
    except Exception as e:
        print(f"  [ERROR] Falló descarga {url}: {e}")

def run_scraper():
    driver = setup_driver()
    try:
        print(f"--- Iniciando Scraping SFC ({YEARS_TO_SCRAPE}) ---")
        print(f"Guardando en: {BASE_DIR}")
        
        print(f"Navegando a página principal...")
        driver.get(MAIN_URL)
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "a")))
        time.sleep(5)
        
        main_links = driver.find_elements(By.TAG_NAME, "a")
        year_links = []
        
        for link in main_links:
            txt = link.text.strip()
            href = link.get_attribute("href")
            if txt in YEARS_TO_SCRAPE and href:
                year_links.append((txt, href))
                
        print(f"Enlaces de años encontrados: {len(year_links)}")

        for year, y_url in year_links:
            print(f"\nProcesando Año: {year}")
            
            year_dir = os.path.join(BASE_DIR, year)
            os.makedirs(year_dir, exist_ok=True)
            
            driver.get(y_url)
            time.sleep(5)
            
            doc_links = driver.find_elements(By.TAG_NAME, "a")
            count = 0
            for doc_link in doc_links:
                d_href = doc_link.get_attribute("href")
                d_text = doc_link.text.strip()
                
                if d_href and ("loader.php" in d_href or ".pdf" in d_href or ".doc" in d_href):
                     if "Tools2" in d_href and "descargar" in d_href:
                         # print(f"Descargando: {d_text}...") # Less verbose
                         download_file(d_href, year_dir)
                         count += 1
            
            print(f"Total documentos procesados para {year}: {count}")

    except Exception as e:
        print(f"Error Fatal: {e}")

    finally:
        driver.quit()

if __name__ == "__main__":
    run_scraper()
