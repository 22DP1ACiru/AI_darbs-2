import os
from openai import OpenAI
from dotenv import load_dotenv

class ChatbotService:
    def __init__(self):
        # 1. SOLIS — Ielādē vides mainīgos no .env faila
        load_dotenv()

        # 2. SOLIS — Izgūst Hugging Face API tokenu no vides mainīgajiem
        self.api_key = os.getenv("HUGGINGFACE_API_KEY")
        if not self.api_key:
            raise ValueError("Neizdevās atrast HUGGINGFACE_API_KEY .env failā!")

        # 3. SOLIS — Inicializē OpenAI klientu priekš HuggingFace router
        self.client = OpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=self.api_key
        )

        # 4. SOLIS — Modelis ar OpenAI formātu via HuggingFace router
        self.model_tag = "katanemo/Arch-Router-1.5B:hf-inference"

        # 5. SOLIS — Sistēmas instrukcija čata botam
        self.system_instruction = (
            "Tu esi e-veikala asistents: palīdz tikai ar jautājumiem par precēm, pirkumiem, piegādi, atgriešanu un veikala atbalstu. "
            "Neatbildi uz jautājumiem ārpus veikala tematikas."
        )

    def get_chatbot_response(self, user_message, chat_history=None):
        if chat_history is None:
            chat_history = []
        # Apvieno sistēmas instrukciju ar vēsturi un lietotāja ziņu
        messages = [{"role": "system", "content": self.system_instruction}]
        messages.extend(chat_history)
        messages.append({"role": "user", "content": user_message})

        # Sūta vaicājumu Hugging Face router endpointam (OpenAI chat formatā)
        completion = self.client.chat.completions.create(
            model=self.model_tag,
            messages=messages
        )
        return {"response": completion.choices[0].message.content}

if __name__ == "__main__":
    bot = ChatbotService()
    reply = bot.get_chatbot_response("Sveiki! Kādas preces jūs pārdodat?")
    print(reply)
