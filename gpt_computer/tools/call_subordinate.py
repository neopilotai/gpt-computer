# gpt_computer/tools/call_subordinate.py

from agent import Agent, AgentConfig, UserMessage
from gpt_computer.helpers import projects
from gpt_computer.helpers.tool import Response, Tool


class CallSubordinate(Tool):
    async def execute(self, agent_profile: str, message: str, reset: bool = False, **kwargs):
        # 1. Get project name
        projects.get_context_project_name(self.agent.context)

        # 2. Check if subordinate already exists and matches profile
        subordinate = self.agent.get_data(Agent.DATA_NAME_SUBORDINATE)
        if subordinate and (reset or subordinate.config.profile != agent_profile):
            # If reset or profile mismatch, we might need a new one
            subordinate = None

        if not subordinate:
            # Create new subordinate
            # Derive a config for the subagent by copying the current config and changing the profile
            new_config = AgentConfig(
                chat_model=self.agent.config.chat_model,
                utility_model=self.agent.config.utility_model,
                embeddings_model=self.agent.config.embeddings_model,
                browser_model=self.agent.config.browser_model,
                mcp_servers=self.agent.config.mcp_servers,
                profile=agent_profile,
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
            self.agent.data[Agent.DATA_NAME_SUBORDINATE] = subordinate

        # 3. Add message to subordinate history
        user_msg = UserMessage(message=message)
        subordinate.hist_add_user_message(user_msg)

        # 4. Run monologue
        old_streaming_agent = self.agent.context.streaming_agent
        self.agent.context.streaming_agent = subordinate
        try:
            response_text = await subordinate.monologue()
        finally:
            self.agent.context.streaming_agent = old_streaming_agent

        # 5. Return response (AgentContext._process_chain handles passing it back to superior if called via communicate,
        # but if called as a tool, we just return the result to the current agent's history)
        return Response(message=response_text, break_loop=False)

    async def after_execution(self, response, **kwargs):
        # The base Tool.after_execution handles hist_add_tool_result and printing.
        await super().after_execution(response, **kwargs)
