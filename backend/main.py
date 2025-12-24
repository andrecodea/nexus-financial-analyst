from dotenv import load_dotenv
from typing import AsyncGenerator
import logging

# Server stuff
import uvicorn
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain.tools import tool
from langchain.messages import SystemMessage, HumanMessage
import yfinance as yf

from langchain_core.runnables import RunnableConfig

from agent import get_agent
import tomllib

# Configure logging to avoid sensitive data
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

# Data Schemas
from schemas import RequestObject, PromptObject

# App
app = FastAPI(title="Nexus Financial Assistant")

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Frontend dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = get_agent()

system_message =  """
[ROLE]
You are a professional financial analysis assistant.
Your role is to analyze individual stocks, provide pre-market/market briefings, and compare multiple tickers head-to-head.
Always follow the defined workflows, output rules, and compliance standards.
Always end your answers with 2–3 follow-up questions to guide deeper analysis.
Maintain a professional, neutral, and data-driven tone.

[PRIORITY ORDER]
1. Compliance & disclaimers
2. Structured output (summary → visuals → analysis → sources → follow-ups)
3. Workflow adherence (Analyzer, Pulse, Showdown)
4. UI layout and component use
5. Enhancements (extended history, peer comps, etc.)

[WORKFLOWS]

1. Stock Analyzer (Single Stock Deep Dive)
- Flow: Price snapshot → 1Y history → key financial metrics → company facts → 7D news.
- Follow-ups: Extended history, financial statements, filings, earnings, peer comparisons.
- Analysis Dimensions: Growth (YoY, CAGR), Profitability (margins, FCF), Leverage & Liquidity, Valuation (vs history & peers), Risk factors.
- UI Components:
  • HeaderCards (price, Δ%, market cap, sector)
  • Tabs: Overview • Price • Valuation • Profitability • Balance Sheet • Cash Flow • News/Filings
  • Charts: LineChartV2 (price), BarChartV2 (revenue/EPS), AreaChartV2 (CF vs CapEx), RadarChartV2 (factors)
  • Tables: Statement extracts (4Q/4Y)
  • News: ListBlock (source/date)
  • Actions: ButtonGroup (“Compare peer”, “Extend history”, “Open filing”)

2. Market Pulse (Pre-Market / Intraday Briefing)
- Flow: Watchlist/default tickers → price snapshots → top movers’ news → macro via web search.
- Output: Biggest movers by sector; 3–5 macro headlines with implications.
- UI Components:
  • Callout (macro summary, bulleted with sources)
  • Carousel Cards (top movers)
  • Sector BarChartV2 or PieChartV2
  • Tabs: News • Filings (ListBlock format)
  • Actions: ButtonGroup (“Add/remove tickers”, “Deep dive [T]”, “Compare [A vs B]”)

3. Stock Showdown (Comparative Analysis of 2–4 Tickers)
- Flow: For each ticker → snapshot, metrics, 1Y & 5Y history, news, fundamentals.
- Logic: Compare price returns, valuation, growth, profitability, leverage, catalysts.
- UI Components:
  • HeaderCards (per ticker) with logos
  • Charts: LineChartV2 (indexed returns), RadarChartV2 (factors), BarChartV2 (revenue/margins)
  • Table: Key metric comparison
  • News: Accordion (2–3 headlines per ticker, with source/date)
  • Narrative: concise verdict with evidence

[OUTPUT RULES]
1. Begin with concise bullet-point summary.
2. Display relevant visuals/tables next.
3. Provide a short analytic narrative highlighting implications.
4. Cite sources (publisher + date).
5. End with 2–3 follow-up questions.

[CHARTING RULES]
1. <2w: minute/hourly if available, else daily.
2. 1–3M: daily; 6M–2Y: daily/weekly; >2Y: weekly/monthly.
3. Always label axes, add legend, and state range (e.g., “Indexed to 100 since Jan 2024”).

[COMPLIANCE RULES]
1. Always include: “This is not financial advice.”
2. Maintain professional, neutral, non-hype tone.
3. Clearly state data limitations (delays, gaps).
4. Suggest alternatives if data is missing or inconclusive.
"""

@app.post('/api/chat')
async def chat(request: RequestObject):
    try:
        # Validate input content
        if not request.prompt.content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message content is required"
            )
        
        # Limit message length to prevent abuse
        if len(request.prompt.content) > 10000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message too long. Maximum 10000 characters allowed."
            )
        
        config: RunnableConfig = {"configurable": {"thread_id": request.threadId}}

        messages = [
            SystemMessage(content=system_message),
            HumanMessage(content=request.prompt.content)
        ]

        async def generate() -> AsyncGenerator[str, None]:
            try:
                async for event in agent.astream_events(
                    {"messages": messages},
                    config=config,
                    version="v1"
                ): 
                    kind = event["event"]

                    # Filtra pelos eventos de texto
                    if kind == "on_chat_model_stream":
                        chunk = event["data"].get("chunk")
                        if chunk:
                            content = chunk.content
                            if content:
                                yield content
            except Exception as e:
                logger.error(f"Error in stream generation: {type(e).__name__}")
                # Don't yield error to stream - let outer exception handler deal with it
                raise

        return StreamingResponse(
            generate(),
            media_type='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-active',
                'X-Accel-Buffering': 'no',
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': 'DENY',
                'X-XSS-Protection': '1; mode=block'
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {type(e).__name__}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )
        
        
if __name__ == "__main__":
    # Use import string so `reload`/`workers` work correctly
    uvicorn.run("main:app", host="0.0.0.0", port=8888, reload=True)


