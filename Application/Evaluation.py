import streamlit as st
from llama_index.core import (VectorStoreIndex, Document, ServiceContext, StorageContext,
    load_index_from_storage)
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
import openai
from llama_index.core import SimpleDirectoryReader
import logging
import sys, os,json
import traceback
from location import get_current_location
from llama_index.core.evaluation import FaithfulnessEvaluator

from main import get_loc

openai.api_key = "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"
os.environ['OPENAI_API_KEY'] = "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"

# Load documents and build index
documents = SimpleDirectoryReader("./data").load_data()
index = VectorStoreIndex.from_documents(documents)

# create llm
llm = OpenAI(model="gpt-3.5-turbo", temperature=0.3)


# define evaluator
evaluator = FaithfulnessEvaluator(llm=llm)

# query index
query_engine = index.as_query_engine()
response = query_engine.query(
    "How many lots are available in harbfront?"
)
# eval_result = evaluator.evaluate_response(response=response)
# print(str(eval_result.passing))

get_loc()
