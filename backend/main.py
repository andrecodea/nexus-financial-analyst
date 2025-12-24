# Imports environment variable loading, type casting and logging components
from dotenv import load_dotenv
from typing import AsyncGenerator
import logging

# Imports API and serving components
import uvicorn
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

# Imports AI components
from langchain.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from agent import get_agent

# Imports data schemas
from schemas import RequestObject, PromptObject

# Imports prompt loading components
import tomllib
from pathlib import Path

# Configure logging to avoid sensitive data
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Configures logging and loads environment variables
logger = logging.getLogger(__name__)
load_dotenv()

# Initializes app and configures CORS middleware
app = FastAPI(title="Nexus Financial Assistant")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Frontend dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initializes AI agent
agent = get_agent()

# Load system prompt from prompt.toml (open in binary as required by tomllib)
prompt_path = Path(__file__).resolve().parent / "prompt.toml"
system_message = ""
try:
    with prompt_path.open("rb") as f:
        prompt_file = tomllib.load(f)
    system_message = prompt_file.get("prompt", "")
    if not system_message:
        logger.warning("`prompt.toml` loaded but contains no 'prompt' key or it is empty")
except FileNotFoundError:
    logger.error(f"prompt.toml not found at {prompt_path}")
except tomllib.TOMLDecodeError as e:
    logger.error(f"Error parsing prompt.toml: {e}")
except Exception as e:
    logger.error(f"Unexpected error loading prompt.toml: {type(e).__name__}: {e}")

# Sets API endpoint as a POST request via async chat function
@app.post('/api/chat')
async def chat(request: RequestObject):
    """Handle chat POST requests.

    Validates incoming `RequestObject`, enforces length limits and
    streams AI responses as server-sent events.
    """
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
        
        # Configures the tread ID as a LangChain runnable
        config: RunnableConfig = {"configurable": {"thread_id": request.threadId}}

        # Sets message history order
        messages = [
            SystemMessage(content=system_message),
            HumanMessage(content=request.prompt.content)
        ]

        # Asyncronous stream generator
        async def generate() -> AsyncGenerator[str, None]:
            """Async generator yielding streamed chunks from the AI agent.

            Yields string chunks to be forwarded in the StreamingResponse.
            Exceptions are logged and re-raised to be handled by the caller.
            """
            try:
                async for event in agent.astream_events(
                    {"messages": messages},
                    config=config,
                    version="v1"
                ): 
                    kind = event["event"]

                    # Filters through text events
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
        
        # Return a streaming response: the generator yields AI model text
        # chunks which are forwarded as server-sent events (SSE).
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
    uvicorn.run("main:app", host="0.0.0.0", port=8888, reload=True)


