# gpt_computer/tools/search_engine.py

import json

from gpt_computer.helpers import duckduckgo_search, searxng
from gpt_computer.helpers.print_style import PrintStyle
from gpt_computer.helpers.tool import Response, Tool


class SearchEngine(Tool):
    async def execute(self, query: str, **kwargs) -> Response:
        # Try SearXNG first
        try:
            results = await searxng.search(query)
            if results and 'results' in results:
                formatted_results = []
                for res in results['results'][:10]: # Limit to top 10
                    formatted_results.append({
                        "title": res.get("title"),
                        "url": res.get("url"),
                        "content": res.get("content") or res.get("snippet")
                    })
                return Response(message=json.dumps(formatted_results, indent=2), break_loop=False)
        except Exception as e:
            PrintStyle.error(f"SearXNG search failed: {str(e)}")

        # Fallback to DuckDuckGo
        try:
            results = duckduckgo_search.search(query)
            return Response(message=json.dumps(results, indent=2), break_loop=False)
        except Exception as e:
            return Response(message=f"Error performing search: {str(e)}", break_loop=False)
