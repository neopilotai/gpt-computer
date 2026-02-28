from agent import AgentContext
from gpt_computer.helpers import persist_chat
from gpt_computer.helpers.api import ApiHandler, Input, Output, Request
from gpt_computer.systems.scheduler.task_scheduler import TaskScheduler


class RemoveChat(ApiHandler):
    async def process(self, input: Input, request: Request) -> Output:
        ctxid = input.get("context", "")

        scheduler = TaskScheduler.get()
        scheduler.cancel_tasks_by_context(ctxid, terminate_thread=True)

        context = AgentContext.use(ctxid)
        if context:
            # stop processing any tasks
            context.reset()

        AgentContext.remove(ctxid)
        persist_chat.remove_chat(ctxid)

        await scheduler.reload()

        tasks = scheduler.get_tasks_by_context_id(ctxid)
        for task in tasks:
            await scheduler.remove_task_by_uuid(task.uuid)

        # Context removal affects global chat/task lists in all tabs.
        from gpt_computer.helpers.state_monitor_integration import mark_dirty_all
        mark_dirty_all(reason="api.chat_remove.RemoveChat")

        return {
            "message": "Context removed.",
        }
