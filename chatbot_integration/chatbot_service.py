# chatbot_integration/chatbot_service.py
import os
import httpx
from openai import OpenAI
from dotenv import load_dotenv
from models import Product

load_dotenv()

class ChatbotService:
    def __init__(self):
        api_key = os.getenv("HUGGINGFACE_API_KEY")
        if not api_key:
            raise ValueError("HUGGINGFACE_API_KEY nav .env failā!")

        http_client = httpx.Client(timeout=30.0)
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api-inference.huggingface.co/v1",
            http_client=http_client
        )

        self.system_prompt = {
            "role": "system",
            "content": (
                "Tu esi e-veikala asistents. Atbildi īsi, precīzi un tikai par precēm. "
                "Ja jautājums nav par veikalu — saki: 'Atvainojiet, es palīdzu tikai ar e-veikalu.'"
            )
        }

    def _get_products(self):
        try:
            products = Product.query.all()
            if not products:
                return "Nav preču."
            return "Pieejamās preces:\n" + "\n".join(
                f"- {p.name}: {p.price} EUR, noliktavā {p.stock}" for p in products
            )
        except:
            return "Nevarēju ielādēt preces."

    def _is_relevant(self, msg: str) -> bool:
        keywords = ["prece", "cena", "pirkt", "veikals", "pieejams", "kas ir", "cik", "noliktava"]
        return any(k in msg.lower() for k in keywords)

    def get_chatbot_response(self, user_msg: str, history=None):
        if history is None:
            history = []
        try:
            if not self._is_relevant(user_msg):
                return {"response": "Atvainojiet, es palīdzu tikai ar e-veikalu."}

            products = self._get_products()
            full_msg = f"{products}\nJautājums: {user_msg}"

            messages = [self.system_prompt] + history + [{"role": "user", "content": full_msg}]

            completion = self.client.chat.completions.create(
                model="katanemo/Arch-Router-1.5B",
                messages=messages,
                max_tokens=150,
                temperature=0.7
            )
            return {"response": completion.choices[0].message.content.strip()}
        except Exception as e:
            print(f"[API ERROR] {e}")
            return {"response": "Tehniska kļūda. Mēģiniet vēlāk."}