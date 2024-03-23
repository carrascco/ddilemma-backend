import psycopg2
import os
import requests
from eventregistry import *
from transformers import pipeline

# Cargar el modelo de clasificación de texto preentrenado
classifier = pipeline("zero-shot-classification")
categoria = "social"


#Definimos la lista de noticias
news = []

# Función para extraer las noticias de El Mundo y analizar su componente de social
def extract_news_and_analyze():
    
     er = EventRegistry(apiKey = os.environ['NEWS_API_KEY'])
    #  today = datetime.datetime.now().isoformat().split('T')[0]
     query = {
        "$query": {
            "$and": [
            {
                "locationUri": "http://en.wikipedia.org/wiki/Spain"
            },
            {
                "sourceLocationUri": "http://en.wikipedia.org/wiki/Spain"
            },
            {
                "dateStart": "2024-03-22",
                "dateEnd": "2024-03-22",
                "lang": "spa"
            }
            ]
        }
        }
     q = QueryArticlesIter.initWithComplexQuery(query)
    
     for article in q.execQuery(er, maxItems=70):
    # Guarda las noticias en una lista de diccionarios
        texto=article['body']
        news.append({
            'title': article['title'],
            'source': article['source']['title'],
            'body': texto,
            'social': classifier(texto, candidate_labels=[categoria])['scores'][0],
            'url': article['url'],
            'imageURL': article['image']
        })





extract_news_and_analyze();

#Mostrar las 5 noticias con mayor componente social
news.sort(key=lambda x: x['social'], reverse=True)
for i in range(5):
    print(f"La noticia {i+1} es: {news[i]['title']}, con un componente social de {news[i]['social']}")
    print(f"La fuente de la noticia es: {news[i]['source']}")
    print("-----------------------------------------------------------------")











#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
#------------------------CONEXIÓN A LA BASE DE DATOS------------------------
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------


# TABLE noticias (
#     id serial PRIMARY KEY,
#     url text,
#     titulo text NOT NULL,
#     cuerpo text NOT NULL,
#     fuente text,
#     url_imagen text
# );
# INSERT INTO noticias (url, titulo, cuerpo, fuente, url_imagen) VALUES ('https://www.ejemplo.com/noticia-1', 'Título de la noticia 1', 'Contenido de la noticia 1', 'Fuente de la noticia 1', 'https://www.ejemplo.com/imagen-1.jpg');
# Así se inserta una noticia en la tabla de noticias
#Esta es la tabla de noticias

# Se obtiene la URL de la base de datos de las variables de entorno
DATABASE_URL = os.environ['DATABASE_URL']
# Conexión a la base de datos
conn = psycopg2.connect(DATABASE_URL, sslmode='require')

# Crea un cursor para ejecutar consultas SQL
cur = conn.cursor()

# Nos disponemos a insertar la primera noticia en la base de datos
noticia = news[0]
insert_query = f"INSERT INTO noticias (url, titulo, cuerpo, fuente, url_imagen) VALUES ('{noticia['url']}', '{noticia['title']}', '{noticia['body']}', '{noticia['source']}', '{noticia['imageURL']}');"

# Ejecuta la consulta SQL para visualizar la tabla de noticias
cur.execute(insert_query)
conn.commit()

#Comprobamos que se ha insertado la noticia
cur.execute("SELECT * FROM noticias;")

print("\nNoticia introducida correctamente: ", cur.fetchall())

# Cierra el cursor y la conexión
cur.close()
conn.close()
