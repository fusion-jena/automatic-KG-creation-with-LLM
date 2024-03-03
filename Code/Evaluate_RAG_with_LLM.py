from helper_functions import load_llm, load_cqs, read_txt, get_embeddings
from langchain.prompts import PromptTemplate
import pandas as pd

df = pd.read_csv("../Evaluation/CQ_answers/Publication_1_CQ_Evaluation.csv")
df1 = pd.read_csv("../Evaluation/CQ_answers/Publication_3_CQ_Evaluation.csv")
df2 = pd.read_csv("../Evaluation/CQ_answers/Publication_5_CQ_Evaluation.csv")
df3 = pd.read_csv("../Evaluation/CQ_answers/Publication_7_CQ_Evaluation.csv")
df4 = pd.read_csv("../Evaluation/CQ_answers/Publication_8_CQ_Evaluation.csv")

frames = [df, df1, df2, df3, df4]
fidf = pd.concat(frames)
fidf.reset_index(inplace=True, drop=True)

RAG_LLM_Judge_template = = read_txt("../Prompts/Judge_LLM_CQ_answers.txt")

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
    
    
def conv_int_he(value):
    if value >= 6:
        return "Right"
    elif value < 3:
        return "Wrong"
    else:
        return "Partial"
fidf['Judge_llm_score_str'] = fidf['Judge_llm_score'].apply(conv_int_he)
fidf.to_csv("../Evaluation/CQ_answers/Pub_1_3_5_7_8_RAG_Eval_with_LLM.csv",index=False)

non_matching_rows = fidf[fidf['Evaluation'] != fidf['Judge_llm_score_str']]

print(non_matching_rows.shape)
