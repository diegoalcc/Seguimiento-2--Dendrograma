import os
import json
import re
import string
import numpy as np
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.cluster.hierarchy import dendrogram, linkage

#############################################
# PREPROCESAMIENTO DEL TEXTO
#############################################

def preprocess_text(text):
    """
    Convierte el texto a minúsculas, elimina signos de puntuación y espacios redundantes.
    """
    text = text.lower()
    text = re.sub(r'[' + re.escape(string.punctuation) + ']', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

#############################################
# TF-IDF Y MATRIZ DE DISTANCIAS
#############################################

def compute_distance_matrix(documents):
    """
    Convierte los abstracts a una matriz TF-IDF y calcula la matriz de distancia
    usando similitud coseno (1 - similitud).
    """
    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(documents)
    similarity = cosine_similarity(X)
    distance = 1 - similarity
    return distance

#############################################
# ALGORITMOS DE CLUSTERING JERÁRQUICO
#############################################

def hierarchical_clustering_average(dist_matrix):
    """
    Agrupamiento jerárquico con Average Linkage.
    Calcula la distancia promedio entre los elementos de dos clusters.
    """
    return linkage(dist_matrix, method='average')

def hierarchical_clustering_ward(dist_matrix):
    """
    Agrupamiento jerárquico con Ward Linkage.
    Minimiza la varianza dentro de los clusters.
    """
    return linkage(dist_matrix, method='ward')

#############################################
# GENERACIÓN DE DENDROGRAMAS
#############################################

def plot_dendrogram(linkage_matrix, labels, title, filename):
    """
    Genera y guarda un dendrograma en formato PNG con mejor diseño y etiquetas de texto.
    """
    plt.figure(figsize=(20, 12))
    color_thresh = 0.6 * np.max(linkage_matrix[:, 2])  # Umbral de colores

    dendrogram(
        linkage_matrix,
        labels=labels,  # Usamos los textos preprocesados de los abstracts como etiquetas
        leaf_rotation=90,  # Gira las etiquetas para mejor legibilidad
        leaf_font_size=10,  # Tamaño de fuente para que se vea claro
        color_threshold=color_thresh,
        show_contracted=True,
    )

    plt.title(title, fontsize=18, fontweight='bold')
    plt.xlabel("Abstracts (Preprocesados)", fontsize=14)
    plt.ylabel("Distancia", fontsize=14)
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig(filename)
    print(f"Dendrograma guardado en: {filename}")
    plt.close()

#############################################
# PROCESO PRINCIPAL
#############################################

def main():
    # Leer el JSON generado
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_filepath = os.path.join(script_dir, "processed_articles.json")
    
    if not os.path.exists(json_filepath):
        print("No se encontró el archivo processed_articles.json.")
        return
    
    with open(json_filepath, "r", encoding="utf-8") as f:
        articles_data = json.load(f)
    
    print(f"Número total de artículos: {len(articles_data)}")
    
    # Extraer abstracts y preprocesar
    abstracts = [article.get("abstract", "") for article in articles_data]
    processed_abstracts = [preprocess_text(ab) for ab in abstracts if ab.strip()]

    if not processed_abstracts:
        print("No se encontraron abstracts válidos.")
        return
    
    # Limitar a 100 abstracts
    sample_limit = 100
    if len(processed_abstracts) > sample_limit:
        print(f"Se encontraron {len(processed_abstracts)} abstracts, se usarán solo los primeros {sample_limit}.")
        processed_abstracts = processed_abstracts[:sample_limit]

    # Calcular la matriz de distancia
    dist_matrix = compute_distance_matrix(processed_abstracts)
    
    # Crear carpeta de resultados si no existe
    results_folder = os.path.join(script_dir, "resultados")
    os.makedirs(results_folder, exist_ok=True)

    # Clustering con Average Linkage
    linkage_average = hierarchical_clustering_average(dist_matrix)
    plot_dendrogram(linkage_average, processed_abstracts, "Dendrograma - Average Linkage", os.path.join(results_folder, "dendrogram_average.png"))

    # Clustering con Ward Linkage (Nuevo método)
    linkage_ward = hierarchical_clustering_ward(dist_matrix)
    plot_dendrogram(linkage_ward, processed_abstracts, "Dendrograma - Ward Linkage", os.path.join(results_folder, "dendrogram_ward.png"))

    print("Proceso de clustering y generación de dendrogramas completado.")

if __name__ == "__main__":
    main()
