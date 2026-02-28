from agent import AgentContext
from gpt_computer.api.message import Message
from gpt_computer.helpers.defer import DeferredTask


class MessageAsync(Message):
    async def respond(self, task: DeferredTask, context: AgentContext):
        return {
            "message": "Message received.",
            "context": context.id,
        }
