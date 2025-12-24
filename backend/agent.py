import os
import logging
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

# Configure logging
logger = logging.getLogger(__name__)


def get_agent():
    """
    Creates and returns a configured LangChain agent with financial analysis tools.
    Validates required environment variables before initialization.
    """
    
    # Validate required environment variables
    required_vars = ['OPENAI_API_KEY', 'LLM_NAME']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}. "
            f"Please check your .env file."
        )
    
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

    logger.info("Financial analysis agent initialized successfully")
    return create_agent(model=model, checkpointer=memory,tools=tools)