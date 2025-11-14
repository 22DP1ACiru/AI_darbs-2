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
 
    def get_chatbot_response(self, user_message, chat_history=None, products_info=""):
        """
        Get chatbot response with product information included in the system prompt.
        Args:
            user_message: Current user message
            chat_history: Previous conversation history
            products_info: Product information from database
        """
        if chat_history is None:
            chat_history = []
            
        # pārbaudīt vai ziņa ir saistīta ar e-veikalu
        if self._is_clearly_unrelated(user_message):
            return {
                "response": "I specialize in helping with electronics products and our e-shop services. How can I assist you with computers, peripherals, or your order today?",
                "status": "success"
            }
            
        # TODO: 3. SOLIS - Sistēmas instrukcijas definēšana ar produktu informāciju
        system_instruction = self._create_system_prompt(products_info)
        
        # TODO: 4. SOLIS - Ziņojumu saraksta izveide masīvā
        # Tajā jābūt sistēmas instrukcijai, visai sarunas vēsture un pēdējā lietotāja ziņa.
        # 1. Sistēmas instrukcija (role: "system")
        # 2. Visa iepriekšējā sarunas vēsture (izmantojot .extend(), lai pievienotu visus elementus no chat_history)
        # 3. Pēdējā lietotāja ziņa (role: "user")
        messages = [
            {"role": "system", "content": system_instruction}
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
                max_tokens=250,
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
            error_message = "Sorry, I'm experiencing technical difficulties. Please try again later."
            return {"response": error_message, "status": "error"}
    
    def _create_system_prompt(self, products_info):
        """Create system prompt with current product information."""
        base_prompt = (
            "You are a helpful AI assistant for an electronics e-shop. "
            "Your purpose is to assist customers with electronics products, orders, and shop services.\n\n"
            
            "IMPORTANT GUIDELINES:\n"
            "1. Stay focused on electronics, computers, peripherals, and shop-related topics\n"
            "2. If asked about unrelated topics, politely redirect to shop services\n"
            "3. Only provide information about products from the current catalog\n"
            "4. Keep responses concise and helpful\n"
            "5. Be friendly and professional\n\n"
        )
        
        # pievienot informāciju par produktu ja ir pieejama
        if products_info:
            base_prompt += f"CURRENT PRODUCT CATALOG:\n{products_info}\n\n"
        
        base_prompt += (
            "TOPICS YOU CAN HELP WITH:\n"
            "- Computers, laptops, tablets\n"
            "- Peripherals: mice, keyboards, monitors, printers\n"
            "- Storage: SSDs, hard drives, USB drives\n"
            "- Networking: routers, cables, adapters\n"
            "- Gaming equipment\n"
            "- Product specifications and pricing\n"
            "- Order status and shipping\n"
            "- Product availability\n"
            "- Technical support for electronics\n"
            "- Product recommendations\n\n"
            
            "RESPONSE STYLE:\n"
            "- Be helpful and informative\n"
            "- Keep answers under 100 words when possible\n"
            "- Focus on the customer's needs\n"
            "- Use the product catalog for accurate information\n"
            "- If unsure, suggest contacting customer support\n"
        )
        
        return base_prompt
    
    def _is_clearly_unrelated(self, user_message):
        """
        Simple check for clearly unrelated questions to save API calls.
        Only blocks obvious non-shop questions.
        """
        user_message_lower = user_message.lower()
        
        # nesaistoši jautājumi
        clearly_unrelated = [
            'politics', 'government', 'election', 'president',
            'religion', 'god', 'church', 'bible', 'quran',
            'sports', 'football', 'basketball', 'tennis',
            'movie', 'film', 'actor', 'celebrity',
            'weather', 'climate', 'forecast',
            'medical', 'health', 'doctor', 'hospital',
            'financial advice', 'investment', 'stock market',
            'legal advice', 'lawyer', 'court'
        ]
        
        # pārbaudīt un izslēgt nesaistošus jautājumus
        return any(topic in user_message_lower for topic in clearly_unrelated)
    