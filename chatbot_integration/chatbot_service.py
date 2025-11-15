import os
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatbotService:
    def __init__(self):
        load_dotenv()
        
        # Model configuration
        self.model_name = "katanemo/Arch-Router-1.5B"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        logger.info(f"Ielādējam modeli {self.model_name} uz {self.device}...")
        
        try:
            # Load model and tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
                trust_remote_code=True
            )
            
            if self.device == "cuda":
                self.model = self.model.to(self.device)
                
            logger.info("Modelis veiksmīgi ielādēts")
            
        except Exception as e:
            logger.exception(f"Neizdevās ielādēt modeli: {str(e)}")
            raise

        # Sistēmas instrukcija čatbotam
        self.system_instruction = (
            "Tu esi e-veikala asistents. Atbildi tikai par šo veikalu un tā produktiem. "
            "Ja jautājums nav saistīts ar veikalu vai tā precēm, atsaki īsi, ka vari palīdzēt tikai ar saistītiem jautājumiem. "
            "Būsi īss un precīzs atbildēs. Atgriezīsi tikai atbildi bez papildu komentāriem."
        )

    def get_chatbot_response(self, user_message: str, chat_history: Optional[List[Dict[str, str]]] = None, 
                           products_info: Optional[str] = None) -> Dict[str, str]:
        """
        Ģenerē atbildi no čatbota.
        
        Args:
            user_message: Lietotāja ziņojums
            chat_history: Saraksts ar iepriekšējiem ziņojumiem formātā [{"role": "user/assistant", "content": "ziņojums"}]
            products_info: Informācija par pieejamiem produktiem
            
        Returns:
            Vārdnīca ar čatbota atbildi
        """
        if chat_history is None:
            chat_history = []
        if products_info is None:
            products_info = ""

        # Veidojam promptu ar sistēmas instrukciju un kontekstu
        prompt_parts = ["<|system|>", self.system_instruction]
        
        # Pievienojam informāciju par produktiem, ja tāda ir
        if products_info:
            prompt_parts.append("\nPieejamie produkti:" + products_info)
        
        # Pievienojam sarunas vēsturi
        for msg in chat_history[-4:]:  # Saglabājam pēdējos 4 ziņojumus kontekstam
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            if role == 'user':
                prompt_parts.append(f"\n{content}")
            else:
                prompt_parts.append(f"<|assistant|>{content}")
        
        # Pievienojam pašreizējo lietotāja ziņojumu
        prompt_parts.append(f"\n{user_message}")
        prompt_parts.append("<|assistant|>")
        
        prompt = "\n".join(prompt_parts)
        
        try:
            # Pārveidojam ievadu tokenos
            inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
            
            # Pārnesam uz GPU, ja tāds ir pieejams
            if self.device == "cuda":
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Ģenerējam atbildi
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=150,
                    temperature=0.7,
                    top_p=0.9,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    no_repeat_ngram_size=3
                )
            
            # Atkodējam atbildi
            full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Izgūstam tikai asistenta atbildi (viss pēc pēdējā <|assistant|> tag)
            assistant_response = full_response.split("<|assistant|>")[-1].strip()
            
            # Pārbaudām, vai atbilde ir saistīta ar veikala kontekstu
            if not self._is_relevant_response(assistant_response, user_message):
                assistant_response = "Es varu atbildēt tikai uz jautājumiem par mūsu veikalu un tā produktiem."
            
            return {"response": assistant_response}
            
        except Exception as e:
            logger.exception(f"Kļūda, ģenerējot atbildi: {str(e)}")
            return {"response": "Radās kļūda, apstrādājot jūsu pieprasījumu. Lūdzu, mēģiniet vēlreiz vēlāk."}
    
    def _is_relevant_response(self, response: str, user_message: str) -> bool:
        """Pārbauda, vai atbilde ir saistīta ar veikala kontekstu."""
        # Vienkārša pārbaude, vai atbilde nav bezsatura
        if not response or len(response.strip()) < 3:
            return False
            
        # Pārbaude, vai atbilde nav pārāk īsa, lai būtu jēga
        if len(response.split()) < 3:
            return False
            
        return True