from helper_functions import load_llm, load_cqs, read_txt, get_embeddings
from langchain.prompts import PromptTemplate
from langchain.document_loaders import UnstructuredFileLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
import textwrap
import numpy as np

model_id = 'mistralai/Mixtral-8x7B-Instruct-v0.1'
embedding_model_id = "sentence-transformers/all-MiniLM-L12-v2"
llm = load_llm(model_id, embedding_model_id)

CQs = load_cqs("../CQs/CQs.txt")

template = read_txt("../Prompts/RAG_question_answering.txt")
prompt_template = PromptTemplate(input_variables=["query"], template=template)

for d in [1,3,5,7,8]:
    loader = UnstructuredFileLoader(f"../Data/Pdfs/{d}.pdf")
    documents = loader.load()
    text_splitter=RecursiveCharacterTextSplitter(chunk_size=2500, chunk_overlap=100)
    text_chunks=text_splitter.split_documents(documents)
    vectorstore=FAISS.from_documents(text_chunks, get_embeddings(embedding_model_id))
    chain = RetrievalQA.from_chain_type(llm=llm, chain_type = "stuff",return_source_documents=False, retriever=vectorstore.as_retriever())                                     
    for cq,p in zip(CQs,np.arange(1,len(CQs)+1)):
        prompt = prompt_template.format(query=cq)
        result = chain({"query": prompt}, return_only_outputs=True)
        wrapped_text = textwrap.fill(result['result'], width=100)
        with open(f'../Data/Ans_to_cqs/Original_not_processed/Publication{d}_CQ{p}.txt', 'w') as f:
            f.write(wrapped_text)