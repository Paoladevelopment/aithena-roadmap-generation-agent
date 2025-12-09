## Learning Roadmap Generation

Este proyecto implementa un tutor inteligente que guía al usuario por varias etapas (intereses, conocimientos previos, preferencias, etc.) y finalmente genera y guarda un **roadmap de aprendizaje personalizado** (con objetivos, tareas y recursos recomendados).

Se construye con **FastAPI**, **LangChain / LangGraph**, **OpenAI**, **Tavily**, **MongoDB** y **PostgreSQL**.

---

## Estructura del proyecto

```text
learning-roadmap-generation/
├─ main.py                        # Punto de entrada FastAPI (endpoints / y /chat, /events)
├─ Procfile                       # Comando para desplegar (Railway)
├─ requirements.txt               # Dependencias para pip
├─ vercel.json                    # (obsoleto para este proyecto; pensado para Vercel)
├─ auth.py                        # Lógica de autenticación / JWT
├─ langgraph.json                 # Configuración de LangGraph
├─ chroma_db/                     # Datos locales de Chroma (vector DB)
├─ tutorgpt/
│  ├─ graph.py                    # Definición del grafo LangGraph y flujo de asistentes
│  ├─ route_workflow.py           # Lógica para enrutar al siguiente “assistant”
│  ├─ notifications.py            # Notificador SSE para avisar cuando el roadmap está listo
│  ├─ core/
│  │  ├─ state.py                 # Tipo de estado global + snapshot (_last_state)
│  │  ├─ assistant.py             # Wrapper Assistant para los sub-assistants
│  │  ├─ dialog_flow.py           # Manejo de la pila de estados de diálogo
│  │  ├─ llm_config.py            # Configuración del LLM (ChatOpenAI) y safe_llm_invoke
│  │  ├─ utilities.py             # Utilidades para crear nodos de herramientas y entrada
│  ├─ utils/
│  │  └─ config.py                # Configuración (DB, Mongo, etc.) vía variables de entorno
│  ├─ tools/
│  │  ├─ search_tools.py          # Integración con Tavily para búsqueda de recursos
│  │  └─ utilities.py             # Tool para obtener información de usuario desde Postgres
│  ├─ models/
│  │  └─ tavily.py                # Modelos Pydantic para Tavily (SearchInput, SearchOutput, etc.)
│  ├─ introduction_assistant/     # Assistant de introducción (prompt, routes, tools)
│  ├─ interest_discovery_assistant/
│  ├─ prior_knowledge_assistant/
│  ├─ learning_preferences_assistant/
│  ├─ time_availability_assistant/
│  ├─ resource_preferences_assistant/
│  ├─ roadmap_generation_assistant/
│  │  ├─ prompts.py               # Prompt de alto nivel para generación de roadmap
│  │  ├─ roadmap_generation_assistant.py # Runnable + tools usados en esta fase
│  │  └─ tools.py                 # Lógica para resumir info, generar roadmap, añadir recursos y guardar
│  └─ primary_assistant/          # Assistant principal que decide a qué sub-assistant ir
```

---

## Requisitos

- Python **3.9+**
- Acceso a:
  - **OpenAI API** (modelo `gpt-4o`)
  - **Tavily API** (para búsqueda de recursos web)
  - **MongoDB** (para guardar roadmaps)
  - **PostgreSQL** (para leer datos de usuario)
- Variables de entorno (Railway / `.env` en local), por ejemplo:
  - `OPENAI_API_KEY`
  - `TAVILY_API_KEY`
  - `MONGODB_URI`
  - `DB_URI` **o** `DB_HOST`, `DB_NAME`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`
  - Cualquier secreto que use `auth.py` para los JWT

---

## Instalación local

1. Clonar el repositorio:

```bash
git clone https://github.com/tu-usuario/learning-roadmap-generation.git
cd learning-roadmap-generation
```

2. Crear y activar un entorno virtual (opcional pero recomendado):

```bash
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate         # Windows
```

3. Instalar dependencias:

```bash
pip install -r requirements.txt
```

4. Crear un archivo `.env` en la raíz con tus claves, por ejemplo:

```env
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
MONGODB_URI=mongodb+srv://...
DB_URI=postgresql://user:pass@host:port/dbname
JWT_SECRET=...
```

---

## Ejecutar la API localmente

```bash
python main.py
# o
uvicorn main:app --reload
```

- La API quedará escuchando en `http://127.0.0.1:8001` (o el puerto que definas).

Endpoints principales:

- `GET /` → Health check sencillo, devuelve `{"message": "Hello World"}`.
- `POST /chat` → Endpoint principal del tutor.
- `GET /events` → Endpoint de **Server-Sent Events (SSE)** para notificar cuando el roadmap está listo.

---

## Manual de usuario (cómo probar el flujo completo)

### 1. Autenticación y JWT

El endpoint `/chat` y `/events` esperan un `Authorization: Bearer <token>` que `auth.py` validará.

- En tu entorno real, ese token vendrá de tu sistema de login.
- Para pruebas locales, asegúrate de que:
  - `auth.py` pueda decodificar el token con los secretos de tu `.env`.
  - El token contenga un `user_id` válido que exista en tu base de datos Postgres.

*(Si lo quieres simplificar para debug, puedes adaptar temporalmente `auth.py` para aceptar un token fijo.)*

---

### 2. Probar el chat del tutor (`/chat`)

Con `curl`:

```bash
curl -X POST "http://127.0.0.1:8001/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TU_JWT_AQUI>" \
  -d '{"human_say": "Quiero aprender programación en Go, crea un roadmap para mí."}'
```

- El grafo LangGraph se encargará de:
  - Obtener `user_info` desde Postgres.
  - Pasar por los sub-assistants (introducción, intereses, etc.) si corresponde.
  - Cuando toque, invocar el assistant de **roadmap_generation**.

El usuario verá respuestas conversacionales del tutor (en español).  
Cuando el tutor decida que es momento de generar el roadmap, llamará al tool `create_complete_roadmap`, que:

- Lanza un **job en background** que:
  - Llama a `generate_roadmap` (con el LLM).
  - Añade recursos con Tavily (`add_resources_to_roadmap`).
  - Guarda el roadmap en MongoDB (`save_roadmap_to_database`).
- Devuelve inmediatamente control al LLM para que responda algo tipo:  
  *“¡Perfecto! Tu roadmap personalizado está siendo creado. Te notificaremos cuando esté completado.”*

---

### 3. Probar las notificaciones SSE (`/events`)

Este endpoint permite que el frontend se “suscriba” a eventos de tipo  
`roadmap <ID> ya se ha creado`.

#### 3.1. Abrir el stream SSE (en terminal)

```bash
curl -N \
  -H "Accept: text/event-stream" \
  -H "Authorization: Bearer <TU_JWT_AQUI>" \
  http://127.0.0.1:8001/events
```

- Esta conexión se queda abierta.
- Todavía no debería imprimir nada.

#### 3.2. Disparar la creación de un roadmap

En otra terminal, usa `/chat` como en el paso 2, con un mensaje que haga que el asistente genere un roadmap.

- El tool `create_complete_roadmap` lanzará el trabajo en background.
- Cuando `save_roadmap_to_database` inserte el documento en Mongo, llamará a:

```python
notifier.notify_roadmap_ready(user_id, str(result.inserted_id))
```

#### 3.3. Ver el evento SSE

En la terminal donde corre el `curl -N`, deberías ver algo así:

```text
data: roadmap 64f1a2b3c4d5e6f7890abcde ya se ha creado
```

Eso es precisamente el mensaje que el frontend puede usar para mostrar un toast:

> “Tu roadmap ya está listo”.

---

## Cómo integrarlo en el frontend (resumen)

- Mantener una conexión SSE a `/events` (con el JWT del usuario).
- Cada vez que llegue un `message`:

  - Leer `event.data`, por ejemplo:  
    `roadmap 64f1a2b3c4d5e6f7890abcde ya se ha creado`
  - Mostrar un toast/notificación con ese texto.
  - Opcional: extraer el `ID` para enlazar a una pantalla de detalle del roadmap.

Ejemplo (pseudo‑código):

```ts
const es = new EventSource("/events", { withCredentials: true });

es.onmessage = (event) => {
  const message = event.data; // "roadmap <id> ya se ha creado"
  showToast(message);
};
```

---

## Despliegue en Railway (resumen rápido)

- Asegúrate de tener:
  - `requirements.txt`
  - `Procfile` con:

    ```txt
    web: uvicorn main:app --host 0.0.0.0 --port $PORT
    ```

- Crear proyecto en Railway → **Deploy from GitHub**.
- Configurar variables de entorno (`OPENAI_API_KEY`, `TAVILY_API_KEY`, `MONGODB_URI`, `DB_URI`, etc.).
- Railway instalará dependencias y ejecutará el comando del `Procfile`.

Una vez desplegado, puedes repetir las pruebas de `/chat` y `/events` usando la URL pública de Railway en lugar de `http://127.0.0.1:8001`.


