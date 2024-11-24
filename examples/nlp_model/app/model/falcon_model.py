import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import logging

class FalconModel:
    def __init__(self):
        """
        Initialize the Falcon-7B model and tokenizer using Hugging Face.
        """
        logging.basicConfig(level=logging.INFO)
        try:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.device = torch.device(device)
            logging.info(f"Using device: {self.device}")
        except Exception as e:
            logging.error(f"Error initializing device: {e}")
            raise

        logging.info("Loading Falcon-7B model...")
        self.tokenizer = AutoTokenizer.from_pretrained(
            "tiiuae/falcon-7b-instruct",
            use_fast=True,
            cache_dir="/app/.cache"
        )
        self.tokenizer.pad_token = self.tokenizer.eos_token  # Use EOS token as padding

        self.model = AutoModelForCausalLM.from_pretrained(
            "tiiuae/falcon-7b-instruct",
            torch_dtype=torch.float16 if self.device.type == "cuda" else torch.float32,
            cache_dir="/app/.cache"
        )

        if self.device.type == "cuda":
            self.model.half()  # Use FP16 on CUDA
        self.model.to(self.device)

        if torch.__version__ >= "2.0":
            self.model = torch.compile(self.model)

        logging.info("Model loaded successfully.")

    def generate(self, prompt: str, max_length: int = 50) -> str:
        """
        Generate text from the given prompt using Falcon-7B.
        """
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            padding=True,
            truncation=True
        ).to(self.device)
        
        outputs = self.model.generate(
            inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            max_length=max_length,
            do_sample=True,
            temperature=0.7,
            top_k=50,
            top_p=0.9
        )
        
        result = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        logging.info(f"Prompt: {prompt}")
        logging.info(f"Generated Text: {result}")
        return result
