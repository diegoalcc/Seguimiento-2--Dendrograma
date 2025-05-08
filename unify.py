import os
import bibtexparser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase

# Carpeta que contiene los archivos BibTeX
folder_path = 'D:/td/2025-1/Algoritmos/ws_proyectoAlgoritmos/data'

def load_bibtex_file(file_path):
    """
    Carga un archivo BibTeX y devuelve sus entradas.
    """
    with open(file_path, encoding='utf-8') as bibtex_file:
        bib_database = bibtexparser.load(bibtex_file)
    return bib_database.entries

def separate_duplicates(entries):
    """
    Identifica entradas duplicadas y separa las únicas de las repetidas.
    """
    unique_entries = {}
    duplicate_entries = []
    
    for entry in entries:
        key = entry.get('doi', (entry.get('title', '') + entry.get('author', '')))
        if key in unique_entries:
            duplicate_entries.append(entry)  # Si ya existe, se considera duplicado
        else:
            unique_entries[key] = entry
    
    return list(unique_entries.values()), duplicate_entries

# Cargar todos los archivos BibTeX en la carpeta
all_entries = []
for filename in os.listdir(folder_path):
    if filename.endswith(".bib"):
        file_path = os.path.join(folder_path, filename)
        print(f"Cargando {filename}...")
        entries = load_bibtex_file(file_path)
        all_entries.extend(entries)

# Separar entradas únicas y duplicadas
print("Identificando duplicados...")
unique_entries, duplicate_entries = separate_duplicates(all_entries)

# Guardar las entradas únicas en un nuevo archivo BibTeX
bib_db_unique = BibDatabase()
bib_db_unique.entries = unique_entries
output_unique_path = os.path.join(folder_path, 'unified_references.bib')

writer = BibTexWriter()
with open(output_unique_path, 'w', encoding='utf-8') as output_file:
    output_file.write(writer.write(bib_db_unique))

# Guardar los artículos duplicados en un archivo separado
if duplicate_entries:
    bib_db_duplicates = BibDatabase()
    bib_db_duplicates.entries = duplicate_entries
    output_duplicates_path = os.path.join(folder_path, 'duplicated_references.bib')
    with open(output_duplicates_path, 'w', encoding='utf-8') as output_file:
        output_file.write(writer.write(bib_db_duplicates))
    print(f"Archivo con duplicados generado: {output_duplicates_path}")
else:
    print("No se encontraron artículos duplicados.")

print(f"Unificación completada. Archivo generado: {output_unique_path}")