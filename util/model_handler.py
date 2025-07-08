import json
from PIL import Image 
from http import HTTPStatus
import torch
import requests
from io import BytesIO
import random
import re
torch.manual_seed(1)
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Base handler

class BaseModelHandler:
    def __init__(self, model_name):
        self.model_name = model_name
        self.SYSTEM_PROMPT = ("Please analyze the provided images of document pages or slides carefully "
                              "and answer the following question(s) based on the visual and textual information present in images.\n"
                              "Please keep the answer concise. Output only the answer without any explaination.\n"
                              "Out put 'Not answerable' if the document does not provide enough information.")

    def load_model(self, model_name: str):
        raise Exception("Not Implemented")
    
    def ask(self, input_string: str, img_dir: str):
        raise Exception("Not Implemented")
        
    def load_img(self, img_dir):
        if img_dir.startswith('http://') or img_dir.startswith('https://'):
            response = requests.get(img_dir)
            image = Image.open(BytesIO(response.content)).convert('RGB')
        else:
            image = Image.open(img_dir).convert('RGB')

        return image
    
    def __repr__(self):
        return f"<Model Handler for: {self.model_name}>"

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Handler for Phi-3-Vision

class Phi3VHandler(BaseModelHandler):
    def __init__(self):
        super().__init__('Phi-3v')

        self.load_model()

    def load_model(self):
        from transformers import AutoModelForCausalLM 
        from transformers import AutoProcessor 
        model_id = "microsoft/Phi-3-vision-128k-instruct" 
        self.model = AutoModelForCausalLM.from_pretrained(model_id, device_map="cuda", trust_remote_code=True, torch_dtype="auto").eval()
        self.processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)


    def ask(self, question_string: str, img_dir: str):
        
        # prepare prompt
        system_prompt = ('You are an expert in optical music recognition (OMR) and music theory, '
                         'trained to analyze music sheet images, extract musical information, and answer questions based on the notation.\n')
        
        prompt = (system_prompt + f'A chat between a curious human and an artificial intelligence assistant. '
              f'The assistant gives helpful, detailed, and polite answers to the human\'s questions. '
              f'USER: {question_string}\nPlease make the answer as concise as possible. ASSISTANT:')

        # setup message
        # we do zero-shot test, so ignore demonstrations
        messages = [
        # {"role": "user", "content": f"<|image_1|>\n{demo_q}"}, 
        # {"role": "assistant", "content": f"{demo_a}"}, 
        {"role": "user", "content": f"<|image_1|>\n{prompt}"} 
        ]

        # load image from dir
        image = self.load_img(img_dir)
        
        prompt_in = self.processor.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.processor(prompt_in, [image], return_tensors="pt").to("cuda")
        
        generation_args = { 
            "max_new_tokens": 500,
            "temperature": 0.0,
            "do_sample": False,
        }

        generate_ids = self.model.generate(**inputs, eos_token_id=self.processor.tokenizer.eos_token_id, **generation_args)

        # remove input tokens 
        generate_ids = generate_ids[:, inputs['input_ids'].shape[1]:]
        model_answer = self.processor.batch_decode(generate_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0] 
        
        return model_answer

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Handler for Phi-3-Vision-Lora

class LoraPhi3VHandler(BaseModelHandler):
    def __init__(self, lora_dir):
        super().__init__('Phi-3v-Lora')

        self.load_model(lora_dir)

    def load_model(self, lora_dir):
        from transformers import AutoModelForCausalLM 
        from transformers import AutoProcessor 
        model_id = "microsoft/Phi-3-vision-128k-instruct" 
        self.model = AutoModelForCausalLM.from_pretrained(model_id, device_map="cuda", trust_remote_code=True, torch_dtype="auto")
        self.processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)
        self.model.load_adapter(lora_dir)
        # print(self.model)


    def ask(self, question_string: str, img_dir: str):

        # prepare prompt
        # system_prompt = ('You are an expert in optical music recognition (OMR) and music theory, '
                        #  'trained to analyze music sheet images, extract musical information, and answer questions based on the notation.\n')
        
        prompt = '' + f'USER: Answer the question:\n{question_string}. ASSISTANT:'

        # setup message
        # we do zero-shot test, so ignore demonstrations
        messages = [
        # {"role": "user", "content": f"<|image_1|>\n{demo_q}"}, 
        # {"role": "assistant", "content": f"{demo_a}"}, 
        {"role": "user", "content": f"<|image_1|>\n{prompt}"} 
        ]

        # load image from dir
        image = self.load_img(img_dir)
        
        prompt_in = self.processor.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.processor(prompt_in, [image], return_tensors="pt").to("cuda")
        
        generation_args = { 
            "max_new_tokens": 500,
            "temperature": 0.1,
            "do_sample": False,
        }

        with torch.no_grad():
            generate_ids = self.model.generate(**inputs, eos_token_id=self.processor.tokenizer.eos_token_id, **generation_args)

        # remove input tokens 
        generate_ids = generate_ids[:, inputs['input_ids'].shape[1]:]
        model_answer = self.processor.batch_decode(generate_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0] 
        
        return model_answer



# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Handler for PaliGemma

class PaliGemmaHandler(BaseModelHandler):
    def __init__(self):
        super().__init__('PaliGemma')

        self.load_model()

    def load_model(self):
        from transformers import AutoProcessor, PaliGemmaForConditionalGeneration
        from PIL import Image
        model_id = "google/paligemma-3b-mix-448"
        self.model = PaliGemmaForConditionalGeneration.from_pretrained(model_id, device_map="cuda")
        self.processor = AutoProcessor.from_pretrained(model_id)


    def ask(self, question_string: str, img_dir: str):
        
        # prepare prompt
        system_prompt = ('You are an expert in optical music recognition (OMR) and music theory, '
                         'trained to analyze music sheet images, extract musical information, and answer questions based on the notation.\n')
        
        prompt = '<image>\n' + system_prompt + f'Answer the question:\n{question_string}\n ASSISTANT:'

        raw_image = self.load_img(img_dir)
        
        inputs = self.processor(prompt, raw_image, return_tensors="pt").to('cuda')
        output = self.model.generate(**inputs, max_new_tokens=4096)
    
        model_answer = self.processor.decode(output[0], skip_special_tokens=True).split('ASSISTANT:')[1].strip()
        
        return model_answer


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Handler for PaliGemma Lora


class LoraPaliGemmaHandler(BaseModelHandler):
    def __init__(self, lora_dir):
        super().__init__('Lora32PaliGemma')

        self.load_model(lora_dir=lora_dir)

    def load_model(self, lora_dir):
        from transformers import AutoProcessor, PaliGemmaForConditionalGeneration
        model_id = "google/paligemma-3b-mix-448"
        self.model = PaliGemmaForConditionalGeneration.from_pretrained(model_id, device_map="cuda")
        self.processor = AutoProcessor.from_pretrained(model_id)
        self.model.load_adapter(lora_dir)

    def ask(self, question_string: str, img_dir: str):
        
        # prepare prompt
        # system_prompt = ('You are an expert in optical music recognition (OMR) and music theory, '
        #                  'trained to analyze music sheet images, extract musical information, and answer questions based on the notation.\n')
        
        prompt = f'<image>\nAnswer the question:\n{question_string}\n ASSISTANT:'

        raw_image = self.load_img(img_dir)
        
        inputs = self.processor(prompt, raw_image, return_tensors="pt").to('cuda')
        output = self.model.generate(**inputs, max_new_tokens=4096)
    
        model_answer = self.processor.decode(output[0], skip_special_tokens=True).split('ASSISTANT:')[1].strip()
        
        return model_answer

