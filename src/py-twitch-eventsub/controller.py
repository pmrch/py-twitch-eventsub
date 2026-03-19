import dotenv
dotenv.load_dotenv()

import logging 
import websockets.exceptions as wsexc

from datetime import datetime
from typing import Optional
from websockets import Data
from websockets.asyncio.client import connect
from websockets.protocol import State

from models import Message, WelcomeMessage, NotificationMessage
from handlers import ExcAction, HandlerHub, CallbackType, NotificationEvent
from shared import UserConfig, read_config
from logger import setup_logging
from subscriber import subscribe_to_event, SubEvent

class TwitchController:
    def __init__(self) -> None:
        self.ws = None
        self.ws_endpoint: str = "wss://eventsub.wss.twitch.tv/ws"
        self.http_enpoint: str = "https://api.twitch.tv/helix/eventsub/subscriptions"
        self.session_id: str = ""
        
        self.config: UserConfig = read_config()
        self.logger: logging.Logger = setup_logging("EventSub")
        self.handlers: HandlerHub = HandlerHub()

    def register_callback(self, evt: NotificationEvent, callback: CallbackType) -> None:
        self.handlers.register_callback(type(evt), callback)
        
    def set_dev_mode(self, dev_ws: str, dev_http: str) -> None:
        self.ws_endpoint = dev_ws
        self.http_enpoint = dev_http
        
    async def handle_message(self, message: Optional[Message]) -> None:
        if message is None:
            self.logger.debug("Unhandled notification!")
            return
        
        if isinstance(message, WelcomeMessage):
            self.session_id = message.payload.session.id
            self.logger.info(f"Received Welcome message, saved Session ID: {self.session_id}")
            
            await subscribe_to_event(
                self.http_enpoint, self.config, self.session_id, 
                SubEvent.CHAT_MESSAGE, self.logger
            )
            
            return
            
        if isinstance(message, NotificationMessage):
            ts: datetime = message.metadata.message_timestamp
            await self.handlers.handle_notification(message.payload.event, ts)

    async def start(self) -> None:
        self.ws = await connect(self.ws_endpoint)
        
        while self.ws.state == State.OPEN:
            try:
                msg: Data = await self.ws.recv(decode=True)
                if isinstance(msg, bytes):
                    continue
                
                handled: Optional[Message] = self.handlers.handle_message(msg)
                if handled is not None:
                    await self.handle_message(handled)
                
            except wsexc.WebSocketException as e:
                exc: ExcAction = self.handlers.handle_ws_exception(e, self.logger)
                match exc:
                    case ExcAction.SKIP: continue
                    case ExcAction.RECONNECT: pass
                    case ExcAction.EXIT:
                        self.ws = None
                        self.logger.warning("Since Twitch shut our WebSocket down cleanly, we quit!")
                        return
                    case ExcAction.EXIT_FATAL:
                        self.ws = None
                        raise