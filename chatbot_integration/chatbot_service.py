import os
from openai import OpenAI
from dotenv import load_dotenv


class ChatbotService:
    def __init__(self):

        load_dotenv()
        api_key = os.getenv("HUGGINGFACE_API_KEY")

        self.client = OpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=api_key
        )

        self.system_instruction = (
        "You are a helpful assistant working **only** for an e-shop. "
        "You must answer **only** questions related to products, prices, descriptions, categories, delivery, or store policies. "
        "If a user asks about anything unrelated to the shop or its products, you must politely respond: "
        "'I'm sorry, but I can only help with questions about our products or services.' "
        "Keep answers short, clear, and relevant to the product catalog."
        )

    def get_chatbot_response(self, user_message, chat_history=None, product_context=None):
        if chat_history is None:
            chat_history = []

        shop_keywords = [
            "product", "price", "delivery", "order", "buy", "cart", "shop", "return",
            "warranty", "payment", "category", "stock", "available", "discount",
            "shipping", "item", "purchase", "customer", "service"
            "mouse", "keyboard", "monitor", "laptop", "headphones", "smartphone",
            "ssd", "ram", "graphics card", "processor", "tablet", "charger",
            "portable", "accessory", "gadget", "electronics", "device",
            "warranty", "refund", "exchange", "shipping", "delivery time",
            "tracking", "invoice", "billing", "checkout", "offer", "deal",
            "specification", "feature", "review", "rating",
            "brand", "model", "color", "size", "weight", "bluetooth"
        ]

        if not any(word.lower() in user_message.lower() for word in shop_keywords):
            return {
                "response": (
                    "I'm sorry, but I can only help with questions about our shop and its products. "
                    "Please ask about prices, delivery, or product details."
                )
            }

        messages = [
            {"role": "system", "content": self.system_instruction},
        ]

        messages.extend(chat_history)

        if product_context:
            messages.append({
                "role": "user",
                "content": f"Product context: {product_context}"
            })

        messages.append({
            "role": "user",
            "content": user_message
        })


        try:
            chat_completion = self.client.chat.completions.create(
                model="katanemo/Arch-Router-1.5B",
                messages=messages,
            )

            response_text = chat_completion.choices[0].message.content.strip()

            chat_history.append({"role": "assistant", "content": response_text})

            return {"response": response_text}

        except Exception as e:
            # 🔥 Ловим ошибки API, чтобы Flask не падал
            return {"error": f"Failed to get AI response: {str(e)}"}
