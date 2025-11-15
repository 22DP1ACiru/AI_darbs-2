import os
from openai import OpenAI
from dotenv import load_dotenv
import json   # JSON produktu formatēšanai

class ChatbotService:
    def __init__(self):
        # 1. SOLIS - API atslēgas ielāde
        load_dotenv()

        # Atbalsts vairākiem API key variantiem
        hf_key = (
            os.getenv("HUGGINGFACE_API_KEY")
            or os.getenv("HF_TOKEN")
            or os.getenv("HF_API_KEY")
        )
        if not hf_key:
            raise RuntimeError("Hugging Face API key not found. Set env variable.")

        # 2. SOLIS - OpenAI klienta inicializācija ar HF router
        self.client = OpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=hf_key
        )

        # 3. SOLIS - Sistēmas instrukcijas definēšana (īsa un skaidra)
        self.system_instruction = (
            "Tu esi e-veikala virtuālais asistents. Atbildi tikai par produktiem, piegādi, cenām un atgriešanu. "
            "Ieteikumus sniedz tikai no pieejamā produktu saraksta. "
            "Ja lietotājs jautā par kaut ko ārpus veikala, pieklājīgi pāradresē sarunu uz veikalā pieejamajām precēm."
        )

    def get_chatbot_response(self, user_message, chat_history=None, products_text=None):

        if chat_history is None:
            chat_history = []

        # Vienkāršs dublikātu filtrs
        try:
            if len(chat_history) >= 2:
                last_user_index = None
                for i in range(len(chat_history)-1, -1, -1):
                    if chat_history[i].get("role") == "user":
                        last_user_index = i
                        break
                if last_user_index is not None and chat_history[last_user_index]["content"].strip() == user_message.strip():
                    if last_user_index + 1 < len(chat_history) and chat_history[last_user_index+1]["role"] == "assistant":
                        return {"response": chat_history[last_user_index+1]["content"], "info": "reused_cached_response"}
        except:
            pass

        # 4. SOLIS - Ziņojumu saraksta izveide
        messages = []

        # Sistēmas instrukcija — tikai noteikumi
        messages.append({
            "role": "system",
            "content": self.system_instruction
        })

        # Produkta JSON pievienots kā "user" ziņa ar CONTEXT:
        if products_text:
            messages.append({
                "role": "user",
                "content": f"CONTEXT: Šis ir veikala produktu saraksts JSON formātā. Izmanto tikai šos produktus atbildēs:\n{products_text}"
            })

        # Sarunas vēsture
        if chat_history:
            messages.extend(chat_history)

        # Lietotāja jautājums
        messages.append({"role": "user", "content": user_message})

        # 5. SOLIS - HF API izsaukums
        try:
            completion = self.client.chat.completions.create(
                model="katanemo/Arch-Router-1.5B",
                messages=messages,
                max_tokens=300,
                temperature=0.25
            )
        except Exception as e:
            return {"response": f"Atvainojiet, servera kļūda: {str(e)}", "error": True}

        # 6. SOLIS - Atbildes apstrāde
        try:
            reply = completion.choices[0].message.content

            if not reply or not reply.strip():
                reply = "Atvainojiet, es nevarēju atrast atbildi."

            return {"response": reply}

        except Exception as e:
            return {"response": f"Neizdevās apstrādāt AI atbildi: {str(e)}", "error": True}
