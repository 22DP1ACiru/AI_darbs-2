import os
import logging
import sys
from typing import List, Dict

from dotenv import load_dotenv
try:
    from openai import OpenAI
except Exception:
    OpenAI = None


class ChatbotService:
    def __init__(self):
        # TODO: 1. SOLIS - API atslēgas ielāde
        # load_dotenv() to load environment variables from a .env file
        # os.getenv() to read "HUGGINGFACE_API_KEY"
        load_dotenv()
        self.api_key = os.getenv("HUGGINGFACE_API_KEY")

        # TODO: 2. SOLIS - OpenAI klienta inicializācija izmantojot "katanemo/Arch-Router-1.5B" modeli
        # Initialize the OpenAI-compatible client pointing to Hugging Face Router API
        # The model must be "katanemo/Arch-Router-1.5B" as required by the assignment
        self.model = "katanemo/Arch-Router-1.5B"
        self.client = None
        if self.api_key and OpenAI is not None:
            try:
                # Use the HF Router OpenAI-compatible endpoint
                self.client = OpenAI(base_url="https://router.huggingface.co/v1", api_key=self.api_key)
            except Exception as e:
                logging.warning(f"Failed to initialize OpenAI-compatible client: {e}")
                self.client = None
        else:
            if not self.api_key:
                logging.warning("HUGGINGFACE_API_KEY not found in environment variables.")
            if OpenAI is None:
                logging.warning("openai package is not available. Install 'openai' to use the Router API.")

        # TODO: 3. SOLIS - Sistēmas instrukcijas definēšana
        # Define the system instruction for the assistant behavior
        self.system_instruction = (
            "You are a helpful e-shop assistant. Your role is to help customers with questions about products, "
            "orders, and general shopping assistance. Be friendly, concise, and professional. Only answer "
            "questions related to the e-shop and its products. If asked about unrelated topics, politely redirect "
            "the conversation back to shopping."
        )

    def _normalize_history(self, chat_history: List[Dict]) -> List[Dict]:
        """Normalize incoming chat history to valid roles and content for the OpenAI API."""
        allowed_roles = {"system", "user", "assistant"}
        normalized: List[Dict] = []
        for msg in chat_history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role not in allowed_roles:
                role = "user"
            normalized.append({"role": role, "content": content})
        return normalized

    def get_chatbot_response(self, user_message, chat_history=None):
        if chat_history is None:
            chat_history = []

        # TODO: 4. SOLIS - Ziņojumu saraksta izveide masīvā
        # Create the messages array: system instruction, full history, and the last user message
        messages: List[Dict] = []
        messages.append({"role": "system", "content": self.system_instruction})
        messages.extend(self._normalize_history(chat_history))
        messages.append({"role": "user", "content": user_message})

        # Fail-fast for missing dependencies or configuration
        if not self.api_key:
            return {"response": "HUGGINGFACE_API_KEY is not set in the environment."}
        if OpenAI is None or self.client is None:
            return {"response": "OpenAI-compatible client is not initialized. Ensure 'openai' is installed and API key is set."}

        try:
            # TODO: 5. SOLIS - HF API izsaukums ar OpenAI bibliotēku, izmantojot chat.completions.create().
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=250,
                top_p=0.9
            )

            # TODO: 6. SOLIS - Atbildes apstrāde un atgriešana
            # chat.completions.create() returns an object with a "choices" list; take the first message's content
            text = ""
            if completion and getattr(completion, "choices", None):
                choice = completion.choices[0]
                msg = getattr(choice, "message", None)
                if msg and getattr(msg, "content", None):
                    text = (msg.content or "").strip()

            text = text or "I'm sorry, I couldn't generate a response. Please try again."
            return {"response": text}

        except Exception as e:
            logging.exception(f"Chat completion call failed: {e}")
            return {"response": "Sorry, I encountered an error while contacting the AI service. Please try again later."}


if __name__ == '__main__':
    # Simple CLI for quick manual testing
    prompt = "Hello, can you help me?" if len(sys.argv) < 2 else " ".join(sys.argv[1:])
    svc = ChatbotService()
    resp = svc.get_chatbot_response(prompt)
    print(resp.get('response'))
