# gpt_computer/tools/a2a_chat.py


from gpt_computer.helpers import fasta2a_client
from gpt_computer.helpers.tool import Response, Tool


class A2AChat(Tool):
    async def execute(self, agent_url: str, message: str, **kwargs) -> Response:
        try:
            conn = await fasta2a_client.connect_to_agent(agent_url)
            response = await conn.send_message(message, attachments=kwargs.get("attachments"))

            # The structure of A2A response might vary, usually it contains 'result' or 'text'
            result_text = ""
            if isinstance(response, dict):
                result = response.get("result", {})
                if isinstance(result, dict):
                    result_text = result.get("text", result.get("content", str(result)))
                else:
                    result_text = str(result)
            else:
                result_text = str(response)

            await conn.close()
            return Response(message=result_text, break_loop=False)
        except Exception as e:
            return Response(message=f"A2A Communication Error: {str(e)}", break_loop=False)
