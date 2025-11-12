import os
from openai import OpenAI
from dotenv import load_dotenv

class ChatbotService:
    def __init__(self):
        # oriģinālie TODO komentāri paliek, lai izsekotu katru soli
        # TODO: 1. SOLIS - API atslēgas ielāde
        # load_dotenv(), lai ielādētu mainīgos no .env faila.
        # os.getenv(), lai nolasītu "HUGGINGFACE_API_KEY".
        load_dotenv()
        self.api_key = os.getenv("HUGGINGFACE_API_KEY")
        
        if not self.api_key:
            raise ValueError("HUGGINGFACE_API_KEY environment variable not set")

        # TODO: 2. SOLIS - OpenAI klienta inicializācija izmantojot "katanemo/Arch-Router-1.5B" modeli
        self.client = OpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=self.api_key
        )
        self.model = "katanemo/Arch-Router-1.5B"

        # TODO: 3. SOLIS - Sistēmas instrukcijas definēšana
        self.system_instruction = (
            "You are an AI assistant for an electronics e-shop specializing in computers and peripheral devices. "
            "Your role is to help customers with product information, recommendations, order assistance, and general inquiries about the shop.\n\n"
            "Guidelines:\n"
            "- Be friendly, helpful, and professional\n"
            "- Provide accurate information about electronics products\n"
            "- Help customers find suitable products based on their needs\n"
            "- Assist with technical questions about computers and peripherals\n"
            "- If you don't know something, admit it and suggest contacting customer support\n"
            "- Keep responses concise but informative\n"
            "- Focus on helping customers make informed purchasing decisions\n\n"
        )

    def get_chatbot_response(self, user_message, chat_history=None):
        if chat_history is None:
            chat_history = []
            
        # TODO: 4. SOLIS - Ziņojumu saraksta izveide masīvā
        # Tajā jābūt sistēmas instrukcijai, visai sarunas vēsture un pēdējai lietotāja ziņa.
        # 1. Sistēmas instrukcija (role: "system")
        # 2. Visa iepriekšējā sarunas vēsture (izmantojot .extend(), lai pievienotu visus elementus no chat_history)
        # 3. Pēdējā lietotāja ziņa (role: "user")
        messages = [
            {"role": "system", "content": self.system_instruction}
        ]
        # pievienot sarunu vēsturi
        messages.extend(chat_history)
        # pievienot pašreizējo lietotāja ziņojumu
        messages.append({"role": "user", "content": user_message})
        try:
            # TODO: 5. SOLIS - HF API izsaukums ar OpenAI bibliotēku, izmantojot chat.completions.create().
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=300,
                temperature=0.7,
                top_p=0.9
            )
            
            # TODO: 6. SOLIS - Atbildes apstrāde un atgriešana
            # chat.completions.create() atgriež objektu ar "choices" sarakstu, tajā jāparbauda, vai ir pieejama atbilde
            if response.choices and len(response.choices) > 0:
                assistant_response = response.choices[0].message.content.strip()
                return {"response": assistant_response, "status": "success"}
            else:
                return {"response": "Sorry, I couldn't generate a response. Please try again.", "status": "error"}
                
        except Exception as e:
            # error handling, ja radās call kļūdas
            error_message = f"Sorry, I'm experiencing technical difficulties. Please try again later. Error: {str(e)}"
            return {"response": error_message, "status": "error"}
        