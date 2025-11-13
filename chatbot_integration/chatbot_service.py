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
            api_key=os.environ["HUGGINGFACE_API_KEY"],
        )

        # TODO: 3. SOLIS - Sistēmas instrukcijas definēšana
        self.system_instruction = (
            "You are a virtual assistant for an online shop. "
            "Answer only questions related to products, categories, prices, "
            "shipping, returns, and store information. "
            "If the question is unrelated to the shop, politely inform that you cannot assist."
            "If you are asked in other languages, say that you can only respond in English."
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
                max_tokens=1024,
                temperature=0.5,
                top_p=0.9,
                frequency_penalty=0,
                presence_penalty=0
            )
        except Exception as e:
            return {"response": f"Error contacting API: {str(e)}"}
        
        # TODO: 6. SOLIS - Atbildes apstrāde un atgriešana
        # chat.completions.create() atgriež objektu ar "choices" sarakstu, tajā jāparbauda, vai ir pieejama atbilde
        try:
            # HuggingFace Router var atgriezt vairākos formātos
            if hasattr(response, "choices"):
                ai_reply = response.choices[0].message.content
            elif hasattr(response, "output"):
                ai_reply = response.output[0].content[0].text
            elif hasattr(response, "output_text"):
                ai_reply = response.output_text
            else:
                ai_reply = str(response)
        except Exception as e:
            ai_reply = f"Error processing response: {str(e)}"

        return {"response": ai_reply}
