import os
import json
import csv
import os
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    text: str
    user_id: str

user_states = {}

products = [
    {
        "name": "Rosas Premium",
        "price": "$95.000",
        "description": "12 rosas rojas con envoltura elegante.",
        "image": "images/rosas.jpg"
    },
    {
        "name": "Girasoles Elegantes",
        "price": "$120.000",
        "description": "Arreglo vibrante con girasoles y follaje decorativo.",
        "image": "images/girasoles.jpg"
    },
    {
        "name": "Arreglo Mixto Especial",
        "price": "$150.000",
        "description": "Combinación de rosas, lirios y flores de temporada.",
        "image": "images/mixto.jpg"
    }
]

def save_order_to_csv(order_data):
    file_path = "pedidos.csv"
    file_exists = os.path.isfile(file_path)

    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(file_path, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "fecha_hora_registro",
                "nombre",
                "producto",
                "ocasion",
                "presupuesto",
                "telefono",
                "direccion",
                "fecha_entrega",
                "dedicatoria"
            ])

        writer.writerow([
            fecha_hora_actual,
            order_data["name"],
            order_data["selected_product"],
            order_data["occasion"],
            order_data["budget"],
            order_data["phone"],
            order_data["address"],
            order_data["delivery_date"],
            order_data["card_message"]
        ])

def get_user_state(user_id):
    if user_id not in user_states:
        user_states[user_id] = {
            "step": "start",
            "name": "",
            "occasion": "",
            "budget": "",
            "selected_product": "",
            "phone": "",
            "address": "",
            "delivery_date": "",
            "card_message": ""
        }
    return user_states[user_id]

def save_order_to_sheets(order_data):
    creds_json = os.environ["GOOGLE_CREDENTIALS"]
    creds_dict = json.loads(creds_json)

    print("CLIENT EMAIL:", creds_dict.get("client_email"))

    scopes = ["https://www.googleapis.com/auth/spreadsheets"]

    creds = Credentials.from_service_account_info(
        creds_dict,
        scopes=scopes
    )

    client = gspread.authorize(creds)

    sheet = client.open_by_url(
        "https://docs.google.com/spreadsheets/d/1TWOTsQgnX0GSIARj4eITNYwmcOeaKwic5U1RyjJ_-k/edit?gid=0#gid=0"
    ).sheet1

    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    row = [
        fecha_hora_actual,
        order_data["name"],
        order_data["selected_product"],
        order_data["occasion"],
        order_data["budget"],
        order_data["phone"],
        order_data["address"],
        order_data["delivery_date"],
        order_data["card_message"]
    ]

    sheet.append_row(row)

@app.get("/")
def home():
    return {"message": "Bot de floristería funcionando 🌸"}

@app.post("/chat")
def chat(message: Message):
    texto = message.text.strip()
    texto_lower = texto.lower()
    user_id = message.user_id

    conversation_state = get_user_state(user_id)

    if "hola" in texto_lower:
        conversation_state["step"] = "waiting_name"
        conversation_state["name"] = ""
        conversation_state["occasion"] = ""
        conversation_state["budget"] = ""
        conversation_state["selected_product"] = ""
        conversation_state["phone"] = ""
        conversation_state["address"] = ""
        conversation_state["delivery_date"] = ""
        conversation_state["card_message"] = ""
        return {
            "response": "Hola 🌸 Bienvenido a Floristería Los Colores. Antes de comenzar, ¿cuál es tu nombre?"
        }

    if conversation_state["step"] == "start":
        conversation_state["step"] = "waiting_name"
        return {
            "response": "Hola 🌸 Bienvenido a Floristería Los Colores. Antes de comenzar, ¿cuál es tu nombre?"
        }

    elif conversation_state["step"] == "waiting_name":
        conversation_state["name"] = texto
        conversation_state["step"] = "main_menu"
        return {
            "response": f"Mucho gusto, {texto} 😊 ¿Qué deseas hacer hoy?",
            "options": [
                "💐 Arreglos florales",
                "🎁 Enviar un regalo",
                "📦 Consultar pedido",
                "👨‍💼 Hablar con asesor"
            ]
        }

    elif conversation_state["step"] == "main_menu":
        if "arreglos" in texto_lower or "flores" in texto_lower:
            conversation_state["step"] = "waiting_occasion"
            return {
                "response": "¡Qué bonito! 🌷 ¿Para qué ocasión deseas el arreglo floral?",
                "options": [
                    "❤️ Amor",
                    "🎂 Cumpleaños",
                    "🙏 Condolencias",
                    "🎉 Aniversario",
                    "🌼 Otro"
                ]
            }

        elif "regalo" in texto_lower:
            return {
                "response": "🎁 Claro. Podemos ayudarte con un regalo especial.",
                "options": [
                    "🍫 Chocolates",
                    "🧸 Peluche",
                    "💌 Tarjeta especial",
                    "🎁 Combo con flores"
                ]
            }

        elif "pedido" in texto_lower:
            return {
                "response": "📦 Por favor escribe tu número de pedido para consultarlo."
            }

        elif "asesor" in texto_lower:
            return {
                "response": "👨‍💼 En breve te comunicaremos con un asesor. Por favor espera un momento."
            }

        else:
            return {
                "response": "Por favor selecciona una opción del menú principal.",
                "options": [
                    "💐 Arreglos florales",
                    "🎁 Enviar un regalo",
                    "📦 Consultar pedido",
                    "👨‍💼 Hablar con asesor"
                ]
            }

    elif conversation_state["step"] == "waiting_occasion":
        conversation_state["occasion"] = texto
        conversation_state["step"] = "waiting_budget"
        return {
            "response": f"Perfecto 🌸 Será para: {texto}. ¿Cuál es tu presupuesto aproximado?",
            "options": [
                "$50.000 - $100.000",
                "$100.000 - $150.000",
                "$150.000 - $200.000",
                "Más de $200.000"
            ]
        }

    elif conversation_state["step"] == "waiting_budget":
        conversation_state["budget"] = texto
        conversation_state["step"] = "showing_products"

        return {
            "response": (
                f"Excelente, {conversation_state['name']} 💐\n"
                f"Según la ocasión '{conversation_state['occasion']}' y tu presupuesto '{conversation_state['budget']}', "
                f"estas son algunas opciones recomendadas:"
            ),
            "products": products
        }

    elif conversation_state["step"] == "showing_products":
        conversation_state["selected_product"] = texto
        conversation_state["step"] = "waiting_phone"
        return {
            "response": f"Perfecto 🌸 Elegiste '{texto}'. Ahora por favor escríbeme tu número de teléfono."
        }

    elif conversation_state["step"] == "waiting_phone":
        conversation_state["phone"] = texto
        conversation_state["step"] = "waiting_address"
        return {
            "response": "Gracias 📞 Ahora escríbeme la dirección de entrega."
        }

    elif conversation_state["step"] == "waiting_address":
        conversation_state["address"] = texto
        conversation_state["step"] = "waiting_delivery_date"
        return {
            "response": "Perfecto 📍 ¿Para qué fecha deseas la entrega?"
        }

    elif conversation_state["step"] == "waiting_delivery_date":
        conversation_state["delivery_date"] = texto
        conversation_state["step"] = "waiting_card_message"
        return {
            "response": "Muy bien 💌 ¿Qué mensaje deseas agregar en la tarjeta? Si no quieres mensaje, escribe 'sin dedicatoria'."
        }

    elif conversation_state["step"] == "waiting_card_message":
        conversation_state["card_message"] = texto
        conversation_state["step"] = "finished"

        save_order_to_csv(conversation_state)
        save_order_to_sheets(conversation_state)

        return {
            "response": (
                f"✅ Pedido registrado con éxito\n\n"
                f"**Resumen del pedido**\n"
                f"👤 Nombre: {conversation_state['name']}\n"
                f"💐 Producto: {conversation_state['selected_product']}\n"
                f"🎉 Ocasión: {conversation_state['occasion']}\n"
                f"💰 Presupuesto: {conversation_state['budget']}\n"
                f"📞 Teléfono: {conversation_state['phone']}\n"
                f"📍 Dirección: {conversation_state['address']}\n"
                f"📅 Fecha de entrega: {conversation_state['delivery_date']}\n"
                f"💌 Dedicatoria: {conversation_state['card_message']}\n\n"
                f"Un asesor continuará con tu solicitud. Si deseas comenzar de nuevo, escribe 'hola'."
            )
        }

    else:
        return {
            "response": "Si deseas comenzar de nuevo, escribe 'hola'."
        }