import os
from langchain_tavily import TavilySearch
from tavily import TavilyClient

client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def tavily_search(query: str):
    response = client.search(query=query, max_results=3)
    results = []
    for i, r in enumerate(response["results"], 1):
        title = r.get("title", "Unknown")
        url = r.get("url", "")
        content = r.get("content", "").strip()
        if len(content) > 300:
            content = content[:300].rsplit(" ", 1)[0] + "..."
        results.append(f"{i}. {title} \n {url}\n {content}")

    return "\n\n".join(results)

tavily_search_tool = TavilySearch(search_depth="basic")