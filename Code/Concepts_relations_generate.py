from helper_functions import load_llm, load_cqs, read_txt
from langchain.prompts import PromptTemplate

model_id = 'mistralai/Mixtral-8x7B-Instruct-v0.1'
embedding_model_id = "sentence-transformers/all-MiniLM-L12-v2"
llm = load_llm(model_id, embedding_model_id)

template = read_txt("../Prompts/Concepts_and_relationships_extraction.txt")
prompt_template = PromptTemplate(input_variables=["CQs"], template=template)
prompt = prompt_template.format(CQs=load_cqs(path))

with open("../Concepts_relations/Concepts_and_relationships.txt","w") as f:
    f.write(llm(prompt_n))