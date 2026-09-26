# Contexto activo

## Trabajo actual

Fase 4 (registro de conversaciones): **implementada, probada y aprobada** por el usuario; pendiente de commit.

La siguiente fase no ha comenzado y solo comenzará cuando el usuario lo indique.

## Estado de las fases

* Fase 0 y Fase 1: completadas, commit `d465645`.
* Fase 2 (API FastAPI): completada, commit `29d4357`.
* Fase 3 (cliente HTTP + herramientas): completada, commit `00cbe7d`.
* Fase 4 (registro de conversaciones): implementada, probada y aprobada; pendiente de commit.
* Fases 5 en adelante (integración con Groq, bucle del agente + CLI, E2E, limpieza final): pendientes.
* Todavía no existen:
  * La integración con Groq (el paquete `groq` no está instalado).
  * `LLMClient`, `llm.py` y `prompts.py`.
  * `agent.py`, y por tanto tampoco el bucle del agente.
* `data/conversation_log.csv` todavía no existe: se creará con el primer evento real del agente.

Rama de trabajo: `fase-1-base-persistencia` (conectada a `origin`).

## Entorno

`.venv` con **Python 3.14.6** (en el ordenador actual). Dependencias instaladas desde `requirements-dev.txt`.

## Hecho recientemente (Fase 4)

* `inventory_app/conversation_log.py`: `ConversationLogger(path)` con `log(actor, message, tool_call="")`.
* `tests/test_conversation_log.py`: 18 tests.
* Sin dependencias nuevas y sin cambios en archivos existentes.
* Suite completa: **181 passed** con `pytest` y con `python -m pytest`. `data/inventory.csv` intacto; el log real no se crea en los tests.

## Decisiones tomadas durante la Fase 4

* Una sola clase con un solo método. Solo añade (append) y no mantiene memoria de la conversación: la memoria completa de la sesión será responsabilidad del futuro agente. No depende de ninguna otra capa del proyecto.
* La ruta es obligatoria (sin ruta por defecto ni cambios en `config.py`), así los tests no pueden escribir en el log real por accidente.
* Modo `"a+"`: lee la primera línea y escribe siempre al final. `csv` estándar, UTF-8 sin BOM, fin de línea `\n`.
* Cabecera:
  * Se escribe si el archivo no existe o está vacío.
  * Si el archivo ya tiene contenido y su primera línea no es exactamente `actor,message,tool_call,timestamp`, se rechaza la escritura con `ValueError` sin modificar el archivo.
* Validación del formato del evento, no de reglas del agente:
  * `actor` en `user`/`agent`/`tool`.
  * `message` y `tool_call` deben ser texto (`str`), sin convertir otros tipos.
  * `tool_call` **no** es obligatorio para `actor="tool"`.
  * Si algo no es válido, no se toca el archivo.
* El formato interno de `tool_call` queda deliberadamente abierto hasta implementar el agente.
* Los errores de escritura (`OSError`) se propagan a quien llama; no se ocultan.
* `timestamp` en hora local con su desfase horario, ISO 8601 con precisión de segundos.
* Detalle completo en `techContext.md`.

## Cuestiones abiertas

* Commit de la Fase 4 (no se hace sin indicación del usuario).

## Decisiones pendientes (se cierran en su fase)

| Decisión | Fase |
|---|---|
| URL base de la API y cómo se configura | Al integrar el agente |
| Cómo se convierten las herramientas en definiciones para el modelo | Integración con el LLM (5) |
| Integración con Groq: SDK o HTTP directo, y modelo concreto | 5 |
| Dónde se convierten las excepciones de las herramientas en el resultado estructurado para el modelo | Bucle del agente (6) |
| Formato concreto de `tool_call` (y texto de `message`) en cada tipo de fila del log | Bucle del agente (6) |
| Cómo maneja el agente un fallo al escribir el log (`OSError` o cabecera inválida) y cómo se transforman esos errores para el agente o el LLM | Bucle del agente (6) |
| Límite de pasos del agente | 6 |

Las dos decisiones del registro se aplazan a la Fase 6 porque dependen de cómo el agente use el logger. El logger ya admite cualquiera de las opciones.

## Siguiente paso

Commit de la Fase 4 por parte del usuario. Después, la Fase 5 (integración con Groq) cuando el usuario lo indique.
