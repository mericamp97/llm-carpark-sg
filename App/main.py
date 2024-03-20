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
import pandas as pd

from route import get_top_dataframe

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))


openai.api_key = ""
os.environ['OPENAI_API_KEY'] = ""


def get_loc():
    loc = get_current_location()
    print(loc)
    with open('./data/current_location.json', 'w') as file:
        json.dump(loc, file)


def route_loader(lat, long ,main_df):
    df = get_top_dataframe(lat,long,main_df)
    df.to_csv('./data/nearest_routes.csv')

# Setting up streamlit UI page
def streamlit_setup():
    try:
        st.set_page_config(page_title="Know more about carpark", page_icon="🙂", layout="centered",
                           initial_sidebar_state="auto", menu_items=None)

        st.title("Chat with the ParkLah, your smart parking assistant")
        st.info("Smart Assistant to all your parking enquiries in Singapore ")
    except Exception as e:
        logging.error(f"Error setting up streamlit application : {e}")

# Initializing streamlit chat for users to ask questions
def initialize_chat():
    try:
        if "messages" not in st.session_state.keys():  # Initialize the chat messages history
            st.session_state.messages = [
                {"role": "assistant", "content": "Ask me a question to know more about carparks"}
            ]
    except Exception as e:
        logging.error(f"Error initializing chat : {e}")

# Ingesting and indexing documents relevent to Srivas
# This function uses disc storage for storing the indices created after reading the data
def store_and_index():
    try:
        PERSIST_DIR = "./storage"
        Settings.embed_model = OpenAIEmbedding(model="text-embedding-ada-002")

        if not os.path.exists(PERSIST_DIR):
            # load the documents and create the index
            with st.spinner(text="Loading and indexing – hang tight! This should take 1-2 minutes."):
                documents = SimpleDirectoryReader("./data").load_data()
                index = VectorStoreIndex.from_documents(documents)

                # store it for later
                index.storage_context.persist(persist_dir=PERSIST_DIR)
                return index
        else:
            # load the existing index
            storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
            index = load_index_from_storage(storage_context)
            return index
    except Exception as e:
        logging.error(f"Error loading, storing and indexing data: {e}")

# Initialize chat engine via streamlit and using open ai's llm
def initialize_chat_engine(index):
    try:
        # Call the function to get the current location
        if "chat_engine" not in st.session_state.keys():
            system_prompt = f"""IImagine you're an AI system with access to Singapore's parking datasets. 
            Task 1: Provide detailed car park availability, locations, agencies using CarParkLocation.csv.
             Task 2: Answer route and distance queries using nearest_routes.csv, focusing on the closest car park from the user location. 
             Incorporate the user's current location from current_location.json. Maintain accuracy without mixing datasets.
             For uncertainty, respond with "I am not sure about that." Follow these guidelines to offer precise information on car park availability, locations, agencies, routes, and distances, ensuring each use case is handled from the appropriate dataset for clarity and accuracy.
             Do not hallucinate any fetures."""""

            Settings.llm = OpenAI(model="gpt-3.5-turbo", temperature=0, system_prompt= system_prompt)

            st.session_state.chat_engine = index.as_chat_engine(llm=Settings.llm, chat_mode="openai", verbose=True)
    except Exception as e:
        logging.error(f"Error initializing the chat engine : {e}")

def update_user_prompt():
    try:
        if prompt := st.chat_input("Ask a question"):  # Prompt for user input and save to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
        return prompt
    except Exception as e:
        logging.error(f"Error updating user prompt messages : {e} ")

def display_prior_msgs():
    try:
        for message in st.session_state.messages:  # Display the prior chat messages
            with st.chat_message(message["role"]):
                st.write(message["content"])
    except Exception as e:
        logging.error(f"Error displaying history of messages : {e} ")

# If last message is not from assistant, generate a new response
def chat_bot(prompt):
    try:
        if st.session_state.messages[-1]["role"] != "assistant":
            with st.chat_message("assistant"):
                with st.spinner("Almost there..."):
                    response = st.session_state.chat_engine.chat(prompt)
                    st.write(response.response)
                    message = {"role": "assistant", "content": response.response}
                    st.session_state.messages.append(message)
    except Exception as e:
        logging.error(f"Error in generating response by the assistant : {e} ")

if __name__ == "__main__":

    try:
        main_df = pd.read_csv("./data/carParkLocation_withPrice.csv")

        g = get_current_location()
        lat = g['current_location'][0]
        long = g['current_location'][1]
        route_loader(lat,long,main_df)
        streamlit_setup()
        initialize_chat()
        idx = store_and_index()
        initialize_chat_engine(idx)
        prompt = update_user_prompt()
        display_prior_msgs()
        chat_bot(prompt)
    except Exception as e:
        logging.error(f" Error in main function : {e}")
        traceback.print_exc()

