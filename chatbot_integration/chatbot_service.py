import os
from openai import OpenAI
from dotenv import load_dotenv

class ChatbotService:
    def __init__(self):
        # 1. SOLIS — Vides mainīgo ielāde no .env faila
        load_dotenv()
        api_key = os.getenv("HUGGINGFACE_API_KEY")
        if api_key is None:
            raise ValueError("Neizdevās atrast HUGGINGFACE_API_KEY .env failā!")

        # 2. SOLIS — OpenAI klienta inicializācija Hugging Face modeļa lietošanai
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.endpoints.anyscale.com/v1"
        )

        # 3. SOLIS — Sistēmas instrukcija: bots darbojas kā internetveikala konsultants
        self.system_instruction = (
            "Tu esi e-veikala asistents: palīdz tikai ar jautājumiem par precēm, pirkumiem, piegādi, atgriešanu un veikala atbalstu."
            " Neatbildi uz jautājumiem ārpus veikala tematikas."
        )

    def get_chatbot_response(self, user_message, chat_history=None):
        if chat_history is None:
            chat_history = []

        # 4. SOLIS — Ziņojumu masīva sagatavošana API izsaukumam
        # Vispirms pievieno sistēmas instrukciju
        messages = [
            {"role": "system", "content": self.system_instruction}
        ]
        # Pievieno iepriekšējo čata vēsturi (ja ir)
        messages.extend(chat_history)
        # Pievieno aktuālo lietotāja ziņojumu
        messages.append({"role": "user", "content": user_message})

        # 5. SOLIS — API izsaukums ar modeli "katanemo/arch-router-1.5b"
        response = self.client.chat.completions.create(
            model="katanemo/arch-router-1.5b",
            messages=messages,
            temperature=0.3,
            max_tokens=512
        )

        # 6. SOLIS — Atbildes apstrāde un atgriešana
        # Ja ir pieejama atbilde, nodod to lietotājam, pretējā gadījumā — kļūdas ziņojums
        if response and hasattr(response, "choices") and len(response.choices) > 0:
            return {"response": response.choices[0].message["content"]}
        return {"response": "Kļūda: bots nesaņēma atbildi no AI API."}
