import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

tavily_api_key = os.getenv("TAVILY_API_KEY")

if not tavily_api_key:
    raise ValueError("TAVILY_API_KEY not found in .env file")

tavily_client = TavilyClient(api_key=tavily_api_key)


def search_web(query, max_results=5):
    """
    Search the web and return relevant sources.
    """

    response = tavily_client.search(
        query=query,
        search_depth="basic",
        max_results=max_results
    )

    results = []

    for result in response.get("results", []):
        results.append({
            "title": result.get("title", ""),
            "url": result.get("url", ""),
            "content": result.get("content", "")
        })

    return results


if __name__ == "__main__":
    results = search_web("software engineering internship skills")

    for result in results:
        print("\nTITLE:", result["title"])
        print("URL:", result["url"])
        print("CONTENT:", result["content"][:300])