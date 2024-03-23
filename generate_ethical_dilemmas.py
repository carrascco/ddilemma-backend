import re
import openai
import os
import requests

import psycopg2


#------------------------GENERACIÓN DE DILEMAS ÉTICOS------------------------
# Set up your OpenAI API credentials
client = openai.OpenAI(
    api_key=os.environ['OPENAI_API_KEY']
)

def generate_ethical_dilemma(title, body):

    prompt = (
        "Genera un dilema ético a partir de la siguiente noticia:\n\n"
        f"Noticia: {title}\n"
        f"Resumen: {body}\n\n"
        "Dilema: A partir de esta noticia, quiero que plantees un dilema ético o moral que plantee una elección difícil para los personajes involucrados."
         +" No menciones la noticia en el dilema. Este dilema se presentará antes de mostrar la noticia, por lo que no debe contener información específica sobre la noticia."+
         "Debe ser un dilema sensato, realista y con sentido."
    )

    # Call the OpenAI API to generate a dilemma
    chat_completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            # { "role": "system",
            #  "content":""
            #  },
            {
                "role": "user",
                "content": ("Dilema Ético a partir de Titulares de Noticias: "+
                            "A continuación, se presenta una noticia."
                             +" A partir de esta noticia, genera un dilema ético que plantee una elección difícil para los personajes involucrados."+
                              " Considera los diferentes valores, principios y posibles consecuencias de las acciones para crear un escenario moralmente desafiante.  "
                              +prompt)
 
            }]
    )
    # Extract the generated dilemma from the API response
    dilemma_response = chat_completion.choices[0].message.content
    return dilemma_response

def generate_possible_responses(dilemma):
    # Call the OpenAI API to generate a dilemma
    chat_completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                #We are gonna ask ChatGPT to generate from 2 to 5 possible responses to the dilemma in a very concrete way
                "content": ("Genera de 2 a 5 posibles respuestas al siguiente dilema ético: "+dilemma+"\n\n Quiero que cada posible respuesta sea un número seguido de la posible respuesta. Por ejemplo: 1. Respuesta 1. 2. Respuesta 2. 3. Respuesta 3. 4. Respuesta 4.")
            }]
    )

    # Extract the generated dilemma from the API response
    dilemma_response = chat_completion.choices[0].message.content
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

print()

respuestas = generate_possible_responses(dilema)


#------------------------Inserción del dilema en la BBDD------------------------
#      Columna      |            Tipo             | Ordenamiento | Nulable  |             Por omisión
# ------------------+-----------------------------+--------------+----------+-------------------------------------
#  id               | integer                     |              | not null | nextval('dilemas_id_seq'::regclass)
#  contenido        | text                        |              | not null |
#  respuestas       | text[]                      |              | not null |
#  fecha_generacion | timestamp without time zone |              |          | CURRENT_TIMESTAMP
#  id_noticia       | integer                     |              |          |
# Esto es la tabla de dilemas

# Split the responses by a number followed by a dot and a space
respuestas = re.split(r'\d+\. ', respuestas)

# Remove the first element if it's an empty string
if respuestas and not respuestas[0]:
    respuestas = respuestas[1:]

# Remove the last element if it's an empty string
if respuestas and not respuestas[-1]:
    respuestas = respuestas[:-1]

# Prepare the SQL query
insert_query = f"INSERT INTO dilemas (contenido, respuestas, id_noticia) VALUES (%s, %s, %s);"

# Execute the SQL query
cur.execute(insert_query, (dilema, respuestas, noticia[0]))
conn.commit()

#Comprobamos que se ha insertado el dilema      
cur.execute("SELECT * FROM dilemas;")
print("\nDilema introducido correctamente: ", cur.fetchall())

# Cierra el cursor y la conexión
cur.close()
conn.close()


#------------------------RESETEO DE BBDD de VOTOS------------------------
FIREBASE_API_URL=os.environ['FIREBASE_API_URL']



# Se resetean los votos a 0
data = {
    "votosA": 0,
    "votosB": 0,
    "votosC": 0,
    "votosD": 0
}

response = requests.put(FIREBASE_API_URL, json=data)
print(response.json())


#------------------------FIN DE LA EJECUCIÓN------------------------