# Contexto técnico

## Lenguaje principal

Python 3.13.

El proyecto se ejecutará utilizando un entorno virtual local situado en:

`.venv/`

No se instalarán dependencias globales para el proyecto.

## API

La API REST se desarrollará utilizando:

* FastAPI
* Uvicorn
* Pydantic

FastAPI será responsable de exponer los endpoints HTTP y Pydantic de validar los datos de entrada y salida cuando sea necesario.

## Agente de IA

El agente se desarrollará en Python y estará contenido en:

`agent.py`

El agente será responsable de:

* Mantener el historial de conversación durante la sesión.
* Enviar mensajes al modelo de lenguaje.
* Interpretar las llamadas a herramientas.
* Ejecutar las herramientas disponibles.
* Incorporar los resultados de las herramientas al contexto.
* Repetir el ciclo de razonamiento y ejecución cuando sea necesario.
* Generar la respuesta final para el usuario.
* Registrar la actividad de la conversación.

## Modelo de lenguaje

La integración con el modelo de lenguaje se realizará mediante Groq.

La clave de API se almacenará en un archivo `.env` situado en la raíz del proyecto.

Variable esperada:

`GROQ_API_KEY`

La clave nunca debe escribirse directamente en el código ni incluirse en Git.

## Variables de entorno

Las variables sensibles se gestionarán mediante `.env`.

El archivo `.env` debe estar incluido en `.gitignore`.

No se deben registrar claves, tokens ni credenciales en archivos versionados.

## Persistencia

La primera versión utilizará archivos CSV como sistema de persistencia.

El inventario tendrá un archivo CSV dedicado.

El registro de conversaciones utilizará:

`conversation_log.csv`

### Decisiones aprobadas (Fase 0)

Rutas:

* Inventario: `data/inventory.csv`
* Registro de conversaciones: `data/conversation_log.csv`

Los CSV de `data/` forman parte del proyecto y se versionan en Git (no se excluyen en `.gitignore`), para facilitar la evaluación y la ejecución desde un clon limpio. El contenido inicial de `inventory.csv` se decidirá en la Fase 1.

Formato de `data/inventory.csv`:

```text
name,quantity,unit,min_stock
```

* `name`: texto; identificador del producto. Se compara sin distinguir mayúsculas/minúsculas y se guarda tal como se registró.
* `quantity`: entero `>= 0`.
* `unit`: texto (por ejemplo, "unidades", "bolsas", "kg").
* `min_stock`: entero `>= 0`, específico de cada producto.

Un producto está en stock bajo cuando `quantity <= min_stock`. Este valor se calcula y no se almacena.

Formato de `data/conversation_log.csv`:

```text
actor,message,tool_call,timestamp
```

* Append-only: solo se añaden filas; nunca se sobrescribe ni se reescribe.

Comportamiento previsto de la persistencia (propuesto en Fase 0, se validará con pruebas en la Fase 1):

* Si el archivo de inventario no existe, se considera inventario vacío y se crea con cabecera en la primera escritura.
* Codificación UTF-8, separador `,`.
* Escritura atómica del inventario (archivo temporal en el mismo directorio + `os.replace`) para evitar pérdida de datos.
* Un lock protege cada ciclo lectura-modificación-escritura.
* Si el archivo no se puede leer o su contenido no es válido (cabecera incorrecta, tipos inválidos, duplicados), se produce un error explícito y el archivo no se sobrescribe.
* Los errores de acceso (por ejemplo, el archivo está abierto y bloqueado por otra aplicación) se informan explícitamente.

## Herramientas del agente

El agente no deberá modificar directamente los archivos de inventario desde su lógica de conversación.

Las operaciones sobre el inventario deberán realizarse mediante herramientas claramente definidas que utilicen la API del proyecto.

Las herramientas deberán representar acciones reales que el agente pueda ejecutar, por ejemplo:

* Consultar productos.
* Añadir stock.
* Reducir stock.
* Consultar productos con stock bajo.
* Registrar productos.

La lista definitiva de herramientas y sus contratos se establecerá durante la fase de diseño de la API y del agente.

### Decisiones aprobadas (Fase 0)

* El agente accede al inventario exclusivamente mediante HTTP a la API. No importa la lógica de negocio ni la persistencia.
* `add_stock` y `remove_stock` son herramientas independientes. Ambas reciben una cantidad positiva; el signo del movimiento lo determina la herramienta, no el modelo.
* Los productos inexistentes no se crean automáticamente: si una operación falla porque el producto no existe, el agente debe preguntar al usuario antes de registrarlo.
* Los errores de las herramientas (producto inexistente, stock insuficiente, argumentos inválidos, API no disponible) se devuelven al modelo como resultado estructurado, sin interrumpir el bucle.
* El bucle del agente tiene un límite máximo de pasos (llamadas al modelo por mensaje del usuario) para evitar bucles infinitos.

### Propuesta de herramientas (pendiente de confirmar en la Fase 3)

| Herramienta | Operación de API propuesta |
|---|---|
| `list_products` | `GET /products` |
| `get_product` | `GET /products/{name}` |
| `create_product` | `POST /products` |
| `add_stock` | `POST /products/{name}/stock` con `change` positivo |
| `remove_stock` | `POST /products/{name}/stock` con `change` negativo |
| `get_low_stock_products` | `GET /products/low-stock` |

## Arquitectura inicial

La arquitectura prevista deberá mantener separadas estas responsabilidades:

```text
Usuario
   │
   ▼
Agente
   │
   ├── Modelo de lenguaje (Groq)
   │
   └── Herramientas
          │
          ▼
       API FastAPI
          │
          ▼
      Persistencia CSV
```

La estructura exacta de archivos se decidirá durante la fase de arquitectura antes de implementar la aplicación.

### Estructura aprobada (Fase 0)

`inventory_app/` es el paquete principal y `agent.py`, en la raíz, es el punto de entrada del agente.

Estructura prevista (los archivos se crearán progresivamente en cada fase; ninguno existe todavía):

```text
agent.py                     # Bucle del agente, historial en memoria y CLI de terminal
inventory_app/
  __init__.py
  config.py                  # Configuración desde .env / variables de entorno
  models.py                  # Modelos Pydantic
  errors.py                  # Excepciones de dominio
  repository.py              # Persistencia CSV del inventario
  service.py                 # Lógica de negocio del inventario
  api.py                     # Aplicación FastAPI y endpoints
  api_client.py              # Cliente HTTP de la API (usado por las herramientas)
  tools.py                   # Definición y ejecución de herramientas del agente
  llm.py                     # Integración con Groq tras una interfaz sustituible
  prompts.py                 # Prompt de sistema
  conversation_log.py        # Registro append-only de conversaciones
data/                        # inventory.csv y conversation_log.csv
tests/                       # Pruebas automatizadas (pytest)
requirements.txt             # Dependencias de ejecución
requirements-dev.txt         # Dependencias de desarrollo
.env.example                 # Nombres de variables, sin credenciales
```

Separación de responsabilidades:

* API (`api.py`): endpoints finos, validación y traducción de errores a códigos HTTP.
* Lógica de negocio (`service.py`): reglas del inventario.
* Persistencia (`repository.py`): lectura y escritura del CSV.
* Modelos (`models.py`): contratos de datos.
* El agente (`agent.py`) solo conoce el cliente HTTP, las herramientas, el cliente del modelo y el registro.

Solo la API escribe en `data/inventory.csv`; solo el agente escribe en `data/conversation_log.csv`.

## Pruebas

El proyecto deberá disponer de pruebas automatizadas para validar progresivamente:

* Endpoints de la API.
* Validación de datos.
* Operaciones sobre el inventario.
* Persistencia.
* Herramientas del agente.
* Bucle principal del agente.
* Registro de conversaciones.
* Flujo completo de extremo a extremo.

Las pruebas deberán incorporarse progresivamente junto con cada funcionalidad importante.

### Decisiones aprobadas (Fase 0)

* Framework de pruebas: `pytest`.
* La API y el cliente HTTP se prueban con `TestClient` de FastAPI (compatible con `httpx.Client`), sin levantar un servidor.
* El agente se prueba con un `FakeLLM` de respuestas predefinidas, sin depender de Groq ni de la red.
* Las pruebas usan archivos CSV temporales, nunca los de `data/`.

## Dependencias

Las dependencias deberán mantenerse reducidas a las necesarias para el funcionamiento del proyecto.

Actualmente el entorno virtual contiene principalmente:

* `fastapi`
* `uvicorn`

Las nuevas dependencias deberán añadirse únicamente cuando exista una necesidad concreta y deberán quedar documentadas.

Estado verificado en Fase 0 (`.venv`, Python 3.13.15): `fastapi` 0.141.1, `uvicorn` 0.54.0, `pydantic` 2.13.5 y sus dependencias transitivas. No existe todavía archivo de dependencias.

Decisión aprobada: las dependencias se declararán en `requirements.txt` (ejecución) y `requirements-dev.txt` (desarrollo).

Dependencias aprobadas y fase en la que se instalan (no se instalan antes de la fase que las necesita):

| Dependencia | Uso | Fase |
|---|---|---|
| `python-dotenv` | Lectura de variables de entorno desde `.env` | 1 |
| `pytest` | Pruebas automatizadas (desarrollo) | 1 |
| `httpx` | Comunicación HTTP entre agente/herramientas y la API; requisito de `TestClient` | 3 |
| `groq` | Integración con la API de Groq | 5 |

La Fase 2 no añade dependencias nuevas.

## Configuración prevista

Variables en `.env` (se documentarán en `.env.example` sin valores):

* `GROQ_API_KEY`: obligatoria solo para el agente.
* `GROQ_MODEL`: modelo de Groq; se elegirá en la fase de integración con Groq verificando qué modelos con soporte de herramientas están disponibles.
* Otras variables (URL de la API, rutas de los CSV, límite de pasos del agente) se definirán cuando se implementen.

## Control de versiones

El proyecto utiliza Git y está conectado a GitHub.

Los cambios deberán realizarse de forma controlada y por fases.

No se realizarán commits ni pushes automáticamente sin aprobación.

## Compatibilidad con el repositorio existente

El repositorio procede originalmente de una plantilla de 4Geeks.

Existen archivos heredados como `server.py`, `learn.json` y un README inicial que deberán analizarse antes de decidir si continúan formando parte del proyecto.

No se deben eliminar archivos heredados durante la fase inicial sin analizar previamente su función y justificar el cambio.

Decisiones tomadas en Fase 0:

* `server.py`: servidor Flask de la plantilla para servir HTML estático; no forma parte de la arquitectura. Se revisará en la fase final de limpieza. No eliminar antes.
* `main.py`: `print("Hello World")` de la plantilla. Se revisará en la fase final de limpieza. No eliminar antes.
* `learn.json`: metadatos de la plataforma 4Geeks. Se conserva por si la plataforma lo necesita.
* `README.es.md`: eliminado intencionadamente. El proyecto tendrá un único `README.md` como documentación principal.

## Principio de evolución

Este documento describe el contexto técnico inicial.

Las decisiones técnicas podrán evolucionar durante el desarrollo cuando exista una razón justificada.

Cuando se tome una decisión arquitectónica relevante, deberá quedar documentada y explicada antes de aplicarse.
