from helper_functions import load_llm, load_cqs, read_txt
from langchain.prompts import PromptTemplate
from rdflib import Graph, Namespace

model_id = 'mistralai/Mixtral-8x7B-Instruct-v0.1'
embedding_model_id = "sentence-transformers/all-MiniLM-L12-v2"
llm = load_llm(model_id, embedding_model_id)

template = read_txt("../Prompts/Ontology_creation.txt")
prompt_template = PromptTemplate(input_variables=["concepts", "relations"], template=template)

def get_base_onto_class(owl_file):

    g = Graph()
    g.parse(owl_file)

    # Define commonly used namespaces
    RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    OWL = Namespace("http://www.w3.org/2002/07/owl#")

    classes = []
    relations = []
    # Find classes
    for class_uri in g.subjects(RDF.type, OWL.Class):
        class_label = class_uri.split('#')[-1]
        classes.append(class_label)

    # Find properties
    for prop_uri in g.subjects(RDF.type, OWL.ObjectProperty):
        prop_label = prop_uri.split('#')[-1]
        relations.append(prop_label)
    return classes, relations

content = read_txt("../Concepts_relations/Concepts_and_relationships.txt")
concepts_s_ind = content.find('Concepts:') + len('Concepts:')
relationships_s_ind = content.find('Relationships:') + len('Relationships:')
concepts_e_ind = content.find('Relationships:')
concepts = content[concepts_s_ind:concepts_e_ind].strip()
relationships = content[relationships_s_ind:].strip()
base_onto_class, base_onto_property = get_base_onto_class("../SOTAOntologies/prov-o.owl")

prompt = prompt_template.format(concepts=concepts,relations=relationships,base_onto_class=base_onto_class,base_onto_property=base_onto_property)

with open("../Ontology/DLProv.owl","w") as f:
    f.write(llm(prompt))