# gpt_computer/tools/scheduler.py

import json

from datetime import datetime

from gpt_computer.helpers import projects
from gpt_computer.helpers.tool import Response, Tool
from gpt_computer.systems.scheduler.task_scheduler import (
    AdHocTask,
    PlannedTask,
    ScheduledTask,
    TaskPlan,
    TaskSchedule,
    TaskScheduler,
    TaskState,
)


class Scheduler(Tool):
    async def execute(self, **kwargs) -> Response:
        method = self.method
        scheduler = TaskScheduler.get()

        if method == "list_tasks":
            tasks = scheduler.get_tasks()
            # Apply filters if provided
            if "state" in kwargs:
                tasks = [t for t in tasks if t.state in kwargs["state"]]
            if "type" in kwargs:
                tasks = [t for t in tasks if t.type in kwargs["type"]]
            return Response(message=json.dumps(scheduler.serialize_tasks(tasks), indent=2), break_loop=False)

        elif method == "find_task_by_name":
            tasks = scheduler.find_task_by_name(kwargs.get("name", ""))
            return Response(message=json.dumps(scheduler.serialize_tasks(tasks), indent=2), break_loop=False)

        elif method == "show_task":
            task_info = scheduler.serialize_task(kwargs.get("uuid", ""))
            if not task_info:
                return Response(message=f"Task {kwargs.get('uuid')} not found", break_loop=False)
            return Response(message=json.dumps(task_info, indent=2), break_loop=False)

        elif method == "run_task":
            await scheduler.run_task_by_uuid(kwargs.get("uuid", ""), kwargs.get("context"))
            return Response(message=f"Task {kwargs.get('uuid')} started", break_loop=False)

        elif method == "delete_task":
            await scheduler.remove_task_by_uuid(kwargs.get("uuid", ""))
            return Response(message=f"Task {kwargs.get('uuid')} deleted", break_loop=False)

        elif method == "create_scheduled_task":
            project_name = projects.get_context_project_name(self.agent.context)
            schedule = TaskSchedule(**kwargs["schedule"])
            task = ScheduledTask.create(
                name=kwargs["name"],
                system_prompt=kwargs["system_prompt"],
                prompt=kwargs["prompt"],
                schedule=schedule,
                attachments=kwargs.get("attachments", []),
                context_id=self.agent.context.id if not kwargs.get("dedicated_context") else None,
                project_name=project_name
            )
            await scheduler.add_task(task)
            return Response(message=f"Scheduled task created with UUID: {task.uuid}", break_loop=False)

        elif method == "create_adhoc_task":
            project_name = projects.get_context_project_name(self.agent.context)
            task = AdHocTask.create(
                name=kwargs["name"],
                system_prompt=kwargs["system_prompt"],
                prompt=kwargs["prompt"],
                token="", # Will be generated
                attachments=kwargs.get("attachments", []),
                context_id=self.agent.context.id if not kwargs.get("dedicated_context") else None,
                project_name=project_name
            )
            await scheduler.add_task(task)
            return Response(message=f"Ad-hoc task created with UUID: {task.uuid}", break_loop=False)

        elif method == "create_planned_task":
            project_name = projects.get_context_project_name(self.agent.context)
            plan = TaskPlan.create(todo=[datetime.fromisoformat(dt) for dt in kwargs["plan"]])
            task = PlannedTask.create(
                name=kwargs["name"],
                system_prompt=kwargs["system_prompt"],
                prompt=kwargs["prompt"],
                plan=plan,
                attachments=kwargs.get("attachments", []),
                context_id=self.agent.context.id if not kwargs.get("dedicated_context") else None,
                project_name=project_name
            )
            await scheduler.add_task(task)
            return Response(message=f"Planned task created with UUID: {task.uuid}", break_loop=False)

        elif method == "wait_for_task":
            # This is a bit more complex as it needs to poll for task completion
            uuid = kwargs.get("uuid", "")
            import asyncio
            while True:
                task = scheduler.get_task_by_uuid(uuid)
                if not task or task.state != TaskState.RUNNING:
                    break
                await asyncio.sleep(2)
            return Response(message=f"Task {uuid} result: {task.last_result if task else 'Task not found'}", break_loop=False)

        else:
            return Response(message=f"Unknown method: {method}", break_loop=False)
