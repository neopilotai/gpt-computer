from gpt_computer.helpers import files, projects
from gpt_computer.helpers.api import ApiHandler, Request, Response


class GetChatFilesPath(ApiHandler):
    async def process(self, input: dict, request: Request) -> dict | Response:
        ctxid = input.get("ctxid", "")
        if not ctxid:
            raise Exception("No context id provided")
        context = self.use_context(ctxid)

        project_name = projects.get_context_project_name(context)
        if project_name:
            folder = files.normalize_gptc_path(projects.get_project_folder(project_name))
        else:
            folder = "/root" # root in container

        return {
            "ok": True,
            "path": folder,
        }
