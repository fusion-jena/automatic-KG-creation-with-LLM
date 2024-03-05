from helper_functions import load_llm, read_txt
from langchain.prompts import PromptTemplate
import pandas as pd
import os
from LLM_loader import llm

def Evaluate_KG_with_LLM():
    KG_individual_Eval_path = config.get('Paths', 'KG_individual_Eval_path')
    prompt_cq_ans_version = config.get('Paths', 'prompt_cq_ans_version')
    folder_path = os.path.join(KG_individual_Eval_path, prompt_cq_ans_version)
    dfs = []
    for file in os.listdir(folder_path):
        if file.endswith('.csv'):
            df = pd.read_csv(os.path.join(folder_path, file))
            dfs.append(df)

    fidf = pd.concat(dfs, ignore_index=True)

    KG_Eval_template = read_txt(config.get('Paths', 'KG_Eval_Judge_prompt'))
    prompt_template = PromptTemplate(input_variables=["strings","match_text"], template=KG_Eval_template)

    for index,row in fidf.iterrows():
        strings = row["KG Individual Label"]
        answer = row["CQ LLM Answer"]
        prompt = prompt_template.format(strings=strings, match_text = answer)
        output = llm.invoke(prompt,return_only_outputs=True)
        Response_sindex = output.find("Response: ") + len("Response: ")
        Response_eindex = output.find("\nExplanation:")
        Response = output[Response_sindex:Response_eindex]
        explanation_sindex = output.find("Explanation: ") + len("Explanation: ")
        explanation = output[explanation_sindex:]
        fidf.at[index,"Judge_llm_Response"] = Response
        fidf.at[index,"Judge_llm_explanation"] = explanation
    KG_individual_eval_result = config.get('Paths', 'KG_individual_eval_result')
    csv_path = os.path.join(KG_individual_Eval_path, prompt_cq_ans_version, KG_individual_eval_result)
    fidf.to_csv(csv_path,index=False)
    print(fidf["Judge_llm_Response"].value_counts())
