import psycopg2
import os
import requests
from eventregistry import *
from transformers import pipeline

# Cargar el modelo de clasificación de texto preentrenado
classifier = pipeline("zero-shot-classification")


#Definimos la lista de noticias
news = []

# Función para extraer las noticias de España y analizar su componente de ethic
def extract_news_and_analyze():
    
     er = EventRegistry(apiKey = os.environ['NEWS_API_KEY'])
     today = datetime.datetime.now().isoformat().split('T')[0]
     query = {
        "$query": {
            "$and": [
            {
                 "$or": [
                        {
                            "sourceUri": "elpais.com"
                        },
                        {
                            "sourceUri": "elmundo.es"
                        },
                        {
                            "sourceUri": "larazon.es"
                        },
                        {
                            "sourceUri": "lavanguardia.com"
                        },
                        {
                            "sourceUri": "abc.es"
                        }
                        # ,
                        # {
                        #     "sourceUri": "20minutos.es"
                        # }
                    ]          
            },
            {
                "dateStart": today,
                "dateEnd": today,
                "lang": "spa"
            }
            ]
        }
        }
     q = QueryArticlesIter.initWithComplexQuery(query)
    
     for article in q.execQuery(er, maxItems=180):
    # Guarda las noticias en una lista de diccionarios
        titulo=article['title']
        news.append({
            'title': titulo,
            'source': article['source']['title'],
            'body': article['body'],
            # Cada noticia del diccionario tiene adjunto sus puntajes de categoría
            'health': classifier(titulo, candidate_labels=["salud"])['scores'][0],
            'human rights': classifier(titulo, candidate_labels=["derechos humanos"])['scores'][0],
            'judicial': classifier(titulo, candidate_labels=["judicial"])['scores'][0],
            'politics': classifier(titulo, candidate_labels=["política"])['scores'][0],
            'crime': classifier(titulo, candidate_labels=["crimen"])['scores'][0],

            'url': article['url'],
            'imageURL': article['image']
        })





extract_news_and_analyze()

# Hace un nuevo diccionario con las noticias que tienen mayor componente de cada categoría
news_with_highest_component = {
    'health': max(news, key=lambda x: x['health']),
    'human rights': max(news, key=lambda x: x['human rights']),
    'judicial': max(news, key=lambda x: x['judicial']),
    'politics': max(news, key=lambda x: x['politics']),
    'crime': max(news, key=lambda x: x['crime'])
}

# La API de OpenAI elige la más adecuada para generar un dilema ético
import openai 

client = openai.OpenAI(
    api_key=os.environ['OPENAI_API_KEY']
)
chat_completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            
            {
                "role": "user",
                "content": ("Te voy a dar 5 noticias, pensando en posibles dilemas éticos que se puedan sintetizar a partir de cada una"
                +   " tienes que elegir la más propensa o favorable para generar un dilema ético. ¿Cuál eliges?"
                +   f"1. {news_with_highest_component['health']['title']}\n"
                +   f"2. {news_with_highest_component['human rights']['title']}\n"
                +   f"3. {news_with_highest_component['judicial']['title']}\n"
                +   f"4. {news_with_highest_component['politics']['title']}\n"
                +   f"5. {news_with_highest_component['crime']['title']}\n"
                +   "Escribe consistentemente el número de la noticia que elijas. Sin explicaciones."
                    )
            }]
    )
selection_response = chat_completion.choices[0].message.content
print(selection_response)

selected_num=selection_response.split()[0]

selected_news = news_with_highest_component['health']
if selected_num == "2.":
    selected_news = news_with_highest_component['human rights']
elif selected_num == "3.":
    selected_news = news_with_highest_component['judicial']
elif selected_num == "4.":
    selected_news = news_with_highest_component['politics']
elif selected_num == "5.":
    selected_news = news_with_highest_component['crime']


# # Imprime las 5 noticias con mayor componente ethic
# news.sort(key=lambda x: x['ethic'], reverse=True)
# for i in range(5):
#     print(f"La noticia {i+1} es: {news[i]['title']}, con un componente ethic de {news[i]['ethic']}")
#     print(f"La fuente de la noticia es: {news[i]['source']}")
#     print("-----------------------------------------------------------------")

#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
#------------------------CONEXIÓN A LA BASE DE DATOS------------------------
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import datetime

# Initialize the Firebase SDK

cred = credentials.Certificate( "cred.json" )
firebase_admin.initialize_app(cred)



# Access the Firestore database
db = firestore.client()

noticia = selected_news

noticia_data = {
    "cuerpo": noticia['body'],
    "fuente": noticia['source'],
    "titulo": noticia['title'],
    "url": noticia['url'],
    "url_imagen": noticia['imageURL']
}
print(noticia_data)

timestamp = (datetime.datetime.now() + datetime.timedelta(hours=1)).isoformat()

# Convert the timestamp to string
timestamp_str = str(timestamp)

# Capture the result
try:
    result = db.collection("noticias").document(timestamp_str).set(noticia_data)
    print(result)
except Exception as e:
    print("EXCEPCION: "+e)

# # TABLE noticias (
# #     id serial PRIMARY KEY,
# #     url text,
# #     titulo text NOT NULL,
# #     cuerpo text NOT NULL,
# #     fuente text,
# #     url_imagen text
# # );
# # Esta es la tabla de noticias

# # Se obtiene la URL de la base de datos de las variables de entorno
# DATABASE_URL = os.environ['DATABASE_URL']
# # Conexión a la base de datos
# conn = psycopg2.connect(DATABASE_URL, sslmode='require')

# # Crea un cursor para ejecutar consultas SQL
# cur = conn.cursor()

# # Nos disponemos a insertar la primera noticia en la base de datos
# noticia = news[0]
# insert_query = f"INSERT INTO noticias (url, titulo, cuerpo, fuente, url_imagen) VALUES ('{noticia['url']}', '{noticia['title']}', '{noticia['body']}', '{noticia['source']}', '{noticia['imageURL']}');"

# # Ejecuta la consulta SQL para visualizar la tabla de noticias
# cur.execute(insert_query)
# conn.commit()

# #Comprobamos que se ha insertado la noticia
# cur.execute("SELECT * FROM noticias;")

# print("\nNoticia introducida correctamente: ", cur.fetchall())

# # Cierra el cursor y la conexión
# cur.close()
# conn.close()
