# Progreso

## Fases

| Fase | Descripción | Dependencias nuevas | Estado |
|---|---|---|---|
| 0 | Análisis y arquitectura | — | **Completada y aprobada** |
| 1 | Base y persistencia | `python-dotenv`, `pytest` | **Implementada y validada**; pendiente de revisión del usuario |
| 2 | API FastAPI | ninguna | Pendiente |
| 3 | Cliente HTTP de la API + herramientas | `httpx` | Pendiente |
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

## Pruebas realizadas

Comando: `.venv/Scripts/python -m pytest -q` → **92 passed**.

* `test_repository.py` cubre: archivo inexistente, vacío o solo con cabecera; creación del archivo y del directorio; ida y vuelta; persistencia entre instancias; tipos; `low_stock` no almacenado; líneas en blanco; comas y comillas; CRLF; Unicode y UTF-8 sin BOM; UTF-8 con BOM; archivo no UTF-8; 6 cabeceras inválidas; 8 valores numéricos inválidos; 5 valores de texto inválidos; número de columnas; comilla sin cerrar; 3 variantes de duplicados; no se sobrescribe un archivo corrupto; no se escribe si la mutación falla; error de permisos en lectura; fallo en `os.replace`, en `fsync` y en la primera escritura (original intacto y sin temporales); escritura mediante temporal en el mismo directorio; 20 actualizaciones concurrentes serializadas.
* `test_service.py` cubre: listar (con datos y vacío); obtener; mayúsculas/minúsculas y espacios; los acentos no se ignoran; producto inexistente; alta y persistencia; alta sin archivo previo; limpieza de nombre y unidad; duplicados (sin modificar el CSV); 11 casos de validación del alta y sus límites; añadir y retirar stock; conservar el nombre almacenado, el orden y el resto de productos; retirar hasta cero; stock negativo rechazado sin persistir; ajuste de producto inexistente; 5 ajustes inválidos; propiedad `low_stock` y su límite; listado de stock bajo antes y después de ajustes.

Verificaciones adicionales:

* El hash SHA-256 de `data/inventory.csv` es el mismo antes y después de los tests; además lo comprueba la salvaguarda de `conftest.py`.
* `data/inventory.csv`: UTF-8 sin BOM, sin `\r`, cabecera exacta; se carga con el servicio y devuelve 8 productos y los 3 esperados en stock bajo.
* `get_settings()` resuelve la ruta por defecto, una ruta relativa y una absoluta.
* `pip check`: sin conflictos.
* Pruebas de mutación en una copia temporal (el proyecto no se modificó): cambiar `<=` por `<` → 3 tests fallan; quitar la escritura atómica → 4 tests fallan; quitar el control de stock negativo → 1 test falla.

## Problemas conocidos

* `pytest` ejecutado directamente no encuentra `inventory_app`; hay que usar `python -m pytest` (propuesta: `pytest.ini` con `pythonpath = .`).
* `data/inventory.csv` se escribe con fin de línea `\n`. Con `core.autocrlf=true`, Git puede avisar de la conversión a CRLF; la lectura acepta ambos formatos.
* `.gitignore`, `CLAUDE.md`, `memory-bank/` y todos los archivos de la Fase 1 están sin seguimiento en Git (no se ha hecho commit por indicación del usuario).
* `data/conversation_log.csv` se versionará y el agente le añadirá filas en cada ejecución, así que cada sesión real generará cambios en Git. Es una consecuencia aceptada.
* `server.py` ejecuta un servidor Flask al importarse y Flask no está instalado; no se usa en el proyecto (revisión en la Fase 8).
