from helper_functions import load_llm, read_txt, load_cqs
from langchain.prompts import PromptTemplate
from LLM_loader import llm

def Concepts_relations_generate(config):
    template = read_txt(config.get('Paths', 'Concepts_and_relationships_prompt_path'))
    prompt_template = PromptTemplate(input_variables=["CQs"], template=template)
    prompt = prompt_template.format(CQs=load_cqs(config.get('Paths', 'CQs_path')))

    with open(config.get('Paths', 'Concepts_and_relationships_save_path'),"w") as f:
        f.write(llm.invoke(prompt))
