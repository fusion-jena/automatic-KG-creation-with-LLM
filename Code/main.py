from configparser import ConfigParser
from Concepts_relations_generate import Concepts_relations_generate
from Ontology_creation import Ontology_creation
from RAG_CQ_answering_with_LLMs import RAG_CQ_answering
from Process_CQ_ans import process_cq_ans
from KG_creation_Mixtral import KG_creation
from Evaluate_RAG_with_LLM import Evaluate_RAG
from create_KG_evaluation_csv import KG_indvidual_csv_creation
from Evaluate_KG_with_LLM import Evaluate_KG_with_LLM

def main():
    config = ConfigParser()
    config.read('config.ini')

    Concepts_relations_generate(config)
    Ontology_creation(config)
    RAG_CQ_answering(config)
    process_cq_ans(config)
    KG_creation(config)
    Evaluate_RAG(config)
    KG_indvidual_csv_creation(config)
    Evaluate_KG_with_LLM(config)

if __name__ == "__main__":
    main()
