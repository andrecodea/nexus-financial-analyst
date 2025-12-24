# Creates the tools that the agent will use during execution.

# Imports logging and environment variable importing components
from dotenv import load_dotenv
import logging

# Imports the tool components 
import yfinance as yf
from langchain.tools import tool
from tavily import TavilyClient

# Environment variable loading and logger config
load_dotenv()
logger = logging.getLogger(__name__)

# === TOOLS ===

# Tool: Real-time stock price retrieval
@tool (
        "get_stock_price", 
        description="Returns real-time stock price based on ticker symbol. e.g. NVDA"
        )
def get_stock_price(ticker: str):
    """
    Returns the real-time ticker value.
    
    :param ticker: ticker symbol, e.g. NVDA.
    :type ticker: str
    """
    logger.info(f"Fetching stock price for ticker: {ticker}")
    stock = yf.Ticker(ticker)
    return stock.history()['Close'].iloc[-1]

# Tool: Historical stock price retrieval for a given date range
@tool (
        "get_historical_stock_price", 
        description="Returns historical stock price data based on a ticker symbol e.g. NVDA, and a time range e.g. '5d'."
        )
def get_historical_stock_price(ticker:str, start_date: str, end_date:str):
        """
        Retursn historical ticker price based on a time range. 

        :param ticker: Ticker symbol, e.g. NVDA
        :type ticker: str
        :param start_date: Time range start date
        :type start_date: str
        :param end_date: Time range end date.
        :type end_date: str
        """
        logger.info(f"Fetching historical stock price for ticker: {ticker}")
        stock = yf.Ticker(ticker)
        return stock.history(start=start_date, end=end_date).to_dict() # Estrutura a resposta como dicionário

# Tool: Retrieve a company's balance sheet data
@tool (
        "get_balance_sheet", 
        description="Returns the balance sheet of a ticker symbol, e.g. NVDA"
        )
def get_balance_sheet(ticker: str):
     
     """
     Returns the balance sheet of a ticker symbol, e.g. NVDA.
     
     :param ticker: Ticker symbol e.g. NVDA
     :type ticker: str
     """
     logger.info(f"Fetching balance sheet for ticker: {ticker}")
     stock = yf.Ticker(ticker)
     return stock.balance_sheet

    

# Tool: Retrieve recent news items related to a ticker symbol
@tool (
        "get_stock_news", 
        description="Returns the latest ticker symbol related news e.g. NVDA"
        )
def get_stock_news(ticker: str):
    """
    Returns recent recent news related to the ticker.
    
    :param ticker: Ticker symbol (e.g. NVDA)
    :type ticker: str
    """
    logger.info(f"Fetching news for ticker: {ticker}")
    stock = yf.Ticker(ticker)
    return stock.news


# Tool: Perform web search requests via the Tavily API
@tool (
     "web_search",
     description="Uses Tavily API to search the web."
)
def web_search(query: str):
     """
     Return a web search result through the Tavily API based on a query determined by the agent.
     
     :param query: Web search query
     :type query: str
     """
     logger.info(f"Executing web search for query: {query[:50]}...")  # Logs the first 50 chars 
     tavily_client = TavilyClient()
     return tavily_client.search(query)