# gpt_computer/tools/skills_tool.py

from pathlib import Path

from gpt_computer.helpers import files, skills
from gpt_computer.helpers.tool import Response, Tool


class SkillsTool(Tool):
    async def execute(self, **kwargs) -> Response:
        method = self.method or "list"

        if method == "list":
            return await self.list_skills()
        elif method == "load":
            return await self.load_skill(kwargs.get("skill_name"))
        elif method == "search":
            return await self.search_skills(kwargs.get("query"))
        elif method == "read_file":
            return await self.read_skill_file(kwargs.get("skill_name"), kwargs.get("file_path"))
        else:
            return Response(message=f"Unknown method: {method}", break_loop=False)

    async def list_skills(self) -> Response:
        skill_list = skills.list_skills(agent=self.agent)
        if not skill_list:
            return Response(message="No skills found.", break_loop=False)

        lines = ["Available Skills:"]
        for s in skill_list:
            lines.append(f"- **{s.name}**: {s.description} (v{s.version})")

        return Response(message="\n".join(lines), break_loop=False)

    async def load_skill(self, skill_name: str | None) -> Response:
        if not skill_name:
            return Response(message="Error: skill_name is required for 'load' method.", break_loop=False)

        content = skills.load_skill_for_agent(skill_name, agent=self.agent)
        return Response(message=content, break_loop=False)

    async def search_skills(self, query: str | None) -> Response:
        if not query:
            return Response(message="Error: query is required for 'search' method.", break_loop=False)

        results = skills.search_skills(query, agent=self.agent)
        if not results:
            return Response(message=f"No skills found matching: {query}", break_loop=False)

        lines = [f"Search results for '{query}':"]
        for s in results:
            lines.append(f"- **{s.name}**: {s.description}")

        return Response(message="\n".join(lines), break_loop=False)

    async def read_skill_file(self, skill_name: str | None, file_path: str | None) -> Response:
        if not skill_name or not file_path:
            return Response(message="Error: skill_name and file_path are required for 'read_file' method.", break_loop=False)

        skill = skills.find_skill(skill_name, agent=self.agent)
        if not skill:
            return Response(message=f"Error: skill '{skill_name}' not found.", break_loop=False)

        # Security check: ensure path is within skill directory
        abs_skill_dir = Path(skill.path).resolve()
        target_path = (abs_skill_dir / file_path).resolve()

        if not files.is_in_dir(str(target_path), str(abs_skill_dir)):
            return Response(message="Error: Access denied. File path is outside skill directory.", break_loop=False)

        if not target_path.exists():
            return Response(message=f"Error: File '{file_path}' not found in skill '{skill_name}'.", break_loop=False)

        try:
            content = files.read_file(str(target_path))
            return Response(message=f"File: {file_path}\n\n{content}", break_loop=False)
        except Exception as e:
            return Response(message=f"Error reading file: {str(e)}", break_loop=False)
