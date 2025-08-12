import gspread, os
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

load_dotenv()  # Carga las variables de entorno desde el archivo .env

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GOOGLE_SHEETS_CREDENTIALS_PATH = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH")
GOOGLE_SHEETS_FILE_NAME = os.getenv("GOOGLE_SHEETS_FILE_NAME")

# Acá va el token de BotFather
TOKEN = TELEGRAM_TOKEN

keyboard = [["Horario", "Dirección"],
            ["Formas de pago", "Hablar con alguien"]]

markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Función /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        """¡Hola! Soy un ejemplo de lo que va a ser el bot/asistente automático de tu negocio/emprendimiento.

        A continuación, elegí una opción o escribí alguna de las siguientes palabras/frases:
        '/pedido', '/consulta', 'horario', 'direccion', 'pago/formas de pago' o 'hablar con alguien'.""",
        reply_markup=markup
    )

# Handler general de mensajes:
# (Este handler se encarga de decidir qué hacer o cómo actuar en base al mensaje recibido)
async def main_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Si está esperando consulta
    if context.user_data.get("esperando_consulta"):
        await recibir_consulta(update, context)
    # Si está esperando pedido
    elif context.user_data.get("pedido_tipo"):
        await recibir_pedido(update, context)
    # Si no, mensaje normal
    else:
        await handle_message(update, context)

# Handler para mensajes "normales":
# (Este handler se encarga de responder a las palabras/frases que se definieron como "válidas")
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.lower()
    
    # Estas respuestas cambiarán dependiendo cada negocio/emprendimiento
    if "horario" in texto or "horarios" in texto or "horario de atención" in texto or "horario de atencion" in texto or "horario." in texto:
        respuesta = "Nuestro horario es de lunes a viernes de 9 a 18 hs (esto se modificaría según tu gusto)."
    elif "direccion" in texto or "dirección" in texto or "dónde están" in texto or "donde están" in texto or "dónde están?" in texto or "donde están?" in texto or "dirección." in texto:
        respuesta = "Estamos en Av. Siempreviva 742, Springfield (esto se modificaría según tu gusto)."
    elif "pago" in texto or "formas de pago" in texto or "formas de pago." in texto or "formas de pago?" in texto or "forma de pago?" in texto or "forma de pago." in texto:
        respuesta = "Aceptamos efectivo, transferencia y MercadoPago (esto se modificaría según tu gusto)."
    elif "hablar con alguien" in texto or "hablar con alguien." in texto or "hablar con alguien?" in texto or "quiero hablar con alguien" in texto or "quiero hablar con alguien." in texto:
        respuesta = "En breve un miembro del equipo se va a contactar con vos personalmente. 🤖➡🙋"
    elif "gracias" in texto or "gracias!" in texto or "gracias." in texto or "muchas gracias" in texto or "muchas gracias!" in texto or "muchas gracias." in texto:
        respuesta = "¡De nada! Estoy para ayudarte 😊"
    else:
        respuesta = "Solo estoy programado para responder a ciertas palabras o frases. Gracias por entender!"

    await update.message.reply_text(respuesta)

# Función /consulta
async def consulta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Por favor, escribí tu consulta y te responderemos a la brevedad.")
    context.user_data["esperando_consulta"] = True

# Handler para recibir la consulta (y guardarla en Google Sheets)
async def recibir_consulta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("esperando_consulta"):
        user = update.effective_user
        mensaje = update.message.text
        guardar_en_sheets("Consultas", [user.username, "Consulta", mensaje])
        await update.message.reply_text("Tu consulta fue registrada con éxito. ¡Gracias!")
        context.user_data["esperando_consulta"] = False
    else:
        await handle_message(update, context)

# Función /pedido
async def pedido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Delivery", callback_data="pedido_delivery")],
        [InlineKeyboardButton("Retiro en local", callback_data="pedido_retiro")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "¿Cómo querés recibir tu pedido?",
        reply_markup=reply_markup
    )
    context.user_data["esperando_pedido"] = True

# Handler de los botones inline del mensaje de /pedido
async def handle_botones_pedido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Esto confirma que se tocó el botón

    if query.data == "pedido_delivery":
        mensaje = "Seleccionaste *Delivery*.\nPor favor, escribí tu pedido completo:"
        context.user_data["pedido_tipo"] = "Delivery"
    elif query.data == "pedido_retiro":
        mensaje = "Seleccionaste *Retiro en local*.\nPor favor, escribí tu pedido completo:"
        context.user_data["pedido_tipo"] = "Retiro en local"

    await query.edit_message_text(text=mensaje, parse_mode="Markdown")

# Handler para recibir el pedido del producto (y guardarlo en Google Sheets)
async def recibir_pedido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("esperando_pedido"):
        user = update.effective_user
        producto = update.message.text
        pedido_tipo = context.user_data.get("pedido_tipo", "Desconocido")
        guardar_en_sheets("Pedidos", [user.username, pedido_tipo, producto])
        await update.message.reply_text("Tu pedido fue registrado con éxito. ¡Gracias!")
        context.user_data["esperando_pedido"] = False
        context.user_data["pedido_tipo"] = None
    else:
        await handle_message(update, context)

# Función para guardar datos en Google Sheets
def guardar_en_sheets(nombre_hoja, datos):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_SHEETS_CREDENTIALS_PATH, scope)
        cliente = gspread.authorize(creds)

        # Se abre el archivo por el nombre
        sheet = cliente.open(GOOGLE_SHEETS_FILE_NAME).worksheet(nombre_hoja)

        # Se agrega una nueva fila
        sheet.append_row(datos)
    except Exception as e:
        print(f"Error guardando en Google Sheets: {e}")

# Main para correr el bot
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("consulta", consulta))
app.add_handler(CommandHandler("pedido", pedido))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, main_text_handler))

# El siguiente handler debe agregarse solo una vez, y debe diferenciar entre mensajes de pedido y otros mensajes.
app.add_handler(CallbackQueryHandler(handle_botones_pedido, pattern="^pedido_"))

print("Bot corriendo... / Bot running...")

app.run_polling()
