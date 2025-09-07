import os
from rdflib import RDF, Graph
import csv
import re
from collections import defaultdict
from pathlib import Path

kg_folder_path = "../KG/"
stats_folder_path = "../Stats/"
Path("../Stats").mkdir(parents=True, exist_ok=True)

def extract_concepts_and_instances_from_kg(kg_file):
    g = Graph()
    g.parse(kg_file, format="turtle")

    # Extract unique concepts (classes) and instances
    concepts = set()
    instances = set()
    for s, p, o in g:
        if p == RDF.type:
            concepts.add(o)
            instances.add(s)

    return concepts, instances

def aggregate_concepts_and_instances_by_publication(folder_path):
    publication_data = defaultdict(lambda: defaultdict(lambda: {'concepts': set(), 'instances': set()}))

    for llm_folder in os.listdir(folder_path):
        llm_folder_path = os.path.join(folder_path, llm_folder)

        if os.path.isdir(llm_folder_path):
            for kg_file in os.listdir(llm_folder_path):
                if kg_file.endswith(".ttl"):
                    kg_file_path = os.path.join(llm_folder_path, kg_file)
                    concepts, instances = extract_concepts_and_instances_from_kg(kg_file_path)

                    # Extract publication number from the filename
                    publication_num = re.search(r'\d+', kg_file).group()

                    publication_data[publication_num][llm_folder]['concepts'] = concepts
                    publication_data[publication_num][llm_folder]['instances'] = instances

    return publication_data

def calculate_similarity(publication_data):
    similarity_counts = defaultdict(lambda: defaultdict(lambda: {'concepts': '', 'instances': ''}))
    total_counts = defaultdict(lambda: {'concepts': 0, 'concepts_total': 0, 'instances': 0, 'instances_total': 0})

    for publication, llm_data in publication_data.items():
        llms = list(llm_data.keys())

        for i in range(len(llms)):
            for j in range(i + 1, len(llms)):
                llm1 = llms[i]
                llm2 = llms[j]

                concepts1 = llm_data[llm1]['concepts']
                concepts2 = llm_data[llm2]['concepts']
                instances1 = llm_data[llm1]['instances']
                instances2 = llm_data[llm2]['instances']

                # Find the intersection of concepts and instances
                common_concepts = concepts1.intersection(concepts2)
                common_instances = instances1.intersection(instances2)

                # Calculate the count and percentage for concepts
                common_concepts_count = len(common_concepts)
                total_concepts = len(concepts1.union(concepts2))
                concepts_percentage = (common_concepts_count / total_concepts) * 100 if total_concepts > 0 else 0

                # Calculate the count and percentage for instances
                common_instances_count = len(common_instances)
                total_instances = len(instances1.union(instances2))
                instances_percentage = (common_instances_count / total_instances) * 100 if total_instances > 0 else 0

                # Update similarity counts with count and percentage
                similarity_counts[publication][f"{llm1}-{llm2}"]['concepts'] = f"{common_concepts_count}/{total_concepts} ({concepts_percentage:.2f}%)"
                similarity_counts[publication][f"{llm2}-{llm1}"]['concepts'] = f"{common_concepts_count}/{total_concepts} ({concepts_percentage:.2f}%)"
                similarity_counts[publication][f"{llm1}-{llm2}"]['instances'] = f"{common_instances_count}/{total_instances} ({instances_percentage:.2f}%)"
                similarity_counts[publication][f"{llm2}-{llm1}"]['instances'] = f"{common_instances_count}/{total_instances} ({instances_percentage:.2f}%)"

                # Update total counts for aggregation
                total_counts[f"{llm1}-{llm2}"]['concepts'] += common_concepts_count
                total_counts[f"{llm1}-{llm2}"]['concepts_total'] += total_concepts
                total_counts[f"{llm1}-{llm2}"]['instances'] += common_instances_count
                total_counts[f"{llm1}-{llm2}"]['instances_total'] += total_instances

    return similarity_counts, total_counts

def write_similarity_to_csv(similarity_counts, total_counts, llms):
    # Determine unique pairs of LLMs
    llm_pairs = []
    for i in range(len(llms)):
        for j in range(i + 1, len(llms)):
            llm_pairs.append(f"{llms[i]}-{llms[j]}")

    fieldnames = ['Publication'] + [f"{pair}_Concepts" for pair in llm_pairs] + [f"{pair}_Instances" for pair in llm_pairs]

    with open(os.path.join(stats_folder_path,'kg_concept_and_instance_similarity_counts.csv'), 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for publication, counts in sorted(similarity_counts.items(), key=lambda x: int(x[0])):
            row = {'Publication': publication}
            for pair in llm_pairs:
                row[f"{pair}_Concepts"] = counts.get(pair, {}).get('concepts', '0/0 (0.00%)')
                row[f"{pair}_Instances"] = counts.get(pair, {}).get('instances', '0/0 (0.00%)')
            writer.writerow(row)

        # Write the aggregated total and average
        total_row = {'Publication': 'Total'}
        average_row = {'Publication': 'Average'}
        for pair in llm_pairs:
            total_concepts = total_counts[pair]['concepts_total']
            total_instances = total_counts[pair]['instances_total']

            total_row[f"{pair}_Concepts"] = f"{total_counts[pair]['concepts']}/{total_concepts} ({(total_counts[pair]['concepts'] / total_concepts) * 100 if total_concepts > 0 else 0:.2f}%)"
            total_row[f"{pair}_Instances"] = f"{total_counts[pair]['instances']}/{total_instances} ({(total_counts[pair]['instances'] / total_instances) * 100 if total_instances > 0 else 0:.2f}%)"

            average_row[f"{pair}_Concepts"] = f"{total_counts[pair]['concepts'] / len(similarity_counts):.2f}/{total_concepts / len(similarity_counts):.2f} ({(total_counts[pair]['concepts'] / total_concepts) * 100 if total_concepts > 0 else 0:.2f}%)"
            average_row[f"{pair}_Instances"] = f"{total_counts[pair]['instances'] / len(similarity_counts):.2f}/{total_instances / len(similarity_counts):.2f} ({(total_counts[pair]['instances'] / total_instances) * 100 if total_instances > 0 else 0:.2f}%)"

        writer.writerow(total_row)
        writer.writerow(average_row)

# Main script
if __name__ == "__main__":

    publication_data = aggregate_concepts_and_instances_by_publication(kg_folder_path)

    # Extract the list of LLMs from the folder names
    llms = [folder for folder in os.listdir(kg_folder_path) if os.path.isdir(os.path.join(kg_folder_path, folder))]

    # Calculate the similarity counts
    similarity_counts, total_counts = calculate_similarity(publication_data)

    # Write the similarity counts to a CSV file
    write_similarity_to_csv(similarity_counts, total_counts, llms)

    print("Similarity statistics have been written to kg_concept_and_instance_similarity_counts.csv")
