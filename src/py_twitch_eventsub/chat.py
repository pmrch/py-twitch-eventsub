from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel

from .shared import MessageId

class MessageType(Enum):
    TEXT = "text"
    CHANNEL_POINTS_HIGHLIGHTED = "channel_points_highlighted"
    CHANNEL_POINTS_SUB_ONLY = "channel_points_sub_only"
    USER_INTRO = "user_intro"
    POWER_UPS_MESSAGE_EFFECT = "power_ups_message_effect"
    POWER_UPS_GIGANTIFIED_EMOTE = "power_ups_gigantified_emote"

class Badge(BaseModel):
    set_id: str
    id: str
    info: str
    
class Cheermote(BaseModel):
    prefix: str
    bits: int
    tier: int
    
class Emote(BaseModel):
    id: str
    emote_set_id: str
    owner_id: str
    format: list[str]
    
class Mention(BaseModel):
    user_id: str
    user_name: str
    user_login: str
    
class Fragment(BaseModel):
    type: str
    text: str
    cheermote: Optional[Cheermote] = None
    emote: Optional[Emote] = None
    mention: Optional[Mention] = None
    
class ChatMessage(BaseModel):
    text: str
    fragments: list[Fragment]
    
class Reply(BaseModel):
    parent_message_id: str
    parent_message_body: str
    parent_user_id: str
    parent_user_name: str
    parent_user_login: str
    thread_message_id: str
    thread_user_id: str
    thread_user_name: str
    thread_user_login: str
    
class ChannelChatMessage(BaseModel):
    broadcaster_user_id: str
    broadcaster_user_name: str
    broadcaster_user_login: str
    chatter_user_id: str
    chatter_user_name: str
    chatter_user_login: str
    message_id: MessageId
    message: ChatMessage
    message_type: MessageType
    badges: list[Badge]
    reply: Optional[Reply] = None
    channel_points_custom_reward_id: Optional[str] = None
    source_broadcaster_user_id: Optional[str] = None
    source_broadcaster_user_name: Optional[str] = None
    source_broadcaster_user_login: Optional[str] = None
    source_message_id: Optional[str] = None
    source_badges: Optional[list[Badge]] = None
    is_source_only: Optional[bool] = None