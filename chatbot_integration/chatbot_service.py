import os
from openai import OpenAI
from dotenv import load_dotenv

class ChatbotService:
    def __init__(self):
        # TODO: 1. SOLIS - API atslēgas ielāde
        load_dotenv()
        self.api_key = os.getenv("HUGGINGFACE_API_KEY")

        # Pārbaude, vai atslēga ir ielādēta
        if not self.api_key:
            raise ValueError("HUGGINGFACE_API_KEY nav atrasta .env failā!")

        # TODO: 2. SOLIS - OpenAI klienta inicializācija izmantojot "katanemo/Arch-Router-1.5B" modeli
        self.client = OpenAI(
            base_url="https://router.huggingface.co/v1",
            model="katanemo/Arch-Router-1.5B"
        )

        # TODO: 3. SOLIS - Sistēmas instrukcijas definēšana
        self.system_instruction = (
            "Tu esi e-veikala virtuālais asistents. "
            "Atbildi tikai uz jautājumiem par produktiem, kategorijām, cenām, "
            "piegādi, atgriešanu un veikala informāciju. "
            "Ja jautājums nav saistīts ar veikalu, pieklājīgi pasaki, ka to nevarēsi palīdzēt."
        )

    def get_chatbot_response(self, user_message, chat_history=None, products_text=""):
        if chat_history is None:
            chat_history = []
            
        # TODO: 4. SOLIS - Ziņojumu saraksta izveide masīvā
        # Sistēmas instrukcija (role: "system")
        messages = [
            {"role": "system", "content": self.system_instruction + "\n\nPieejamie produkti:\n" + products_text}
        ]
        
        # Pievieno vēsturi
        messages.extend(chat_history)

        # Pievieno lietotāja pēdējo ziņu
        messages.append({"role": "user", "content": user_message})
        
        # TODO: 5. SOLIS - HF API izsaukums ar OpenAI bibliotēku, izmantojot chat.completions.create().
        try:
            response = self.client.chat.completions.create(
                model="katanemo/Arch-Router-1.5B",
                messages=messages,
                max_tokens=200,
                temperature=0.5,
                top_p=0.9,
                frequency_penalty=0,
                presence_penalty=0
            )
        except Exception as e:
            return {"response": f"Kļūda, sazinoties ar API: {str(e)}"}
        
        # TODO: 6. SOLIS - Atbildes apstrāde un atgriešana
        # chat.completions.create() atgriež objektu ar "choices" sarakstu, tajā jāparbauda, vai ir pieejama atbilde
        try:
            ai_reply = response.choices[0].message['content']
        except:
            ai_reply = "Neizdevās saņemt atbildi no MI modeļa."

        return {"response": ai_reply}

        # Pagaidu atbilde, kas jāaizvieto ar reālo API atbildi tiklīdz būs implementēts.
        return {"response": "AI API response is not implemented yet."}
