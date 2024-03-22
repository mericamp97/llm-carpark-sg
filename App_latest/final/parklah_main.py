from location import get_current_location, get_loc
from agent import indexing_strategy, query_engine_tools
from route import route_loader
import pandas as pd
import logging, sys

#logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

def get_location_and_route_data():
    try:
        # Get the users current location and add to data folder
        get_loc()

        # This is for route data based on OpenMap API based on fetched location
        main_df = pd.read_csv("../data/carParkLocation_withPrice.csv")
        gct = get_current_location()
        lat = gct['current_location'][0]
        long = gct['current_location'][1]
        route_loader(lat, long, main_df)

    except Exception as e:
        logging.error(f"Error in fetching user's current location and route data : {e}")


def chat_with_agent():
    try:
        car,route = indexing_strategy()
        agent = query_engine_tools(car,route)

        print(agent.chat_history)
        return agent.chat_repl()
    except Exception as e:
        logging.error(f"Error in chat agent function : {e}")

if __name__ == "__main__":
    try:
        get_location_and_route_data()

        chat_with_agent()
    except Exception as e:
        logging.error(f"Error in main function : {e}")
