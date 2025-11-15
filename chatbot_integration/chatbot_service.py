import os
import requests
from dotenv import load_dotenv

class ChatbotService:
    def __init__(self):
        print("🔧 Initializing ChatbotService...")
        
        # Load environment variables
        load_dotenv()
        self.api_key = os.getenv("HUGGINGFACE_API_KEY")
        
        print(f"🔑 API Key status: {'Found' if self.api_key else 'NOT FOUND'}")
        
        if not self.api_key:
            raise ValueError("❌ HUGGINGFACE_API_KEY not found in .env file. Please check your .env file.")
        
        if self.api_key == "your_huggingface_api_key_here":
            raise ValueError("❌ Please replace 'your_huggingface_api_key_here' with your actual Hugging Face API key in .env file")
        
        # Use the NEW Hugging Face router endpoint (as of 2024/2025)
        self.model = "katanemo/Arch-Router-1.5B"
        self.api_url = "https://router.huggingface.co/v1/chat/completions"
        self.use_chat_format = True
        
        # System instructions
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
        
        print("✅ ChatbotService initialized successfully (using direct API)")

    def get_chatbot_response(self, user_message, chat_history=None, product_info=None):
        """
        Get AI response from Hugging Face API using direct HTTP requests
        
        Args:
            user_message: User's message
            chat_history: Previous conversation history
            product_info: Information about available products
            
        Returns:
            dict with 'response' and 'success' keys
        """
        print(f"💬 Processing message: {user_message[:50]}...")
        
        if chat_history is None:
            chat_history = []
        
        try:
            # Build messages array
            messages = []
            
            # System instruction with product info
            system_message = self.system_instruction
            if product_info:
                system_message += f"\n\nAVAILABLE PRODUCTS:\n{product_info}"
            
            messages.append({
                "role": "system",
                "content": system_message
            })
            
            # Add conversation history
            messages.extend(chat_history)
            
            # Add current user message
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            print(f"📤 Sending request to API (messages: {len(messages)})")
            
            # Prepare request headers
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Use chat completions format for the new API
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": 1000,
                "temperature": 0.7
            }
            
            # Call Hugging Face API
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=60
            )
            
            print(f"📥 Received response (status: {response.status_code})")
            
            # Check response status
            if response.status_code != 200:
                error_detail = response.text
                print(f"⚠️ API error: {error_detail}")
                
                if response.status_code == 401:
                    return {
                        "response": "Authentication error. Please check the API key configuration.",
                        "success": False,
                        "error": "Unauthorized"
                    }
                elif response.status_code == 429:
                    return {
                        "response": "I'm currently experiencing high demand. Please try again in a moment.",
                        "success": False,
                        "error": "Rate limit exceeded"
                    }
                else:
                    return {
                        "response": "I'm having trouble connecting. Please try again.",
                        "success": False,
                        "error": f"API error: {response.status_code}"
                    }
            
            # Parse response
            data = response.json()
            
            # Extract response from chat completions format
            if "choices" in data and len(data["choices"]) > 0:
                assistant_message = data["choices"][0]["message"]["content"]
                print(f"✅ Response generated: {assistant_message[:50]}...")
                return {
                    "response": assistant_message,
                    "success": True
                }
            
            print("⚠️ Unexpected response format")
            print(f"Response data: {data}")
            return {
                "response": "I apologize, but I couldn't generate a response. Please try again.",
                "success": False
            }
                
        except requests.exceptions.Timeout:
            print("❌ Request timeout")
            return {
                "response": "The request took too long. Please try again.",
                "success": False,
                "error": "Timeout"
            }
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            print(f"❌ Request error: {error_msg}")
            return {
                "response": "I'm sorry, I'm having trouble connecting right now. Please try again in a moment.",
                "success": False,
                "error": error_msg
            }
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error in get_chatbot_response: {error_msg}")
            return {
                "response": "An unexpected error occurred. Please try again.",
                "success": False,
                "error": error_msg
            }