import httpx

from enum import Enum
from logging import Logger
from shared import UserConfig

class SubEvent(Enum):
    CHAT_MESSAGE = "channel.chat.message"
    CHEER_BITS = "channel.cheer"

async def subscribe_to_event(
    url: str, config: UserConfig, session_id: str, 
    event_name: SubEvent, logger: Logger
) -> None:
    eventname: str = event_name.value
    async with httpx.AsyncClient() as client:
        response: httpx.Response = await client.post(
            url,
            headers={
                "Authorization": f"Bearer {config.twitch_token}",
                "Client-Id": config.client_id
            },
            json={
                "type": f"{eventname}",
                "version": "1",
                "condition": {
                    "broadcaster_user_id": config.broadcaster_id,
                    "user_id": config.user_id
                },
                "transport": {
                    "method": "websocket",
                    "session_id": session_id
                }
            }
        )
        
        status: int = response.status_code
        if status >= 200 and status <= 300:
            logger.info(f"Successfully subscribed to event {eventname}✅")
        else:
            logger.warning(f"Failed to subscribe to event {eventname}, status code: {status}")