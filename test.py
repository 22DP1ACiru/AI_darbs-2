import os
from dotenv import load_dotenv
from openai import OpenAI

# 1️⃣ API atslēgas ielāde un OpenAI klienta inicializācija
load_dotenv()
api_key = os.getenv("HUGGINGFACE_API_KEY")

if not api_key:
    raise ValueError("HUGGINGFACE_API_KEY not found in environment variables")

client = OpenAI(
    base_url="https://router.huggingface.co/v1",  # Hugging Face router endpoint
    api_key=api_key
)

# 2️⃣ Sistēmas instrukcija: e-veikala asistents
system_instruction = """
You are an e-shop assistant. ONLY answer questions about:
- Products in our store
- Order status and purchases
- Shopping cart and checkout
- Store policies, shipping, returns
- Product recommendations

STRICT RULES:
1. If asked about anything unrelated to shopping or this store, say:
   'I can only help with questions about our online store and products.'
2. Keep responses brief and helpful
3. If unsure, suggest checking the product catalog or contacting support
4. Never discuss topics outside of e-commerce
"""

# 3️⃣ Lietotāja ziņa
user_message = "Where is my order?"

# 4️⃣ API izsaukums caur chat.completions.create()
completion = client.chat.completions.create(
    model="katanemo/Arch-Router-1.5B",
    messages=[
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": user_message}
    ],
    temperature=0.3,   # mazāk nejaušības
    max_tokens=150     # maksimālais tokenu skaits atbildei
)

# 5️⃣ Atbildes apstrāde un atgriešana
# Hugging Face API caur OpenAI klientu atgriež:
# completion.choices[0].message["content"]
bot_response = completion.choices[0].message.content
print("Assistant:", bot_response)