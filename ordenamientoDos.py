import os
import time
import json
import matplotlib.pyplot as plt

#############################################
# FUNCIÓN PARA LEER DATOS LOCALES (JSON)
#############################################

def read_articles_local():
    """
    Lee el archivo 'processed_articles.json' que se encuentra en la raíz del proyecto.
    Se asume que dicho JSON está al mismo nivel que este script.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_filepath = os.path.join(script_dir, "processed_articles.json")
    
    if not os.path.exists(json_filepath):
        print(f"El archivo {json_filepath} no existe. Verifica el proceso de inserción.")
        return []
    
    with open(json_filepath, "r", encoding="utf-8") as f:
        articles = json.load(f)
    return articles

#############################################
# FUNCIONES PARA CONVERTIR LOS DATOS
#############################################

def process_attribute_data(data):
    """
    Intenta convertir cada elemento a float.
    Si todos pueden convertirse, se utilizarán esos valores (etiqueta "Original");
    de lo contrario, se transforma cada elemento en la suma de los códigos ASCII de sus caracteres
    (etiqueta "SumaASCII").

    Esto permite analizar cualquier tipo de información (texto, numérico, etc.).
    Retorna: (lista_procesada, etiqueta)
    """
    if not data:
        return data, "Sin datos"
    is_numeric = True
    for d in data:
        try:
            float(d)
        except Exception:
            is_numeric = False
            break
    if is_numeric:
        return [float(x) for x in data], "Original"
    else:
        return [sum(ord(c) for c in str(x)) for x in data], "SumaASCII"

#############################################
# FUNCIÓN PARA MEDIR EL TIEMPO DE EJECUCIÓN DE LOS ALGORITMOS
#############################################

def measure_time(algorithm, data):
    """
    Mide el tiempo de ejecución de un algoritmo de ordenamiento aplicado a los datos.
    Retorna el tiempo en milisegundos.
    """
    try:
        start_time = time.time()
        _ = algorithm(data.copy())
        end_time = time.time()
        return (end_time - start_time) * 1000  # Tiempo en ms
    except Exception as e:
        print(f"Error al ejecutar {algorithm.__name__}: {e}")
        return 0

#############################################
# IMPLEMENTACIÓN DE ALGORITMOS DE ORDENAMIENTO
# (Se conservan los 13 originales y se añaden 2 nuevos, totalizando 15)
#############################################

def tim_sort(arr):
    return sorted(arr)

def comb_sort(arr):
    gap = len(arr)
    shrink = 1.3
    sorted_flag = False
    while not sorted_flag:
        gap = int(gap/shrink)
        if gap <= 1:
            gap = 1
            sorted_flag = True
        i = 0
        while i + gap < len(arr):
            if arr[i] > arr[i+gap]:
                arr[i], arr[i+gap] = arr[i+gap], arr[i]
                sorted_flag = False
            i += 1
    return arr

def selection_sort(arr):
    for i in range(len(arr)):
        min_idx = i
        for j in range(i+1, len(arr)):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr

def tree_sort(arr):
    class Node:
        def __init__(self, value):
            self.left = None
            self.right = None
            self.value = value

    def insert(root, node):
        if root is None:
            return node
        if node.value < root.value:
            if root.left is None:
                root.left = node
            else:
                insert(root.left, node)
        else:
            if root.right is None:
                root.right = node
            else:
                insert(root.right, node)
        return root

    def inorder_traversal(root, sorted_arr):
        if root:
            inorder_traversal(root.left, sorted_arr)
            sorted_arr.append(root.value)
            inorder_traversal(root.right, sorted_arr)

    if not arr:
        return arr
    root = Node(arr[0])
    for i in range(1, len(arr)):
        root = insert(root, Node(arr[i]))
    sorted_arr = []
    inorder_traversal(root, sorted_arr)
    return sorted_arr

def pigeonhole_sort(arr):
    min_val = min(arr)
    max_val = max(arr)
    size = int(max_val - min_val + 1)
    holes = [0] * size
    for x in arr:
        holes[int(x - min_val)] += 1
    sorted_arr = []
    for count in range(size):
        while holes[count] > 0:
            sorted_arr.append(count + min_val)
            holes[count] -= 1
    return sorted_arr

def bucket_sort(arr):
    min_val = min(arr)
    max_val = max(arr)
    bucket_count = len(arr)
    buckets = [[] for _ in range(bucket_count)]
    for x in arr:
        bucket_idx = int(bucket_count * (x - min_val) / (max_val - min_val + 1))
        buckets[bucket_idx].append(x)
    for bucket in buckets:
        bucket.sort()
    sorted_arr = []
    for bucket in buckets:
        sorted_arr.extend(bucket)
    return sorted_arr

def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr)//2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)

def heapsort(arr):
    def heapify(arr, n, i):
        largest = i
        l = 2*i + 1
        r = 2*i + 2
        if l < n and arr[l] > arr[largest]:
            largest = l
        if r < n and arr[r] > arr[largest]:
            largest = r
        if largest != i:
            arr[i], arr[largest] = arr[largest], arr[i]
            heapify(arr, n, largest)
    n = len(arr)
    for i in range(n//2 - 1, -1, -1):
        heapify(arr, n, i)
    for i in range(n-1, 0, -1):
        arr[i], arr[0] = arr[0], arr[i]
        heapify(arr, i, 0)
    return arr

def bitonic_sort(arr, up=True):
    def bitonic_merge(A, up):
        if len(A) <= 1:
            return A
        mid = len(A) // 2
        for i in range(mid):
            if (A[i] > A[i+mid]) == up:
                A[i], A[i+mid] = A[i+mid], A[i]
        left = bitonic_merge(A[:mid], up)
        right = bitonic_merge(A[mid:], up)
        return left + right
    if len(arr) <= 1:
        return arr
    else:
        mid = len(arr) // 2
        first = bitonic_sort(arr[:mid], True)
        second = bitonic_sort(arr[mid:], False)
        return bitonic_merge(first + second, up)

def gnome_sort(arr):
    index = 0
    while index < len(arr):
        if index == 0 or arr[index] >= arr[index-1]:
            index += 1
        else:
            arr[index], arr[index-1] = arr[index-1], arr[index]
            index -= 1
    return arr

def binary_insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        left, right = 0, i-1
        while left <= right:
            mid = (left + right) // 2
            if arr[mid] < key:
                left = mid + 1
            else:
                right = mid - 1
        for j in range(i, left, -1):
            arr[j] = arr[j-1]
        arr[left] = key
    return arr

def radix_sort(arr):
    max_val = max(arr)
    exp = 1
    while max_val // exp > 0:
        count_sort(arr, exp)
        exp *= 10
    return arr

def count_sort(arr, exp):
    n = len(arr)
    output = [0] * n
    count = [0] * 10
    for i in range(n):
        index = arr[i] // exp
        count[int(index % 10)] += 1
    for i in range(1, 10):
        count[i] += count[i-1]
    for i in range(n-1, -1, -1):
        index = arr[i] // exp
        output[count[int(index % 10)] - 1] = arr[i]
        count[int(index % 10)] -= 1
    for i in range(n):
        arr[i] = output[i]

def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

# NUEVOS ALGORITMOS

def bidirectional_bubble_sort(arr):
    """
    Burbuja de doble dirección: ordena la lista en ambas direcciones en cada pasada.
    """
    left = 0
    right = len(arr) - 1
    swapped = True
    while swapped:
        swapped = False
        for i in range(left, right):
            if arr[i] > arr[i+1]:
                arr[i], arr[i+1] = arr[i+1], arr[i]
                swapped = True
        right -= 1
        for i in range(right, left, -1):
            if arr[i] < arr[i-1]:
                arr[i], arr[i-1] = arr[i-1], arr[i]
                swapped = True
        left += 1
    return arr

def busrbu_sort(arr):
    """
    Algoritmo de ordenamiento basado en burbuja con variación por pasos de 2 (intercambios en bloques).
    """
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1, 2):  # Intercambia cada 2 elementos
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

#############################################
# GENERACIÓN DE GRÁFICOS
#############################################

def plot_times(algorithms, times, variable, type_label):
    plt.figure(figsize=(10, 6))
    plt.bar(algorithms, times, color='skyblue')
    plt.xlabel('Algoritmos de Ordenamiento')
    plt.ylabel('Tiempo de ejecución (ms)')
    plt.title(f'Comparación de tiempos para {variable} ({type_label})')
    plt.xticks(rotation=45)
    plt.tight_layout()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    results_folder = os.path.join(script_dir, "resultados")
    if not os.path.exists(results_folder):
        os.makedirs(results_folder)
    filename = f"{variable.replace(' ', '_')}.png"
    filepath = os.path.join(results_folder, filename)
    plt.savefig(filepath)
    print(f"Gráfico guardado en: {filepath}")
    
    # Se ha removido plt.show() para evitar que la visualización bloquee la ejecución.
    plt.close()

#############################################
# PROCESO PRINCIPAL
#############################################

def main():
    # Leer el JSON desde la raíz del proyecto
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_filepath = os.path.join(script_dir, "processed_articles.json")
    
    if not os.path.exists(json_filepath):
        print("No se encontraron datos en el archivo processed_articles.json. Verifica el proceso de inserción.")
        return
    
    with open(json_filepath, "r", encoding="utf-8") as f:
        articles_data = json.load(f)
    
    print("Datos extraídos localmente:", len(articles_data))
    if len(articles_data) == 0:
        print("El archivo processed_articles.json está vacío.")
        return

    # Extracción de variables (excluyendo "abstract" para este script)
    variables = {
        'Año': [int(article.get("year", 0)) if str(article.get("year", "0")).isdigit() else 0 for article in articles_data],
        'Author': [article.get("author", "Unknown") for article in articles_data],
        'DOI': [article.get("doi", "Unknown") for article in articles_data],
        'Journal': [article.get("journal", "Unknown") for article in articles_data],
        'Mes': [article.get("month", "Unknown") for article in articles_data],
        'Tipo': [article.get("type", "Unknown") for article in articles_data],
        'Título': [article.get("title", "Unknown") for article in articles_data]
    }

    # Lista de algoritmos (15 en total: 13 originales + 2 nuevos)
    algorithms_list = [
        'TimSort',
        'Comb Sort',
        'Selection Sort',
        'Tree Sort',
        'Pigeonhole Sort',
        'Bucket Sort',
        'Quick Sort',
        'Heap Sort',
        'Bitonic Sort',
        'Gnome Sort',
        'Binary Insertion Sort',
        'Radix Sort',
        'Bubble Sort',
        'Bidirectional Bubble Sort',
        'Busrbu Sort'
    ]

    # Mapeo de nombres a funciones
    algorithms_funcs = {
        'TimSort': tim_sort,
        'Comb Sort': comb_sort,
        'Selection Sort': selection_sort,
        'Tree Sort': tree_sort,
        'Pigeonhole Sort': pigeonhole_sort,
        'Bucket Sort': bucket_sort,
        'Quick Sort': quicksort,
        'Heap Sort': heapsort,
        'Bitonic Sort': bitonic_sort,
        'Gnome Sort': gnome_sort,
        'Binary Insertion Sort': binary_insertion_sort,
        'Radix Sort': radix_sort,
        'Bubble Sort': bubble_sort,
        'Bidirectional Bubble Sort': bidirectional_bubble_sort,
        'Busrbu Sort': busrbu_sort
    }

    for variable, data in variables.items():
        print(f"\nAnalizando variable: {variable} con {len(data)} elementos")
        # Se utiliza la lista completa extraída del JSON para cada atributo
        working_data = data
        processed_data, type_label = process_attribute_data(working_data)
        print(f"Procesado para {variable} ({type_label}): {len(processed_data)} elementos")
        times = []
        for algo_name in algorithms_list:
            function = algorithms_funcs[algo_name]
            time_taken = measure_time(function, processed_data)
            times.append(time_taken)
            print(f"Tiempo de {algo_name} para {variable}: {time_taken:.4f} ms")
        plot_times(algorithms_list, times, variable, type_label)

    print("Proceso completado.")

if __name__ == "__main__":
    main()

