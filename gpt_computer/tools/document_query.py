# gpt_computer/tools/document_query.py

from typing import List, Union

from gpt_computer.helpers.document_query import DocumentQueryHelper
from gpt_computer.helpers.tool import Response, Tool


class DocumentQuery(Tool):
    async def execute(self, document: Union[str, List[str]], queries: List[str] = None, **kwargs) -> Response:
        helper = DocumentQueryHelper(self.agent, progress_callback=lambda x: self.set_progress(x))

        document_uris = [document] if isinstance(document, str) else document

        if not queries:
            # Get content for all documents
            results = []
            for uri in document_uris:
                content = await helper.document_get_content(uri, add_to_db=True)
                results.append(f"Content of {uri}:\n\n{content}")
            return Response(message="\n\n---\n\n".join(results), break_loop=False)
        else:
            # Perform Q&A
            success, answer = await helper.document_qa(document_uris, queries)
            return Response(message=answer, break_loop=False)
