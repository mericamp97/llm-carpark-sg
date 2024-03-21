import openai
import os
import openai
from llama_index.llms.openai import OpenAI
from llama_index.core.evaluation import FaithfulnessEvaluator
from final.agent import query_engine_tools, indexing_strategy

openai.api_key = ""
os.environ['OPENAI_API_KEY'] = ""

# create llm
llm = OpenAI(model="gpt-3.5-turbo", temperature=0.3)


# define evaluator
evaluator = FaithfulnessEvaluator(llm=llm)

# Get our agend loaded
car, route = indexing_strategy()
agent = query_engine_tools(car, route)

# query our agent
query_engine = agent
response = query_engine.query(
    "Can you show me carparks in Bishan?"
)

# check faithful evaluator
eval_result = evaluator.evaluate_response(response=response)
print(f"Faithful Evaluator response : {str(eval_result.passing)}") # true should be a good response and false would mean an innucarate one


