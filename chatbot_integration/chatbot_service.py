from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv

class ChatbotService:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("HUGGINGFACE_API_KEY")
        if not self.api_key:
            raise RuntimeError("HUGGINGFACE_API_KEY is not set in the .env file.")

        # HF InferenceClient with chat endpoint
        self.client = InferenceClient(token=self.api_key)

    def get_chatbot_response(self, user_message, chat_history=None):
        if chat_history is None:
            chat_history = []

        # Get products from the DB as a simple list
        from routes.shop import get_products_from_db
        products_info = get_products_from_db()

        # Strict system instruction
        system_instruction = (
            "You are an online store assistant. Only answer questions about available store products, "
            "orders, delivery, and returns. "
            "If a question is not related to the store, respond only: 'I can only assist with store-related information.'\n"
            "Available products:\n"
            f"{products_info}"
        )

        # Build messages list
        messages = [{"role": "system", "content": system_instruction}]
        messages.extend(chat_history)
        messages.append({"role": "user", "content": user_message})

        # HF API call
        try:
            response = self.client.chat.completions.create(
                model="katanemo/Arch-Router-1.5B",
                messages=messages,
                temperature=0.0,
                max_tokens=256
            )
        except Exception as e:
            return {"response": f"An error occurred with the HF API call: {str(e)}"}

        # Process response
        if response and hasattr(response, "choices") and len(response.choices) > 0:
            bot_reply = response.choices[0].message.get("content", "").strip()
            return {"response": bot_reply}
        else:
            return {"response": "HF API did not return a response."}
