import os
import logging
from typing import List, Dict, Any

from dotenv import load_dotenv
from openai import OpenAI

# Load .env
load_dotenv()

HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

if not HF_API_KEY:
    raise RuntimeError("Missing HUGGINGFACE_API_KEY in .env")

# ✅ Correct Hugging Face OpenAI-compatible endpoint
client = OpenAI(
    api_key=HF_API_KEY,
    base_url="https://router.huggingface.co/v1"
)

SYSTEM_MESSAGE = """
You are an online store assistant.
You only help with products from the store.

Rules:
- ONLY use products from the provided product list.
- If the question is unrelated to the store, answer:
  "I can only assist with products from our online store."
- Do NOT invent new products.
- Keep responses short and helpful.
"""

SHOP_KEYWORDS = [
    "product", "buy", "price", "cost", "store", "shop", "order",
    "delivery", "discount", "model", "specifications", "in stock"
]


def build_product_context(products: List[Dict[str, Any]]) -> str:
    if not products:
        return "There are no available products in the store."

    lines = ["List of available products:"]
    for p in products:
        name = p.get("name", "Unnamed Product")
        price = p.get("price", "Unknown")
        desc = p.get("description", "") or ""

        lines.append(f"- {name}, price: {price}. Description: {desc}")

    return "\n".join(lines)


def is_shop_related(message: str, product_context: str) -> bool:
    text = (message or "").lower()

    if any(word in text for word in SHOP_KEYWORDS):
        return True

    for line in product_context.lower().splitlines():
        if line.startswith("- "):
            name = line[2:].split(",")[0].strip()
            if name and name in text:
                return True

    return False


def get_chatbot_response(
    user_message: str,
    history: List[Dict[str, str]],
    products: List[Dict[str, Any]]
) -> str:
    try:
        product_context = build_product_context(products)

        # Block unrelated questions
        if not is_shop_related(user_message, product_context):
            return "I can only assist with products from our online store."

        messages = [{"role": "system", "content": SYSTEM_MESSAGE}]

        # Add history
        for msg in history:
            role = msg.get("role")
            content = msg.get("content")
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content})

        # Add user message with products
        messages.append({
            "role": "user",
            "content": (
                f"{product_context}\n\n"
                f"User question: {user_message}\n"
                f"Use ONLY the products above in your answer."
            )
        })

        # ✅ REQUIRED BY PDF: katanemo/Arch-Router-1.5B
        response = client.chat.completions.create(
            model="katanemo/Arch-Router-1.5B",
            messages=messages,
            max_tokens=256,
            temperature=0.4,
        )

        return response.choices[0].message.content.strip()

    except Exception:
        logging.exception("Error while calling the Hugging Face API")
        return "An error occurred while processing your request. Please try again later."
