import os
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

class ChatbotService:
    def __init__(self, system_instruction: str):
        load_dotenv()
        HF_TOKEN = os.getenv("HF_TOKEN")

        if not HF_TOKEN:
            raise ValueError("HF_TOKEN missing in .env file!")

        self.client = InferenceClient(token=HF_TOKEN)
        self.system_instruction = system_instruction
        print(system_instruction)

    def ask(self, message: str, history=None) -> str:
        try:
            messages = []

            if self.system_instruction:
                messages.append({"role": "system", "content": self.system_instruction})

            if history:
                messages.extend(history)

            messages.append({"role": "user", "content": message})

            response = self.client.chat.completions.create(
                model="katanemo/Arch-Router-1.5B",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )

            return response.choices[0].message["content"].strip()

        except Exception as e:
            print("HF chat error:", e)
            return "AI API error."

    def get_chatbot_response(self, message: str, history: list):
        answer = self.ask(message, history)

        return {
            "response": answer
        }





        
