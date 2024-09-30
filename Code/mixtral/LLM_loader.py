from helper_functions import load_llm
from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')
model_id = config.get('Models', 'model_id')
embedding_model_id = config.get('Models', 'embedding_model_id')
llm = load_llm(model_id, embedding_model_id)
