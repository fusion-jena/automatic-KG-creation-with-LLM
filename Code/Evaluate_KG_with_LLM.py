from helper_functions import load_llm, load_cqs, read_txt, get_embeddings
from langchain.prompts import PromptTemplate
import pandas as pd

folder_path = "../Evaluation/KG_individual/Prompt_v1_CQ_Ans_v2/"
dfs = []
for file in os.listdir(folder_path):
    if file.endswith('.csv'):
        df = pd.read_csv(os.path.join(folder_path, file))
        dfs.append(df)

fidf = pd.concat(dfs, ignore_index=True)

KG_Eval_template = read_txt("../Prompts/Judge_LLM_KG_individual.txt")
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
    
fidf.to_csv("../Evaluation/KG_individual/Prompt_v1_CQ_Ans_v2/Prompt_v1_CQ_Ans_v2_KGs_Eval_with_LLM.csv",index=False)
print(fidf["Judge_llm_Response"].value_counts())
