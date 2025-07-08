from util.model_handler import *
import os
os.system('clear')
import json
import numpy as np
import re
import argparse
from tqdm import tqdm

def get_image_dir(example, train_image_dir):
    doc_id = example['doc_id']
    image_dir = os.path.join(train_image_dir, f'{doc_id}.png')
    return image_dir


parser = argparse.ArgumentParser()
parser.add_argument("--n_test_data", default=100, help="n_test_data", type=int)
parser.add_argument("--lora_dir", default="puar-playground/Phi-3-MusiX", help="lora_dir", type=str)
parser.add_argument("--test_qa_dir", default="./test_qa_omr.json", help="test_qa_dir", type=str)
parser.add_argument("--test_image_dir", default="./images", help="test_data_dir", type=str)
args = parser.parse_args()



if __name__=='__main__':
    
    test_model_handler = LoraPhi3VHandler(lora_dir=args.lora_dir)

    model_name = test_model_handler.model_name
    print(model_name)


    test_data = json.load(open(args.test_qa_dir, 'r'))
    n_test_data = min(args.n_test_data, len(test_data))

    result = []

    cnt = 0
    for i, example in enumerate(tqdm(test_data[:args.n_test_data])):
        doc_id = example['doc_id']
        question = example['question']
        answer_true = example['answer']

        image_dir = get_image_dir(example, args.test_image_dir)
        answer_model = test_model_handler.ask(question, image_dir)

        print(doc_id, '>' * 120)
        print(f'question: {question}')
        print(f'true_answer: {answer_true}')
        print(f'answer_model: {answer_model}')

        result.append({'doc_id': doc_id, 'question': question, 'answer_true': answer_true, 'answer_model': answer_model})

        if cnt % 100 == 0:
            json.dump(result, open('./result/test_result.json', 'w'), indent=4)

    json.dump(result, open('./result/test_result.json', 'w'), indent=4)