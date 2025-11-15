import os
import requests
from dotenv import load_dotenv

class ChatbotService:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        self.api_key = os.getenv("HUGGINGFACE_API_KEY")
        
        if not self.api_key:
            print("Warning: HUGGINGFACE_API_KEY not found in environment variables")
        
        # Hugging Face OpenAI-compatible router endpoint
        self.api_url = "https://router.huggingface.co/v1/chat/completions"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

        # System instruction for e-shop assistant
        self.system_instruction = (
            "You are an e-shop assistant. ONLY answer questions about: "
            "- Products in our store\n"
            "- Order status and purchases\n" 
            "- Shopping cart and checkout\n"
            "- Store policies, shipping, returns\n"
            "- Product recommendations\n\n"
            "STRICT RULES:\n"
            "1. If asked about anything unrelated to shopping or this store, say: "
            "'I can only help with questions about our online store and products.'\n"
            "2. Keep responses brief and helpful\n"
            "3. If unsure, suggest checking the product catalog or contacting support\n"
            "4. Never discuss topics outside of e-commerce"
        )

    def get_chatbot_response(self, user_message, chat_history=None, product_context=""):
        if not self.api_key:
            return {"response": "Chatbot service is currently unavailable. Please try again later."}

        if chat_history is None:
            chat_history = []

        # Build the prompt with system instruction, context, and conversation history
        messages = [
            {"role": "system", "content": self.system_instruction},
        ]
        if product_context:
            messages.append({"role": "system", "content": f"Product context: {product_context}"})

        # Append chat history
        for msg in chat_history[-6:]:
            messages.append({"role": msg["role"], "content": msg["content"]})

        # Append current user message
        messages.append({"role": "user", "content": user_message})

        payload = {
            "model": "katanemo/Arch-Router-1.5B",
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 150
        }

        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()

            # Hugging Face returns choices as a list of message objects
            if "choices" in result and len(result["choices"]) > 0:
                bot_message = result["choices"][0]["message"]
                bot_response = bot_message.get("content") or bot_message.get("content", "")
                return {"response": bot_response.strip() if bot_response else "I didn't get a proper response."}

            return {"response": "I didn't get a proper response. Please try again."}

        except requests.exceptions.RequestException as e:
            print(f"Hugging Face API error: {e}")
            return {"response": "The assistant is temporarily unavailable. Please try again later."}
