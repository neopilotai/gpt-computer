# gpt_computer/tools/browser_agent.py

from agent import Agent, AgentConfig, UserMessage
from gpt_computer.helpers.tool import Response, Tool


class BrowserAgent(Tool):
    async def execute(self, message: str, reset: bool = False, **kwargs):
        # Browser agent is a specialized subordinate agent
        # It uses the "browser" profile

        subordinate = self.agent.get_data("_browser_subordinate")
        if subordinate and reset:
            subordinate = None

        if not subordinate:
            new_config = AgentConfig(
                chat_model=self.agent.config.chat_model,
                utility_model=self.agent.config.utility_model,
                embeddings_model=self.agent.config.embeddings_model,
                browser_model=self.agent.config.browser_model,
                mcp_servers=self.agent.config.mcp_servers,
                profile="browser",
                memory_subdir=self.agent.config.memory_subdir,
                knowledge_subdirs=self.agent.config.knowledge_subdirs,
                code_exec_ssh_enabled=self.agent.config.code_exec_ssh_enabled,
                code_exec_ssh_addr=self.agent.config.code_exec_ssh_addr,
                code_exec_ssh_port=self.agent.config.code_exec_ssh_port,
                code_exec_ssh_user=self.agent.config.code_exec_ssh_user,
                code_exec_ssh_pass=self.agent.config.code_exec_ssh_pass,
                additional=self.agent.config.additional.copy()
            )

            subordinate = Agent(self.agent.number + 1, new_config, self.agent.context)
            subordinate.data[Agent.DATA_NAME_SUPERIOR] = self.agent
            self.agent.set_data("_browser_subordinate", subordinate)

        user_msg = UserMessage(message=message)
        subordinate.hist_add_user_message(user_msg)

        old_streaming_agent = self.agent.context.streaming_agent
        self.agent.context.streaming_agent = subordinate
        try:
            response_text = await subordinate.monologue()
        finally:
            self.agent.context.streaming_agent = old_streaming_agent

        return Response(message=response_text, break_loop=False)
