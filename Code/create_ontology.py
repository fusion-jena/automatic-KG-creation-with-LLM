import os
import csv
from rdflib import Graph, Namespace, RDF, RDFS, OWL, Literal, URIRef, XSD

models = ['GPT4', 'GPT3.5', 'Gemini']
ontology_folder = "../Ontology/"
concept_relations_folder = "Concepts_relations"

# Define namespaces
DLPROV = Namespace("https://w3id.org/dlprov#")
PROV = Namespace("http://www.w3.org/ns/prov#")

# Function to load concept relations from concept_relations.txt
def load_concept_relations(file_path):
    concepts = []
    relationships = []
    data_properties = []
    inverse_properties = []

    with open(file_path, 'r') as file:
        lines = file.readlines()

        current_section = None
        for line in lines:
            line = line.strip()
            if line.startswith('Concepts:'):
                current_section = 'Concepts'
                concepts.extend(line.split(':')[1].strip().split(', '))
            elif line.startswith('Relationships:'):
                current_section = 'Relationships'
                relationships.extend(line.split(':')[1].strip().split(', '))
            elif line.startswith('DataProperties:'):
                current_section = 'DataProperties'
                data_properties.extend(line.split(':')[1].strip().split(', '))
            elif line.startswith('InverseProperties:'):
                current_section = 'InverseProperties'
                inverse_properties.extend(line.split(':')[1].strip().split(', '))
            elif current_section:
                # If the line doesn't start with one of the section headers, it belongs to the current section
                if line:
                    if current_section == 'Concepts':
                        concepts.extend(line.split(', '))
                    elif current_section == 'Relationships':
                        relationships.extend(line.split(', '))
                    elif current_section == 'DataProperties':
                        data_properties.extend(line.split(', '))
                    elif current_section == 'InverseProperties':
                        inverse_properties.extend(line.split(', '))

    return concepts, relationships, data_properties, inverse_properties


# Function to create RDF triples for concepts, relationships, properties
def create_ontology(model_name, concepts, relationships, data_properties, inverse_properties):
    g = Graph()    
    g.bind("dlprov", DLPROV)
    print(f'model_name:{model_name}')
    print(f'concepts:{concepts}')
    print(f'relationships:{relationships}')

    # Define classes (concepts) as subclasses of DLPROV:Entity
    for concept in concepts:
        concept_uri = DLPROV[concept]
        print(f'concept_uri:{concept_uri}')
        g.add((concept_uri, RDF.type, OWL.Class))
        g.add((concept_uri, RDFS.subClassOf, PROV.Entity))
        g.add((concept_uri, RDFS.label, Literal(concept, datatype=XSD.string)))

    # Define relationships (object properties)
    for rel in relationships:
        rel_uri = DLPROV[rel]
        print(f'rel_uri:{rel_uri}')
        g.add((rel_uri, RDF.type, OWL.ObjectProperty))
        g.add((rel_uri, RDFS.label, Literal(rel, datatype=XSD.string)))

    # Define data properties
    for prop in data_properties:
        prop_uri = DLPROV[prop]
        print(f'prop_uri:{prop_uri}')
        g.add((prop_uri, RDF.type, OWL.DatatypeProperty))
        g.add((prop_uri, RDFS.label, Literal(prop, datatype=XSD.string)))

    # Define inverse properties
    for inv_prop in inverse_properties:
        inv_prop_uri = DLPROV[inv_prop]
        print(f'inv_prop_uri:{inv_prop_uri}')
        g.add((inv_prop_uri, RDF.type, OWL.ObjectProperty))
        g.add((inv_prop_uri, OWL.inverseOf, inv_prop_uri))
        g.add((inv_prop_uri, RDFS.label, Literal(inv_prop, datatype=XSD.string)))

    # # Define relationships between concepts and properties (for demonstration)
    # # These should be replaced with actual relationships from your data
    # for concept in concepts:
    #     for rel in relationships:
    #         g.add((DLPROV[concept], DLPROV[rel], DLPROV[concept + '_' + rel]))

    # Save the ontology to a Turtle file
    ontology_folder_path = os.path.join(ontology_folder, model_name, 'Ontology')
    os.makedirs(ontology_folder_path, exist_ok=True)
    ontology_file = os.path.join(ontology_folder_path, f'dlprov.ttl')
    print(ontology_file)
    g.serialize(destination=ontology_file, format='turtle')
    print(g.serialize(format='turtle'))

    print(f'Ontology for {model_name} created and saved at {ontology_file}')

# Main script
if __name__ == "__main__":
    # List of models with their concept_relations.txt paths
    for model in models:
        model_folder = os.path.join(ontology_folder, model, concept_relations_folder)
        if not os.path.isdir(model_folder):
            print(f"Warning: {concept_relations_folder} folder not found for {model}. Skipping.")
            continue     
    
    
        concept_relations_file = os.path.join(model_folder, 'concept_relation_data_inverse.txt')
        
        concepts, relationships, data_properties, inverse_properties = load_concept_relations(concept_relations_file)
        create_ontology(model, concepts, relationships, data_properties, inverse_properties)
