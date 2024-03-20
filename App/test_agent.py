from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
)
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
import openai,os
from llama_index.agent.openai import OpenAIAgent
from llama_index.core.tools import QueryEngineTool, ToolMetadata

openai.api_key = ""
os.environ['OPENAI_API_KEY'] = ""

def indexing_strategy():
    try:
        storage_context = StorageContext.from_defaults(
            persist_dir="./storage_test/carpark"
        )
        carpark_index = load_index_from_storage(storage_context)

        storage_context = StorageContext.from_defaults(
            persist_dir="./storage_test/route"
        )
        route_index = load_index_from_storage(storage_context)
        storage_context = StorageContext.from_defaults(
            persist_dir="./storage_test/current_location"
        )
        currloc_index = load_index_from_storage(storage_context)

        index_loaded = True
    except:
        index_loaded = False

    if not index_loaded:
        # load data
        carpark_docs = SimpleDirectoryReader(
            input_files=["./data/carParkLocation_withPrice.csv"]
        ).load_data()
        route_docs = SimpleDirectoryReader(
            input_files=["./data/nearest_routes.csv"]
        ).load_data()

        # currloc_docs = SimpleDirectoryReader(
        #     input_files=["./data/current_location.json"]
        # ).load_data()

        # build index
        carpark_index = VectorStoreIndex.from_documents(carpark_docs)
        route_index = VectorStoreIndex.from_documents(route_docs)
        #currloc_index = VectorStoreIndex.from_documents(currloc_docs)

        # persist index
        carpark_index.storage_context.persist(persist_dir="./storage_test/carpark")
        route_index.storage_context.persist(persist_dir="./storage_test/route")
        #currloc_index.storage_context.persist(persist_dir="./storage_test/current_location")
    return carpark_index, route_index #currloc_index

def query_engine_tools(carpark_index, route_index):
    carPark_engine = carpark_index.as_chat_engine(similarity_top_k=2)
    Route_engine = route_index.as_chat_engine(similarity_top_k=2)
    #currloc_engine = currloc_index.as_chat_engine(similarity_top_k=1)

    query_engine_tools = [
        QueryEngineTool(
            query_engine=carPark_engine,
            metadata=ToolMetadata(
                name="CarPark",
                description=(
                    "Provides information about CarParking availability/lots and the parking prices on different days across different developments and "
                    "areas/addressed across Singapore. Use this to answer questions related to number of parking lots, address of carparks, agency in different areas acorss Singapore."
                    "Use a detailed plain text question as input to the tool."
                ),
            ),
        ),
        QueryEngineTool(
            query_engine=Route_engine,
            metadata=ToolMetadata(
                name="Route",
                description=(
                    """Please provide detailed information about the routes and distances to the nearest available car parks. 
                    This information should only be used for questions related to finding the route, distance, and displaying the nearest car parks when the user asks for locations near them or 
                    when they mention from their current location.
                Use a detailed plain text question as input to the tool."""
                ),
            ),
        ),
    # QueryEngineTool(
    #         query_engine=currloc_engine,
    #         metadata=ToolMetadata(
    #             name="CurrentLocation",
    #             description=(
    #                 "Provides information about the current user location "
    #                 "Use this only for questions related to display current user location and n"
    #                 "Use a detailed plain text question as input to the tool."
    #             ),
    #         ),
    #     )
    ]
    #Settings.llm = OpenAI(model="gpt-3.5-turbo", temperature=0)
    agent = OpenAIAgent.from_tools(query_engine_tools,verbose=True)
    return agent

# c,r = indexing_strategy()
# agent = query_engine_tools(c,r)
#
# agent.chat_repl()


# def load_agent(query_engine_tools):
#     agent = OpenAIAgent.from_tools(query_engine_tools, verbose=True)
#     return agent


