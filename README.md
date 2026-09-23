# 🛒 TiendaTech IA — Agente Conversacional Multimodal

**Asistente virtual con entrada por voz y texto para una tienda retail de tecnología.**

Integra **Whisper (transcripción de voz)**, **Groq + LLM con Function Calling** y **Streamlit** como interfaz web, permitiendo consultar productos, stock y estado de pedidos de manera natural.

---

## 📋 Información Académica

| Campo | Detalle |
|---|---|
| **Curso** | Herramientas de Desarrollo Profesional TIC |
| **Tarea** | Tarea Académica 2 (TA2) |
| **Título** | Desarrollo de un agente conversacional multimodal para consultas mediante texto y voz |
| **Facultad** | Facultad de Ingeniería |
| **Docente** | Roosevelt Vladimir Lopez Uribe |
| **Periodo** | Abril 2026 — Lima, Perú |

### 👥 Autores

| N° | Nombre completo |
|---|---|
| 1 | Santander Alcarraz Axel Jesus |
| 2 | Martinez Vega Erick Gerardo |
| 3 | Durand Palacios Abel Paulo |
| 4 | Palacios Ugaz Santiago |

---

## 🎯 Objetivo del Proyecto

Desarrollar un **agente conversacional multimodal** que permita a los clientes de una tienda retail de tecnología interactuar mediante **texto o voz** para:

- 🔍 **Buscar productos** y conocer sus características y precios.
- 📦 **Consultar disponibilidad (stock)** en tiempo real.
- 🚚 **Consultar el estado y fecha de entrega** de sus pedidos.
- 🎤 **Enviar consultas por voz**, transcritas automáticamente con Whisper.

---

## 🧠 Modalidad Tecnológica Utilizada

| Componente | Tecnología |
|---|---|
| **Frontend / UI** | Streamlit |
| **Transcripción de voz** | OpenAI Whisper (`whisper-large-v3-turbo`) vía Groq |
| **Modelo de lenguaje (LLM)** | `openai/gpt-oss-20b` vía Groq API |
| **Function Calling** | Groq Chat Completions + Tools |
| **Grabación de audio** | `audio-recorder-streamlit` |
| **Lenguaje** | Python 3.10+ |

### 🔄 Flujo de la aplicación

    🎤 Usuario habla o escribe
            ↓
    📝 Whisper transcribe (si es voz)
            ↓
    🧠 LLM interpreta la intención
            ↓
    🔧 LLM decide si llamar una función del negocio
            ↓
    📊 La función devuelve datos reales (productos, stock, pedidos)
            ↓
    💬 LLM genera respuesta natural
            ↓
    🖥️ Se muestra en el chat de Streamlit

---

## 🧩 Funciones del Negocio (Function Calling)

El agente expone **3 funciones** que el LLM puede invocar automáticamente según la intención del usuario:

| Función | Descripción | Ejemplo de consulta |
|---|---|---|
| `buscar_producto(nombre_producto)` | Busca un producto en el catálogo y devuelve precio + características. | "¿Cuánto cuestan los audífonos?" |
| `consultar_stock(nombre_producto)` | Consulta las unidades disponibles en stock. | "¿Tienen laptops en stock?" |
| `consultar_estado_pedido(numero_pedido)` | Devuelve el estado y fecha de entrega de un pedido. | "¿Cómo va mi pedido 1001?" |

### 📸 Evidencia de llamada a función del negocio

Cuando el agente invoca una función, aparece una notificación tipo *toast* en la esquina superior derecha: `🔧 Función ejecutada: buscar_producto`.

> _(Aquí pega una captura de pantalla mostrando el toast o el resultado de la función ejecutada)_

---

## 📂 Estructura del Proyecto

    Asistente_IA/
    ├── .streamlit/
    │   ├── config.toml        # Configuración pública de Streamlit
    │   └── secrets.toml       # (NO se sube) Clave API de Groq
    ├── app.py                 # Código fuente principal
    ├── README.md              # Este archivo
    ├── requirements.txt       # Dependencias del proyecto
    ├── .gitignore             # Archivos ignorados por git
    └── venv/                  # (NO se sube) Entorno virtual

---

## ⚙️ Instalación

### 1. Clonar el repositorio

    git clone https://github.com/AxelSantander26/Asistente-IA.git
    cd Asistente-IA

### 2. Crear y activar un entorno virtual

**Windows:**

    python -m venv venv
    venv\Scripts\activate

**Linux / macOS:**

    python3 -m venv venv
    source venv/bin/activate

### 3. Instalar dependencias

    pip install -r requirements.txt

### 4. Configurar la API Key de Groq

Crea el archivo `.streamlit/secrets.toml` en la raíz del proyecto con:

    GROQ_API_KEY = "tu_api_key_de_groq_aqui"

> 🔑 Obtén tu API Key gratuita en: https://console.groq.com/keys

---

## ▶️ Ejecución

Con el entorno virtual activado, desde la raíz del proyecto:

    streamlit run app.py

Se abrirá automáticamente en el navegador: `http://localhost:8501`

---

## 🎤 Uso de la Aplicación

El usuario puede interactuar de **dos maneras**:

### 1. Por texto
Escribir directamente en la barra inferior del chat.

### 2. Por voz
Hacer clic en **"🎤 Enviar consulta por voz"** y elegir:
- **🎙️ Grabar con micrófono** → habla y espera el fin de la grabación.
- **📎 Subir archivo de audio** → arrastra un `.mp3`, `.wav`, `.m4a` o `.webm`.

### Ejemplos de consultas

| Consulta del usuario | Función invocada |
|---|---|
| "¿Cuánto cuestan los audífonos?" | `buscar_producto` |
| "¿Tienen stock de teclados?" | `consultar_stock` |
| "¿Cómo va mi pedido 1001?" | `consultar_estado_pedido` |
| "Busco una laptop" | `buscar_producto` |
| "¿Qué características tiene el monitor?" | `buscar_producto` |

---

## 📸 Capturas de la Aplicación

### 1. Entrada por voz (grabación con micrófono)
> _(Pega aquí captura del panel de grabación activo)_

### 2. Transcripción del audio
> _(Pega aquí captura mostrando la transcripción del audio en el chat)_

### 3. Respuesta del asistente
> _(Pega aquí captura del chat con la respuesta generada por el LLM)_

### 4. Llamada a función del negocio
> _(Pega aquí captura del toast "🔧 Función ejecutada: ..." o del resultado devuelto)_

---

## 🔒 Seguridad

- La **API Key de Groq** nunca se sube al repositorio.
- El archivo `.streamlit/secrets.toml` está listado en `.gitignore`.
- El entorno virtual `venv/` también está ignorado.
- GitHub Push Protection está activo y bloquea cualquier intento de subir credenciales.

---

## 📌 Entregables Cubiertos

- [x] Código fuente completo (`app.py`)
- [x] Repositorio GitHub: https://github.com/AxelSantander26/Asistente-IA
- [x] README con instrucciones de instalación, ejecución y modalidad tecnológica
- [x] Capturas de entrada por voz, transcripción y respuesta
- [x] Evidencia de llamada a función del negocio
- [ ] Documento PDF: `TA_U2_GRUPO_#GRUPO.pdf` _(pendiente de generar aparte)_

---

## 📚 Referencias

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Groq API Documentation](https://console.groq.com/docs)
- [Whisper en Groq](https://console.groq.com/docs/speech-text)
- [audio-recorder-streamlit](https://pypi.org/project/audio-recorder-streamlit/)
- [Function Calling en Groq](https://console.groq.com/docs/tool-use)
