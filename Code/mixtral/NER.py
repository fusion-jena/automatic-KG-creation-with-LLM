from helper_functions import load_cqs, read_txt
import numpy as np
from LLM_loader import llm

def NER_mixtral(config):
    for pub in [1,3,5,7,8,9,10,12,13,14,16,18,19,20,24,25,27,28,33,34,37,38,39,41,42,43,44,45,46,47]:
        CQs = load_cqs(config.get('Paths', 'CQs_path'))
        combined_prompt = read_txt(config.get('Paths', 'NER_prompt'))
        Answer_format  = '''
        Answer:::
        Provide your answer as follows:
        Named Entities: For each provided Concept(Corresponding Named Entity,..), ...
        Answer:::
        '''
        for i in [2,5,6,4,12,15,13,22,17,19,20,8,25]:
        Answer = read_txt(f"{config.get('Paths', 'Ans_to_cq_output_folder')}Publication{pub}_CQ{i}.txt")
        prompt = f"Q: {CQs[i-1]}\nA: {Answer}\n"
        combined_prompt += prompt
        combined_prompt +=Answer_format
        #print(combined_prompt)
        output = llm.invoke(combined_prompt)
        with open(f"{config.get('Paths', 'NER_mixtral_save')}Publication{pub}_concepts.txt", 'w') as f:
            f.write(output)
