import datetime
import re
import openai
import os
import requests

import psycopg2


#------------------------GENERACIÓN DE DILEMAS ÉTICOS------------------------
# Credenciales de OpenAi
client = openai.OpenAI(
    api_key=os.environ['OPENAI_API_KEY']
)

def generate_ethical_dilemma(title, body):

    prompt = (
        "Quiero que generes un dilema ético a partir de la siguiente noticia:\n\n"
        f"Titular: {title}\n"
        f"Resumen: {body}\n\n\n\n"
        "Dilema: A partir de esta noticia, quiero que plantees un dilema ético o moral. Quiero que seas consciente de que el usuario verá el dilema que presentes, y después la noticia (por lo que el contenido del dilema debe ser comprensible sin necesidad de leer la noticia)."
         +" No menciones la noticia en el dilema. Puedes mencionar los hechos (si conviene, también puedes explicar la situación sin concretar demasiado) pero sin dar nombres (a no ser que sea necesario para que el dilema tenga sentido)."+
         "Debe ser un dilema sensato, realista y con sentido (no algo obvio y evidente). Máximo 150 palabras. \n" 
         +"El dilema debe estar fuertemente relacionado con el titular (para encontrar el mejor dilema posible puedes utilizar la noticia entera, o únicamente lo que se declara en el titular, si crees que va a dar un mejor resultado)."+
          " Enuncia el dilema directamente. Debe ser claro y conciso, exponiendo el único dilema, sin divagar en opciones y preguntas. \n"
    )

    # Llama a la API de OpenAI para generar un dilema
    chat_completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            
            {
                "role": "user",
                "content": (prompt+
                              " Considera los diferentes valores, principios y posibles consecuencias de las acciones para crear un escenario moralmente desafiante, creando un dilema en base a los hechos.\n"+
                              "No quiero un dilema que sea obvia la elección o fácil de resolver (reduciendo al absurdo, no quiero dilemas del estilo 'es ético matar?' o 'es ético vestir lo que uno quiere?')"
                               +". Quiero un dilema que haga pensar y que no tenga una respuesta clara. Por ello, analiza bien el dilema más confrontante que puedas generar." 
                               +"Por favor, antes de enviar el dilema, analizalo y piensa si es evidente, tonto u obvio, y evita que así sea. Tomando en cuenta la cultura occidental, no quiero que sea un dilema obvio (contando con los valores occidentales)\n"+
                               " Es decir, el dilema debe respetar los derechos humanos y valores evidentes, evitando caer en preguntas de respuesta muy obvia para el lector."
                              )
 
            }]
    )
    print(prompt)
    # Extrae el dilema generado de la respuesta de la API
    dilemma_response = chat_completion.choices[0].message.content
    return dilemma_response

def generate_possible_responses(dilemma):
    # Llama a la API de OpenAI para generar posibles respuestas al dilema
    chat_completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                
                "content": (
    "Genera de 2 a 3 posibles respuestas al siguiente dilema ético: "
    +dilemma+"\n Debes ofrecer respuestas distintas, sensatas y contundentes en base al dilema planteado."
     +
      " Cada respuesta debe representar un punto de vista único e incompatible con las demás. No quiero que las respuestas sean largas, quiero que sean concisas, sin extenderse, que sean de pocas palabras (a no ser que sea necesario una mini explicación)."
    +"\n Quiero que cada posible respuesta sea un número seguido de la posible respuesta."+
     " Por ejemplo: 1. {Respuesta 1}.\n 2. {Respuesta 2}.\n 3. {Respuesta 3}. \n\n\n Recuerda que cada respuesta debe ser única y diferente a las demás."
     +" Puede haber hasta 3 respuestas, pero no tiene porque ser necesariamente 3. Sólo las necesarias para responder al dilema, ya sean 2 o 3. "+
     "Importante: no quiero dos respuestas que representen el mismo punto de vista o parecido."+" Evita respuestas ambiguas o genéricas. Tampoco quiero respuestas ABIERTAS, ni de \"depende\". Evita también respuestas intermedias. Las respuestas deben representar las distintas opciones del dilema")
            }]
    )

    # Extrae las posibles respuestas generadas de la respuesta de la API
    dilemma_response = chat_completion.choices[0].message.content
    return dilemma_response

#------------------------CONEXIÓN A LA BASE DE DATOS------------------------

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate( "cred.json" )
firebase_admin.initialize_app(cred)

# Access the Firestore database
db = firestore.client()
# Access the noticias collection
noticias_ref = db.collection('noticias')
# Get all documents in the noticias collection
noticias_docs = noticias_ref.get()
# Get the first element
last_doc = noticias_docs[-1]


# Access the data of the last document
noticia = last_doc.to_dict()


# Generar el dilema ético

dilema = generate_ethical_dilemma(noticia['titulo'], noticia['cuerpo'])

print()

respuestas = generate_possible_responses(dilema)



# Extraer las posibles respuestas
respuestas = re.split(r'\d+\. ', respuestas)

# Eliminar las respuestas vacías
if respuestas and not respuestas[0]:
    respuestas = respuestas[1:]

# Eliminar la última respuesta si está vacía
if respuestas and not respuestas[-1]:
    respuestas = respuestas[:-1]

timestamp = (datetime.datetime.now() 
             + datetime.timedelta(hours=1)
             ).isoformat()

# Convert the timestamp to string
timestamp_str = str(timestamp)

dilema_data = {
    "contenido": dilema,
    "respuestas": respuestas,
    "id_noticia": last_doc.id,
    "fecha_generacion": timestamp_str,
    "votos": [0,0,0,0]
}
try:

    result = db.collection("dilemas").document(timestamp_str).set(dilema_data)
    print(result.transform_results)
    print(result.transform_results.count)
    # Create a collection "comentarios" inside the document
    comentarios_ref = db.collection('dilemas').document(timestamp_str).collection('comentarios')
except Exception as e:
    print("Error al insertar datos en Firebase:", e)

