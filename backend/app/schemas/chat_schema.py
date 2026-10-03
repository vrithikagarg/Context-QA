from pydantic import BaseModel, Field


class ChatBody(BaseModel):
    # Bounded: every character is sent to the LLM and billed.
    message: str = Field(min_length=1, max_length=2000)
