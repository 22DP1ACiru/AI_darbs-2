import os
from openai import OpenAI
from dotenv import load_dotenv

class ChatbotService:
    def __init__(self):
        """
        Initialize the chatbot service:
        1. Load environment variables from .env
        2. Get HuggingFace API key
        3. Initialize OpenAI client for HF router model
        """
        # TODO: 1. Load API key
        load_dotenv()  # Load environment variables from .env file
        self.api_key = os.getenv("HUGGINGFACE_API_KEY")  # Read API key
        
        if not self.api_key:
            raise ValueError("HUGGINGFACE_API_KEY environment variable not set")
        
        # TODO: 2. Initialize OpenAI client for HF router
        self.client = OpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=self.api_key
        )
        self.model = "katanemo/Arch-Router-1.5B"
 
    def get_chatbot_response(self, user_message, chat_history=None, products_info=""):
        """
        Get chatbot response with product info included in the system prompt.
        
        Args:
            user_message (str): Current user message
            chat_history (list): Previous conversation messages
            products_info (str): Product info from DB
        
        Returns:
            dict: {"response": str, "status": "success"|"error"}
        """
        if chat_history is None:
            chat_history = []
            
        # If the message is clearly unrelated to the shop, return a polite redirection
        if self._is_clearly_unrelated(user_message):
            return {
                "response": (
                    "I specialize in helping with electronics products and our e-shop services. "
                    "How can I assist you with computers, peripherals, or your order today?"
                ),
                "status": "success"
            }
        
        # TODO: 3. Create system prompt including product information
        system_instruction = self._create_system_prompt(products_info)
        
        # TODO: 4. Construct message array for API call
        messages = [{"role": "system", "content": system_instruction}]
        messages.extend(chat_history)  # Add previous chat history
        messages.append({"role": "user", "content": user_message})  # Add current user message
        
        try:
            # TODO: 5. Call HF API via OpenAI client
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=250,
                temperature=0.7,
                top_p=0.9
            )
            
            # TODO: 6. Process and return assistant's reply
            if response.choices and len(response.choices) > 0:
                assistant_response = response.choices[0].message.content.strip()
                return {"response": assistant_response, "status": "success"}
            else:
                return {
                    "response": "Sorry, I couldn't generate a response. Please try again.",
                    "status": "error"
                }
                
        except Exception as e:
            # Log exception for debugging
            print(f"ChatbotService API error: {e}")
            error_message = "Sorry, I'm experiencing technical difficulties. Please try again later."
            return {"response": error_message, "status": "error"}
    
    def _create_system_prompt(self, products_info):
        """
        Create system prompt for the chatbot, including product catalog.
        """
        base_prompt = (
            "You are a helpful AI assistant for an electronics e-shop. "
            "Assist customers with products, orders, and shop services.\n\n"
            
            "GUIDELINES:\n"
            "1. Focus on electronics, computers, peripherals, and shop-related topics\n"
            "2. Politely redirect unrelated questions to shop services\n"
            "3. Only provide info from current product catalog\n"
            "4. Keep responses concise and helpful\n"
            "5. Be friendly and professional\n\n"
        )
        
        # Add current product info if available
        if products_info:
            base_prompt += f"CURRENT PRODUCT CATALOG:\n{products_info}\n\n"
        
        # Add topics the assistant can help with
        base_prompt += (
            "TOPICS YOU CAN HELP WITH:\n"
            "- Computers, laptops, tablets\n"
            "- Peripherals: mice, keyboards, monitors, printers\n"
            "- Storage: SSDs, hard drives, USB drives\n"
            "- Networking: routers, cables, adapters\n"
            "- Gaming equipment\n"
            "- Product specs and pricing\n"
            "- Order status and shipping\n"
            "- Product availability\n"
            "- Technical support for electronics\n"
            "- Product recommendations\n\n"
            
            "RESPONSE STYLE:\n"
            "- Be helpful and informative\n"
            "- Keep answers under 100 words when possible\n"
            "- Focus on customer's needs\n"
            "- Use product catalog for accurate info\n"
            "- If unsure, suggest contacting customer support\n"
        )
        
        return base_prompt
    
    def _is_clearly_unrelated(self, user_message):
        """
        Simple heuristic to filter out clearly unrelated questions.
        
        Returns True if the message is clearly off-topic.
        """
        user_message_lower = user_message.lower()
        
        # List of clearly unrelated topics
        unrelated_topics = [
            'politics', 'government', 'election', 'president',
            'religion', 'god', 'church', 'bible', 'quran',
            'sports', 'football', 'basketball', 'tennis',
            'movie', 'film', 'actor', 'celebrity',
            'weather', 'climate', 'forecast',
            'medical', 'health', 'doctor', 'hospital',
            'financial advice', 'investment', 'stock market',
            'legal advice', 'lawyer', 'court'
        ]
        
        return any(topic in user_message_lower for topic in unrelated_topics)
