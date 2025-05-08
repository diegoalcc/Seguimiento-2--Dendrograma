import os
import time
import requests
import csv
import pandas as pd
import bibtexparser
import mysql.connector
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup

#####################################
# CONFIGURACIÓN Y CONSTANTES
#####################################

# Definición de URLs base para cada base de datos
BASE_URLS = {
    "IEEE": "https://ieeexplore.ieee.org/search/searchresult.jsp?queryText=",
    "ScienceDirect": "https://www.sciencedirect.com/search?qs=",
    "Nature": "https://www.nature.com/search?q="
}
# Términos a buscar:
SEARCH_TERMS = ["Computational Thinking", "Abstraction"]

# Carpeta para almacenar archivos CSV y BibTeX
DATA_FOLDER = os.path.join(os.getcwd(), "data")
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

# Session global para Requests (para preservar cookies, etc.)
session = requests.Session()

#####################################
# STEP 1: SCRAPING
#####################################

def get_articles(database, search_term):
    """
    Realiza la búsqueda en la base de datos indicada para el término dado y
    extrae información relevante. Retorna una lista de diccionarios.
    """
    url = BASE_URLS[database] + search_term.replace(" ", "+")
    # Headers para simular un navegador real
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/115.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": url
    }
    
    print(f"[Scraping] Accediendo a: {url}")
    response = session.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Error accediendo a {database} para el término '{search_term}': {response.status_code}")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    articles = []
    
    if database == "IEEE":
        results = soup.select(".List-results-item")
        for result in results:
            title_tag = result.find("a")
            title = title_tag.text.strip() if title_tag else "Unknown"
            authors_tag = result.find("p", class_="author")
            authors = authors_tag.text.strip() if authors_tag else "Unknown"
            year_tag = result.find("div", class_="publisher-info-container")
            year = year_tag.text.strip() if year_tag else "Unknown"
            doi_tag = result.find("a", href=lambda href: href and "doi.org" in href)
            doi = doi_tag.get("href") if doi_tag else "No DOI"
            url_tag = result.find("a")
            url_result = url_tag.get("href") if url_tag else "No URL"
            abstract = "N/A"
            articles.append({
                "Article title": title,
                "Authors": authors,
                "Volume year": year,
                "DOI": doi,
                "URL": url_result,
                "Abstract": abstract,
                "Journal title": "IEEE"
            })
    
    elif database == "ScienceDirect":
        results = soup.select(".ResultItem")
        for result in results:
            title_tag = result.find("h2")
            title = title_tag.text.strip() if title_tag else "Unknown"
            authors_tag = result.find("span", class_="Authors")
            authors = authors_tag.text.strip() if authors_tag else "Unknown"
            year_tag = result.find("span", class_="PublicationDate")
            year = year_tag.text.strip() if year_tag else "Unknown"
            doi = "No DOI"  # ScienceDirect a veces no muestra el DOI directamente.
            url_tag = result.find("a")
            url_result = url_tag.get("href") if url_tag else "No URL"
            abstract = "N/A"
            articles.append({
                "Article title": title,
                "Authors": authors,
                "Volume year": year,
                "DOI": doi,
                "URL": url_result,
                "Abstract": abstract,
                "Journal title": "ScienceDirect"
            })
    
    elif database == "Nature":
        results = soup.select(".app-article-item")
        for result in results:
            title_tag = result.find("h3")
            title = title_tag.text.strip() if title_tag else "Unknown"
            authors_tag = result.find("ul", class_="app-article-authors")
            authors = authors_tag.text.strip() if authors_tag else "Unknown"
            meta_tag = result.find("div", class_="app-article-meta")
            year = meta_tag.text.strip() if meta_tag else "Unknown"
            doi = "No DOI"
            url_tag = result.find("a")
            url_result = url_tag.get("href") if url_tag else "No URL"
            abstract = "N/A"
            articles.append({
                "Article title": title,
                "Authors": authors,
                "Volume year": year,
                "DOI": doi,
                "URL": url_result,
                "Abstract": abstract,
                "Journal title": "Nature"
            })
    
    return articles

def run_scraper():
    """
    Ejecuta el proceso de scraping en las tres bases de datos para los términos
    designados y retorna la lista completa de artículos.
    """
    all_articles = []
    for database in BASE_URLS.keys():
        for term in SEARCH_TERMS:
            print(f"[Scraping] Buscando en {database} con el término '{term}'...")
            articles = get_articles(database, term)
            all_articles.extend(articles)
            time.sleep(2)  # Pausa para evitar saturar el servidor
    print(f"[Scraping] Se encontraron un total de {len(all_articles)} artículos.")
    return all_articles

def save_csv(data, filename="scraped_articles.csv"):
    """
    Guarda la información extraída en un archivo CSV.
    """
    if not data:
        print("No hay datos para guardar en CSV.")
        return None
    csv_path = os.path.join(DATA_FOLDER, filename)
    keys = data[0].keys()
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        dict_writer = csv.DictWriter(f, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)
    print(f"[CSV] Datos guardados en: {csv_path}")
    return csv_path

#####################################
# STEP 2: CONVERTIR CSV A BIBTEX
#####################################

def csv_to_bibtex(csv_file_path, bibtex_file_path):
    df = pd.read_csv(csv_file_path)
    with open(bibtex_file_path, mode="w", encoding="utf-8") as bib_file:
        for index, row in df.iterrows():
            authors = row["Authors"] if isinstance(row["Authors"], str) else "Unknown"
            year = row["Volume year"] if not pd.isna(row["Volume year"]) else "UnknownYear"
            bib_key = f"{authors.split(' ')[0]}{year}".replace(" ", "") if isinstance(authors, str) else f"Unknown{year}"
            bib_file.write(f"@article{{{bib_key},\n")
            bib_file.write(f"  author = {{{authors}}},\n")
            bib_file.write(f"  title = {{{row['Article title']}}},\n")
            bib_file.write(f"  year = {{{year}}},\n")
            if "Journal title" in row and pd.notna(row["Journal title"]):
                bib_file.write(f"  journal = {{{row['Journal title']}}},\n")
            if "DOI" in row and pd.notna(row["DOI"]):
                bib_file.write(f"  doi = {{{row['DOI']}}},\n")
            if "URL" in row and pd.notna(row["URL"]):
                bib_file.write(f"  url = {{{row['URL']}}},\n")
            bib_file.write("}\n\n")
    print(f"[Convert] Archivo BibTeX generado: {bibtex_file_path}")

#####################################
# STEP 3: UNIFICACIÓN Y DUPLICADOS
#####################################

def load_bibtex_file(file_path):
    with open(file_path, encoding="utf-8") as bibtex_file:
        bib_database = bibtexparser.load(bibtex_file)
    return bib_database.entries

def separate_duplicates(entries):
    unique_entries = {}
    duplicate_entries = []
    for entry in entries:
        key = entry.get("doi", entry.get("title", "") + entry.get("author", ""))
        if key in unique_entries:
            duplicate_entries.append(entry)
        else:
            unique_entries[key] = entry
    return list(unique_entries.values()), duplicate_entries

def unify_bibtex_files(data_folder):
    all_entries = []
    for filename in os.listdir(data_folder):
        if filename.endswith(".bib"):
            file_path = os.path.join(data_folder, filename)
            print(f"[Unify] Cargando archivo BibTeX: {filename}")
            entries = load_bibtex_file(file_path)
            all_entries.extend(entries)
    print("[Unify] Identificando duplicados...")
    unique_entries, duplicate_entries = separate_duplicates(all_entries)
    bib_db_unique = bibtexparser.bibdatabase.BibDatabase()
    bib_db_unique.entries = unique_entries
    output_unique_path = os.path.join(data_folder, "unified_references.bib")
    writer = bibtexparser.bwriter.BibTexWriter()
    with open(output_unique_path, "w", encoding="utf-8") as output_file:
        output_file.write(writer.write(bib_db_unique))
    
    if duplicate_entries:
        bib_db_duplicates = bibtexparser.bibdatabase.BibDatabase()
        bib_db_duplicates.entries = duplicate_entries
        output_duplicates_path = os.path.join(data_folder, "duplicated_references.bib")
        with open(output_duplicates_path, "w", encoding="utf-8") as output_file:
            output_file.write(writer.write(bib_db_duplicates))
        print(f"[Unify] Archivo con duplicados generado: {output_duplicates_path}")
    else:
        print("[Unify] No se encontraron artículos duplicados.")
    
    print(f"[Unify] Unificación completada. Archivo generado: {output_unique_path}")
    return output_unique_path

#####################################
# STEP 4: INSERTAR BIBTEX EN LA BASE DE DATOS
#####################################

def connect_to_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="articles_db"
        )
        return conn
    except mysql.connector.Error as err:
        print("Error en la conexión a la base de datos:", err)
        return None

def insert_article(cursor, article):
    sql = """INSERT INTO articles 
    (abstract, author, doi, issn, journal, keywords, month, note, number, pages, title, type, url, volume, year) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    values = (
        article.get("abstract", "Unknown"),
        article.get("author", "Unknown"),
        article.get("doi", "Unknown"),
        article.get("issn", "Unknown"),
        article.get("journal", "Unknown"),
        article.get("keywords", "Unknown"),
        article.get("month", "Unknown"),
        article.get("note", "Unknown"),
        article.get("number", "Unknown"),
        article.get("pages", "Unknown"),
        article.get("title", "Unknown"),
        article.get("type", "Unknown"),
        article.get("url", "Unknown"),
        article.get("volume", "Unknown"),
        int(article.get("year", "0")) if str(article.get("year", "0")).isdigit() else 0
    )
    cursor.execute(sql, values)

def insert_bibtex_to_db(bibtex_file_path):
    with open(bibtex_file_path, encoding="utf-8") as bibtex_file:
        bib_db = bibtexparser.load(bibtex_file)
    conn = connect_to_db()
    if not conn:
        print("[Insert] No se pudo conectar a la base de datos.")
        return
    cursor = conn.cursor()
    for entry in bib_db.entries:
        insert_article(cursor, entry)
    conn.commit()
    cursor.close()
    conn.close()
    print("[Insert] Artículos almacenados en la base de datos.")

#####################################
# STEP 5: ANÁLISIS Y VISUALIZACIONES
#####################################

def analyze_data():
    conn = connect_to_db()
    if not conn:
        print("[Analyze] No se pudo conectar a la base de datos para análisis.")
        return
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM articles")
    articles_data = cursor.fetchall()
    cursor.close()
    conn.close()
    
    if not articles_data:
        print("[Analyze] No se encontraron artículos para analizar.")
        return

    try:
        years = [int(article["year"]) for article in articles_data if str(article["year"]).isdigit()]
        if years:
            plt.figure(figsize=(10,6))
            plt.hist(years, bins=range(min(years), max(years)+2), color="skyblue", edgecolor="black")
            plt.xlabel("Año de publicación")
            plt.ylabel("Número de artículos")
            plt.title("Distribución de artículos por año")
            plt.show()
        else:
            print("[Analyze] No hay datos numéricos de año para analizar.")
    except Exception as e:
        print("[Analyze] Error durante la generación de la gráfica:", e)

#####################################
# MAIN: PIPELINE INTEGRADO
#####################################

def main_pipeline():
    # STEP 1: Scraping y guardado a CSV
    print("=== Iniciando Scraping de artículos ===")
    scraped_articles = run_scraper()
    csv_path = save_csv(scraped_articles, "scraped_articles.csv")
    if not csv_path:
        return
    
    # STEP 2: Conversión de CSV a BibTeX
    bibtex_path = os.path.join(DATA_FOLDER, "converted_articles.bib")
    csv_to_bibtex(csv_path, bibtex_path)
    
    # STEP 3: Unificación de archivos BibTeX (incluyendo los convertidos)
    unified_bibtex_path = unify_bibtex_files(DATA_FOLDER)
    
    # STEP 4: Inserción en la Base de Datos
    insert_bibtex_to_db(unified_bibtex_path)
    
    # STEP 5: Análisis y Visualización
    analyze_data()
    
    print("=== Pipeline ejecutado exitosamente ===")

if __name__ == "__main__":
    main_pipeline()
