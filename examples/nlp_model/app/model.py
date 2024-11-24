import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer  # Import the correct model class
import logging

class NLPModel:
    def __init__(self):
        """
        Initialize the Flan-T5-Large model and tokenizer using Hugging Face.
        """
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = torch.device(device)

        print(f"Using device: {self.device}")
        print("Loading Flan-T5-Large model...")
        self.tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-xxl", cache_dir="/app/.cache")
        self.model = AutoModelForSeq2SeqLM.from_pretrained(  # Corrected to use Seq2SeqLM
            "google/flan-t5-large",
            torch_dtype=torch.float16 if self.device.type == "cuda" else torch.float32,
            cache_dir="/app/.cache"
        )
        self.model.to(self.device)
        print("Model loaded successfully.")

    def generate(self, prompt: str, max_length: int = 128) -> str:
        """
        Generate text from the given prompt using flan-t5-xxl.
        """
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        outputs = self.model.generate(
            inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            max_length=max_length,
            do_sample=True,
            temperature=0.7,
            top_k=50,
            top_p=0.9
        )
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
