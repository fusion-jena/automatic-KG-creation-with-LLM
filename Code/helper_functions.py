import os
import re
import transformers
from langchain.embeddings import HuggingFaceEmbeddings
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from langchain import HuggingFacePipeline
import torch
from huggingface_hub import login
from dotenv import load_dotenv
from rdflib import Graph, Namespace
load_dotenv(override = True)
access_token_read = os.getenv('access_token_read_hf')
login(token = access_token_read)

def load_llm(model_id,embedding_model_id):
    bnb_config = transformers.BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type='nf4',
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=torch.bfloat16
    )
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model_id,model_kwargs={'device': 'cuda'})
    model_config = transformers.AutoConfig.from_pretrained(model_id)
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id,
        trust_remote_code=True,
        config=model_config,
        quantization_config=bnb_config,
        device_map='auto')
    model.eval()
    pipe = pipeline(model=model, tokenizer=tokenizer,
        #return_full_text=True,  # langchain expects the full text
        task='text-generation',
        temperature=0.00001,
        max_new_tokens=25000,  # max number of tokens to generate in the output
        #repetition_penalty=1.1,  # without this output begins repeating
        device_map = "auto"
    )
    llm=HuggingFacePipeline(pipeline=pipe, model_kwargs={'temperature':0.00001})
    return llm


def load_cqs(CQs_path):
    with open(CQs_path) as f:
        lines = f.readlines()
    CQs = [l[:-1] for l in lines]
    return CQs

def read_txt(txt_path):
    with open(txt_path,'r') as f:
        content = f.read()
    return content

def get_embeddings(embedding_model_id):
    return HuggingFaceEmbeddings(model_name=embedding_model_id,model_kwargs={'device': 'cuda'})
    
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
    

def extract_and_save_concepts(result, output_file_path):
    with open(output_file_path, 'w') as f:
        result = result.replace('Knowledge Graph:', '')
        f.write(result)
    print(f"Result: {result}")
    print("\n")
    
def conv_int_he(value):
    if value >= 6:
        return "Right"
    elif value < 3:
        return "Wrong"
    else:
        return "Partial"
        
def find_rdf_triples(g, predicate, ontology_concept):
    # Find RDF triples in the graph g that match the given predicate and ontology concept
    triples = []
    for subj, pred, obj in g.triples((None, predicate, ontology_concept)):
        print(subj)
        print(pred)
        print(obj)
        triples.append((subj, pred, obj))
    return triples
    
def extract_kg_info(triples):
    # Extract KG individual and label from RDF triples
    # For demonstration purposes, let's assume we are extracting the first match
    kg_individual = None
    kg_individual_label = None
    if triples:
        subj, _, _ = triples[0]
        kg_individual = str(subj)
        # Assuming there's an RDFS label associated with the individual
        kg_individual_label = str(subj).split('#')[-1]  # Extract the individual label from its URI
    return kg_individual, kg_individual_label

    
