import nest_asyncio
import uuid
from typing import List, Any, Dict, Optional

from gpt_computer.core.context import AgentContext, UserMessage, AgentContextType, AgentConfig

nest_asyncio.apply()

class Agent:
    DATA_NAME_SUBORDINATE = "_subordinate"
    DATA_NAME_SUPERIOR = "_superior"

    def __init__(self, context: AgentContext, number: int = 0):
        self.context = context
        self.agent_name = context.name
        self.number = number
        self.data: Dict[str, Any] = {}
        # Delay import to avoid circular dependency
        from gpt_computer.helpers.history import History
        self.history = History(agent=self)

    @property
    def config(self):
        return self.context.config

    def set_data(self, key: str, value: Any):
        self.data[key] = value

    async def monologue(self) -> str:
        # Placeholder for the actual agent loop
        self.context.log.log(type="info", content=f"Agent {self.number} monologue started (Runtime v1)")
        return f"Task completed by Agent {self.number} (Runtime v1)"

    def handle_critical_exception(self, e):
        self.context.log.log(type="error", content=f"Critical exception in Agent {self.number}: {e}")

    def hist_add_user_message(self, msg: UserMessage):
        self.context.log.log(type="user", content=msg.message)
    
    def read_prompt(self, name: str) -> str:
        return f"Prompt {name}"
        
    def hist_add_tool_result(self, name: str, result: str, **kwargs):
        self.context.log.log(type="tool", heading=f"Tool {name} result", content=result)

class AgentRuntime:
    def __init__(self, config: Optional[AgentConfig] = None):
        self.config = config or AgentConfig()
        self.context = AgentContext(config=self.config, name="AutonomousAgent")
        self.agent = self.context.agent0

    async def run(self, message: str):
        self.context.log.log(type="info", content=f"Starting autonomous runtime for message: {message}")
        user_msg = UserMessage(message=message)
        self.agent.hist_add_user_message(user_msg)
        return await self.agent.monologue()
