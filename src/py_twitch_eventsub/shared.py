import os

from uuid import UUID
from typing import Union
from dataclasses import dataclass

@dataclass
class UserConfig:
    twitch_token: str
    client_id: str
    broadcaster_id: str
    user_id: str

@dataclass
class StringId:
    id: str

@dataclass
class UuidId:
    id: UUID
    
MessageId = Union[UUID, str]

def read_config() -> UserConfig:
    config = UserConfig("", "", "", "")
    
    mapping = {
        "TWITCH_TOKEN": "twitch_token",
        "CLIENT_ID": "client_id", 
        "BROADCASTER_ID": "broadcaster_id",
        "USER_ID": "user_id"
    }
    
    try:
        for env_key, attr in mapping.items():
            value = os.getenv(env_key)
            assert value is not None, f"Environment variable {env_key} failed to load"
            setattr(config, attr, value)
    except AssertionError as e:
        print(f"Error reading env: {e}")
        
    return config