import asyncio 

from datetime import datetime
from py_twitch_eventsub import *

async def chat_handler(evt: NotificationEvent, ts: datetime) -> None:
    assert isinstance(evt, ChannelChatMessage)
    print(f"{evt.chatter_user_name}[{ts}]: {evt.message.text}")

async def cheer_handler(evt: NotificationEvent, ts: datetime) -> None:
    assert isinstance(evt, ChannelCheer)

async def main() -> None:    
    controller = TwitchController()
    controller.register_callback(ChannelChatMessage, chat_handler)
    controller.register_callback(ChannelCheer, cheer_handler)
    
    await controller.start()
    
if __name__ == "__main__":
    asyncio.run(main())