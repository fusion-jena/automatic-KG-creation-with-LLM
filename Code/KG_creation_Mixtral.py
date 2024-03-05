from helper_functions import load_llm, load_cqs, read_txt, get_embeddings
from langchain.prompts import PromptTemplate
from helper_functions import extract_and_save_concepts
from LLM_loader import llm

def KG_creation(config):
    CQs = load_cqs(config.get('Paths', 'CQs_path'))
    combined_prompt = read_txt(config.get('Paths', 'KG_creation_prompt1'))

    for pub in [1,3,5,7,8]:
        for i,cq in enumerate(CQs):
            Answer = read_txt(f"{config.get('Paths', 'Ans_to_cq_output_folder')}Publication{pub}_CQ{i+1}.txt")
            prompt = f"Q{i+1}: {cq}\nA{i+1}: {Answer}\n"
            combined_prompt += prompt
        onto = "Here is the ontology:"
        combined_prompt += onto
        owl_content = read_txt(config.get('Paths', 'Created_onto_path'))
        combined_prompt += f"\nOntology:\n{owl_content}\n"
        Output = llm.invoke(combined_prompt)
        output_file_path = f"{config.get('Paths', 'KG_files')}Publication_{pub}.ttl"
        extract_and_save_concepts(Output, output_file_path)
