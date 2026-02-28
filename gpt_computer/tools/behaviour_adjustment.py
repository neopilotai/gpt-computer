# gpt_computer/tools/behaviour_adjustment.py

from gpt_computer.helpers.tool import Response, Tool


class BehaviourAdjustment(Tool):
    async def execute(self, adjustments: str, **kwargs) -> Response:
        # Behaviour adjustments are typically handled by appending to a list of instructions
        # that are then included in the system prompt.

        if not self.loop_data:
            return Response(message="Error: loop_data not available", break_loop=False)

        if "behaviour" not in self.loop_data.params_persistent:
            self.loop_data.params_persistent["behaviour"] = []

        self.loop_data.params_persistent["behaviour"].append(adjustments)

        result = self.agent.read_prompt("behaviour.updated.md")
        return Response(message=result, break_loop=False)
