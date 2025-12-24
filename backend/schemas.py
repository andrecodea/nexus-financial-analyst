# Creates data schemas validated by Pydantic

# Import pydantic for data validation
from pydantic import BaseModel

# Pydantic models used by the API for request/response payload validation.
class PromptObject(BaseModel):
    """Schema representing a prompt sent to the assistant.

    Attributes:
        content: The text content of the prompt.
        id: Identifier for the prompt message.
        role: Role of the message author (e.g., 'user', 'system').
    """
    content: str
    id: str
    role: str

# Wrapper model for API requests containing the prompt and metadata.
class RequestObject(BaseModel):
    """API request wrapper containing the prompt and metadata.

    Attributes:
        prompt: A `PromptObject` instance with the message content.
        threadId: Conversation/thread identifier used by the agent.
        responseId: Optional response identifier for deduplication/tracking.
    """
    prompt: PromptObject
    threadId: str
    responseId: str