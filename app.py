import streamlit as st
import json
from groq import Groq
from audio_recorder_streamlit import audio_recorder

# ============================================================
# CONFIGURACIÓN INICIAL
# ============================================================
st.set_page_config(page_title="TiendaTech IA", page_icon="🛒", layout="centered")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ============================================================
# BASE DE DATOS SIMULADA
# ============================================================
PRODUCTOS = {
    "audifonos": {"nombre": "Audífonos Inalámbricos XYZ", "precio": 150.0, "stock": 25, "caracteristicas": "Bluetooth 5.0, cancelación de ruido, 20h batería"},
    "laptop": {"nombre": "Laptop UltraBook Pro", "precio": 3500.0, "stock": 8, "caracteristicas": "16GB RAM, SSD 512GB, pantalla 14''"},
    "mouse": {"nombre": "Mouse Gamer RGB", "precio": 85.0, "stock": 50, "caracteristicas": "6400 DPI, 7 botones, iluminación RGB"},
    "teclado": {"nombre": "Teclado Mecánico TKL", "precio": 220.0, "stock": 15, "caracteristicas": "Switches azules, retroiluminado, anti-ghosting"},
    "monitor": {"nombre": "Monitor 24'' Full HD", "precio": 650.0, "stock": 12, "caracteristicas": "75Hz, IPS, HDMI/VGA"},
}

PEDIDOS = {
    "1001": {"cliente": "Juan Pérez", "producto": "audifonos", "estado": "En camino", "fecha_entrega": "2026-09-20"},
    "1002": {"cliente": "María López", "producto": "laptop", "estado": "Procesando", "fecha_entrega": "2026-09-22"},
    "1003": {"cliente": "Carlos Ruiz", "producto": "mouse", "estado": "Entregado", "fecha_entrega": "2026-09-15"},
}

# ============================================================
# FUNCIONES DEL NEGOCIO
# ============================================================
def buscar_producto(nombre_producto: str) -> dict:
    nombre_producto = nombre_producto.lower().strip()
    for key, data in PRODUCTOS.items():
        if key in nombre_producto or nombre_producto in key:
            return {"encontrado": True, "producto": data["nombre"], "caracteristicas": data["caracteristicas"], "precio": data["precio"]}
    return {"encontrado": False, "mensaje": f"No se encontró el producto '{nombre_producto}' en el catálogo."}

def consultar_stock(nombre_producto: str) -> dict:
    nombre_producto = nombre_producto.lower().strip()
    for key, data in PRODUCTOS.items():
        if key in nombre_producto or nombre_producto in key:
            return {"encontrado": True, "producto": data["nombre"], "stock": data["stock"]}
    return {"encontrado": False, "mensaje": f"No se encontró el producto '{nombre_producto}'."}

def consultar_estado_pedido(numero_pedido: str) -> dict:
    numero_pedido = numero_pedido.strip()
    if numero_pedido in PEDIDOS:
        p = PEDIDOS[numero_pedido]
        return {"encontrado": True, "pedido": numero_pedido, "cliente": p["cliente"], "estado": p["estado"], "fecha_entrega": p["fecha_entrega"]}
    return {"encontrado": False, "mensaje": f"No se encontró el pedido con número '{numero_pedido}'."}

FUNCIONES_DISPONIBLES = {
    "buscar_producto": buscar_producto,
    "consultar_stock": consultar_stock,
    "consultar_estado_pedido": consultar_estado_pedido,
}

# ============================================================
# HERRAMIENTAS (SCHEMA)
# ============================================================
tools = [
    {
        "type": "function",
        "function": {
            "name": "buscar_producto",
            "description": "Busca un producto en el catálogo y devuelve sus características y precio.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nombre_producto": {"type": "string", "description": "Nombre del producto (ej: audifonos, laptop, mouse)"}
                },
                "required": ["nombre_producto"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_stock",
            "description": "Consulta la cantidad de unidades disponibles en stock de un producto.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nombre_producto": {"type": "string", "description": "Nombre del producto"}
                },
                "required": ["nombre_producto"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_estado_pedido",
            "description": "Consulta el estado y fecha de entrega de un pedido por su número.",
            "parameters": {
                "type": "object",
                "properties": {
                    "numero_pedido": {"type": "string", "description": "Número de pedido (ej: 1001)"}
                },
                "required": ["numero_pedido"]
            }
        }
    }
]

# ============================================================
# PROMPT DE SISTEMA
# ============================================================
SYSTEM_PROMPT = """
Eres "TiendaTech IA", un asistente virtual especializado en atención al cliente para una tienda retail de tecnología y electrónica.

ROL:
- Asistente amable, eficiente y profesional.

OBJETIVO:
- Ayudar a los clientes a encontrar productos, consultar stock, precios y estado de pedidos.

ALCANCE:
- Solo respondes temas relacionados con productos tecnológicos, stock, precios y pedidos de la tienda.

REGLAS:
1. Sé claro, breve y educativo.
2. Usa 'buscar_producto' para info de productos.
3. Usa 'consultar_stock' para disponibilidad.
4. Usa 'consultar_estado_pedido' para pedidos (pide el número si falta).
5. Si la consulta es ambigua, pide aclaración.
6. Si está fuera de alcance, indícalo amablemente.

TONO:
- Cercano, profesional, español neutro.

RESTRICCIONES:
- No inventes stock, precios ni estados. Usa siempre las funciones.
- No compartas información de otros clientes.
"""

# ============================================================
# ESTADO DE SESIÓN
# ============================================================
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "ultimo_audio_procesado" not in st.session_state:
    st.session_state.ultimo_audio_procesado = None
if "ultimo_archivo_procesado" not in st.session_state:
    st.session_state.ultimo_archivo_procesado = None

# ============================================================
# FUNCIÓN DE TRANSCRIPCIÓN
# ============================================================
def transcribir_audio(audio_bytes: bytes, nombre_archivo: str = "audio.wav"):
    try:
        transcripcion = client.audio.transcriptions.create(
            file=(nombre_archivo, audio_bytes),
            model="whisper-large-v3-turbo",
            language="es"
        )
        return transcripcion.text
    except Exception as e:
        st.error(f"Error al transcribir: {e}")
        return None

# ============================================================
# FUNCIÓN QUE LLAMA AL MODELO Y EJECUTA FUNCIONES
# ============================================================
def generar_respuesta(consulta: str) -> str:
    """Devuelve el texto de respuesta del modelo (sin mostrarlo)."""
    st.session_state.messages.append({"role": "user", "content": consulta})

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=st.session_state.messages,
            tools=tools,
            tool_choice="auto",
            max_tokens=1024
        )
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        if tool_calls:
            st.session_state.messages.append(response_message)
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                if function_name in FUNCIONES_DISPONIBLES:
                    resultado = FUNCIONES_DISPONIBLES[function_name](**function_args)
                    st.toast(f"🔧 Función ejecutada: {function_name}")

                    st.session_state.messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": json.dumps(resultado, ensure_ascii=False)
                    })

            second_response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=st.session_state.messages,
                max_tokens=1024
            )
            respuesta_final = second_response.choices[0].message.content
        else:
            respuesta_final = response_message.content

        st.session_state.messages.append({"role": "assistant", "content": respuesta_final})
        return respuesta_final

    except Exception as e:
        error_msg = f"Ocurrió un error: {e}"
        st.session_state.messages.append({"role": "assistant", "content": error_msg})
        return error_msg

# ============================================================
# CSS PARA EL PANEL INFERIOR FIJO
# ============================================================
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
    html, body, .stApp {
        font-family: 'Inter', system-ui, sans-serif !important;
    }

    /* Espacio abajo para que el panel fijo no tape los mensajes */
    .block-container {
        padding-bottom: 220px !important;
    }

    /* ===== PANEL INFERIOR FIJO ===== */
    .st-key-panel_inferior {
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        right: 0 !important;
        background: #ffffff !important;
        padding: 10px 16px 10px 16px !important;
        border-top: 1px solid #eef1f6 !important;
        z-index: 999 !important;
        max-width: 720px !important;
        margin: 0 auto !important;
        box-shadow: 0 -4px 20px -8px rgba(15, 23, 42, 0.08) !important;
    }

    /* Expander de audio dentro del panel: compacto y limpio */
    .st-key-panel_inferior [data-testid="stExpander"] {
        background: transparent !important;
        border: none !important;
        margin: 0 0 6px 0 !important;
    }
    .st-key-panel_inferior [data-testid="stExpander"] details {
        background: transparent !important;
        border: none !important;
    }
    .st-key-panel_inferior [data-testid="stExpander"] summary {
        color: #3b82f6 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        padding: 6px 0 !important;
        cursor: pointer;
    }
    .st-key-panel_inferior [data-testid="stExpander"] summary:hover {
        color: #2563eb !important;
    }
    /* Ocultar la flecha material que se ve como texto */
    .st-key-panel_inferior [data-testid="stExpander"] summary [data-testid="stIconMaterial"] {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# INTERFAZ
# ============================================================
st.title("🛒 TiendaTech IA")
st.caption("Asistente por voz para tienda retail · Whisper + Groq + Function Calling")

# --- Botón de Nueva conversación ARRIBA (donde estaba el expander) ---
if st.session_state.chat_history:
    col_nueva, _ = st.columns([1, 3])
    with col_nueva:
        if st.button("🗑️ Nueva conversación", key="nueva_conv"):
            st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            st.session_state.chat_history = []
            st.session_state.ultimo_audio_procesado = None
            st.session_state.ultimo_archivo_procesado = None
            st.rerun()

st.divider()

# --- Historial de conversación ---
if not st.session_state.chat_history:
    with st.chat_message("assistant", avatar="🛒"):
        st.write("¡Hola! 👋 Soy tu asistente de TiendaTech. Puedo ayudarte a consultar productos, stock y el estado de tus pedidos. ¿En qué te puedo ayudar?")

for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        with st.chat_message("user", avatar="👤"):
            st.write(msg["content"])
    elif msg["role"] == "assistant":
        with st.chat_message("assistant", avatar="🛒"):
            st.write(msg["content"])

# --- PANEL INFERIOR FIJO: expander de audio + input de texto ---
with st.container(key="panel_inferior"):
    # 1) Expander de audio ARRIBA del input
    with st.expander("🎤 Enviar consulta por voz", expanded=False):
        tab1, tab2 = st.tabs(["🎙️ Grabar con micrófono", "📎 Subir archivo de audio"])

        with tab1:
            audio_bytes = audio_recorder(
                text="Haz clic para grabar:",
                recording_color="#e74c3c",
                neutral_color="#3498db",
                icon_name="microphone",
                icon_size="2x",
                pause_threshold=2.0,
                key="micro"
            )
            if audio_bytes and audio_bytes != st.session_state.ultimo_audio_procesado:
                st.session_state.ultimo_audio_procesado = audio_bytes
                with st.spinner("Transcribiendo desde el micrófono..."):
                    texto = transcribir_audio(audio_bytes, "grabacion.wav")
                if texto:
                    with st.spinner("Pensando..."):
                        respuesta = generar_respuesta(texto)
                    st.session_state.chat_history.append({"role": "user", "content": texto})
                    st.session_state.chat_history.append({"role": "assistant", "content": respuesta})
                    st.rerun()

        with tab2:
            uploaded_file = st.file_uploader(
                "Selecciona un archivo de audio",
                type=["mp3", "wav", "m4a", "webm"],
                key="uploader"
            )
            if uploaded_file:
                st.audio(uploaded_file)
                file_id = f"{uploaded_file.name}_{uploaded_file.size}"
                if st.button("📝 Transcribir archivo"):
                    if file_id != st.session_state.ultimo_archivo_procesado:
                        st.session_state.ultimo_archivo_procesado = file_id
                        with st.spinner("Transcribiendo archivo..."):
                            texto = transcribir_audio(uploaded_file.read(), uploaded_file.name)
                        if texto:
                            with st.spinner("Pensando..."):
                                respuesta = generar_respuesta(texto)
                            st.session_state.chat_history.append({"role": "user", "content": texto})
                            st.session_state.chat_history.append({"role": "assistant", "content": respuesta})
                            st.rerun()

    # 2) Input de texto DEBAJO del expander
    if prompt := st.chat_input("Escribe tu consulta aquí..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.write(prompt)
        with st.chat_message("assistant", avatar="🛒"):
            with st.spinner("Pensando..."):
                respuesta = generar_respuesta(prompt)
            st.write(respuesta)
        st.session_state.chat_history.append({"role": "assistant", "content": respuesta})
        st.rerun()
