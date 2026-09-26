# Contexto activo

## Trabajo actual

Fase 6 (bucle del agente + CLI): **implementada y probada**, pendiente de revisión del usuario y de commit.

La Fase 7 no ha comenzado y solo comenzará cuando el usuario lo indique.

## Estado de las fases

* Fase 0 y Fase 1: completadas, commit `d465645`.
* Fase 2 (API FastAPI): completada, commit `29d4357`.
* Fase 3 (cliente HTTP + herramientas): completada, commit `00cbe7d`.
* Fase 4 (registro de conversaciones): completada, commit `1859428`.
* Fase 5 (integración con Groq): completada, commit `35b4076`.
* Fase 6 (bucle del agente + CLI): implementada y probada; pendiente de commit.
* Fases 7 y 8 (E2E, limpieza final): pendientes.
* `data/conversation_log.csv` todavía no existe: se creará con el primer mensaje en una sesión real de `python agent.py`.

Rama de trabajo: `fase-1-base-persistencia`, sincronizada con GitHub (`origin`) hasta la Fase 5.

## Entorno

`.venv` con **Python 3.14.6** (en el ordenador actual). Dependencias instaladas desde `requirements-dev.txt`.

Para usar el agente:

1. En una terminal: `uvicorn inventory_app.api:app`.
2. En otra terminal: `python agent.py` (requiere `GROQ_API_KEY` en `.env`).

## Hecho recientemente (Fase 6)

* `agent.py` con `run_tool`, `handle_message` (el bucle) y `main` (CLI), sin clases.
* Quinta herramienta `create_product`: `InventoryApiClient.create_product()` y `tools.create_product()`.
* `INVENTORY_API_URL` en `config.py` (por defecto `http://127.0.0.1:8000`) y en `.env.example`.
* `tests/test_agent.py` (19 tests). Tests nuevos de `create_product` en el cliente y las herramientas. Test real opt-in del agente completo.
* Suite normal: **220 passed, 3 skipped** con `pytest` y con `python -m pytest`. Pruebas reales ejecutadas explícitamente: 3 passed.

## Decisiones tomadas durante la Fase 6 (aprobadas por el usuario)

* Se añade `create_product` como quinta herramienta, porque registrar productos es un requisito funcional. El contrato de la API no cambia.
* `validation_error` pasa a dar `InventoryError` con los motivos de la API, en lugar de `InvalidStockChange`: con `create_product`, un dato inválido no es un cambio de stock.
* `INVENTORY_API_URL` en `config.py`, con valor por defecto.
* El agente es el orquestador. El modelo solo pide herramientas, y `run_tool` valida el nombre y los argumentos exactos antes de ejecutar:
  * Rechaza con `InvalidArguments` los argumentos que faltan o que sobran, y también `{"": {}}`.
  * Rechaza con `UnknownTool` las herramientas que no existen.
  * Devuelve los errores como resultado para el modelo, y la cantidad se pasa tal cual (el agente no cambia el signo).
* Bucle secuencial con un único historial `list[dict]` por sesión. Se conserva `tool_call_id` y los resultados se envían como mensajes `role="tool"`.
* Termina con la respuesta final del modelo, o en `MAX_STEPS = 8` con un mensaje claro.
* Registro:
  * `user`: el texto del usuario.
  * `tool`: el resultado en JSON y `tool_call` con el nombre y los argumentos en JSON.
  * `agent`: el texto que ve el usuario.
* `LLMError`: mensaje seguro, registrado como `agent`; la sesión continúa.
* Si el log no se puede escribir, la sesión termina de forma controlada con un mensaje claro.
* `SYSTEM_PROMPT` dentro de `agent.py`; no se crea `prompts.py`.
* Detalle completo en `techContext.md`.

## Cuestiones abiertas

* Revisión de la Fase 6 y commit (no se hace sin indicación del usuario).
* La CLI etiqueta al asistente como "Carla:" y al usuario como "Tú:", según el ejemplo del usuario. En el resto del proyecto, Carla es la usuaria.

## Siguiente paso

Revisión y commit de la Fase 6 por parte del usuario. Después, la Fase 7 (E2E + pruebas reales con Groq) cuando el usuario lo indique.
