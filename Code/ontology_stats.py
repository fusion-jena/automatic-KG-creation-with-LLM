import os
from rdflib import Graph, Namespace, RDF, OWL
from pathlib import Path
import csv

models = ['GPT4', 'GPT3.5', 'Gemini', 'Mixtral_8_22b']
ontology_folder = "../Ontology/"

def count_axioms(ontology_file):
    g = Graph()
    g.parse(ontology_file, format="turtle")
    
    classes = len(list(g.subjects(RDF.type, OWL.Class)))
    object_properties = len(list(g.subjects(RDF.type, OWL.ObjectProperty)))
    data_properties = len(list(g.subjects(RDF.type, OWL.DatatypeProperty)))
    subClassOf_axioms = len(list(g.triples((None, RDF.type, OWL.Class))))
    total_axioms = len(list(g))
    
    return classes, object_properties, data_properties, subClassOf_axioms, total_axioms

def calculate_statistics_for_models(models):
    model_statistics = {}
    
    for model in models:
        model_folder = os.path.join(ontology_folder, model, 'Ontology')
        if not os.path.isdir(model_folder):
            print(f"Warning: Ontology folder not found for {model}. Skipping.")
            continue
        
        class_count = 0
        object_prop_count = 0
        data_prop_count = 0
        subclassof_count = 0
        axiom_count = 0
        
        for ontology_file in os.listdir(model_folder):
            if ontology_file.endswith(".ttl"):
                ontology_file_path = os.path.join(model_folder, ontology_file)
                classes, object_properties, data_properties, subClassOf_axioms, total_axioms = count_axioms(ontology_file_path)
                
                class_count += classes
                object_prop_count += object_properties
                data_prop_count += data_properties
                subclassof_count += subClassOf_axioms
                axiom_count += total_axioms
        
        model_statistics[model] = {
            'Classes': class_count,
            'Object_Properties': object_prop_count,
            'Data_Properties': data_prop_count,
            'SubClassOf_Axioms': subclassof_count,
            'Total_Axioms': axiom_count
        }
    
    return model_statistics

def write_statistics_to_csv(model_statistics):
    fieldnames = ['Model', 'Classes', 'Object_Properties', 'Data_Properties', 'SubClassOf_Axioms', 'Total_Axioms']

    with open("../Stats/ontology_statistics.csv", 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for model, stats in model_statistics.items():
            writer.writerow({
                'Model': model,
                'Classes': stats['Classes'],
                'Object_Properties': stats['Object_Properties'],
                'Data_Properties': stats['Data_Properties'],
                'SubClassOf_Axioms': stats['SubClassOf_Axioms'],
                'Total_Axioms': stats['Total_Axioms']
            })

# Main script
if __name__ == "__main__":
    model_statistics = calculate_statistics_for_models(models)
    write_statistics_to_csv(model_statistics)

    print("Ontology statistics have been written to ontology_statistics.csv")
