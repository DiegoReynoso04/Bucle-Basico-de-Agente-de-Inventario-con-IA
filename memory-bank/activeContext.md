# Contexto activo

## Trabajo actual

Fase 3 (cliente HTTP de la API + herramientas): **implementada y verificada**, pendiente de commit.

La siguiente fase no ha comenzado y solo comenzará cuando el usuario lo indique.

## Estado de las fases

* Fase 0 y Fase 1: completadas, commit `d465645`.
* Fase 2 (API FastAPI): completada, commit `29d4357`.
* Fase 3: implementada y verificada; pendiente de commit.
* Fases 4 en adelante (registro de conversaciones, integración con el LLM, bucle del agente): pendientes.
* Todavía no existen:
  * La integración con Groq (el paquete `groq` no está instalado).
  * `LLMClient`, `llm.py` y `prompts.py`.
  * `agent.py`, y por tanto tampoco el bucle del agente.
  * `conversation_log.py`.

Rama de trabajo: `fase-1-base-persistencia` (conectada a `origin`).

## Entorno

`.venv` con **Python 3.14.6** (en el ordenador actual). Dependencias instaladas desde `requirements-dev.txt`.

## Hecho recientemente (Fase 3)

* 3A: `inventory_app/api_client.py` con `InventoryApiClient` (`list_products`, `get_low_stock`, `add_stock`, `remove_stock`) y `tests/test_api_client.py` (18 tests).
* 3B: `inventory_app/tools.py` con las herramientas `list_products`, `get_low_stock`, `add_stock` y `remove_stock`, y `tests/test_tools.py` (8 tests).
* `httpx2==2.13.1` pasa de `requirements-dev.txt` a `requirements.txt`. No se añadió ninguna otra dependencia.
* Suite completa: **163 passed** con `pytest` y con `python -m pytest`. `data/inventory.csv` intacto.

## Decisiones tomadas durante la Fase 3

* Arquitectura: `tools.py` → `InventoryApiClient` → HTTP → FastAPI → `InventoryService` → `CsvInventoryRepository` → `data/inventory.csv`.
* El agente accederá al inventario solo por HTTP. `tools.py` y `api_client.py` no importan el servicio ni el repositorio, y no acceden al CSV. `InventoryApiClient` es la única capa que usa `httpx2`.
* `InventoryApiClient` recibe un `httpx2.Client` ya configurado: `TestClient` en los tests y `httpx2.Client(base_url=...)` en producción.
* Los nombres se codifican con `quote(name, safe="")`, para que `/`, `?`, `#` y `%` no rompan la URL.
* Los errores se traducen según el `code` de la API, reutilizando las excepciones de `errors.py`:
  * `product_not_found` → `ProductNotFound`.
  * `not_found` (ruta inexistente) → `InventoryError`, para no confundir una URL incorrecta con un producto inexistente.
  * `insufficient_stock` → `InsufficientStock`.
  * La tabla completa está en `techContext.md`.
* Los errores de conexión se convierten en `InventoryError` con un mensaje propio, sin detalles de `httpx2`.
* `add_stock` y `remove_stock` exigen un entero positivo y lo comprueban antes de hacer la petición. `remove_stock` pasa la cantidad positiva y `InventoryApiClient` la convierte en cambio negativo.
* `tools.py`: cuatro funciones de módulo que delegan en el cliente. No contienen lógica de negocio, no capturan excepciones y no hay abstracción genérica de herramientas. No dependen del formato de Groq.

## Cuestiones abiertas

* Commit de la Fase 3 (no se hace sin indicación del usuario).

## Decisiones pendientes (se cierran en su fase)

| Decisión | Fase |
|---|---|
| URL base de la API y cómo se configura | Al integrar el agente |
| Cómo se convierten las herramientas en definiciones para el modelo | Integración con el LLM (5) |
| Dónde se convierten las excepciones de las herramientas en el resultado estructurado para el modelo | Bucle del agente (6) |
| Formato exacto de las filas `tool` en `conversation_log.csv` | 4 |
| Comportamiento ante fallo de escritura del log | 4 |
| Integración con Groq: SDK o HTTP directo, y modelo concreto | 5 |
| Límite de pasos del agente | 6 |

La numeración sigue el orden de fases aprobado en `progress.md`: 4 = registro de conversaciones, 5 = integración con Groq, 6 = bucle del agente + CLI.

## Siguiente paso

Commit de la Fase 3 por parte del usuario. Después, la siguiente fase cuando el usuario lo indique.
