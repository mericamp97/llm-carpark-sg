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

from main import route_loader, get_loc
from route import get_top_dataframe
from test_agent import indexing_strategy, query_engine_tools


def streamlit_setup():
    try:
        st.set_page_config(page_title="Know more about carpark", page_icon="🙂", layout="centered",
                           initial_sidebar_state="auto", menu_items=None)

        st.title("Chat with the ParkLah, your smart parking assistant")
        st.info("Smart Assistant to all your parking enquiries in Singapore ")
    except Exception as e:
        logging.error(f"Error setting up streamlit application : {e}")

def initialize_chat():
    try:
        if "messages" not in st.session_state.keys():  # Initialize the chat messages history
            st.session_state.messages = [
                {"role": "assistant", "content": "Ask me a question to know more about carparks"}
            ]
    except Exception as e:
        logging.error(f"Error initializing chat : {e}")
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

        # Get the users current location and add to data folder
        get_loc()

        # This is for route data based on OpenMap API based on fetched location
        main_df = pd.read_csv("./data/carParkLocation_withPrice.csv")
        g = get_current_location()
        lat = g['current_location'][0]
        long = g['current_location'][1]
        route_loader(lat, long, main_df)

        # set up streamlit home page
        streamlit_setup()

        #initialize chat history
        initialize_chat()

        # Get seperate indices
        car,route,loc = indexing_strategy()

        #query tool
        agent = query_engine_tools(car,route,loc)

        # initilize session state with the agent
        st.session_state.chat_engine = agent

        # user prompt update and display
        prompt = update_user_prompt()
        display_prior_msgs()
        chat_bot(prompt)

    except Exception as e:
        print(f"Error in main function :{e}")
