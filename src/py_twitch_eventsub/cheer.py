from typing import Optional
from pydantic import BaseModel

class ChannelCheer(BaseModel):
    is_anonymous: bool
    user_id: Optional[str] = None
    user_login: Optional[str] = None
    user_name: Optional[str] = None
    broadcaster_user_id: str
    broadcaster_user_name: str
    broadcaster_user_login: str
    message: str
    bits: int