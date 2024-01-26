import asyncio
from app.processors.state_processor_manager import StateProcessorManager

class TaskManager():

    def __init__(self, bot, queue) -> None:
        self._bot    = bot
        self._queue = queue

    async def start(self):
        
        while True:
            task = await self._queue.get()
            if task is None:
                break

            await task.process(StateProcessorManager)
            
