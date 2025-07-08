from transformers import AutoTokenizer, AutoModelForCausalLM, AutoProcessor
import torch
import torch.nn as nn
from transformers import BitsAndBytesConfig
from peft import get_peft_model, LoraConfig
from transformers import TrainingArguments
import json
from transformers import Trainer
import os
from tqdm import tqdm
from datasets import load_dataset, concatenate_datasets
from PIL import Image, ImageOps
import pathlib
import argparse
import re
from transformers import TrainingArguments


import torch
torch.distributed.init_process_group(backend='gloo')

class phi3_datacollator:
    def __init__(self, processor, args):
        self.processor = processor
        self.args = args

    def __call__(self, examples):
            
        def process_prompt(text: str, system_prompt: str = ''):
            user_prompt = system_prompt + 'Answer the question:\n' + text
            prompt = f"<|image_1|>\n{user_prompt}"
            messages = [
                {"role": "user", "content": f"<|image_1|>\n{user_prompt}"}
            ]
            prompt = self.processor.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            return prompt
        
        def process_answer(answer):
            answer = f"{answer}<|end|>\n<|endoftext|>"
            return answer
        
        images = [Image.open(os.path.join(args.train_image_dir, example["doc_id"]+'.png')).convert("RGB") for example in examples]
        prompts = [process_prompt(example["question"]) for example in examples]
        answers = [process_answer(example['answer']) for example in examples]

        meta_list = [self.processor(
            text=prompt,
            images=[image],
            return_tensors="pt",
            padding=10000,
        ) for prompt, image in zip(prompts, images)]

        batch = []
        ignore_index = -100
        for i, (meta, answer) in enumerate(zip(meta_list, answers)):
            
            prompt_input_ids = meta["input_ids"]
            answer_input_ids = self.processor.tokenizer(answer, add_special_tokens=False, return_tensors="pt")["input_ids"]
            concatenated_input_ids = torch.cat([prompt_input_ids, answer_input_ids], dim=1)
        
            labels = torch.cat(
                [
                    torch.tensor([ignore_index] * len(prompt_input_ids[0])).unsqueeze(0),
                    answer_input_ids,
                ],
                dim=1,
            )

            meta["input_ids"] = concatenated_input_ids
            meta["labels"] = labels

            batch.append(meta)

        input_ids = [d["input_ids"] for d in batch]
        labels = [d["labels"] for d in batch]
        attention_mask = [d["attention_mask"] for d in batch]
        pixel_values = [d["pixel_values"] for d in batch]
        image_sizes = [d["image_sizes"] for d in batch]
        
        def pad_tensor(tensor, pad_value=0, max_length=4096):
            """Pads tensor to max_len along dim=1"""
            pad_size = max_length - tensor.shape[1]
            return torch.nn.functional.pad(tensor, (0, pad_size), value=pad_value)

        # Pad all tensors to match max_len
        longest_len_input = max([x.shape[1] for x in input_ids])
        longest_len_att = max([x.shape[1] for x in attention_mask])

        input_ids_cat = torch.cat([pad_tensor(t, pad_value=self.processor.tokenizer.pad_token_id, max_length=longest_len_input) for t in input_ids], dim=0)
        labels_cat = torch.cat([pad_tensor(t, pad_value=self.processor.tokenizer.pad_token_id, max_length=longest_len_input) for t in labels], dim=0)
        attention_mask_cat = torch.cat([pad_tensor(t, pad_value=0, max_length=longest_len_att) for t in attention_mask], dim=0)
        pixel_values_cat = torch.cat(pixel_values, dim=0)
        image_sizes_cat = torch.cat(image_sizes, dim=0)
        

        batch = {"input_ids": input_ids_cat,
                 "labels": labels_cat,
                 "attention_mask": attention_mask_cat,
                 "pixel_values": pixel_values_cat,
                 "image_sizes": image_sizes_cat
                 }
        
        # Ensure only floating-point tensors require gradients
        for key, value in batch.items():
            if isinstance(value, torch.Tensor) and torch.is_floating_point(value):
                batch[key] = value.clone().detach().requires_grad_(True)

        return batch


def get_lora_target(model):
    
    pattern = re.compile(r"(.*(qkv_proj|gate_up_proj|v_proj|o_proj|down_proj|k_proj|q_proj|up_proj|gate_proj).*$)")
    
    # Filter the modules based on the regex pattern
    model_modules = [name for name, _ in model.named_modules()]
    
    lora_target = [module for module in model_modules if pattern.match(module)]

    return lora_target


def main(args):

    # load model
    model_name = args.model_name
    processor = AutoProcessor.from_pretrained(model_name, trust_remote_code=True)
    
    world_size = int(os.environ.get("WORLD_SIZE", 1))
    ddp = world_size != 1
    device_map = {"": int(os.environ.get("LOCAL_RANK") or 0)} if ddp else None

    model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True, torch_dtype="auto", device_map=device_map)
    
    # select lora target
    lora_target = get_lora_target(model)
    lora_config = LoraConfig(
        r=args.lora_rank,
        target_modules=lora_target,
        task_type="CAUSAL_LM",
    )

    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # print(model)

    # load TrainingArguments
    train_args = TrainingArguments(
            deepspeed=args.deepspeed,
            num_train_epochs=args.num_train_epochs,
            remove_unused_columns=False,
            per_device_train_batch_size=1,
            gradient_accumulation_steps=4,
            warmup_steps=2,
            learning_rate=2e-5,
            weight_decay=1e-6,
            adam_beta2=0.999,
            logging_steps=args.logging_steps,
            optim="adamw_torch",
            save_strategy="steps",
            save_steps=args.save_steps,
            hub_model_id=args.hub_name,  # Specify your repo name
            push_to_hub=False,
            save_total_limit=2,
            output_dir=args.output_dir,
            bf16=True,
            dataloader_pin_memory=False,
            max_grad_norm=1.0,
            report_to="wandb",
            )

    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # load data
    # select OMR train
    dataset_omr = load_dataset('json', data_files=os.path.join(args.train_json_dir, 'train_qa_omr.json'), split='train')
    if args.omr_w < 1.0:
        dataset_omr_selected = dataset_omr.train_test_split(test_size=args.omr_w, shuffle=True, seed=42)['test']
    else:
        dataset_omr_selected = dataset_omr
        
    # select simple train
    dataset_simple = load_dataset('json', data_files=os.path.join(args.train_json_dir, 'train_qa_simple.json'), split='train')
    if args.simple_w < 1.0:
        dataset_simple_selected = dataset_simple.train_test_split(test_size=args.simple_w, shuffle=True, seed=42)['test']
    else:
        dataset_simple_selected = dataset_simple

    # merge train
    train_data = concatenate_datasets([dataset_omr_selected, dataset_simple_selected])
    l_all = len(train_data)
    l_omr = len(dataset_omr_selected)
    l_simple = len(dataset_simple_selected)
    print(f'training using {l_all} QAs, {l_omr} omr QAs, {l_simple} simple QAs.')
    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    

    trainer = Trainer(
        model=model,
        train_dataset=train_data,
        data_collator=phi3_datacollator(processor, args),
        args=train_args
        )

    if list(pathlib.Path(args.output_dir).glob("checkpoint-*")):
        trainer.train(resume_from_checkpoint=True)
    else:
        trainer.train()
    
    trainer.save_state()

    
if __name__=='__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name", default="microsoft/Phi-3-vision-128k-instruct", help="model name", type=str)
    parser.add_argument("--lora_rank", default=32, help="lora rank", type=int)
    parser.add_argument("--save_steps", default=2000, help="number of steps to save checkpoints", type=int)
    parser.add_argument("--logging_steps", default=100, help="number of steps to print loss", type=int)
    parser.add_argument("--num_train_epochs", default=2, help="num_train_epochs", type=int)
    parser.add_argument("--train_json_dir", default='/train_data', help="directory of the json file for training data", type=str)
    parser.add_argument("--train_image_dir", default='/images', help="directory of the image file for training data", type=str)
    parser.add_argument("--omr_w", default=1.0, help="omr percent", type=float)
    parser.add_argument("--simple_w", default=1.0, help="simple percent", type=float)
    parser.add_argument("--output_dir", default=f"adapters/test", 
                        help="directory to save checkpoints", type=str)
    parser.add_argument("--hub_name", default="secret_phi3v_checkpoint", help="repo name on huggingface", type=str)
    parser.add_argument("--deepspeed", type=str, default=None, help="Path to DeepSpeed config JSON")
    parser.add_argument("--hf_token", default=None, help="hf token", type=str, required=True)
    parser.add_argument("--wandb_token", default=None, help="wandb token", type=str, required=True)
    args = parser.parse_args()

    from huggingface_hub import login
    print(f'Logging in to hugging face using token: {args.hf_token}')
    login(args.hf_token)

    # Initialize WandB
    if args.local_rank == 0:
        import wandb
        print(f'Logging in to wandb using token: {args.wandb_token}')
        wandb.login(key=args.wandb_token)
        wandb.init(project="LoRA-Phi3-Vision", name="phi3-vision-lora-training")

    main(args)
    
    
