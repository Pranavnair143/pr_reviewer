from typing import Optional
from pydantic import BaseModel, Field



class CodeSuggestion(BaseModel):
    """Suggestion"""
    line_number: str = Field(description="Line number at which code suggestion is given. It can be a range as well.")
    description: str = Field(description="Suggestion for that specific lines od code")
    example_snippet: Optional[str] = Field(description="Sample/reformed code snippet if required")

class CodeSuggestionListSchema(BaseModel):
    """List of suggestions"""
    suggestions: list[CodeSuggestion] = Field(description="List of suggestions for that file")