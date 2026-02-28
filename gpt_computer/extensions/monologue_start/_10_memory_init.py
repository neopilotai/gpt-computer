
from agent import LoopData
from gpt_computer.helpers import memory
from gpt_computer.helpers.extension import Extension


class MemoryInit(Extension):

    async def execute(self, loop_data: LoopData = LoopData(), **kwargs):
        await memory.Memory.get(self.agent)


