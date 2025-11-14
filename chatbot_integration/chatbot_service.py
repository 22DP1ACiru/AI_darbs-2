import os
import requests
from dotenv import load_dotenv

class ChatbotService:
    def __init__(self):

        # Ielādē API atslēgu no .env
        load_dotenv()
        self.api_key = os.getenv("HUGGINGFACE_API_KEY")

        if not self.api_key:
            raise ValueError("API key not found!")

        # HuggingFace modelis
        self.api_url = "https://router.huggingface.co/v1/chat/completions"

        self.system_instruction = (
            "You are an AI shopping assistant for an online store. "
            "You ONLY answer questions related to the products, prices, stock levels, "
            "orders, shopping cart, checkout, or general information about the shop. "
            "You DO NOT answer questions unrelated to the store. "
            "If a user asks about anything outside the shop context, politely refuse "
            "with a short message stating you can only help with store-related topics. "
            "You MUST use the provided product catalog to answer product questions. "
            "If the information is not in the catalog, say: "
            "\"I don't have information about that product.\""
        )



    # AI atbildes atgriezsana
    def get_chatbot_response(self, user_message, chat_history=None, extra_system_message=""):
        if chat_history is None:
            chat_history = []

        system_message = {
            "role": "system",
            "content": self.system_instruction + "\n\n" + extra_system_message
        }

        messages = [system_message]

        # Pievieno sarunas vēsturi
        messages.extend(chat_history)

        # Pievieno jaunāko lietotāja ziņu
        messages.append({"role": "user", "content": user_message})

        # Izsauc AI api modeli
        payload = {
            "model": "katanemo/Arch-Router-1.5B",
            "messages": messages,
            "max_tokens": 200,
            "temperature": 0.7
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(self.api_url, json=payload, headers=headers)
            response_json = response.json()
        except Exception as e:
            return {"response": f"API call error: {e}"}

        # Atbildes apstrade
        try:
            bot_reply = response_json["choices"][0]["message"]["content"]
        except Exception:
            bot_reply = f"Error returning AI response: {response_json}"

        return {"response": bot_reply}
