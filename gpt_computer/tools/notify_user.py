# gpt_computer/tools/notify_user.py

from gpt_computer.helpers.notification import (
    NotificationManager,
    NotificationPriority,
    NotificationType,
)
from gpt_computer.helpers.tool import Response, Tool


class NotifyUser(Tool):
    async def execute(self, message: str, title: str = "", detail: str = "", type: str = "info", **kwargs) -> Response:
        try:
            notif_type = NotificationType(type.lower())
        except ValueError:
            notif_type = NotificationType.INFO

        NotificationManager.send_notification(
            type=notif_type,
            priority=NotificationPriority.NORMAL,
            message=message,
            title=title,
            detail=detail
        )

        result = self.agent.read_prompt("fw.notify_user.notification_sent.md")
        return Response(message=result, break_loop=False)
