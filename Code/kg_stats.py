import os
import re
from rdflib import RDF, Graph
import csv
from pathlib import Path

kg_folder_path = "../KG/"
stats_folder_path = "../Stats/"

Path("../Stats").mkdir(parents=True, exist_ok=True)

def count_concepts_and_instances_in_kg(kg_file):
    g = Graph()
    g.parse(kg_file, format="turtle")

    # Count the number of unique concepts (classes) and instances
    concepts = set()
    instances = set()

    for s, p, o in g:
        if p == RDF.type:
            concepts.add(o)
            instances.add(s)

    return len(concepts), len(instances)

def aggregate_concept_counts(folder_path):
    publication_concept_count = {}

    for llm_folder in os.listdir(folder_path):
        llm_folder_path = os.path.join(folder_path, llm_folder)

        if os.path.isdir(llm_folder_path):
            for kg_file in os.listdir(llm_folder_path):
                if kg_file.endswith(".ttl"):
                    kg_file_path = os.path.join(llm_folder_path, kg_file)
                    num_concepts, num_instances = count_concepts_and_instances_in_kg(kg_file_path)

                    publication_num = re.search(r'\d+', kg_file).group()

                    if publication_num not in publication_concept_count:
                        publication_concept_count[publication_num] = {}

                    publication_concept_count[publication_num][llm_folder] = {
                        'Concepts': num_concepts,
                        'Instances': num_instances
                    }

    return publication_concept_count

def write_aggregated_stats_to_csv(publication_concept_count, llms):
    fieldnames = ['Publication'] + [f'{llm}_Concepts' for llm in llms] + [f'{llm}_Instances' for llm in llms]
    total_concepts = {llm: 0 for llm in llms}
    total_instances = {llm: 0 for llm in llms}

    with open(os.path.join(stats_folder_path, 'kg_aggregated_concept_instance_counts.csv'), 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for publication, counts in sorted(publication_concept_count.items(), key=lambda x: int(x[0])):
            row = {'Publication': publication}
            for llm in llms:
                if llm in counts:
                    row[f'{llm}_Concepts'] = counts[llm]['Concepts']
                    row[f'{llm}_Instances'] = counts[llm]['Instances']
                    total_concepts[llm] += counts[llm]['Concepts']
                    total_instances[llm] += counts[llm]['Instances']
                else:
                    row[f'{llm}_Concepts'] = 0
                    row[f'{llm}_Instances'] = 0
            writer.writerow(row)

        # Add the total concepts and instances row
        total_row = {'Publication': 'Total'}
        for llm in llms:
            total_row[f'{llm}_Concepts'] = total_concepts[llm]
            total_row[f'{llm}_Instances'] = total_instances[llm]
        writer.writerow(total_row)

# Main script
if __name__ == "__main__":
    publication_concept_count = aggregate_concept_counts(kg_folder_path)

    # Extract the list of LLMs from the folder names
    llms = [folder for folder in os.listdir(kg_folder_path) if os.path.isdir(os.path.join(kg_folder_path, folder))]

    # Write the aggregated data to a CSV file
    write_aggregated_stats_to_csv(publication_concept_count, llms)

    print("Aggregated statistics have been written to kg_aggregated_concept_instance_counts.csv")
