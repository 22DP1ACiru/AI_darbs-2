import os
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
from pathlib import Path

class ChatbotService:
    def __init__(self):
        # 1. SOLIS - .env faila ielāde ar diagnostiku
        env_path = Path('.') / '.env'
        load_dotenv(dotenv_path=env_path)
        hf_api_key = os.getenv("HUGGINGFACE_API_KEY")

        # Diagnostika
        if hf_api_key is None:
            raise ValueError(
                "HUGGINGFACE_API_KEY nav iestatīts vai .env fails netika atrasts!"
            )
        else:
            print("HUGGINGFACE_API_KEY ir veiksmīgi ielādēts (rādīts tikai sākuma daļa):", hf_api_key[:5] + "...")

        # 2. SOLIS - Hugging Face Inference klienta inicializācija
        try:
            self.client = InferenceClient(api_key=hf_api_key)
            print("Hugging Face klienta inicializācija veiksmīga.")
        except Exception as e:
            raise ValueError(f"Neizdevās inicializēt HF klientu: {e}")

        # 3. SOLIS - Sistēmas instrukcijas definēšana
        self.system_instruction = (
            "Tu esi draudzīgs un zinošs AI palīgs, kas palīdz lietotājam ar dažādiem jautājumiem."
        )

    def get_chatbot_response(self, user_message, chat_history=None):
        if chat_history is None:
            chat_history = []

        messages = [{"role": "system", "content": self.system_instruction}]
        messages.extend(chat_history)
        messages.append({"role": "user", "content": user_message})

        # 5. SOLIS - HF API izsaukums ar diagnostiku
        try:
            response = self.client.chat_completion(
                model="katanemo/Arch-Router-1.5B:hf-inference",
                messages=messages,
                temperature=0.7,
            )
        except Exception as e:
            print("API izsaukuma kļūda:", e)
            return {"response": f"Kļūda AI API izsaukumā: {e}"}

        # 6. SOLIS - Atbildes apstrāde
        try:
            ai_message = response.choices[0].message.content
            return {"response": ai_message}
        except (AttributeError, IndexError):
            return {"response": "AI atbilde nav pieejama."}


# --- Testa palaišana ---
if __name__ == "__main__":
    bot = ChatbotService()
    resp = bot.get_chatbot_response("Sveiki, kā klājas?")
    print("AI atbilde:", resp)
