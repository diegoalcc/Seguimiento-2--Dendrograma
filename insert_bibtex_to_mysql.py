import os
import json
import bibtexparser

#############################################
# FUNCIONES DE PROCESAMIENTO
#############################################

def load_bibtex_file(file_path):
    """
    Carga el archivo BibTeX y devuelve una lista de entradas.
    """
    try:
        with open(file_path, encoding='utf-8') as bibtex_file:
            content = bibtex_file.read()
            # Para depurar, puedes imprimir el contenido
            # print("Contenido del archivo BibTeX:")
            # print(content)
            bib_database = bibtexparser.loads(content)
        return bib_database.entries
    except Exception as e:
        print("Error al cargar el archivo BibTeX:", e)
        return []

def process_articles(entries):
    """
    Procesa cada entrada del archivo BibTeX y extrae los atributos necesarios.
    """
    processed = []
    for entry in entries:
        article = {
            "abstract": entry.get("abstract", "Unknown"),
            "author": entry.get("author", "Unknown"),
            "doi": entry.get("doi", "Unknown"),
            "issn": entry.get("issn", "Unknown"),
            "journal": entry.get("journal", "Unknown"),
            "keywords": entry.get("keywords", "Unknown"),
            "month": entry.get("month", "Unknown"),
            "note": entry.get("note", "Unknown"),
            "number": entry.get("number", "Unknown"),
            "pages": entry.get("pages", "Unknown"),
            "title": entry.get("title", "Unknown"),
            "type": entry.get("ENTRYTYPE", "Unknown"),  # Por ejemplo: article, inproceedings, etc.
            "url": entry.get("url", "Unknown"),
            "volume": entry.get("volume", "Unknown"),
            "year": entry.get("year", "Unknown")
        }
        processed.append(article)
    return processed

def save_processed_articles(processed_data, output_file):
    """
    Guarda los artículos procesados en un archivo JSON.
    """
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(processed_data, f, indent=4)
        print("Los artículos han sido procesados y guardados en", output_file)
    except Exception as e:
        print("Error al guardar el archivo JSON:", e)

#############################################
# PROCESO PRINCIPAL
#############################################

if __name__ == "__main__":
    # Ruta al archivo BibTeX unificado. Ajusta según corresponda.
    bibtex_file_path = r'C:\Users\Brandon\OneDrive\ANALISIS DE ALGOTIMOS\seg 1 analisis de algoritmos\AlgoritmosBr\Algoritmos\ws_proyectoAlgoritmos\data\unified_references.bib'
    
    print("Cargando el archivo BibTeX unificado...")
    entries = load_bibtex_file(bibtex_file_path)
    print(f"Entradas cargadas: {len(entries)}")
    
    if len(entries) == 0:
        print("No se encontraron entradas en el archivo BibTeX. Verifica su contenido.")
    else:
        print("Procesando los artículos y extrayendo atributos...")
        processed = process_articles(entries)
    
        # Guardamos el JSON en la raíz del proyecto (al mismo nivel que la carpeta "data")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_file = os.path.join(script_dir, "processed_articles.json")
        save_processed_articles(processed, output_file)
    
    print("Proceso finalizado. Los artículos se han procesado sin conectarse a ninguna base de datos.")

