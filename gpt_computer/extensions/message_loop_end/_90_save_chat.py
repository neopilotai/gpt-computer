from agent import AgentContextType, LoopData
from gpt_computer.helpers import persist_chat
from gpt_computer.helpers.extension import Extension


class SaveChat(Extension):
    async def execute(self, loop_data: LoopData = LoopData(), **kwargs):
        # Skip saving BACKGROUND contexts as they should be ephemeral
        if self.agent.context.type == AgentContextType.BACKGROUND:
            return

        persist_chat.save_tmp_chat(self.agent.context)
