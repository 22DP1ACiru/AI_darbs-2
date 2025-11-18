import os
from openai import OpenAI
from dotenv import load_dotenv

class ChatbotService:
    def __init__(self):
        # TODO: 1. SOLIS - API atslēgas ielāde
        # load_dotenv(), lai ielādētu mainīgos no .env faila.
        # os.getenv(), lai nolasītu "HUGGINGFACE_API_KEY".
        load_dotenv()
        api_key = os.getenv("HUGGINGFACE_API_KEY")
        # Pārbauda vai API atslēga ir 
        if not api_key:
            raise ValueError("HUGGINGFACE_API_KEY nav iestatīts .env failā")

        # TODO: 2. SOLIS - OpenAI klienta inicializācija izmantojot "katanemo/Arch-Router-1.5B" modeli
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://router.huggingface.co/v1",
        )


        self.model = self.model = "katanemo/Arch-Router-1.5B:hf-inference"


        # TODO: 3. SOLIS - Sistēmas instrukcijas definēšana
        self.system_instruction = (
            "You are a friendly and helpful e-shop assistant. "
            "You answer only questions related to this online store, its products, "
            "ordering process, delivery, and user profile. "
            "Give short, clear, and helpful answers. "
            "If the user asks something unrelated to the shop, you MUST refuse. "
            "DO NOT answer any questions that are not connected with this website's products or services. "
            "If the question is unrelated, ALWAYS reply: "
            "\"Sorry, I can only help with information about our online shop and its products.\""
        )
    def get_chatbot_response(self, user_message, chat_history=None):
        if chat_history is None:
            chat_history = []
        # --- HARD FILTER: Only allow questions related to the e-shop and its products ---
        # If the message contains none of these keywords, we immediately return a fixed reply
        # and DO NOT call the AI model (this reduces unnecessary API usage).
        allowed_keywords = [
            "product", "products", "price", "order", "delivery", "cart",
            "shop", "item", "stock", "checkout", "payment", "shipping",
            "prece", "preces", "cena", "pasūtījums", "piegāde", "grozs", "veikals"
        ]

        lower_msg = user_message.lower()

        # If the message is not related to the shop → return static reply
        if not any(word in lower_msg for word in allowed_keywords):
            return {
                "response": (
                    "Sorry, I can only help with information about our online shop, "
                    "its products, prices, orders, and delivery. "
                    "Please ask something related to our e-shop."
                )
            }
        # --- ONLY IF MESSAGE IS VALID → build messages for the model ---
        messages = [
            {"role": "system", "content": self.system_instruction}
        ]
        messages.extend(chat_history)
        messages.append({"role": "user", "content": user_message})
            
        # TODO: 4. SOLIS - Ziņojumu saraksta izveide masīvā
        # Tajā jābūt sistēmas instrukcijai, visai sarunas vēsture un pēdējai lietotāja ziņa.
        # 1. Sistēmas instrukcija (role: "system")
        # 2. Visa iepriekšējā sarunas vēsture (izmantojot .extend(), lai pievienotu visus elementus no chat_history)
        # 3. Pēdējā lietotāja ziņa (role: "user")
        
        # 1
        messages = [
            {"role": "system", "content": self.system_instruction}
        ]
        
        # 2
        messages.extend(chat_history)
        
        # 3
        
        messages.append({"role": "user", "content": user_message})

        # TODO: 5. SOLIS - HF API izsaukums ar OpenAI bibliotēku, izmantojot chat.completions.create().
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=256,
                temperature=0.4,
            )
        # TODO: 6. SOLIS - Atbildes apstrāde un atgriešana
        # chat.completions.create() atgriež objektu ar "choices" sarakstu, tajā jāparbauda, vai ir pieejama atbilde
            bot_reply = ""

            if completion and completion.choices:
                first_choice = completion.choices[0]
                # Jaunākajā OpenAI stilā atbilde ir iekš first_choice.message.content
                if hasattr(first_choice, "message") and first_choice.message:
                    bot_reply = (first_choice.message.content or "").strip()
                # Drošības pēc – ja būtu vecāks formāts
                elif hasattr(first_choice, "text"):
                    bot_reply = (first_choice.text or "").strip()

            if not bot_reply:
                bot_reply = "I am sorry, but I couldn't generate a response at this time."

        except Exception as e:
            print(f"Chatbot error: {e}")
            bot_reply = "I am sorry, but I am currently unable to respond."

        return {"response": bot_reply}
        # Pagaidu atbilde, kas jāaizvieto ar reālo API atbildi tiklīdz būs implementēts.
        #return {"response": "AI API response is not implemented yet."}
