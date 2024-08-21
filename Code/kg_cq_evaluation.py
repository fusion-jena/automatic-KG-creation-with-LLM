import os
import re
import rdflib
import csv
from urllib.parse import unquote
from pathlib import Path

stats_folder_path = "../Stats/"
Path("../Stats").mkdir(parents=True, exist_ok=True)

models = ['GPT4', 'GPT3.5', 'Gemini', 'Mixtral_8_22b']
cq_folder_path = "../RAG_CQ_ans/V1_processed"
kg_folder_path = "../KG/"
cq_kg_file = '../CQs/CQs_KG.txt'

def load_cq_answers(cq_folder):
    cq_answers = {}
    for cq_file in os.listdir(cq_folder):
        if cq_file.endswith(".txt") and "CQ" in cq_file:
            publication_num = re.search(r'Publication(\d+)_CQ\d+\.txt', cq_file).group(1)
            with open(os.path.join(cq_folder, cq_file), 'r') as file:
                if publication_num not in cq_answers:
                    cq_answers[publication_num] = {}
                cq_number = re.search(r'CQ(\d+)', cq_file).group(1)
                cq_answers[publication_num][cq_number] = file.read().strip()
    return cq_answers

def get_relevant_cq_kg_numbers():
    # Read the competency questions with their CQ numbers
    relevant_cq_kg_numbers = []
    with open(cq_kg_file, 'r') as f:
        for line in f:
            if line.strip():
                parts = line.split(':', 1)
                if len(parts) == 2:
                    cq_number = int(parts[0][2:])
                    relevant_cq_kg_numbers.append(cq_number)
    return relevant_cq_kg_numbers

def extract_instances_from_kg(kg_file):
    g = rdflib.Graph()
    g.parse(kg_file, format="turtle")

    instances = set()
    for s, p, o in g:
        local_part = s.split('#')[-1]  # Get the part after the last '#'
        cleaned_instance = local_part.replace('_', ' ')
        decoded_local_part = unquote(cleaned_instance)  # URL decode the local part
        instances.add(decoded_local_part)

    return instances

def evaluate_kg(cq_answers, relevant_cq_numbers, kg_folder):
    evaluation_results = {}

    for model_name in models:
        model_folder_path = os.path.join(kg_folder, model_name)

        if os.path.isdir(model_folder_path):
            for kg_file in os.listdir(model_folder_path):
                if kg_file.endswith(".ttl"):
                    kg_file_path = os.path.join(model_folder_path, kg_file)
                    publication_num = re.search(r'\d+', kg_file).group()

                    if publication_num in cq_answers:
                        combined_cq_answers_list = []
                        for cq in relevant_cq_numbers:
                            cq = str(cq)
                            if str(cq) in cq_answers[publication_num]:
                                combined_cq_answers_list.append(cq_answers[publication_num][cq])
                            else:
                                print(f'Warning: CQ{cq} not found for Publication{publication_num}')

                        combined_cq_answers = ' '.join(combined_cq_answers_list)

                        kg_instances = extract_instances_from_kg(kg_file_path)

                        correct_instances = 0
                        for instance in kg_instances:
                            if instance in combined_cq_answers:
                                correct_instances += 1

                        if publication_num not in evaluation_results:
                            evaluation_results[publication_num] = {}
                        evaluation_results[publication_num][model_name] = {
                            'Total_Instances': len(kg_instances),
                            'Correct_Instances': correct_instances,
                            'Percentage': f"{(correct_instances / len(kg_instances) * 100):.2f}%" if len(kg_instances) > 0 else "0%"
                        }

    return evaluation_results

def write_evaluation_results_to_csv(evaluation_results):
    fieldnames = ['Publication'] + models
    with open(os.path.join(stats_folder_path, 'kg_cq_evaluation_results.csv'), 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(fieldnames)

        for publication_num, results in sorted(evaluation_results.items(), key=lambda x: int(x[0])):
            row = [publication_num]
            for model in models:
                if model in results:
                    total_instances = results[model]['Total_Instances']
                    correct_instances = results[model]['Correct_Instances']
                    percentage = results[model]['Percentage']
                    row.append(f"{correct_instances}/{total_instances} ({percentage})")
                else:
                    row.append("0/0 (0%)")
            writer.writerow(row)

        # Add total row
        total_results = {model: {'Total_Instances': 0, 'Correct_Instances': 0} for model in models}
        for results in evaluation_results.values():
            for model in models:
                if model in results:
                    total_results[model]['Total_Instances'] += results[model]['Total_Instances']
                    total_results[model]['Correct_Instances'] += results[model]['Correct_Instances']

        total_row = ['Total']
        for model in models:
            total_instances = total_results[model]['Total_Instances']
            correct_instances = total_results[model]['Correct_Instances']
            percentage = f"{(correct_instances / total_instances * 100):.2f}%" if total_instances > 0 else "0%"
            total_row.append(f"{correct_instances}/{total_instances} ({percentage})")
        writer.writerow(total_row)

# Main script
if __name__ == "__main__":
    cq_answers = load_cq_answers(cq_folder_path)
    relevant_cq_numbers = get_relevant_cq_kg_numbers()
    evaluation_results = evaluate_kg(cq_answers, relevant_cq_numbers, kg_folder_path)
    write_evaluation_results_to_csv(evaluation_results)

    print("Evaluation results have been written to kg_cq_evaluation_results.csv")
