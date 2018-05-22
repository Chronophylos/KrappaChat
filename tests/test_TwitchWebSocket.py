from krappachat.pubsub import TwitchWebSocket
import krappachat.pubsub
from blinker import Namespace
import asyncio
from krappachat.secret import nickname, oauth, channels

namespace = Namespace()
Signal = namespace.signal

krappachat.pubsub.register_signal(namespace)


async def test():
    tws = TwitchWebSocket()
    await tws.start()
    tws.connect(nickname, oauth)
    for channel in channels:
        tws.join(channel)


asyncio.get_event_loop().run_until_complete(test())
asyncio.get_event_loop().run_forever()
