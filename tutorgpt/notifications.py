import asyncio
from typing import Dict, Optional, AsyncIterator


class RoadmapNotifier:
    """
    Simple in-memory notifier to push 'roadmap ready' events per user.
    Uses an asyncio.Queue per user to stream Server-Sent Events (SSE).
    """

    def __init__(self) -> None:
        self._queues: Dict[str, asyncio.Queue[str]] = {}
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def set_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """Attach the main asyncio event loop, used by background threads."""
        self._loop = loop

    def _get_queue(self, user_id: str) -> asyncio.Queue[str]:
        if user_id not in self._queues:
            self._queues[user_id] = asyncio.Queue()
        return self._queues[user_id]

    async def stream(self, user_id: str) -> AsyncIterator[str]:
        """
        Async generator that yields SSE-formatted messages for a given user.
        """
        queue = self._get_queue(user_id)
        while True:
            message = await queue.get()
            yield f"data: {message}\n\n"

    def notify_roadmap_ready(self, user_id: str, roadmap_id: str) -> None:
        """
        Enqueue a 'roadmap ready' message for the given user.
        Safe to call from background threads.
        """
        if self._loop is None:
            return

        queue = self._get_queue(user_id)
        message = f"El roadmap {roadmap_id} ya se ha creado"

        def _put_nowait() -> None:
            queue.put_nowait(message)

        # Use the main loop so this can be called from any thread.
        self._loop.call_soon_threadsafe(_put_nowait)


notifier = RoadmapNotifier()


