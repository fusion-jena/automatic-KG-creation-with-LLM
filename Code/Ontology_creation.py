from helper_functions import load_llm, load_cqs, read_txt
from langchain.prompts import PromptTemplate

model_id = 'mistralai/Mixtral-8x7B-Instruct-v0.1'
embedding_model_id = "sentence-transformers/all-MiniLM-L12-v2"
llm = load_llm(model_id, embedding_model_id)

template = read_txt("../Prompts/Ontology_creation.txt")
prompt_template = PromptTemplate(input_variables=["concepts", "relations"], template=template)

concepts_relationships = read_txt("../Concepts_relations/Concepts_and_relationships.txt")
concepts_s_ind = content.find('Concepts:') + len('Concepts:')
relationships_s_ind = content.find('Relationships:') + len('Relationships:')
concepts_e_ind = content.find('Relationships:')
concepts = content[concepts_s_ind:concepts_e_ind].strip()
relationships = content[relationships_s_ind:].strip()

prompt = prompt_template.format(concepts=concepts,relations=relationships)

with open("../Ontology/DLProv.owl","w") as f:
    f.write()