import os
import pandas as pd

# Carpeta donde están los archivos CSV
folder_path = 'C:\proyectoAlgoritmos\ws_proyectoAlgoritmos\data' 

# Función para convertir un CSV a BibTeX
def csv_to_bibtex(csv_file_path, bibtex_file_path): 
    # Cargar el archivo CSV
    df = pd.read_csv(csv_file_path)
    
    # Abrir el archivo BibTeX para escribir en UTF-8
    with open(bibtex_file_path, mode='w', encoding='utf-8') as bib_file:
        for index, row in df.iterrows():
            # Asegurarnos de que el campo Authors es una cadena y no es nulo
            authors = row['Authors'] if isinstance(row['Authors'], str) else "Unknown"
            year = row['Volume year'] if not pd.isna(row['Volume year']) else "Unknown Year"
            
            # Generar clave única para la entrada BibTeX (usamos el primer apellido del autor y el año)
            bib_key = f"{authors.split(' ')[0]}{year}".replace(" ", "") if isinstance(authors, str) else f"Unknown{year}"
            
            # Escribir la entrada en el archivo BibTeX
            bib_file.write(f"@article{{{bib_key},\n")
            bib_file.write(f"  author = {{{authors}}},\n")
            bib_file.write(f"  title = {{{row['Article title']}}},\n")
            bib_file.write(f"  year = {{{year}}},\n")
            
            if 'Journal title' in row and pd.notna(row['Journal title']):
                bib_file.write(f"  journal = {{{row['Journal title']}}},\n")
            
            if 'DOI' in row and pd.notna(row['DOI']):
                bib_file.write(f"  doi = {{{row['DOI']}}},\n") 
            
            if 'URL' in row and pd.notna(row['URL']):
                bib_file.write(f"  url = {{{row['URL']}}},\n")
            
            bib_file.write("}\n\n")

# Recorrer la carpeta en busca de archivos CSV
for filename in os.listdir(folder_path):
    if filename.endswith(".csv"):
        csv_file_path = os.path.join(folder_path, filename)
        bibtex_file_path = os.path.join(folder_path, filename.replace(".csv", ".bib"))
        # Convertir el archivo CSV a BibTeX
        csv_to_bibtex(csv_file_path, bibtex_file_path)

print("Conversion completada.")