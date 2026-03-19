import json 
import logging
import websockets.exceptions as wsexc

from datetime import datetime
from typing import Optional, Union, Callable, Any, Awaitable
from enum import Enum

from websockets import Data
from websockets.exceptions import WebSocketException

from .models import Message, WelcomeMessage, NotificationMessage
from .chat import ChannelChatMessage
from .cheer import ChannelCheer

NotificationEvent = Union[ChannelChatMessage | ChannelCheer]
CallbackType = Callable[[NotificationEvent, datetime], Awaitable[None]]

class ExcAction(Enum):
    SKIP = 0
    RECONNECT = 1
    EXIT = 2
    EXIT_FATAL = 3

class HandlerHub:
    def __init__(self) -> None:
        self.callbacks: dict[type[NotificationEvent], CallbackType] = dict()
    
    @staticmethod
    def handle_message(msg: Data) -> Optional[Message]:
        json_msg: dict = json.loads(msg)
        message_type: str = json_msg["metadata"]["message_type"]
        
        match message_type.strip():
            case "session_welcome":
                model = WelcomeMessage.model_validate(json_msg)
                return model
            case "session_keepalive":
                model = Message.model_validate(json_msg)
                return model
            case "notification":
                model = NotificationMessage.model_validate(json_msg)
                return model
        
        return None

    @staticmethod
    def handle_ws_exception(exc: WebSocketException, logger: logging.Logger) -> ExcAction:
        match exc:
            case wsexc.PayloadTooBig(size=size, max_size=max_size) if size:
                logger.info(f"Too large of a message was received, max size was {max_size}, got {size}")
                return ExcAction.SKIP
            case wsexc.ConnectionClosedOK:
                logger.info(f"WebSocket disconnected cleanly with code 1001 or 1000.")
                return ExcAction.EXIT
            case wsexc.ConnectionClosedError(rcvd=rcvd) if rcvd:
                match rcvd.code:
                    case 1006:  # truly abnormal, no close frame received
                        logger.warning(f"WebSocket closed abnormally: {rcvd.reason}")
                        return ExcAction.RECONNECT
                    case 4000 | 4001 | 4002 | 4003 | 4004 | 4007:  # Twitch specific
                        logger.info(f"Twitch closed connection with code {rcvd.code}: {rcvd.reason}")
                        return ExcAction.EXIT
                    case _:
                        logger.warning(f"WebSocket closed with error code {rcvd.code}: {rcvd.reason}")
                        return ExcAction.RECONNECT
            case wsexc.ConnectionClosed(rcvd=rcvd) if rcvd:
                logger.warning(f"Connection closed with code {rcvd.code}, {rcvd.reason}")
                return ExcAction.RECONNECT
            case wsexc.ProtocolError: 
                logger.warning("WebSocket connection encountered a protocol error!")
                return ExcAction.RECONNECT
            case wsexc.NegotiationError:
                logger.warning("WebSocket negotiation error occured")
                return ExcAction.RECONNECT
            case wsexc.ConcurrencyError:
                logger.warning("Concurrecny error occured for WebSocket")
                return ExcAction.RECONNECT
        
        logger.fatal(f"Something went fundamentally wrong with WebSocket")
        return ExcAction.EXIT_FATAL

    def register_callback(self, evt: type[NotificationEvent], callback: CallbackType) -> None:
        self.callbacks[evt] = callback
        
    async def handle_notification(self, ntf: NotificationEvent, ts: datetime) -> None:
        key = type(ntf)
        
        if key not in self.callbacks:
            print(f"Not registered: {key}")
            for i, j in self.callbacks.items():
                print(f"{i} -> {j}")
            return
        
        await self.callbacks[key](ntf, ts)