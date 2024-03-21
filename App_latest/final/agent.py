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
            persist_dir="../storage_test/carpark"
        )
        carpark_index = load_index_from_storage(storage_context)

        storage_context = StorageContext.from_defaults(
            persist_dir="../storage_test/route"
        )
        route_index = load_index_from_storage(storage_context)
        storage_context = StorageContext.from_defaults(
            persist_dir="../storage_test/current_location"
        )
        currloc_index = load_index_from_storage(storage_context)

        index_loaded = True
    except:
        index_loaded = False

    if not index_loaded:
        # load data
        carpark_docs = SimpleDirectoryReader(
            input_files=["../data/carParkLocation_withPrice.csv"]
        ).load_data()
        route_docs = SimpleDirectoryReader(
            input_files=["../data/nearest_routes.csv"]
        ).load_data()

        # build index
        carpark_index = VectorStoreIndex.from_documents(carpark_docs)
        route_index = VectorStoreIndex.from_documents(route_docs)

        # persist index
        carpark_index.storage_context.persist(persist_dir="./storage_test/carpark")
        route_index.storage_context.persist(persist_dir="./storage_test/route")
    return carpark_index, route_index

def query_engine_tools(carpark_index, route_index):
    carPark_engine = carpark_index.as_chat_engine(similarity_top_k=2)
    Route_engine = route_index.as_chat_engine(similarity_top_k=2)

    query_engine_tools = [
        QueryEngineTool(
            query_engine=carPark_engine,
            metadata=ToolMetadata(
                name="CarPark",
                description=(
                    "Provides information about CarParking availability/lots and the parking prices on different days across different developments and "
                    "areas/addresses across Singapore. Use this to answer questions related to number of parking lots available, address of carparks, agency ,carpark prices in different areas acorss Singapore."
                    "Do not use this to show carparks when the user asks them to show carparks near them, but can be used to show for carparks near a given location"
                    "Use a detailed plain text question as input to the tool. Do not hallucinate any features."
                ),
            ),
        ),
        QueryEngineTool(
            query_engine=Route_engine,
            metadata=ToolMetadata(
                name="Route",
                description=(
                    """This dataset contains the same columns as the carPark_engine above, but with 2 extra columns : distance to carpark and the routes/directions to them.
                    Please use this when the user asks for carparks near them or when they mention show me the closest carparks from their current location and not from any other location.
                    Also use this when the user asks information on the "distance" and "routes" to nearest carparks. 
                    Use a detailed plain text question as input to the tool. Do not hallucinate any features."""
                )
            ),
        ),

    ]
    llm = OpenAI(model="gpt-3.5-turbo", temperature=0.1)
    agent = OpenAIAgent.from_tools( query_engine_tools,llm = llm,verbose=True)
    return agent




