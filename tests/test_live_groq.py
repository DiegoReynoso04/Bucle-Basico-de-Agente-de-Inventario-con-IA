"""Prueba real contra Groq (consume tokens). No forma parte de la suite normal.

Solo se ejecuta de forma explícita:

    $env:GROQ_LIVE = "1"; pytest tests/test_live_groq.py

Comprueba lo que los tests simulados no pueden: que el endpoint, el modelo y el
formato de tool calls siguen siendo los que espera LLMClient, y que el agente completo
funciona con el modelo real (con la API en TestClient sobre un CSV temporal).
"""

import csv
import os

import pytest

import agent
from inventory_app.api_client import InventoryApiClient
from inventory_app.config import get_settings
from inventory_app.conversation_log import ConversationLogger
from inventory_app.llm import LLMClient

pytestmark = pytest.mark.skipif(
    os.getenv("GROQ_LIVE") != "1", reason="prueba real con Groq: requiere GROQ_LIVE=1"
)


@pytest.fixture
def llm() -> LLMClient:
    api_key = get_settings().groq_api_key
    if not api_key:
        pytest.fail("GROQ_API_KEY no está definida en .env")
    return LLMClient(api_key)


def test_live_text_response(llm):
    response = llm.complete([{"role": "user", "content": "Responde solo con la palabra: hola"}])

    assert response["content"].strip()
    assert response["tool_calls"] == []


def test_live_tool_call(llm):
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_low_stock",
                "description": "Devuelve los productos del inventario que están por agotarse.",
                "parameters": {"type": "object", "properties": {}},
            },
        }
    ]

    response = llm.complete(
        [{"role": "user", "content": "¿Qué productos están por agotarse? Usa la herramienta."}], tools
    )

    assert [call["name"] for call in response["tool_calls"]] == ["get_low_stock"]
    # Solo se comprueba que los argumentos llegan como objeto: en la primera prueba real,
    # el modelo envió {"": {}} para esta herramienta sin parámetros. Qué hacer con
    # argumentos inesperados es responsabilidad del agente (Fase 6), no de LLMClient.
    assert isinstance(response["tool_calls"][0]["arguments"], dict)


def test_live_agent_answers_low_stock_question(llm, client, tmp_path):
    log_path = tmp_path / "conversation_log.csv"
    messages = [{"role": "system", "content": agent.SYSTEM_PROMPT}]

    reply = agent.handle_message(
        "¿Qué productos están por agotarse?",
        messages,
        llm,
        InventoryApiClient(client),
        ConversationLogger(log_path),
    )

    with log_path.open(encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))
    tool_names = [row["tool_call"] for row in rows if row["actor"] == "tool"]
    assert any('"get_low_stock"' in name for name in tool_names)
    assert reply != agent.LIMIT_REPLY
    # sample_products: Leche de avena (12 <= 20) y Jarabe de vainilla (4 <= 4).
    assert "avena" in reply.lower()
