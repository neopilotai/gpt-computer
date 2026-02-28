from typing import Any

from gpt_computer.helpers import settings
from gpt_computer.helpers.api import ApiHandler, Request, Response


class SetSettings(ApiHandler):
    async def process(self, input: dict[Any, Any], request: Request) -> dict[Any, Any] | Response:
        frontend = input.get("settings", input)
        backend = settings.convert_in(settings.Settings(**frontend))
        backend = settings.set_settings(backend)
        out = settings.convert_out(backend)
        return dict(out)
