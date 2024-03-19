from transformers import pipeline

# Cargar el modelo de clasificación de texto preentrenado
classifier = pipeline("zero-shot-classification")

# Texto que deseas clasificar
texto = "La tasa de desempleo alcanza un máximo de cinco años en medio de la desaceleración económica"

# Categoría que deseas evaluar
categoria = "económico"

# Realizar la clasificación
resultado = classifier(texto, candidate_labels=[categoria])

# Mostrar el resultado
print(f"Sentimiento económico del texto: {resultado['scores'][0]}")
