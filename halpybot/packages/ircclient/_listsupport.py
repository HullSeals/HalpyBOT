"""
listsupport.py - Handler for LIST IRC commands

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from __future__ import annotations
from typing import List, Optional
import asyncio
from pydle.features.rfc1459 import RFC1459Support


class ListHandler(RFC1459Support):
    """ListHandler: Process the response to /LIST and save the list of channels"""

    def __init__(
        self,
        nickname: str = "HalpyLISTener",
        fallback: Optional[List] = None,
        username=None,
        realname=None,
        **kwargs,
    ):
        super().__init__(
            nickname,
            fallback if fallback is not None else [],
            username,
            realname,
            **kwargs,
        )
        self._pending_query = asyncio.Queue()
        self._channellist = set()

    async def all_channels(self) -> List[str]:
        await self.rawmsg("LIST")
        # Create future
        future = asyncio.get_event_loop().create_future()
        await self._pending_query.put(future)
        try:
            channels = await future
            return list(channels)
        except asyncio.CancelledError:
            # We don't care if it's cancelled as this should only happen on shutdown
            pass

    async def on_raw_321(self, *args):
        # Results incoming, empty channel list
        self._channellist.clear()

    async def on_raw_322(self, message):
        # Called by Pydle when we get a new channel, add to list
        self._channellist.add(message.params[1])

    async def on_raw_323(self, *args):
        # Set results
        future = await self._pending_query.get()
        future.set_result(self._channellist)
