from helper_functions import load_llm, read_txt, conv_int_he
from langchain.prompts import PromptTemplate
import pandas as pd
from LLM_loader import llm

def Evaluate_RAG(config):
    paths = [config['Paths'][f'path{i}_cq_ans_eval'] for i in range(1, 6)]
    frames = []
    for file_path in paths:
        df = pd.read_csv(file_path)
        frames.append(df)
    fidf = pd.concat(frames)
    fidf.reset_index(inplace=True, drop=True)

    RAG_LLM_Judge_template = read_txt(config.get('Paths', 'RAG_LLM_Judge_prompt'))
    prompt_template = PromptTemplate(input_variables=["ground_truth","prediction_answer","question"], template=RAG_LLM_Judge_template)
    for index,row in fidf.iterrows():
        question = row["CQ"]
        ground_truth = row["CQ Ground Truth"]
        answer = row["CQ LLM Answer Processed"]
        prompt = prompt_template.format(ground_truth=ground_truth, prediction_answer = answer, question=question)
        output = llm.invoke(prompt,return_only_outputs=True)
        score_sindex = output.find("score: ") + len("score: ")
        score_eindex = output.find("\nExplanation:")
        score = int(output[score_sindex:score_eindex])
        explanation_sindex = output.find("Explanation: ") + len("Explanation: ")
        explanation = output[explanation_sindex:]
        fidf.at[index,"Judge_llm_score"] = score
        fidf.at[index,"Judge_llm_explanation"] = explanation

    fidf['Judge_llm_score_str'] = fidf['Judge_llm_score'].apply(conv_int_he)
    fidf.to_csv(config.get('Paths', 'RAG_LLM_Eval_csv_path'),index=False)

    non_matching_rows = fidf[fidf['Evaluation'] != fidf['Judge_llm_score_str']]

    print(non_matching_rows.shape)
