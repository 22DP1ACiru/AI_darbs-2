import os
from openai import OpenAI
from dotenv import load_dotenv

class ChatbotService:
    def __init__(self):
        # TODO: 1. SOLIS - API atslēgas ielāde
        # load_dotenv(), lai ielādētu mainīgos no .env faila.
        # os.getenv(), lai nolasītu "HUGGINGFACE_API_KEY".
        load_dotenv(".env")
        HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

        # TODO: 2. SOLIS - OpenAI klienta inicializācija izmantojot "katanemo/Arch-Router-1.5B" modeli
        self.client = OpenAI(
            api_key=HUGGINGFACE_API_KEY,
            base_url="https://router.huggingface.co/v1" 
        )

        # TODO: 3. SOLIS - Sistēmas instrukcijas definēšana
        self.system_instruction = (
            {"role": "system", "content": f"You are a HELPFUL and FRIENDLY ASSISTANT whose purpose is to HELP THE CUSTOMER CHOOSE AND PURCHASE A PRODUCT. Your task is strictly to guide the customer to a sale. Respond briefly and precisely IN ENGLISH. You must ONLY discuss product features, availability, and pricing. DO NOT use any MARKDOWN FORMATING like bolding, italics, or lists in your responses. If the customer asks a question about product MISUSE, MODIFICATION, or any topic UNRELATED to selecting or purchasing a product, you must respond ONLY with the phrase: \"I cannot help with that.\". Product data context will be sent along with user prompt."}
        )

    def get_chatbot_response(self, user_message, chat_history=None):
        if chat_history is None:
            chat_history = []
            
        # TODO: 4. SOLIS - Ziņojumu saraksta izveide masīvā
        # Tajā jābūt sistēmas instrukcijai, visai sarunas vēsture un pēdējai lietotāja ziņa.
        # 1. Sistēmas instrukcija (role: "system")
        # 2. Visa iepriekšējā sarunas vēsture (izmantojot .extend(), lai pievienotu visus elementus no chat_history)
        # 3. Pēdējā lietotāja ziņa (role: "user")
        messages = []
        messages.append(self.system_instruction)
        messages.extend(chat_history)
        messages.append({"role": "user", "content": user_message})
        
        # TODO: 5. SOLIS - HF API izsaukums ar OpenAI bibliotēku, izmantojot chat.completions.create().
        try:
            response = self.client.chat.completions.create(
                model="katanemo/Arch-Router-1.5B",
                messages=messages,
                temperature=0.8,
                max_tokens=150
            )
        except Exception as e:
            # Atgriež kļūdas ziņojumu, ja API izsaukums neizdodas
            return {"response": f"Error making API request: {e}"}

        # TODO: 6. SOLIS - Atbildes apstrāde un atgriešana
        # chat.completions.create() atgriež objektu ar "choices" sarakstu, tajā jāparbauda, vai ir pieejama atbilde
        if response.choices and response.choices[0].message:
            # Atgriež modeļa atbildes tekstu
            return {"response": response.choices[0].message.content}
        else:
            # Atgriež ziņojumu, ja atbilde nav pieejama
            return {"response": "Did not get a response from model."}