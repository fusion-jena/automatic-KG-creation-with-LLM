import os
import re
from helper_functions import remove_question_and_query, remove_repeated_sentences

def process_cq_ans(config):
    input_folder = config.get('Paths', 'Ans_to_cq_input_folder')   
    output_folder = config.get('Paths', 'Ans_to_cq_output_folder') 

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.startswith("Pub") and filename.endswith(".txt"):
            with open(os.path.join(input_folder, filename), 'r') as file:
                text = file.read()
                text = text.replace('\n', ' ')
            text = remove_repeated_sentences(text)
            text = remove_question_and_query(text)
            with open(os.path.join(output_folder, filename), 'w') as file:
                file.write(text)
