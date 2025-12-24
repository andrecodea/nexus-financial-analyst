import yfinance as yf
import logging
from langchain.tools import tool
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Real time stock prices
@tool (
        "get_stock_price", 
        description="Gets real time stock price based on ticker symbol. e.g. NVDA"
        )
def get_stock_price(ticker: str):
    logger.info(f"Fetching stock price for ticker: {ticker}")
    stock = yf.Ticker(ticker)
    return stock.history()['Close'].iloc[-1]

# Historical stock prices
@tool (
        "get_historical_stock_price", 
        description="Gets historical stock price data based on a ticker symbol e.g. NVDA, and a time range e.g. '5d'."
        )
def get_historical_stock_price(ticker:str, start_date: str, end_date:str):
        logger.info(f"Fetching historical stock price for ticker: {ticker}")
        stock = yf.Ticker(ticker)
        return stock.history(start=start_date, end=end_date).to_dict()

# Ticker balance sheet
@tool (
        "get_balance_sheet", 
        description="Gets the balance sheet of a ticker symbol e.g. NVDA"
        )
def get_balance_sheet(ticker: str):
     logger.info(f"Fetching balance sheet for ticker: {ticker}")
     stock = yf.Ticker(ticker)
     return stock.balance_sheet

    

# Stock news
@tool (
        "get_stock_news", 
        description="Gets the top K latest ticker symbol related news e.g. NVDA"
        )
def get_stock_news(ticker: str):
    logger.info(f"Fetching news for ticker: {ticker}")
    stock = yf.Ticker(ticker)
    return stock.news


# Web search
@tool (
     "web_search",
     description="Uses Tavily API to search the web."
)
def web_search(query: str):
     logger.info(f"Executing web search for query: {query[:50]}...")  # Log only first 50 chars
     tavily_client = TavilyClient()
     return tavily_client.search(query)