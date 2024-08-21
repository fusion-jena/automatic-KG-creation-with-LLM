from configparser import ConfigParser
from Concepts_relations_generate import Concepts_relations_generate
from Ontology_creation import Ontology_creation
from RAG_CQ_answering_with_LLMs import RAG_CQ_answering
from Process_CQ_ans import process_cq_ans
from NER import NER_mixtral

def main():
    config = ConfigParser()
    config.read('config.ini')

    Concepts_relations_generate(config)
    Ontology_creation(config)
    RAG_CQ_answering(config)
    process_cq_ans(config)
    NER__mixtral(config)

if __name__ == "__main__":
    main()
