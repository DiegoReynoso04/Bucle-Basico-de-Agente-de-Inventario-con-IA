English | [Español](README.es.md)

# Basic AI inventory agent loop

Carla runs a small family business that supplies coffee shops. This project lets her check and update her inventory by typing in natural language in the terminal, with no forms or spreadsheets:

```text
You: 30 units of oat milk just arrived.
You: We sold 12 bags of arabica today.
You: Which products are running low?
```

It has two parts:

1. **A REST API (FastAPI)** that manages the inventory and stores it in a CSV file.
2. **An AI agent (`agent.py`)** that interprets the messages with a **Groq** language model and works on the inventory **only through the API**, using tools.

There is no frontend: the interface is the terminal. The agent talks to Carla in Spanish.

## Architecture

```text
User (terminal)
   │
   ▼
agent.py ──────────────► LLMClient (inventory_app/llm.py) ──HTTP──► Groq
   │                        (openai/gpt-oss-120b)
   ├──► ConversationLogger ──► data/conversation_log.csv
   │
   ▼
tools.py ──► InventoryApiClient ──HTTP──► FastAPI API (inventory_app/api.py)
                                               │
                                               ▼
                                        InventoryService (service.py)
                                               │
                                               ▼
                                   CsvInventoryRepository (repository.py)
                                               │
                                               ▼
                                        data/inventory.csv
```

- **The agent never reads or writes the inventory CSV.** Every operation goes through the API.
- **No agent framework or LLM SDK.** The loop is hand-written in `agent.py` and Groq is called over plain HTTP with `httpx2`.

## The API

Products have `name`, `quantity`, `unit` and `min_stock`. A product is **running low** (`low_stock: true`) when `quantity <= min_stock`.

| Method and path | What it does | Response |
|---|---|---|
| `GET /health` | Checks that the API is running | `200 {"status": "ok"}` |
| `GET /products` | Lists all products | `200` |
| `GET /products/low-stock` | Lists the products running low (low-stock alerts) | `200` |
| `GET /products/{name}` | Returns one product | `200` or `404` |
| `POST /products` | Registers a product: `{"name", "quantity", "unit", "min_stock"}` | `201`, `409` if it already exists, `422` if the data is invalid |
| `POST /products/{name}/stock` | Stock in or out: `{"change": 30}` adds and `{"change": -12}` subtracts | `200`, `404`, `409` if stock would go negative, `422` |

- **Names:** case-insensitive, accents matter, no `/` or double spaces, and `low-stock` is reserved.
- **Errors:** always shaped `{"code", "message", "details"}`. Internal errors (500) never expose system paths.
- **Interactive docs:** with the API running, at `http://127.0.0.1:8000/docs`.

## Persistence

- **Inventory:** stored in **`data/inventory.csv`**, with the columns `name,quantity,unit,min_stock`.
  - Changes survive API restarts.
  - Writes are atomic: a temporary file is written and then replaces the original.
  - The path can be changed with the `INVENTORY_CSV_PATH` variable (see configuration).
- **Initial inventory:** 8 products. Oat milk, 12 oz cup lids and vanilla syrup start out running low.

## The agent

`python agent.py` opens a conversation in the terminal. To finish, type `salir` or press Ctrl+C.

### Tools

The model receives these tools, with descriptions and parameters typed in JSON Schema. Each one calls an API endpoint:

| Tool | Parameters | Endpoint |
|---|---|---|
| `list_products` | — | `GET /products` |
| `get_low_stock` | — | `GET /products/low-stock` |
| `add_stock` | `name`, `quantity` (positive integer) | `POST /products/{name}/stock` with a positive `change` |
| `remove_stock` | `name`, `quantity` (positive integer) | `POST /products/{name}/stock` with a negative `change` |
| `create_product` | `name`, `quantity`, `unit`, `min_stock` | `POST /products` |

- **Sign of the quantities:** the model never decides the sign. `add_stock` and `remove_stock` always receive a positive quantity.
- **Validation:** the agent validates the tool name and the exact arguments before running it.
- **Unknown products:** they are never created automatically. The agent asks Carla first.

### Loop: observe → think → act → update → repeat

For each message, `handle_message()` in `agent.py`:

1. **Observe:** adds the user's message to the history and logs it.
2. **Think:** sends the history and the tools to the model.
3. **Act:** if the model requests tools, the agent runs them in order through the API.
4. **Update:** adds the model's reply and each tool result (`role="tool"` messages) to the history. Errors, such as insufficient stock, are also sent back to the model so it can explain them to Carla.
5. **Repeat:** asks the model again until it answers without requesting tools.

Three safety limits:
- **Step limit:** at most 8 model calls per message (`MAX_STEPS`).
- **Session memory:** the full history stays in memory for the whole session, so earlier messages can be referenced.
- **Groq errors:** if Groq fails, the agent shows a clear message and the session continues.

### Conversation log

Every event is appended to **`data/conversation_log.csv`**, created with the first message:

```text
actor,message,tool_call,timestamp
```

| `actor` | `message` | `tool_call` |
|---|---|---|
| `user` | What the user types | empty |
| `tool` | Tool result as JSON (`{"result": ...}` or `{"error": ...}`) | `{"name": ..., "arguments": {...}}` as JSON |
| `agent` | Reply the user sees | empty |

- **Format:** `timestamp` follows ISO 8601 with time zone.
- **Append-only:** previous records are never overwritten, not even across sessions.

## Structure

```text
agent.py                       Agent: loop, model tools and CLI
inventory_app/
  api.py                       FastAPI API (endpoints and errors)
  service.py                   Inventory business rules
  repository.py                CSV reading and writing
  models.py                    Pydantic models and naming rules
  errors.py                    Inventory exceptions
  api_client.py                HTTP client for the API (used by the agent)
  tools.py                     Agent tools
  llm.py                       Groq HTTP client (LLMClient)
  conversation_log.py          Append-only conversation log
  config.py                    Configuration from the environment and .env
data/
  inventory.csv                Inventory
  conversation_log.csv         Conversation log (created when the agent is used)
tests/                         Tests (pytest)
memory-bank/                   Project context and decisions
requirements.txt               Runtime dependencies
requirements-dev.txt           Development dependencies (adds pytest)
.env.example                   Configuration template, no secrets
```

## Requirements

- Python 3.13 or newer (tested with 3.14.6).
- A Groq API key to use the agent. The API and the regular tests don't need it.

## Installation

```bash
python -m venv .venv
```

Activate the environment:
- Windows (PowerShell): `.venv\Scripts\Activate.ps1`
- Linux and macOS: `source .venv/bin/activate`

Then install the dependencies:

```bash
pip install -r requirements-dev.txt
```

## Configuration

Copy `.env.example` to `.env` and fill in the key. `.env` is in `.gitignore` and is never committed.

| Variable | Required | Default | Use |
|---|---|---|---|
| `GROQ_API_KEY` | Yes, for the agent | — | Groq API key |
| `INVENTORY_CSV_PATH` | No | `data/inventory.csv` | Inventory CSV. A relative path is resolved from the project root |
| `INVENTORY_API_URL` | No | `http://127.0.0.1:8000` | API address used by the agent |

## Usage

You need two terminals, both with the virtual environment activated.

**Terminal 1: start the API**

```bash
uvicorn inventory_app.api:app
```

**Terminal 2: start the agent**

```bash
python agent.py
```

```text
Carla: ¡Hola! ¿En qué puedo ayudarte? (escribe "salir" para terminar)
Tú: ¿Qué productos están por agotarse?
Carla: ...
```

If the API isn't running, the agent explains it in its reply instead of crashing.

## Tests

```bash
pytest
```

- **Coverage:** the CSV repository, the service, the API, the HTTP client, the tools, the log, the Groq client and the full agent, including an end-to-end test with the API served by Uvicorn.
- **Fake Groq:** the regular tests use a fake model. They need no key, never connect to Groq and never modify `data/inventory.csv`.

**Real Groq tests (optional).** `tests/test_live_groq.py` contains tests that call the real model and consume tokens. They are skipped unless explicitly enabled.

PowerShell:

```powershell
$env:GROQ_LIVE = "1"; pytest tests/test_live_groq.py
```

Linux and macOS:

```bash
GROQ_LIVE=1 pytest tests/test_live_groq.py
```

If many run back to back, Groq may answer `HTTP 429` (per-minute limit). In that case, rerun the affected test after a minute.

## Author

**Diego Reynoso Flores** · [GitHub](https://github.com/DiegoReynoso04)
