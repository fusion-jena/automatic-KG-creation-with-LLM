import os
import re
import csv
from rdflib import Graph, Namespace
from helper_functions import find_rdf_triples, extract_kg_info

def KG_indvidual_csv_creation(config):
    # Folder containing the text files
    folder_path = config.get('Paths', 'Ans_to_cq_v1_summary')

    # Path to the file containing the competency questions
    cq_file = config.get('Paths', 'CQs_path')

    # Regular expression pattern to extract the publication number from filenames
    pattern = re.compile(r'Publication(\d+)_CQ(\d+)')

    # Mapping of competency questions to ontology concepts
    cq_ontology_mapping = {
        "What data formats are used in the deep learning pipeline?": ["DataFormat"],
        "What are the sources of input data for the deep learning pipeline?": ["Source", "InputData"],
        "How was raw data collected in terms of methods and tools?": ["Method", "Tool"],
        "Is the source code openly accessible, and if so, what is the repository link?": ["RepositoryLink"],
        "What preprocessing steps are involved before training the deep learning model?": ["PreprocessingStep"],
        "Are there transformations or augmentations applied to the input data?": ["TransformationAugmentation"],
        "Does the paper discuss data bias or ethical implications?": ["Bias", "EthicalImplication"],
        "What is the architecture of the deep learning model in the pipeline?": ["Architecture", "Model"],
        "How was the model selected for a specific task?": ["ModelSelectionProcess", "Model"],
        "What were the considerations in the model selection process?": ["Consideration"],
        "How many models are used in the pipeline?": ["NumberOfModels"],
        "Are the models considered state-of-the-art?": ["StateOfTheArt", "Model"],
        "How is the model initialized?": ["Initialization",  "Model"],
        "Are there specific weight configurations used during initialization?": ["WeightConfiguration"],
        "Are there optimization algorithms or learning rate schedules used during training?": ["OptimizationAlgorithm", "LearningRateSchedule"],
        "What is the convergence criteria or stopping condition for the training process?": ["ConvergenceCriteria", "TrainingProcedure"],
        "Which software frameworks or libraries are used to build the model?": ["SoftwareFrameworkLibrary"],
        "What hardware infrastructures are used for model training?": ["HardwareInfrastructure"],
        "What hyperparameters are used in the model?": ["Hyperparameter"],
        "Why were those specific hyperparameters selected?": ["Hyperparameter"],
        "Are the provided hyperparameters fine-tuned?": ["FineTuning"],
        "What metrics are used to evaluate the model?": ["Metric"],
        "Did the authors use different metrics for different problems?": ["Metric"],
        "Is there sufficient information to reproduce the deep learning pipeline?": ["Reproducibility"],
        "What measures are taken to explain model predictions?": ["Explanation", "PredictionClassification"],
        "What is the versioning strategy for trained models?": ["VersioningStrategy"],
        "How are different versions of datasets managed?": ["DatasetVersion"],
        "How are updates to datasets documented?": ["UpdateFrequency"],
        "What annotations or labels are associated with the data?": ["PredictionClassification"],
        "How are these annotations or labels used in the model?": [],
        "What predictions or classifications are generated by the deep learning model?": ["PredictionClassification"],
        "How is uncertainty or confidence in model predictions captured?": ["UncertaintyConfidence"],
        "Are there post-processing steps applied to the model's output?": ["PostProcessing"],
        "Is the trained model deployed, and if not, what is the reason?": ["Deployment"],
        "What hardware and software are used for model deployment?": ["SoftwareFrameworkLibrary", "HardwareInfrastructure"],
        "How often are model weights updated by retraining with new data?": [],
        "What ethical considerations are taken into account during development and deployment?": ["EthicalImplication"],
        "How is bias in the data addressed?": ["BiasAddressing"],
        "Is there transparency in the decision-making process regarding bias?": ["Transparency"],
        "Are privacy and security measures implemented in handling sensitive data?": ["PrivacySecurityMeasure", "SensitiveData"]
    }


    # Read the competency questions from the file
    with open(cq_file, 'r') as f:
        cq_lines = f.readlines()
        cq_lines = [line.strip() for line in cq_lines]

    # Dictionary to store content for each publication
    publication_dict = {}

    # Iterate through files in the folder
    for filename in os.listdir(folder_path):
        # Check if the file is a text file
        if filename.endswith('.txt'):
            file_path = os.path.join(folder_path, filename)
            # Extract the publication number and CQ number from the filename using regular expression
            match = pattern.search(filename)
            if match:
                publication_no = int(match.group(1))
                cq_no = int(match.group(2))
                # Read the content of the file
                with open(file_path, 'r') as file:
                    content = file.read().strip()
                    # Add content to the dictionary
                    publication_dict.setdefault(publication_no, {}).setdefault(cq_no, []).append(content)


    ontology_ns = Namespace("https://w3id.org/dlprovenance#")

    # Define RDF namespaces
    RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")

    folder_path = config.get('Paths', 'KG_individual_Eval_path')
    os.makedirs(folder_path, exist_ok=True)

    # Iterate through the publication numbers and write content to respective CSV files
    for publication_no, cq_data in publication_dict.items():
        print(publication_no)
        #if publication_no != 3:
        #    continue
        version = config.get('Paths', 'prompt_cq_ans_version')
        kg_files_directory = config.get('Paths', 'kg_files_path')
        kg_eval_filename_format = config.get('Paths', 'kg_eval_filename_format')
        # Path to the KG file
        kg_file = os.path.join(kg_files_directory, f'{version}', f'Publication_{publication_no}.ttl')

        # Parse the KG file
        g = Graph()
        g.parse(kg_file, format="ttl")

        # Create a separate CSV file for each publication number
        csv_file = os.path.join(folder_path, f'{version}', kg_evaluation_filename_format.format(publication_no=publication_no))
        # Write content to CSV file
        with open(csv_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            # Write header row
            writer.writerow(['Publication No.', 'CQ No.', 'CQ', 'CQ LLM Answer', 'Ontology Concept', 'KG Individual', 'KG Individual Label'])
            # Write content to CSV file
            for cq_no in range(1, 41):  # Assuming there are 40 CQs
                for content in cq_data.get(cq_no, [''] * 3):  # Get content for each CQ, fill with empty strings if not present
                    # Find the ontology concepts associated with the current CQ
                    ontology_concepts = cq_ontology_mapping.get(cq_lines[cq_no - 1], [])

                    for ontology_concept in ontology_concepts:

                        for subj, pred, obj in g.triples((None, RDF.type, ontology_ns[ontology_concept])):
                            for s, p, o in g.triples((subj, RDFS.label, None)):
                                rdfs_label = str(o)
                                writer.writerow([publication_no, cq_no, cq_lines[cq_no - 1], content, ontology_concept, s, rdfs_label])
