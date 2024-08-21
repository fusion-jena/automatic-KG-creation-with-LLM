import os
import re
import rdflib
from rdflib import Graph, Namespace, Literal, RDF
from urllib.parse import quote

# Define the folders and files paths
ner_folder = '../NER/'
kg_folder = '../KG/'


# Define the namespace
DLPROV = Namespace("https://w3id.org/dlprov#")

# Function to read named entities from a publication file
def read_named_entities(file_path):
    named_entities = {}
    exclude_phrases = ["not mentioned", "Not mentioned", "Not Provided",
                       "not explicitly mentioned", "not provided", "Not explicitly mentioned"]
    f = open(file_path, "r")
    lines = f.readlines()

    #lines = str(lines).strip().split('\n')


    for line in lines[1:]:  # Skip the first line
        # Using regular expression to correctly split at the first parenthesis
        #line = line.strip().split('\n')
        if 'named entities' in line.lower() or 'for each provided concept' in line.lower():
            continue
        if line.strip():
            if ':' in line:
                concept, entity_str = line.split(':', 1)
                concept = concept.strip()
                entity_str = entity_str.strip()
                entities = [entity.strip() for entity in entity_str.split(',')]
                filtered_entities = [entity for entity in entities if entity not in exclude_phrases]
                if filtered_entities:
                    named_entities[concept] = filtered_entities

            else:
                concept, entities_str = line.split('(', 1)
                entities_str = entities_str.rstrip('),')
                entities = [entity.strip() for entity in entities_str.split(',')]
                filtered_entities = [entity for entity in entities if entity not in exclude_phrases]
                if filtered_entities:
                    named_entities[concept.strip()] = filtered_entities

    return named_entities

# Clean and encode entity names
def clean_and_encode(entity_name):
    # Remove unwanted characters and encode
    entity_name = entity_name.replace('\\', '').replace(')', '').strip()
    return quote(entity_name.replace(' ', '_'))

# Convert named entities to KG
def create_kg(named_entities):

    g = Graph()
    g.bind("dlprov", DLPROV)

    for concept, entities in named_entities.items():
        #print(f'concept: {concept}')
        #print(f'entities: {entities[0]}')
        if ("not mentioned" in entities[0].lower()) or ("not provided" in entities[0].lower()):            
            continue


        concept_uri = DLPROV[clean_and_encode(concept.strip())]


        for entity in entities:
            entity_name, *abbr = entity.split('(')
            if entity_name:
                entity_name = entity_name.strip()
                abbr = abbr[0].strip(')') if abbr else None
                entity_uri = DLPROV[clean_and_encode(entity_name)]
                g.add((entity_uri, RDF.type, concept_uri))
                if abbr:
                    abbr_uri = DLPROV[clean_and_encode(abbr)]
                    g.add((abbr_uri, RDF.type, concept_uri))

    return g


# Function to write the KG to a file
def write_kg_to_file(kg, output_file):
    kg.serialize(destination=output_file, format='turtle')

# Main script
if __name__ == "__main__":
    models = ['GPT4', 'GPT3.5', 'Gemini', 'Mixtral_8_22b']
    for model_name in models:
        llm_model_path = os.path.join(ner_folder, model_name)
        kg_model_path = os.path.join(kg_folder, model_name)
        # Iterate through the publications
        for publication_file in os.listdir(llm_model_path):
            if publication_file.endswith('.txt'):
                publication_path = os.path.join(llm_model_path, publication_file)
                print('Publication Path: {}'.format(publication_path))
                named_entities = read_named_entities(publication_path)
                print('named_entities: {}'.format(named_entities))


                # Create KG
                kg = create_kg(named_entities)

                # Output KG file
                output_file = os.path.join(kg_model_path, publication_file.replace('.txt', '_KG.ttl'))
                write_kg_to_file(kg, output_file)
