# py-twitch-eventsub

A lightweight Python library for handling Twitch EventSub WebSocket events — only covering the specific event types I currently need.  
It's built on top of **websockets**, **httpx**, and **pydantic**, with a focus on being simple, transparent, and reliable.

---

## ⚡ Overview

`py-twitch-eventsub` sets up a Twitch EventSub WebSocket session, automatically subscribes to events, and handles a small,
carefully chosen subset of events:

- ✅ `session_welcome`
- ✅ `session_keepalive`
- ✅ `session_reconnect`
- ✅ `notification` (with `channel.chat.message` and `channel.cheer`)
- ✅ `revocation` (logged as a warning)
- ⚠️ Other events are recognized but ignored with a warning.

This library is **not** a full Twitch SDK — it's meant for small integrations, personal bots, and experiments where you only need core
EventSub behavior and want full control of the flow. However in the future I might extend.

---

## 🔧 Example

```python
import asyncio
from datetime import datetime
from py_twitch_eventsub import *

async def chat_handler(evt: NotificationEvent, ts: datetime) -> None:
    assert isinstance(evt, ChannelChatMessage)
    print(f"{evt.chatter_user_name}[{ts}]: {evt.message.text}")

async def cheer_handler(evt: NotificationEvent, ts: datetime) -> None:
    assert isinstance(evt, ChannelCheer)
    user = evt.user_name or "Anonymous"
    print(f"{user} cheered {evt.bits} bits!")

async def main() -> None:
    controller = TwitchController()

    # Optional: use local Twitch CLI WebSocket server for dev/testing
    # controller.set_dev_mode(
    #     "http://127.0.0.1:8080/eventsub/subscriptions",
    #     "ws://127.0.0.1:8080/ws"
    # )

    controller.register_callback(ChannelChatMessage, chat_handler)
    controller.register_callback(ChannelCheer, cheer_handler)

    await controller.start()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 📡 Handled Events

| Event Type | Description | Status |
|---|---|---|
| `session_welcome` | Saves session ID and subscribes to events | ✅ |
| `session_keepalive` | Keeps the connection alive | ✅ |
| `session_reconnect` | Transparently reconnects to the new URL provided by Twitch | ✅ |
| `notification` | Handles `channel.chat.message` and `channel.cheer` | ✅ |
| `revocation` | Logs subscription revocation as a warning | ✅ |
| *other events* | Logged but ignored | ⚠️ ignored |

---

## 🧰 Requirements

- Python 3.10 or newer
- A Twitch application with a valid OAuth token and Client ID

Example `.env` file:

```env
TWITCH_TOKEN=your_oauth_token_here
CLIENT_ID=your_client_id_here
USER_ID=your_user_id_here
BROADCASTER_ID=target_broadcaster_id_here
```

> ⚠️ `channel.cheer` requires a **broadcaster** user access token with the `bits:read` scope — the bot's token is not sufficient.  
> For local testing, use the [Twitch CLI](https://dev.twitch.tv/docs/cli/) mock WebSocket server with `set_dev_mode()`.

---

## 📥 Installation

### GitHub
```bash
pip install git+https://github.com/pmrch/py-twitch-eventsub.git
```

### Local
```bash
pip install -e .
```

### PyPI (for later)
Once the API is stable and documented, I might publish to PyPI.

---

## 🔁 Reconnection

The library handles WebSocket errors automatically with up to **5 reconnect attempts** and exponential backoff (2s, 4s, 8s, 16s):

| Error | Action |
|---|---|
| `ConnectionClosed` | Reconnect |
| `ConnectionClosedError` (1006) | Reconnect |
| `PayloadTooBig` | Skip |
| `ProtocolError` | Reconnect |
| `NegotiationError` | Reconnect |
| `ConcurrencyError` | Reconnect |
| `ConnectionClosedOK` | Exit cleanly |
| Twitch 4xxx codes | Exit cleanly |
| Everything else | Fatal — raises |

---

## 🧪 Local Development / Testing

To test without connecting to real Twitch, use the [Twitch CLI](https://dev.twitch.tv/docs/cli/) mock WebSocket server:

```bash
twitch event websocket start-server
```

Then point your controller at the local server:

```python
controller.set_dev_mode(
    "http://127.0.0.1:8080/eventsub/subscriptions",
    "ws://127.0.0.1:8080/ws"
)
```

Trigger mock events in a separate terminal:

```bash
twitch event trigger cheer -F ws://127.0.0.1:8080/ws --transport websocket
twitch event trigger channel.chat.message -F ws://127.0.0.1:8080/ws --transport websocket
```

---

## 🤝 Contributing

Pull requests are **welcome**, but **I'll only merge them if they align with the library's current goals and style.**  
This isn't a general-purpose Twitch library — it's a focused one.  
That said, if you've got a good addition or cleanup that fits well, I'll happily review it.  
Moreover you are free to fork this repository and maintain your own version.

---

## 📜 License

MIT © 2026  
Free to use, modify, and adapt with attribution.

---

## 💬 Author

Created by **pmrch** — just a self-learnt developer in high-school. Claude.ai also assisted throughout the development
of this library. This project is a Python rewrite of [rs-twitch-eventsub](https://github.com/pmrch/rs-twitch-eventsub) and part of a larger personal goal.