# gpt_computer/tools/wait.py

from datetime import datetime, timedelta, timezone

from gpt_computer.helpers import wait
from gpt_computer.helpers.tool import Response, Tool


class Wait(Tool):
    async def execute(self, seconds: float = 0, minutes: float = 0, hours: float = 0, days: float = 0, until: str = None, **kwargs) -> Response:
        now = datetime.now(timezone.utc)
        is_duration_wait = True

        if until:
            target_time = datetime.fromisoformat(until.replace('Z', '+00:00'))
            is_duration_wait = False
        else:
            total_seconds = seconds + (minutes * 60) + (hours * 3600) + (days * 86400)
            target_time = now + timedelta(seconds=total_seconds)

        def get_heading(remaining_text: str):
            return f"icon://timer {self.agent.agent_name}: Waiting ({remaining_text})"

        await wait.managed_wait(self.agent, target_time, is_duration_wait, self.log, get_heading)

        result = self.agent.read_prompt("fw.wait_complete.md")
        return Response(message=result, break_loop=False)
