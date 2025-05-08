import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#####################################
# CONFIGURACIÓN Y CONSTANTES
#####################################

LIBRARY_URL = "https://library.uniquindio.edu.co/databases"
FACULTY_NAME = "Facultad de Ingeniería"
DATABASE_NAMES = ["IEEE", "ScienceDirect", "Nature"]
SEARCH_TERMS = ["Computational Thinking", "Abstraction"]

DATA_FOLDER = os.path.join(os.getcwd(), "data")
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

#####################################
# FUNCIONES AUXILIARES PARA BIBTEX
#####################################

def generate_bibtex_key(author, year):
    if author and author.strip():
        first_author = author.split()[0]
    else:
        first_author = "Unknown"
    return f"{first_author}{year}"

def make_bib_entry(entry):
    bib_key = generate_bibtex_key(entry.get("Authors", "Unknown"), entry.get("Volume year", "Unknown"))
    bibtex_entry = f"@article{{{bib_key},\n"
    bibtex_entry += f"  author = {{{entry.get('Authors', 'Unknown')}}},\n"
    bibtex_entry += f"  title = {{{entry.get('Article title', 'Unknown')}}},\n"
    bibtex_entry += f"  year = {{{entry.get('Volume year', 'Unknown')}}},\n"
    if entry.get("Journal title"):
        bibtex_entry += f"  journal = {{{entry.get('Journal title')}}},\n"
    if entry.get("DOI") and entry.get("DOI") != "No DOI":
        bibtex_entry += f"  doi = {{{entry.get('DOI')}}},\n"
    if entry.get("URL") and entry.get("URL") != "No URL":
        bibtex_entry += f"  url = {{{entry.get('URL')}}},\n"
    if entry.get("Abstract") and entry.get("Abstract") != "N/A":
        bibtex_entry += f"  abstract = {{{entry.get('Abstract')}}},\n"
    if entry.get("CitationBib"):
        bibtex_entry += f"  citation_bib = {{{entry.get('CitationBib')}}},\n"
    if entry.get("CitationSCS"):
        bibtex_entry += f"  citation_scs = {{{entry.get('CitationSCS')}}},\n"
    bibtex_entry += "}\n\n"
    return bibtex_entry

#####################################
# CONFIGURACIÓN DEL DRIVER DE SELENIUM
#####################################

def setup_driver():
    """
    Configura ChromeDriver usando el perfil "Default" de Chrome.
    Asegúrate de que no haya ninguna instancia de Chrome abierta.
    """
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    # Asegúrate de ajustar la ruta del perfil al tuyo
    chrome_options.add_argument("--user-data-dir=C:/Users/Brandon/AppData/Local/Google/Chrome/User Data/Default")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

#####################################
# FUNCIONES DE NAVEGACIÓN E INTERACCIÓN
#####################################

def get_database_links(driver):
    # Se asume que ya hiciste manualmente clic en "Facultad de Ingeniería" y se desplegaron las bases de datos
    print("""
--------------------------------------------------------------------------------
Ya hiciste clic en "Facultad de Ingeniería" y se han desplegado los enlaces 
de las bases de datos (IEEE, ScienceDirect, Nature, etc.). 
Cuando confirmes que la página muestra los enlaces, presiona ENTER para continuar.
--------------------------------------------------------------------------------
""")
    input("Presiona ENTER para continuar...")
    links = {}
    for db in DATABASE_NAMES:
        try:
            element = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, db))
            )
            links[db] = element.get_attribute("href")
        except Exception as e:
            print(f"Error al obtener el enlace para {db}: {e}")
    return links

def search_database(driver, base_url, database, search_term):
    if database == "IEEE":
        search_url = base_url + "?queryText=" + search_term.replace(" ", "+")
    elif database == "ScienceDirect":
        search_url = base_url + "?qs=" + search_term.replace(" ", "+")
    elif database == "Nature":
        search_url = base_url + "?q=" + search_term.replace(" ", "+")
    else:
        search_url = base_url
    driver.get(search_url)
    
    # En IEEE puede aplicarse la búsqueda por URL, pero se intenta también obtener el campo de búsqueda
    try:
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='search']"))
        )
        search_box.clear()
        search_box.send_keys(search_term)
        search_box.send_keys(Keys.ENTER)
    except Exception:
        pass

    # Hacer scroll para cargar más resultados
    last_height = driver.execute_script("return document.body.scrollHeight")
    for _ in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(4)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def get_articles_selenium(driver, database):
    articles = []
    if database == "IEEE":
        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "xpl-results-item"))
            )
            results = driver.find_elements(By.TAG_NAME, "xpl-results-item")
            for result in results:
                try:
                    title = result.find_element(By.CSS_SELECTOR, "h3 a").text.strip()
                except:
                    title = "Unknown"
                try:
                    authors = result.find_element(By.CSS_SELECTOR, "xpl-authors-name-list p").text.strip()
                except:
                    authors = "Unknown"
                try:
                    publisher_info = result.find_element(By.CSS_SELECTOR, "div.publisher-info-container").text.strip()
                except:
                    publisher_info = "Unknown"
                try:
                    doi_elem = result.find_element(By.CSS_SELECTOR, "a[href*='doi.org']")
                    doi = doi_elem.get_attribute("href")
                except:
                    doi = "No DOI"
                try:
                    url_art = result.find_element(By.CSS_SELECTOR, "h3 a").get_attribute("href")
                except:
                    url_art = "No URL"
                article = {
                    "Article title": title,
                    "Authors": authors,
                    "Volume year": publisher_info,
                    "DOI": doi,
                    "URL": url_art,
                    "Abstract": "N/A",
                    "Journal title": "IEEE",
                    "CitationBib": "",
                    "CitationSCS": ""
                }
                # Abrir la página del artículo para intentar descargar los archivos de citas
                if url_art != "No URL":
                    current_window = driver.current_window_handle
                    driver.execute_script("window.open(arguments[0]);", url_art)
                    driver.switch_to.window(driver.window_handles[-1])
                    time.sleep(3)
                    try:
                        bib_button = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '.bib')]"))
                        )
                        bib_link = bib_button.get_attribute("href")
                        article["CitationBib"] = bib_link
                        print(f"Descargando archivo .bib: {bib_link}")
                        driver.get(bib_link)
                        time.sleep(2)
                    except Exception as e:
                        print("No se encontró un archivo .bib en:", url_art)
                        article["CitationBib"] = ""
                    try:
                        scs_button = driver.find_element(By.XPATH, "//a[contains(@href, '.scs')]")
                        scs_link = scs_button.get_attribute("href")
                        article["CitationSCS"] = scs_link
                        print(f"Descargando archivo .scs: {scs_link}")
                        driver.get(scs_link)
                        time.sleep(2)
                    except Exception as e:
                        print("No se encontró un archivo .scs en:", url_art)
                        article["CitationSCS"] = ""
                    driver.close()
                    driver.switch_to.window(current_window)
                articles.append(article)
        except Exception as e:
            print("[Selenium Scraper] IEEE: Error obteniendo resultados:", e)
    elif database == "ScienceDirect":
        try:
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".ResultItem")))
            results = driver.find_elements(By.CSS_SELECTOR, ".ResultItem")
            for result in results:
                try:
                    title = result.find_element(By.CSS_SELECTOR, "h2").text.strip()
                except:
                    title = "Unknown"
                try:
                    authors = result.find_element(By.CSS_SELECTOR, ".Authors").text.strip()
                except:
                    authors = "Unknown"
                try:
                    year = result.find_element(By.CSS_SELECTOR, ".Publication-date").text.strip()
                except:
                    year = "Unknown"
                doi = "No DOI"
                try:
                    url_art = result.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                except:
                    url_art = "No URL"
                article = {
                    "Article title": title,
                    "Authors": authors,
                    "Volume year": year,
                    "DOI": doi,
                    "URL": url_art,
                    "Abstract": "N/A",
                    "Journal title": "ScienceDirect"
                }
                articles.append(article)
        except Exception as e:
            print("[Selenium Scraper] ScienceDirect: Error obteniendo resultados:", e)
    elif database == "Nature":
        try:
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".app-article-item")))
            results = driver.find_elements(By.CSS_SELECTOR, ".app-article-item")
            for result in results:
                try:
                    title = result.find_element(By.CSS_SELECTOR, "h3").text.strip()
                except:
                    title = "Unknown"
                try:
                    authors = result.find_element(By.CSS_SELECTOR, ".app-article-author-list").text.strip()
                except:
                    authors = "Unknown"
                try:
                    year = result.find_element(By.CSS_SELECTOR, ".app-article-meta").text.strip()
                except:
                    year = "Unknown"
                doi = "No DOI"
                try:
                    url_art = result.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                except:
                    url_art = "No URL"
                article = {
                    "Article title": title,
                    "Authors": authors,
                    "Volume year": year,
                    "DOI": doi,
                    "URL": url_art,
                    "Abstract": "N/A",
                    "Journal title": "Nature"
                }
                articles.append(article)
        except Exception as e:
            print("[Selenium Scraper] Nature: Error obteniendo resultados:", e)
    return articles

def save_articles_to_bib(articles, database, term):
    if articles:
        timestamp = int(time.time() * 1000)
        filename = f"{database}_citations_{term.replace(' ', '_')}_{timestamp}.bib"
        filepath = os.path.join(DATA_FOLDER, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            for article in articles:
                bib_entry = make_bib_entry(article)
                f.write(bib_entry)
        print(f"[Selenium Scraper] {database}: {len(articles)} artículos guardados en {filepath}")
    else:
        print(f"[Selenium Scraper] {database}: No se encontraron artículos para el término '{term}'.")

#####################################
# FUNCIÓN PRINCIPAL
#####################################

def main():
    driver = setup_driver()
    
    print("[Portal] Ingresando al portal de la universidad...")
    driver.get(LIBRARY_URL)
    
    db_links = get_database_links(driver)
    print("Enlaces obtenidos desde el portal:", db_links)
    
    for db, base_url in db_links.items():
        for term in SEARCH_TERMS:
            print(f"[{db}] Buscando el término '{term}'...")
            search_database(driver, base_url, db, term)
            time.sleep(3)
            articles = get_articles_selenium(driver, db)
            save_articles_to_bib(articles, db, term)
            time.sleep(2)
    
    driver.quit()

if __name__ == "__main__":
    print("=== Iniciando scraping desde el portal de la universidad y guardado en 'data' ===")
    main()
    print("=== Proceso de scraping finalizado ===")

















