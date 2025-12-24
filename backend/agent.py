import os
from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver

from tools import (
    get_stock_price, 
    get_historical_stock_price,
    get_balance_sheet,
    get_stock_news,
    web_search
)

# load environment variables from a .env file
load_dotenv()


def get_agent():

    """
    Docstring for get_agent
    """

    model = ChatOpenAI(
            model = os.getenv('LLM_NAME', ""),
            base_url = os.getenv('LLM_BASE_URL',"")
        )
    
    memory = InMemorySaver()

    tools = [
        get_stock_price, 
        get_historical_stock_price, 
        get_balance_sheet, 
        get_stock_news,
        web_search
        ]

    return create_agent(model=model, checkpointer=memory,tools=tools)