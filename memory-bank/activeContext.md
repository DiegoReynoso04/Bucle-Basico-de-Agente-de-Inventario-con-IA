# Contexto activo

## Trabajo actual

Fase 2 (API FastAPI): **implementada y validada con pruebas**, pendiente de revisión del usuario y de commit.

La Fase 3 no ha comenzado y solo comenzará cuando el usuario lo indique.

Rama de trabajo: `fase-1-base-persistencia`. La Fase 0 y la Fase 1 están en el commit `d465645`; los cambios de la Fase 2 todavía no tienen commit.

## Entorno

El proyecto se trasladó a otro ordenador. Allí se creó un `.venv` nuevo con **Python 3.14.6** y se instaló `requirements-dev.txt`. La suite de la Fase 1 pasó sin cambios (92 tests) antes de empezar la Fase 2.

## Hecho recientemente (Fase 2)

* `inventory_app/api.py`: aplicación FastAPI con 6 endpoints, creada con `create_app(service=None)`; `app = create_app()` para Uvicorn.
* `inventory_app/models.py`: reglas nuevas del nombre de producto y modelo `StockChange`.
* `pytest.ini` (`pythonpath = .`): ya se puede ejecutar `pytest` directamente.
* `httpx2==2.13.1` añadido a `requirements-dev.txt` e instalado en `.venv` (lo usa `TestClient`).
* `tests/conftest.py`: fixture `client`. `tests/test_api.py`: 27 tests de la API. Tests nuevos de las reglas de nombre y de `StockChange` en `tests/test_service.py`, y una fila nueva en `tests/test_repository.py`.
* Suite completa: **137 passed** (92 de la Fase 1 + 45 nuevos), con `pytest` y con `python -m pytest`.

## Decisiones tomadas durante la Fase 2

* Endpoints: `GET /health`, `GET /products`, `GET /products/low-stock`, `GET /products/{name}`, `POST /products`, `POST /products/{name}/stock`. `/products/low-stock` se declara antes que `/products/{name}`.
* Nombres de producto: de 1 a 100 caracteres tras quitar los espacios exteriores; sin espacios dobles; sin `/`; `low-stock` reservado (sin distinguir mayúsculas). La identidad sigue sin distinguir mayúsculas y los acentos siguen contando. Las reglas están en el modelo, así que también valen al leer el CSV.
  * Motivo: el nombre viaja en la ruta. El servidor decodifica `%2F` antes de elegir ruta, así que un nombre con `/` no llegaría nunca a `/products/{name}`.
* Stock: `{"change": n}`, con `n` entero estricto; positivo para entradas, negativo para salidas. El 0 lo rechaza el servicio (`invalid_stock_change`) y los tipos inválidos, Pydantic (`validation_error`).
* No hay SKU, ni ID público, ni endpoint para fijar el stock absoluto.
* Formato uniforme de error `{"code", "message", "details"}`, con los códigos descritos en `techContext.md`.
* Los errores 500 (`storage_error`) devuelven un mensaje genérico. El detalle, que incluye rutas del sistema de archivos, solo se registra con `logging` (biblioteca estándar).
* Arquitectura sencilla: las rutas se declaran dentro de `create_app`, que usa un único `InventoryService` (y un único repositorio con su `RLock`) por aplicación. **No se usan `APIRouter`, `Depends` ni `app.state`**: con 6 endpoints aportaban más conceptos que beneficio. Se decidió explícitamente para mantener el proyecto educativo.
* Importar `api.py` no lee el CSV; se lee al atender cada petición.
* Tests: se revisaron y simplificaron de 83 a 45 tests nuevos. Se quitaron los casos repetidos entre capas, un test de concurrencia que solo detectaba el fallo a veces y un test que repetía uno del repositorio. Las reglas se prueban caso a caso en el modelo y con un caso representativo por HTTP.

## Cuestiones abiertas

* Revisión de la Fase 2 por el usuario y commit (no se hace sin su indicación).

## Decisiones pendientes (se cierran en su fase)

| Decisión | Fase |
|---|---|
| Lista definitiva de herramientas | 3 |
| Si `httpx2` pasa también a `requirements.txt` (cuando lo use `InventoryApiClient` en ejecución) | 3 |
| URL base de la API para el cliente (configuración) | 3 |
| Formato exacto de las filas `tool` en `conversation_log.csv` | 4 |
| Comportamiento ante fallo de escritura del log | 4 |
| Integración con Groq: SDK o HTTP directo, y modelo concreto | 5 |
| Límite de pasos del agente | 6 |

## Siguiente paso

Revisión de la Fase 2 y commit por parte del usuario. Después, la Fase 3 (cliente HTTP de la API + herramientas) cuando el usuario lo indique.
