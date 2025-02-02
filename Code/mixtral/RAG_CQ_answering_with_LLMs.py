from helper_functions import load_llm, load_cqs, read_txt, get_embeddings
from langchain.prompts import PromptTemplate
from langchain.document_loaders import UnstructuredFileLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
import textwrap
import numpy as np
from LLM_loader import llm

def RAG_CQ_answering(config):
    CQs = load_cqs(config.get('Paths', 'CQs_path'))
    embedding_model_id = config.get('Models', 'embedding_model_id')
    template = read_txt(config.get('Paths', 'RAG_question_answering_prompt'))
    prompt_template = PromptTemplate(input_variables=["query"], template=template)

    for d in [1,3,5,7,8,9,10,12,13,14,16,18,19,20,24,25,27,28,33,34,37,38,39,41,42,43,44,45,46,47]:
        loader = UnstructuredFileLoader(f"{config.get('Paths', 'pdfs_path')}{d}.pdf")
        documents = loader.load()
        text_splitter=RecursiveCharacterTextSplitter(chunk_size=2500, chunk_overlap=100)
        text_chunks=text_splitter.split_documents(documents)
        vectorstore=FAISS.from_documents(text_chunks, get_embeddings(embedding_model_id))
        chain = RetrievalQA.from_chain_type(llm=llm, chain_type = "stuff",return_source_documents=False, retriever=vectorstore.as_retriever())                                     
        for cq,p in zip(CQs,np.arange(1,len(CQs)+1)):
            prompt = prompt_template.format(query=cq)
            result = chain({"query": prompt}, return_only_outputs=True)
            wrapped_text = textwrap.fill(result['result'], width=100)
            with open(f"{config.get('Paths', 'Ans_to_cq_input_folder')}Publication{d}_CQ{p}.txt", 'w') as f:
                f.write(wrapped_text)
