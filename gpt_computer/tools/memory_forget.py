# gpt_computer/tools/memory_forget.py

from gpt_computer.systems.memory.base import Memory
from gpt_computer.helpers.tool import Response, Tool

DEFAULT_THRESHOLD = 0.7


class MemoryForget(Tool):

    async def execute(self, query="", threshold=DEFAULT_THRESHOLD, filter="", **kwargs):
        db = await Memory.get(self.agent)

        # delete_documents_by_query returns the list of removed documents
        removed = await db.delete_documents_by_query(query=query, threshold=threshold, filter=filter)

        result = self.agent.read_prompt("fw.memories_deleted.md", memory_count=len(removed))
        return Response(message=result, break_loop=False)
