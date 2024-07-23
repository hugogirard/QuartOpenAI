from dataclasses import dataclass
from datetime import datetime,timezone

@dataclass
class Message:
    id: str
    role: str
    content: str
    date: datetime
    citation: list[object]

@dataclass
class Citation:
    url: str
    title: str

@dataclass
class Usage:
    completion_tokens: int
    prompt_tokens: int
    total_tokens: int
    
    def to_json(self):
        return {
            "completion_tokens": self.completion_tokens,
            "prompt_tokens": self.prompt_tokens,
            "total_tokens": self.total_tokens
        }

@dataclass
class ChatHistory:
    conversation_id: str
    messages: list[Message]
    usage: Usage

    def to_json(self):
        return {
            "conversation_id": self.conversation_id,
            "messages": [message.__dict__ for message in self.messages],
            "usage": self.usage.to_json()     
        }



