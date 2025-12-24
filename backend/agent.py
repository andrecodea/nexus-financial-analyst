# Imports OS, logging and environment variables importing components
import os
import logging
from dotenv import load_dotenv

# Imports the AI components for agent creation
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver

# Imports agent tools
from tools import (
    get_stock_price, 
    get_historical_stock_price,
    get_balance_sheet,
    get_stock_news,
    web_search
)

# Loads environment variables and configures the logger
load_dotenv()
logger = logging.getLogger(__name__)

# === AGENT ===

# Creates agent via LangChain
def get_agent():
    """
    Creates and returns a configured LangChain agent with financial analysis tools.
    Validates required environment variables before initialization.
    """
    
    # Validates required environment variables
    required_vars = ['OPENAI_API_KEY', 'LLM_NAME']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}. "
            f"Please check your .env file."
        )
    
    # Configures AI model
    model = ChatOpenAI(
            model = os.getenv('LLM_NAME', ""),
            base_url = os.getenv('LLM_BASE_URL',"")
        )
    
    # Initialize an in-memory saver to persist lightweight agent state/checkpoints
    memory = InMemorySaver()

    # Register the tool functions that the agent can call for financial data
    # and web searches. These are passed to the LangChain agent on creation.
    tools = [
        get_stock_price, 
        get_historical_stock_price, 
        get_balance_sheet, 
        get_stock_news,
        web_search
        ]

    # Logs the execution and returns agent
    logger.info("Financial analysis agent initialized successfully")
    return create_agent(model=model, checkpointer=memory,tools=tools)