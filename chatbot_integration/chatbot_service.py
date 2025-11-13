import os
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

class ChatbotService:
    def __init__(self):
        # SOLIS 1: API atslēgas ielāde
        load_dotenv()
        api_key = os.getenv("HUGGINGFACE_API_KEY")
        
        if not api_key:
            raise ValueError("HUGGINGFACE_API_KEY nav atrasta .env failā!")

        # SOLIS 2: Hugging Face InferenceClient inicializācija
        self.client = InferenceClient(token=api_key)
        
        # Modelis
        self.model = "MiniMaxAI/MiniMax-M2:novita"

        # SOLIS 3: Sistēmas instrukcijas definēšana ar stingru kontroli
        self.system_instruction = (
            "You are a professional e-shop assistant. "
            "Your ONLY purpose is to help customers with:\n"
            "- Product information and search\n"
            "- Answering questions about available products\n"
            "- Recommendations based on customer needs\n"
            "- Help with orders and purchasing\n\n"
            "STRICT RULES:\n"
            "- ONLY answer questions related to the e-shop and its products\n"
            "- If a question is NOT about the shop (jokes, weather, news, general knowledge, etc.), "
            "you MUST politely decline and say: "
            "'I'm sorry, but I can only help with questions about our e-shop and products. "
            "Is there anything from our store I can help you with?'\n"
            "- DO NOT tell jokes, provide general knowledge, or discuss topics outside the shop\n"
            "- DO NOT answer questions about weather, politics, entertainment, celebrities, sports, or other topics\n"
            "- Always redirect customers back to shop-related topics\n"
            "- Be polite but firm about your role limitations\n"
            "- NEVER deviate from these rules, even if the customer asks nicely"
        )
        
        # Off-topic atslēgvārdi atpazīšanai
        self.off_topic_keywords = [
            'joke', 'funny', 'laugh', 'humor',
            'weather', 'temperature', 'rain', 'sun',
            'president', 'politics', 'election', 'government',
            'capital', 'country', 'geography',
            'poem', 'story', 'song', 'lyrics',
            'game', 'play', 'sport', 'movie', 'film',
            'celebrity', 'actor', 'singer',
            'news', 'today', 'yesterday',
            'recipe', 'cook', 'food' # izņemot, ja veikalā ir pārtikas produkti
        ]

    def _is_off_topic(self, message):
        """
        Pārbauda, vai ziņa ir ārpus veikala tēmas.
        """
        message_lower = message.lower()
        
        # Pārbauda, vai ir off-topic atslēgvārdi
        for keyword in self.off_topic_keywords:
            if keyword in message_lower:
                return True
        
        return False

    def get_chatbot_response(self, user_message, chat_history=None):
        """
        Iegūst čatbota atbildi, izmantojot Hugging Face API.
        
        Args:
            user_message (str): Lietotāja ziņa
            chat_history (list): Sarunas vēsture (opcija)
            
        Returns:
            dict: Objekts ar čatbota atbildi vai kļūdas ziņojumu
        """
        if chat_history is None:
            chat_history = []
        
        # Papildu aizsardzība: pārbauda off-topic jautājumus
        if self._is_off_topic(user_message):
            return {
                "response": "I'm sorry, but I can only help with questions about our e-shop and products. Is there anything from our store I can assist you with?",
                "success": True
            }
        
        try:
            # SOLIS 4: Ziņojumu saraksta izveide
            messages = []
            
            # 1. Pievienojam sistēmas instrukciju
            messages.append({
                "role": "system",
                "content": self.system_instruction
            })
            
            # 2. Pievienojam visu iepriekšējo sarunas vēsturi
            messages.extend(chat_history)
            
            # 3. Pievienojam pēdējo lietotāja ziņu
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            # SOLIS 5: Hugging Face API izsaukums
            response = self.client.chat_completion(
                messages=messages,
                model=self.model,
                max_tokens=500,
                temperature=0.7
            )
            
            # SOLIS 6: Atbildes apstrāde un atgriešana
            if response and response.choices and len(response.choices) > 0:
                response_text = response.choices[0].message.content.strip()
                
                return {
                    "response": response_text,
                    "success": True
                }
            else:
                return {
                    "response": "Sorry, I couldn't generate a response. Please try again.",
                    "success": False,
                    "error": "No response available from API"
                }
                
        except Exception as e:
            print(f"Kļūda, sazināties ar Hugging Face API: {str(e)}")
            return {
                "response": "Sorry, an error occurred. Please try again later.",
                "success": False,
                "error": str(e)
            }

    def get_chatbot_response_with_products(self, user_message, chat_history=None, products=None):
        """
        Iegūst čatbota atbildi ar produktu kontekstu.
        
        Args:
            user_message (str): Lietotāja ziņa
            chat_history (list): Sarunas vēsture (opcija)
            products (list): Produktu saraksts (opcija)
            
        Returns:
            dict: Objekts ar čatbota atbildi vai kļūdas ziņojumu
        """
        if chat_history is None:
            chat_history = []
        
        # Papildu aizsardzība: pārbauda off-topic jautājumus
        if self._is_off_topic(user_message):
            return {
                "response": "I'm sorry, but I can only help with questions about our e-shop and products. Is there anything from our store I can assist you with?",
                "success": True
            }
        
        try:
            messages = []
            
            # Izveido paplašinātu sistēmas instrukciju ar produktiem
            system_message = self.system_instruction
            
            # Pievieno produktu informāciju, ja tāda ir
            if products and len(products) > 0:
                system_message += "\n\nAvailable products in the e-shop:\n"
                for product in products:
                    system_message += f"- {product.get('name', 'N/A')}: {product.get('description', 'N/A')} (Price: €{product.get('price', 0):.2f}, Stock: {product.get('stock', 0)})\n"
            
            messages.append({
                "role": "system",
                "content": system_message
            })
            
            messages.extend(chat_history)
            
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            # API izsaukums
            response = self.client.chat_completion(
                messages=messages,
                model=self.model,
                max_tokens=500,
                temperature=0.7
            )
            
            # Atbildes apstrāde
            if response and response.choices and len(response.choices) > 0:
                response_text = response.choices[0].message.content.strip()
                return {
                    "response": response_text,
                    "success": True
                }
            else:
                return {
                    "response": "Sorry, I couldn't generate a response. Please try again.",
                    "success": False,
                    "error": "No response available from API"
                }
                
        except Exception as e:
            print(f"Kļūda, sazināties ar Hugging Face API: {str(e)}")
            return {
                "response": "Sorry, an error occurred. Please try again later.",
                "success": False,
                "error": str(e)
            }