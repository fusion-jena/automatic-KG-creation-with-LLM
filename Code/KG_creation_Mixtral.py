from helper_functions import load_llm, load_cqs, read_txt, get_embeddings
from langchain.prompts import PromptTemplate

model_id = 'mistralai/Mixtral-8x7B-Instruct-v0.1'
embedding_model_id = "sentence-transformers/all-MiniLM-L12-v2"
llm = load_llm(model_id, embedding_model_id)

def read_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read().strip()
    return content

def extract_and_save_concepts(result, output_file_path):
    with open(output_file_path, 'w') as f:
        result = result.replace('Knowledge Graph:', '')
        f.write(result)
    print(f"Result: {result}")
    print("\n")

    
CQs = load_cqs("../CQs/CQs.txt")
combined_prompt = read_txt("../Prompts/KG_creation_prompt1.txt")

for pub in [1,3,5,7,8]:
    for i,cq in enumerate(CQs):
        Answer = read_file(f'../Data/Ans_to_cqs/V2_processed/Publication{pub}_CQ{i+1}.txt')
        prompt = f"Q{i+1}: {cq}\nA{i+1}: {Answer}\n"
        combined_prompt += prompt
    onto = "Here is the ontology:"
    combined_prompt += onto
    owl_content = read_file("../Ontology/DLProv.owl")
    combined_prompt += f"\nOntology:\n{owl_content}\n"
    Output = llm(combined_prompt)
    output_file_path = f'../KG_files/Prompt_v1_CQ_Ans_v2/Publication_{pub}.ttl'
    extract_and_save_concepts(Output, output_file_path)
