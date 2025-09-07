import os

# Define the folder and file paths
cq_file = '../CQs/CQs_KG.txt'
#cq_file = '../CQs/CQs.txt'
publication_folder = '../RAG_CQ_ans/V1_processed'
prompt_folder = '../NER_prompt/selected_CQs'

# Read the competency questions with their CQ numbers
competency_questions = {}
with open(cq_file, 'r') as f:
    for line in f:        
        if line.strip():  # Ensure no empty lines are processed
            parts = line.split(':', 1)
            if len(parts) == 2:
                cq_number = int(parts[0][2:])
                question = parts[1].strip()
                competency_questions[cq_number] = question

# Get the list of files in the publication folder
publication_files = [f for f in os.listdir(publication_folder) if f.endswith('.txt')]

# Dictionary to hold the publication content
publications = {}

# Process each file in the publication folder
for file in publication_files:
    # Extract the publication name and question number from the file name
    parts = file.split('_CQ')
    publication_name = parts[0]
    cq_number = int(parts[1].split('.txt')[0])
    
    # Read the content of the file
    with open(os.path.join(publication_folder, file), 'r') as f:
        content = f.read().strip()
    
    # Add the content to the corresponding publication entry
    if publication_name not in publications:
        publications[publication_name] = {}
    publications[publication_name][cq_number] = content

# Create the NER prompt files for each publication
for publication_name, content_dict in publications.items():
    output_file = os.path.join(prompt_folder, f'{publication_name}.txt')
    with open(output_file, 'w') as f:
        # Write the instructions
        f.write(""" %INSTRUCTIONS: Your task is to do Named Entity Recognition. You extract named entities from the provided competency question answers. 
        Use provided concepts to understand which named entities to extract from competency answers. 
        Concepts: Method, RawData, DataFormat, DataAnnotationTechnique, DataAugmentationTechnique, Dataset, PreprocessingStep, DataSplitCriteria, CodeRepository, DataRepository, CodeRepositoryLink, DataRepositoryLink, DeepLearningModel, Hyperparameter, HyperparameterOptimization, OptimizationTechnique, TrainingCompletionCriteria, RegularizationMethod, ModelPerformanceMonitoringStrategy, Framework, HardwareResource, PostprocessingStep, PerformanceMetric, GeneralizabilityMeasure, RandomnessStrategy, ModelPurpose, DataBiasTechnique, ModelDeploymentProcess, DeploymentPlatform.         
        Example: DeepLearningModel(CNN, RNN, Transformer), Framework(TensorFlow, PyTorch), PerformanceMetric(Accuracy, mean IoU)
        Below are the competency questions and answers: \n""")
        
        # Write each CQ and its corresponding answer in ascending order
        for cq_number in sorted(content_dict.keys()):
            if cq_number in competency_questions:
                cq = competency_questions[cq_number]
                answer = content_dict[cq_number]
                f.write(f'CQ: {cq}\n')
                f.write(f'Answer: {answer}\n\n')
        f.write("""Provide your answer as follows:
        Named Entities: For each provided Concept(Corresponding Named Entity,..), ...""")
