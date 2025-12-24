import yfinance as yf
from langchain.tools import tool
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

# Real time stock prices
@tool (
        "get_stock_price", 
        description="Gets real time stock price based on ticker symbol. e.g. NVDA"
        )
def get_stock_price(ticker: str):
    print("get_stock_price tool is being executed...")
    stock = yf.Ticker(ticker)
    return stock.history()['Close'].iloc[-1]

# Historical stock prices
@tool (
        "get_historical_stock_price", 
        description="Gets historical stock price data based on a ticker symbol e.g. NVDA, and a time range e.g. '5d'."
        )
def get_historical_stock_price(ticker:str, start_date: str, end_date:str):
        print("get_historical_stock_price tool is being used...")
        stock = yf.Ticker(ticker)
        return stock.history(start=start_date, end=end_date).to_dict()

# Ticker balance sheet
@tool (
        "get_balance_sheet", 
        description="Gets the balance sheet of a ticker symbol e.g. NVDA"
        )
def get_balance_sheet(ticker: str):
     print("get_balance_sheet tool is being used...")
     stock = yf.Ticker(ticker)
     return stock.balance_sheet

    

# Stock news
@tool (
        "get_stock_news", 
        description="Gets the top K latest ticker symbol related news e.g. NVDA"
        )
def get_stock_news(ticker: str):
    print("get_stock_news tool is being used...")
    stock = yf.Ticker(ticker)
    return stock.news


# Web search
@tool (
     "web_search",
     description="Uses Tavily API to search the web."
)
def web_search(query: str):
     print("web_search tool is being executed...")
     tavily_client = TavilyClient()
     return tavily_client.search(query)