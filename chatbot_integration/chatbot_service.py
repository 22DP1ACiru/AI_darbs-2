import os
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
from pathlib import Path

class ChatbotService:
    def __init__(self, product_data=""):
        env_path = Path('.') / '.env'
        load_dotenv(dotenv_path=env_path)
        hf_api_key = os.getenv("HUGGINGFACE_API_KEY")

        if hf_api_key is None:
            raise ValueError("HUGGINGFACE_API_KEY nav iestatīts .env failā")
        else:
            print("HUGGINGFACE_API_KEY ielādēts:", hf_api_key[:5] + "...")

        self.client = InferenceClient(api_key=hf_api_key)
        self.product_data = product_data
        self.system_instruction = f"""
[INSTRUKCIJA]
Tu esi e-veikala čatbots. 
*Atbildes jāveido tikai par e-veikalu un produktiem.* 
Ja jautājums ir par produktiem, grozu, cenām vai pasūtījumiem, atbildi tieši, izmantojot zemāk sarakstu:
{product_data}

*Ja jautājums nav saistīts ar e-veikalu, atbildi:
"Atvainojiet, es varu palīdzēt tikai ar jautājumiem par e-veikalu."*
"""

    def is_on_topic(self, user_message):
        """
        Vienkāršs filtrs, lai bloķētu ārpus tēmas jautājumus.
        Ja ziņa satur vārdus, kas nav saistīti ar e-veikalu, atgriež False.
        """
        off_topic_keywords = [
            "weather", "temperature", "news", "sports", "covid", "time",
        "movie", "music", "politics", "travel", "flight", "tourism",
        "restaurant", "hotel", "holiday", "celebrity", "stock", "finance",
        "football", "soccer", "tennis", "basketball", "recipe", "recipe for",
        "recipe of", "recipe", "recipe for", "recipe of", "programming",
        "code", "python", "java", "javascript", "math", "calculation",
        "joke", "funny", "humor", "game", "video game", "gaming", "tv show"
        ]
        user_lower = user_message.lower()
        for kw in off_topic_keywords:
            if kw in user_lower:
                return False
        return True

    def get_chatbot_response(self, user_message, chat_history=None):
        if not self.is_on_topic(user_message):
            return {"response": "Atvainojiet, es varu palīdzēt tikai ar jautājumiem par e-veikalu."}

        if chat_history is None:
            chat_history = []

        messages = [{"role": "system", "content": self.system_instruction}]
        messages.extend(chat_history)
        messages.append({"role": "user", "content": user_message})

        try:
            response = self.client.chat_completion(
                model="katanemo/Arch-Router-1.5B",
                messages=messages,
                temperature=0.7,
            )
            ai_message = response.choices[0].message.content
            return {"response": ai_message}

        except Exception as e:
            print("API kļūda:", e)
            return {"response": f"Kļūda AI API izsaukumā: {e}"}


# --- Testa palaišana ---
if __name__ == "__main__":
    product_data = "- Produkts A, 10.99$\n- Produkts B, 5.50$\n- Produkts C, 20.00$"
    bot = ChatbotService(product_data=product_data)

    # On-topic example
    print(bot.get_chatbot_response("Pastāsti par produktiem."))

    # Off-topic example
    print(bot.get_chatbot_response("Kāds ir laiks Dubajā?"))
