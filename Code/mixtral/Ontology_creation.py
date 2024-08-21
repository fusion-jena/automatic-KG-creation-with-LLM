from helper_functions import load_llm, read_txt, get_base_onto_class
from langchain.prompts import PromptTemplate
from rdflib import Graph, Namespace
from LLM_loader import llm

def Ontology_creation(config):
    template = read_txt(config.get('Paths', 'Ontology_creation_prompt'))
    prompt_template = PromptTemplate(input_variables=["concepts", "relations","data_properties","InverseProperties","base_onto_class","base_onto_property"], template=template)
    concepts_s_ind = content.find('Concepts:') + len('Concepts:')
    concepts_e_ind = content.find('Relationships:')
    concepts = content[concepts_s_ind:concepts_e_ind].strip()
    
    relationships_s_ind = content.find('Relationships:') + len('Relationships:')
    relationships_e_ind = content.find('DataProperties:')
    relationships = content[relationships_s_ind:relationships_e_ind].strip()
    
    data_properties_s_ind = content.find('DataProperties:') + len('DataProperties:')
    data_properties_e_ind = content.find('InverseProperties:')
    data_properties = content[data_properties_s_ind:data_properties_e_ind].strip()
    
    inverse_properties_s_ind = content.find('InverseProperties:') + len('InverseProperties:')
    inverse_properties = content[inverse_properties_s_ind:].strip()
    base_onto_class, base_onto_property = get_base_onto_class(config.get('Paths', 'SOTAOntology_path'))

    prompt = prompt_template.format(concepts=concepts,relations=relationships,base_onto_class=base_onto_class,base_onto_property=base_onto_property)

    with open(config.get('Paths', 'Created_onto_path'),"w") as f:
        f.write(llm.invoke(prompt))
