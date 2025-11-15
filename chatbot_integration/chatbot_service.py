import os
from dotenv import load_dotenv
try:
    import openai
except Exception:
    openai = None

class ChatbotService:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        self.api_key = os.getenv("HUGGINGFACE_API_KEY")
        self.router_url = "https://router.huggingface.co/v1"
        self.model = os.getenv("HF_ROUTER_MODEL", "meta-llama/Llama-3.1-8B-Instruct")
        # Define context with available products for the assistant
        self.products_context = (
            "Available products in our shop:\n"
            "- Wireless Ergonomic Mouse ($29.99)\n"
            "- Mechanical Gaming Keyboard ($89.99)\n"
            "- Noise-Cancelling Headphones ($149.99)\n"
            "- USB-C Hub Multiport Adapter ($39.99)\n"
            "- Portable SSD 1TB ($119.99)\n"
        )
        # Define system instructions for the chatbot
        self.system_instruction = (
            "You are an e-commerce assistant for an online shop. "
            "You must ONLY answer questions related to the shop, its products, or shopping. "
            "If the user asks about anything else (math, geography, politics, etc.), politely refuse and redirect to shop topics. "
            "Do NOT solve math problems, do NOT give opinions, and do NOT acknowledge unrelated topics. "
            "Always steer the conversation back to the shop and its products. "
            "Be friendly, concise, and helpful.\n"
            f"{self.products_context}"
        )

    def get_chatbot_response(self, user_message, chat_history=None):
        """
        Generate a chatbot response using HuggingFace Router API.
        """

        # Limit user input to 500 characters
        user_message = user_message[:500]
        if chat_history is None:
            chat_history = []
        # Start message list with system instructions
        messages = [
            {"role": "system", "content": self.system_instruction}
        ]
        # Add previous chat history
        messages.extend(chat_history)
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        try:
            #. Create OpenAI client for HuggingFace Router
            client = openai.OpenAI(base_url=self.router_url, api_key=self.api_key)
            # Call chat completion endpoint
            resp = client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=256,
                temperature=0.7
            )
            # Extract and return the chatbot's reply
            reply = getattr(resp.choices[0].message, "content", "").strip()
            return {"response": reply}
        except Exception as exc:
            # Return error message if API call fails
            return {"response": f"HF Router API call failed: {exc}"}