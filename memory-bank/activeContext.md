# Contexto activo

## Trabajo actual

Fase 1 (base y persistencia): **implementada y validada con pruebas**, pendiente de revisión por el usuario.

La Fase 2 no ha comenzado y solo comenzará cuando el usuario lo indique.

## Hecho recientemente (Fase 1)

* Instaladas en `.venv`: `python-dotenv` 1.2.3 y `pytest` 9.1.1.
* Creados `requirements.txt`, `requirements-dev.txt` y `.env.example`; `.gitignore` ampliado con `.pytest_cache/`.
* Creado el paquete `inventory_app/` con `config.py`, `models.py`, `errors.py`, `repository.py` y `service.py`.
* Creado `data/inventory.csv` con 8 productos iniciales (3 en stock bajo).
* Creados `tests/conftest.py`, `tests/test_repository.py` y `tests/test_service.py`: 92 tests, todos pasan.

## Decisiones tomadas durante la Fase 1

* `INVENTORY_CSV_PATH` (opcional) permite cambiar la ruta del inventario; una ruta relativa se resuelve desde la raíz del proyecto. Por defecto: `data/inventory.csv`.
* Enteros estrictos en los modelos: se rechazan booleanos, decimales y cadenas numéricas (`"10"`), en lugar de convertirlos.
* El nombre solo se limpia de espacios exteriores (no se colapsan espacios internos ni se ignoran acentos). La identidad es `name.strip().casefold()`.
* Error adicional `InvalidStockChange`: el ajuste de stock debe ser un entero distinto de cero.
* El repositorio expone `load`, `save` y `update(mutate)`. `update` lee, aplica la mutación y escribe bajo el mismo `RLock`; si la mutación lanza una excepción, no se escribe nada.
* Lectura con `utf-8-sig` (acepta UTF-8 con o sin BOM); escritura en UTF-8 sin BOM, fin de línea `\n`.
* Un archivo vacío (0 bytes) o con solo la cabecera se trata como inventario vacío.
* Las filas en blanco se ignoran. Los números deben ser solo dígitos ASCII (se rechazan `" 5"`, `"+5"`, `"2.5"`).
* Los productos se devuelven en el orden en que están almacenados; los nuevos se añaden al final.
* `conftest.py` incluye una salvaguarda de sesión que falla si algún test modifica `data/inventory.csv`.

## Cuestiones abiertas

* Los tests deben ejecutarse con `.venv/Scripts/python -m pytest`. Con `pytest` directamente falla la importación de `inventory_app`. Se propone añadir un `pytest.ini` mínimo (`pythonpath = .`), pendiente de aprobación.
* Posible actualización de `techContext.md` con las decisiones de implementación de la Fase 1, pendiente de aprobación.

## Decisiones pendientes (se cierran en su fase)

| Decisión | Fase |
|---|---|
| Contrato definitivo de los endpoints (incluido cómo tratar nombres con `/` en la ruta) | 2 |
| Lista definitiva de herramientas | 3 |
| Formato exacto de las filas `tool` en `conversation_log.csv` | 4 |
| Comportamiento ante fallo de escritura del log | 4 |
| Integración con Groq: SDK o HTTP directo, y modelo concreto | 5 |
| Límite de pasos del agente | 6 |

## Siguiente paso

Revisión de la Fase 1 por el usuario. Después, la Fase 2 (API FastAPI) cuando el usuario lo indique.
