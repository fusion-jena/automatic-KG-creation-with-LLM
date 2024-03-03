import os
import re

def remove_question_and_query(text):
    if "Question:" in text:
        return text[:text.index("Question:")]
    elif "Query:" in text:
        return text[:text.index("Query:")]
    elif "References" in text:
        return text[:text.index("References")]
    elif "Reference(s):" in text:
        return text[:text.index("Reference(s):")]
    elif "Answer:" in text:
        return text[:text.index("Answer:")]
    else:
        return text

def remove_repeated_sentences(text):
    sentences = text.split('.')
    seen = set()
    result = []
    for sentence in sentences:
        sentence = sentence.strip().replace('\n', ' ')
        sentence = re.sub(r'\s+', ' ', sentence)
        if sentence.strip() not in seen:
            seen.add(sentence.strip())
            result.append(sentence.strip())
    return '. '.join(result)

input_folder = "../Data/Ans_to_cqs/Original_not_processed/"   
output_folder = "../Data/Ans_to_cqs/V2_processed/" 

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
