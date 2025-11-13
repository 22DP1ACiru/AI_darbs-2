import os
from openai import OpenAI
from dotenv import load_dotenv

class ChatbotService:
    def __init__(self):
        # 1. SOLIS - API atslēgas ielāde
        load_dotenv()
        api_key = os.getenv("HUGGINGFACE_API_KEY")
        
        if not api_key:
            raise ValueError("HUGGINGFACE_API_KEY nav atrasta .env failā")

        # 2. SOLIS - OpenAI klienta inicializācija
        self.client = OpenAI(
            base_url="https://api-inference.huggingface.co/v1/",
            api_key=api_key
        )
        
        self.model = "katanemo/Arch-Router-1.5B"

        # 3. SOLIS - Sistēmas instrukcijas definēšana
        self.system_instruction = (
            "You are a helpful e-shop assistant for 'My E-Shop'. "
            "Your role is to help customers with product information, answer questions about the shop, "
            "assist with navigation, and provide recommendations. "
            "IMPORTANT RULES:\n"
            "1. ONLY answer questions related to the e-shop, its products, orders, shipping, and shopping assistance.\n"
            "2. If asked about topics unrelated to the e-shop (politics, weather, personal advice, etc.), "
            "politely redirect the user back to shopping-related topics.\n"
            "3. Be friendly, professional, and concise in your responses.\n"
            "4. When discussing products, reference the available product list provided.\n"
            "5. If you don't have specific information, be honest and suggest contacting customer support.\n"
            "6. Do not make up product information that isn't in the provided list.\n"
            "7. Always stay in character as an e-shop assistant."
        )

    def get_chatbot_response(self, user_message, chat_history=None, product_info=None):
        if chat_history is None:
            chat_history = []
        
        try:
            # 4. SOLIS - Ziņojumu saraksta izveide
            messages = []
            
            system_message = self.system_instruction
            if product_info:
                system_message += f"\n\nAVAILABLE PRODUCTS:\n{product_info}"
            
            messages.append({
                "role": "system",
                "content": system_message
            })
            
            messages.extend(chat_history)
            
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            # 5. SOLIS - API izsaukums
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1000,
                temperature=0.7,
                stream=False
            )
            
            # 6. SOLIS - Atbildes apstrāde
            if response.choices and len(response.choices) > 0:
                assistant_message = response.choices[0].message.content
                return {
                    "response": assistant_message,
                    "success": True
                }
            else:
                return {
                    "response": "I apologize, but I couldn't generate a response. Please try again.",
                    "success": False
                }
                
        except Exception as e:
            print(f"Error in chatbot service: {str(e)}")
            return {
                "response": "I'm sorry, I'm having trouble connecting right now. Please try again in a moment.",
                "success": False,
                "error": str(e)
            }