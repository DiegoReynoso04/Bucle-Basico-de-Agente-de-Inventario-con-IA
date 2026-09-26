# Contexto activo

## Trabajo actual

Fase 5 (integración con Groq mediante `LLMClient`): **implementada y probada**, pendiente de revisión del usuario y de commit.

La Fase 6 no ha comenzado y solo comenzará cuando el usuario lo indique.

## Estado de las fases

* Fase 0 y Fase 1: completadas, commit `d465645`.
* Fase 2 (API FastAPI): completada, commit `29d4357`.
* Fase 3 (cliente HTTP + herramientas): completada, commit `00cbe7d`.
* Fase 4 (registro de conversaciones): completada, commit `1859428`.
* Fase 5 (integración con Groq): implementada y probada; pendiente de commit.
* Fases 6 en adelante (bucle del agente + CLI, E2E, limpieza final): pendientes.
* Todavía no existen `agent.py` (ni el bucle del agente, ni su memoria de conversación) ni `prompts.py`.
* `data/conversation_log.csv` todavía no existe: se creará con el primer evento real del agente.

Rama de trabajo: `fase-1-base-persistencia` (conectada a `origin`).

## Entorno

`.venv` con **Python 3.14.6** (en el ordenador actual). Dependencias instaladas desde `requirements-dev.txt`.

## Hecho recientemente (Fase 5)

* `inventory_app/llm.py`: `LLMClient(api_key, http=None)` con `complete(messages, tools=None)`, y `LLMError`.
* `inventory_app/config.py`: `Settings.groq_api_key` (variable `GROQ_API_KEY`).
* `tests/test_llm.py`: 17 tests sin red. `tests/test_live_groq.py`: 2 tests reales, solo con `GROQ_LIVE=1`.
* Suite normal: **198 passed, 2 skipped** con `pytest` y con `python -m pytest`. Prueba real ejecutada explícitamente: 2 passed.

## Decisiones tomadas durante la Fase 5

* API HTTP directa de Groq (`POST https://api.groq.com/openai/v1/chat/completions`) con `httpx2`. **Sin SDK `groq` ni `openai`**, y sin dependencias nuevas.
* Modelo elegido para todo el proyecto: `openai/gpt-oss-120b`.
  * Está disponible en Groq, admite tool use y se usa por HTTP directo.
  * Está centralizado en la constante `MODEL` de `llm.py`, sin configuración para elegir modelo.
  * No admite tool calls en paralelo: la Fase 6 diseñará el bucle de forma secuencial.
* `LLMClient` es la única capa que conoce la comunicación HTTP con Groq. Recibe las herramientas como datos y no importa ni ejecuta `tools.py`.
* La clave se lee de `GROQ_API_KEY` en `config.py` y se pasa a `LLMClient`. Si falta, se lanza `LLMError`.
* `complete` envía `messages` y, si se pasan, `tools` en formato de Groq. `LLMClient` no conoce las herramientas del inventario.
* Devuelve `{"content", "tool_calls": [{"id", "name", "arguments": dict}], "message"}`. Con eso se distingue una respuesta de texto de una petición de herramientas.
  * Los argumentos se convierten de texto JSON a `dict`, sin corregirlos.
  * `message` es un `dict` listo para añadirlo al historial.
* El caso `{"": {}}` observado en la prueba real queda como cuestión de la Fase 6, no de `LLMClient`.
* Errores de HTTP, conexión, timeout y respuestas inesperadas dan `LLMError` con mensajes seguros, sin la clave ni detalles internos. Sin reintentos.
* Timeout de 30 s. Sin streaming ni gestión de límites.
* Detalle completo en `techContext.md`.

## Cuestiones abiertas

* Revisión de la Fase 5 y commit (no se hace sin indicación del usuario).

## Decisiones pendientes (Fase 6: bucle del agente + CLI)

| Decisión |
|---|
| URL base de la API de inventario y cómo se configura |
| Definición de las 4 herramientas para el modelo (nombre, descripción, JSON Schema de parámetros) y cómo se ejecuta cada tool call |
| System prompt de Carla |
| Qué hacer con argumentos inesperados del modelo (por ejemplo `{"": {}}`) o con una herramienta desconocida |
| Dónde y cómo se convierten las excepciones de las herramientas (y `LLMError`) en el resultado estructurado para el modelo o en el mensaje para Carla |
| Formato concreto de `tool_call` (y texto de `message`) en cada tipo de fila del log |
| Cómo maneja el agente un fallo al escribir el log (`OSError` o cabecera inválida) |
| Límite de pasos del agente |
| Diseño secuencial del bucle (el modelo no admite tool calls en paralelo) |

## Siguiente paso

Revisión y commit de la Fase 5 por parte del usuario. Después, la Fase 6 (bucle del agente + CLI) cuando el usuario lo indique.
