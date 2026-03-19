from enum import Enum
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, JsonValue, model_validator

from chat import ChannelChatMessage
from cheer import ChannelCheer

NotificationEvent = ChannelChatMessage | ChannelCheer
    
class Session(BaseModel):
    id: str
    status: str
    connected_at: str
    keepalive_timeout_seconds: int
    reconnect_url: Optional[str] = None
    recovery_url: Optional[str] = None
    
class Transport(BaseModel):
    method: str
    session_id: str

class Subscription(BaseModel):
    id: str
    status: str
    type: str
    version: str
    cost: int
    condition: JsonValue
    transport: Transport
    created_at: datetime

class Metadata(BaseModel):
    message_id: str
    message_type: str
    message_timestamp: datetime
    
class Payload(BaseModel):
    session: Session

class SubPayload(BaseModel):
    subscription: Subscription
    
class Message(BaseModel):
    metadata: Metadata
    
class WelcomeMessage(Message):
    payload: Payload
    
class KeepaliveMessage(Message):
    payload: Optional[Payload] = None
    
class NotificationPayload(SubPayload):
    event: NotificationEvent
    
    @model_validator(mode='before')
    @classmethod
    def parse_event(cls, data: dict[str, Any]) -> dict[str, Any]:
        subscription = data.get('subscription', {})
        event_type = subscription.get('type')
        raw_event = data.get('event', {})
        
        match event_type:
            case "channel.chat.message":
                data['event'] = ChannelChatMessage(**raw_event)
            case "channel.cheer":
                data['event'] = ChannelCheer(**raw_event)
            case _:
                data['event'] = None
        
        return data
        
class NotificationMessage(Message):
    payload: NotificationPayload