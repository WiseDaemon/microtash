import os
import re
import urllib.parse
import urllib.request
import json
from typing import Dict, Any, List, Optional
import httpx
from app.config import settings

def auto_fetch_web_info(query: str) -> Dict[str, Any]:
    """
    Auto-fetches comprehensive description, key takeaways, and metadata
    from the web given just a book name, author, or concept/idea.
    Uses Firecrawl Web Search, Wikipedia API, and OpenLibrary with seamless fallbacks.
    """
    clean_query = query.strip()
    sources = []
    fetched_texts = []
    resolved_author = ""
    resolved_title = clean_query

    # 1. Try Firecrawl Web Search (Rich live summaries, chapter outlines, and articles)
    firecrawl_key = os.environ.get("FIRECRAWL_API_KEY", "")
    if firecrawl_key:
        try:
            search_query = f"{clean_query} complete chapter by chapter book summary all key ideas takeaways"
            resp = httpx.post(
                "https://api.firecrawl.dev/v1/search",
                headers={"Authorization": f"Bearer {firecrawl_key}"},
                json={"query": search_query, "limit": 4},
                timeout=10.0
            )
            if resp.status_code == 200:
                data = resp.json()
                results = data.get("data", [])
                for item in results:
                    title = item.get("title", "")
                    desc = item.get("description", "")
                    markdown = item.get("markdown", "")
                    url = item.get("url", "")
                    
                    if url:
                        sources.append({"title": title or "Web Source", "url": url})
                    
                    content_piece = desc
                    if markdown and len(markdown) > len(desc):
                        # Clean markdown and take comprehensive snippet
                        cleaned_md = re.sub(r"\[.*?\]\(.*?\)", "", markdown)
                        cleaned_md = re.sub(r"#{1,6}\s*", "", cleaned_md)
                        content_piece = cleaned_md[:3000]

                    if content_piece:
                        fetched_texts.append(f"Source ({title}):\n{content_piece}")
        except Exception as e:
            print(f"[WebFetcher] Firecrawl search failed: {e}")

    # 2. Try Wikipedia API (Encyclopedic overview for authors, books, concepts)
    try:
        wiki_search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(clean_query)}&utf8=&format=json"
        req = urllib.request.Request(wiki_search_url, headers={"User-Agent": "MicrostashApp/1.0"})
        with urllib.request.urlopen(req, timeout=5) as r:
            wiki_data = json.loads(r.read().decode("utf-8"))
            search_items = wiki_data.get("query", {}).get("search", [])
            if search_items:
                top_hit = search_items[0]["title"]
                # Fetch summary for top hit
                summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(top_hit)}"
                req_sum = urllib.request.Request(summary_url, headers={"User-Agent": "MicrostashApp/1.0"})
                with urllib.request.urlopen(req_sum, timeout=5) as sum_r:
                    sum_data = json.loads(sum_r.read().decode("utf-8"))
                    extract = sum_data.get("extract", "")
                    if extract:
                        fetched_texts.append(f"Wikipedia ({top_hit}):\n{extract}")
                        sources.append({"title": f"Wikipedia: {top_hit}", "url": f"https://en.wikipedia.org/wiki/{urllib.parse.quote(top_hit)}"})
                        if not resolved_title or resolved_title.lower() in clean_query.lower():
                            resolved_title = top_hit
    except Exception as e:
        print(f"[WebFetcher] Wikipedia fetch failed: {e}")

    # 3. Try OpenLibrary API (Author, subjects, editions)
    try:
        ol_url = f"https://openlibrary.org/search.json?q={urllib.parse.quote(clean_query)}&limit=1"
        req = urllib.request.Request(ol_url, headers={"User-Agent": "MicrostashApp/1.0"})
        with urllib.request.urlopen(req, timeout=5) as r:
            ol_data = json.loads(r.read().decode("utf-8"))
            docs = ol_data.get("docs", [])
            if docs:
                doc = docs[0]
                if not resolved_author and doc.get("author_name"):
                    resolved_author = doc["author_name"][0]
                subjects = doc.get("subject", [])[:6]
                if subjects:
                    fetched_texts.append(f"OpenLibrary Subjects: {', '.join(subjects)}")
    except Exception as e:
        print(f"[WebFetcher] OpenLibrary fetch failed: {e}")

    # Combine fetched text
    combined_description = "\n\n".join(fetched_texts).strip()
    if not combined_description:
        combined_description = (
            f"Key concept, mental models, and principles relating to {clean_query}. "
            f"Analyzing core tenets, historical origins, practical applications, and common pitfalls."
        )

    return {
        "query": clean_query,
        "resolved_title": resolved_title,
        "resolved_author": resolved_author or "Curated Thinker",
        "description": combined_description,
        "sources": sources
    }
