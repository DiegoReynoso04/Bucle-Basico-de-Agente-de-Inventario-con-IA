# Progreso

## Fases

| Fase | Descripción | Dependencias nuevas | Estado |
|---|---|---|---|
| 0 | Análisis y arquitectura | — | **Completada y aprobada** |
| 1 | Base y persistencia | `python-dotenv`, `pytest` | **Completada** (commit `d465645`) |
| 2 | API FastAPI | `httpx2` (solo desarrollo, para `TestClient`) | **Implementada y validada**; pendiente de revisión del usuario y de commit |
| 3 | Cliente HTTP de la API + herramientas | ninguna prevista (`httpx2` ya instalado; decidir si pasa a `requirements.txt`) | Pendiente |
| 4 | Conversation log (se crea `data/conversation_log.csv`) | — | Pendiente |
| 5 | Integración con Groq (SDK o HTTP directo, a decidir) | a decidir | Pendiente |
| 6 | Bucle del agente + CLI | — | Pendiente |
| 7 | E2E + pruebas reales con Groq | — | Pendiente |
| 8 | Limpieza final + README + revisión | — | Pendiente |

Orden de fases aprobado. Cada fase incluye sus propias pruebas y no se avanza a la siguiente sin indicación del usuario.

## Fase 1: resultado

Archivos creados:

* `requirements.txt`: `fastapi==0.141.1`, `uvicorn==0.54.0`, `pydantic==2.13.5`, `python-dotenv==1.2.3`.
* `requirements-dev.txt`: `-r requirements.txt` + `pytest==9.1.1`.
* `.env.example`: `GROQ_API_KEY=` vacío e `INVENTORY_CSV_PATH` comentado.
* `inventory_app/`: `__init__.py`, `config.py`, `models.py`, `errors.py`, `repository.py`, `service.py`.
* `data/inventory.csv`: inventario inicial.
* `tests/`: `conftest.py`, `test_repository.py`, `test_service.py`.

Archivo modificado: `.gitignore` (+ `.pytest_cache/`).

Contenido inicial de `data/inventory.csv`:

```text
name,quantity,unit,min_stock
Café arábica,40,bolsas,10
Café descafeinado,8,bolsas,5
Leche de avena,12,unidades,20
Leche entera,48,unidades,24
Vasos de cartón 12 oz,500,unidades,200
Tapas para vasos 12 oz,150,unidades,200
Jarabe de vainilla,4,botellas,4
Azúcar en sobres,1000,unidades,300
```

En stock bajo: Leche de avena (12 ≤ 20), Tapas para vasos 12 oz (150 ≤ 200) y Jarabe de vainilla (4 ≤ 4, caso límite).

## Pruebas realizadas (Fase 1)

Comando: `.venv/Scripts/python -m pytest -q` → **92 passed**.

* `test_repository.py` cubre: archivo inexistente, vacío o solo con cabecera; creación del archivo y del directorio; ida y vuelta; persistencia entre instancias; tipos; `low_stock` no almacenado; líneas en blanco; comas y comillas; CRLF; Unicode y UTF-8 sin BOM; UTF-8 con BOM; archivo no UTF-8; 6 cabeceras inválidas; 8 valores numéricos inválidos; 5 valores de texto inválidos; número de columnas; comilla sin cerrar; 3 variantes de duplicados; no se sobrescribe un archivo corrupto; no se escribe si la mutación falla; error de permisos en lectura; fallo en `os.replace`, en `fsync` y en la primera escritura (original intacto y sin temporales); escritura mediante temporal en el mismo directorio; 20 actualizaciones concurrentes serializadas.
* `test_service.py` cubre: listar (con datos y vacío); obtener; mayúsculas/minúsculas y espacios; los acentos no se ignoran; producto inexistente; alta y persistencia; alta sin archivo previo; limpieza de nombre y unidad; duplicados (sin modificar el CSV); 11 casos de validación del alta y sus límites; añadir y retirar stock; conservar el nombre almacenado, el orden y el resto de productos; retirar hasta cero; stock negativo rechazado sin persistir; ajuste de producto inexistente; 5 ajustes inválidos; propiedad `low_stock` y su límite; listado de stock bajo antes y después de ajustes.

Verificaciones adicionales:

* El hash SHA-256 de `data/inventory.csv` es el mismo antes y después de los tests; además lo comprueba la salvaguarda de `conftest.py`.
* `data/inventory.csv`: UTF-8 sin BOM, sin `\r`, cabecera exacta; se carga con el servicio y devuelve 8 productos y los 3 esperados en stock bajo.
* `get_settings()` resuelve la ruta por defecto, una ruta relativa y una absoluta.
* `pip check`: sin conflictos.
* Pruebas de mutación en una copia temporal (el proyecto no se modificó): cambiar `<=` por `<` → 3 tests fallan; quitar la escritura atómica → 4 tests fallan; quitar el control de stock negativo → 1 test falla.

La Fase 1 se validó de nuevo en otro ordenador, con un `.venv` nuevo con Python 3.14.6: 92 passed.

## Fase 2: resultado

Archivos creados:

* `inventory_app/api.py`: `create_app(service=None)` con los 6 endpoints y los manejadores de errores; `app = create_app()` para `uvicorn inventory_app.api:app`.
* `pytest.ini`: `pythonpath = .`.
* `tests/test_api.py`.

Archivos modificados:

* `inventory_app/models.py`: reglas del nombre (`/`, espacios dobles, `low-stock` reservado) y modelo `StockChange`.
* `requirements-dev.txt`: + `httpx2==2.13.1`.
* `tests/conftest.py`: fixture `client`.
* `tests/test_service.py`: tests de las reglas de nombre y de `StockChange`.
* `tests/test_repository.py`: una fila inválida nueva (nombre con `/`).

`requirements.txt` no cambia. `service.py`, `repository.py`, `config.py` y `errors.py` no cambian.

## Pruebas realizadas (Fase 2)

Comandos: `pytest` y `python -m pytest` → **137 passed** (92 de la Fase 1 + 45 nuevos: 27 en `test_api.py`, 17 del modelo en `test_service.py` y 1 en `test_repository.py`).

* `test_api.py` cubre:
  * Consultas: `/health`; listar; stock bajo (y que `low-stock` no se toma como producto); obtener; nombre codificado en la URL con acentos, espacios y otras mayúsculas; producto inexistente (404).
  * Alta: crear y persistir (201); duplicado (409, CSV intacto); nombre con `/`, espacios dobles o `low-stock` (422, CSV intacto); cantidad negativa o `"10"` (422); JSON mal formado (422).
  * Stock: entrada; salida; stock insuficiente (409, con `details` y CSV intacto); `change` igual a 0 (422, `invalid_stock_change`); `change` `"5"` o ausente (422, `validation_error`); producto inexistente (404).
  * Rutas: ruta inexistente e `/` codificada como `%2F` (404, `not_found`); método no permitido (405, cabecera `Allow`).
  * Almacenamiento: error 500 (`storage_error`) en lectura y escritura, sin rutas internas en la respuesta y con el detalle en el log.
  * Creación de la aplicación: `create_app()` usa `INVENTORY_CSV_PATH` y no lee el CSV hasta recibir una petición.
  * Todos los errores se comprueban con el formato `{code, message, details}`.
* Tests del modelo: nombres rechazados (`/`, espacios dobles, `low-stock` en varias mayúsculas); nombres parecidos válidos; reglas aplicadas tras quitar los espacios exteriores; `StockChange` acepta enteros (incluido 0) y rechaza `"5"`, `1.5`, `true` y `null`.

Verificaciones adicionales:

* El hash de `data/inventory.csv` es el mismo antes y después de los tests y el archivo no tiene cambios respecto al commit; además lo vigila la salvaguarda de `conftest.py`.
* El `data/inventory.csv` real sigue siendo válido con las nuevas reglas de nombre (8 productos).
* Uvicorn importa `inventory_app.api:app` (con `uvicorn.importer.import_from_string`) y la aplicación expone los 6 endpoints.
* No quedan referencias a `APIRouter`, `Depends`, `get_service` ni `app.state`.
* `pip check`: sin conflictos.

## Problemas conocidos

* `data/inventory.csv` se escribe con fin de línea `\n`. Con `core.autocrlf=true`, Git puede avisar de la conversión a CRLF; la lectura acepta ambos formatos.
* Los cambios de la Fase 2 están pendientes de commit (se hará cuando lo indique el usuario).
* Si un CSV editado a mano contiene un nombre que incumple las nuevas reglas (por ejemplo, con `/`), la carga falla con `StorageError` (500 en la API). Es intencionado: se prefiere un error explícito a un producto al que no se puede acceder.
* `data/conversation_log.csv` se versionará y el agente le añadirá filas en cada ejecución, así que cada sesión real generará cambios en Git. Es una consecuencia aceptada.
* `server.py` ejecuta un servidor Flask al importarse y Flask no está instalado; no se usa en el proyecto (revisión en la Fase 8).
