import os
from openai import OpenAI
from dotenv import load_dotenv

class ChatbotService:
    def __init__(self):
        load_dotenv()
        hf_api_key = os.getenv("HUGGINGFACE_API_KEY")

        if not hf_api_key:
            raise ValueError("HUGGINGFACE_API_KEY nav atrasts .env failā!")

        self.client = OpenAI(
            api_key=hf_api_key,
            base_url="https://router.huggingface.co/v1"  
        )

        self.system_instruction = (
            "You are an AI assistant for this e-shop website ONLY. "
            "You MUST answer ONLY about products, prices, stock, shopping, cart, checkout, or delivery. "
            "You MUST NEVER answer jokes, personal questions, stories, politics, or anything not related to this shop. "
            "If the user asks anything off-topic, respond ONLY with: "
            "'I can only help with questions about our shop and products.' "
            "Use the product list below to give accurate answers. "
            "Be polite, clear, and helpful."
        )

    def get_chatbot_response(self, user_message, chat_history=None, product_list=""):
        if chat_history is None:
            chat_history = []

        messages = [
            {"role": "system", "content": self.system_instruction + "\n\nAvailable products:\n" + product_list},
            *chat_history,
            {"role": "user", "content": user_message}
        ]

        try:
            response = self.client.chat.completions.create(
                model="katanemo/Arch-Router-1.5B",  
                messages=messages,
                max_tokens=256,
                temperature=0.7
            )
            return {"response": response.choices[0].message.content.strip()}
        except Exception as e:
            return {"error": f"AI kļūda: {str(e)}"}