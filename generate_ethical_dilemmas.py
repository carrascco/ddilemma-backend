import openai
import os

import psycopg2


#------------------------GENERACIÓN DE DILEMAS ÉTICOS------------------------
# Set up your OpenAI API credentials
client = openai.OpenAI(
    api_key=os.environ['OPENAI_API_KEY']
)

def generate_ethical_dilemma(title, body):

    # Call the OpenAI API to generate a dilemma
    chat_completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{
                "role": "user",
                "content": ( 
                    "Genera un dilema a partir de la siguiente noticia: \n"+title)
                    #"Título de la noticia: " + title + "Cuerpo de la noticia: " + body+" A partir de esta noticia quiero que me plantees un dilema ético (que sea ciertamente desafiante, y no una pregunta obvia)."
                     #       +" Quiero que tu respuesta sea sólo el Dilema moral."),
            }]
    )

    # Extract the generated dilemma from the API response
    dilemma_response = chat_completion.choices[0].message.content

    print(dilemma_response)
    return dilemma_response

#---------------------------------------------------------------------------
#-----------Conexión a BBDD para extraer noticia y generar dilema-----------
#---------------------------------------------------------------------------
# TABLE noticias (
#     id serial PRIMARY KEY,
#     url text,
#     titulo text NOT NULL,
#     cuerpo text NOT NULL,
#     fuente text,
#     url_imagen text
# );

# Se obtiene la URL de la base de datos de las variables de entorno
DATABASE_URL = os.environ['DATABASE_URL']
# Conexión a la base de datos
conn = psycopg2.connect(DATABASE_URL, sslmode='require')

# Crea un cursor para ejecutar consultas SQL
cur = conn.cursor()

# Seleccionar la última noticia (basandose en el ID que es autoincremental)
cur.execute("SELECT * FROM noticias ORDER BY id DESC LIMIT 1;")
noticia = cur.fetchone()

# Generar el dilema ético
dilema = generate_ethical_dilemma(noticia[2], noticia[3])

# Cierra el cursor y la conexión
cur.close()
conn.close()

#------------------------INSERCIÓN DEL DILEMA EN LA BASE DE DATOS------------------------