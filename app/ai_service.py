import os
import json
import re
from typing import List, Dict, Any, Optional
import httpx
from app.config import settings

def extract_ideas_from_content(
    input_text: str,
    source_title: str = "Unknown Source",
    author: str = "Unknown Author",
    topic: str = "Mental Models",
    provider: str = "gemini",
    num_ideas: int = 3
) -> List[Dict[str, Any]]:
    """
    Deconstructs raw text, article content, or a book chapter into structured Deepstash-style idea cards.
    Tries requested provider first (NVIDIA or Gemini), falling back seamlessly if necessary.
    """
    # If input looks like an HTTP URL, attempt to scrape the main text
    cleaned_input = input_text.strip()
    if cleaned_input.startswith("http://") or cleaned_input.startswith("https://"):
        cleaned_input = fetch_url_content(cleaned_input)

    # Prompt design for atomic microlearning cards
    system_prompt = (
        "You are an expert master microlearning curator for Deepstash, an app designed to replace doomscrolling with bite-sized wisdom. "
        "Your mission is to comprehensively extract atomic, high-leverage ideas from the provided book or material. "
        "Each idea MUST be distinct, actionable, memorable, and self-contained.\n\n"
        "CRITICAL CONTENT SEPARATION RULE:\n"
        "- 'summary' is the bite-sized microlearning overview (50-80 words, 1-2 punchy paragraphs for rapid swiping).\n"
        "- 'detailed_explanation' MUST be an authentic, comprehensive masterclass breakdown of the underlying concept (250-400 words, structured in 3 distinct parts). "
        "DO NOT repeat or paraphrase the summary! Explain:\n"
        "  1. The Core Mechanism & First Principles (how it works mechanically beneath the surface)\n"
        "  2. Cognitive & System Dynamics (why human instinct or organizations systematically fail here)\n"
        "  3. Nuance & Boundary Conditions (where this model fails or must not be applied).\n"
        "- 'example' MUST be a concrete, real-world case study or historical story (100-180 words) featuring specific people, companies, or events with measurable outcomes.\n\n"
        "Return ONLY a valid JSON array of objects with the exact following schema:\n"
        "[\n"
        "  {\n"
        "    \"title\": \"Punchy Headline Concept (e.g. The Two-Minute Rule)\",\n"
        "    \"one_liner\": \"Bold, memorable 1-sentence hook\",\n"
        "    \"summary\": \"Concise microlearning summary (50-80 words).\",\n"
        "    \"detailed_explanation\": \"Authentic in-depth analysis (250-400 words) structured across First Principles, Dynamics, and Boundary Conditions. MUST NOT BE THE SAME AS THE SUMMARY.\",\n"
        "    \"example\": \"Concrete real-world case study (100-180 words) with verifiable entities and outcomes.\",\n"
        "    \"visual_diagram\": \"Valid Mermaid.js graph code (e.g. graph TD or graph LR with 3-4 nodes and styles) visually explaining the conceptual mechanism or flow.\",\n"
        "    \"quote\": \"Inspiring quote or key statement attributed to the author.\",\n"
        "    \"action_item\": \"Concrete 'Try it today' actionable step the reader can execute right away.\",\n"
        "    \"author\": \"Author or primary thinker\",\n"
        "    \"source\": \"Book, paper, or source title\",\n"
        "    \"topic\": \"Category (e.g. Mental Models, Productivity, Stoicism, Wealth, Psychology, Tech, Health)\",\n"
        "    \"tags\": [\"Tag1\", \"Tag2\", \"Tag3\"],\n"
        "    \"read_time_mins\": 1,\n"
        "    \"color_theme\": \"indigo\"\n"
        "  }\n"
        "]"
    )

    if num_ideas <= 0:
        count_instruction = (
            "Extract ALL the fundamental ideas, chapters, mental models, and principles across the entire book. "
            "You MUST generate between 8 and 12 distinct atomic idea cards (one card for each core chapter or foundational concept) "
            "so the reader gets a complete, exhaustive breakdown of the entire book from start to finish."
        )
    else:
        count_instruction = f"Extract exactly {num_ideas} high-leverage atomic microlearning idea cards from the material."

    user_prompt = (
        f"{count_instruction}\n"
        f"Reference Author: {author}\n"
        f"Reference Source: {source_title}\n"
        f"Preferred Category: {topic}\n\n"
        f"--- MATERIAL & CHAPTER SUMMARIES ---\n"
        f"{cleaned_input[:18000]}\n"
        f"--- END MATERIAL ---\n\n"
        "Output strictly a valid JSON array of idea cards with no markdown backticks and no conversational filler."
    )

    # Execution order based on provider preference
    if provider.lower() == "nvidia":
        try:
            return call_nvidia_api(system_prompt, user_prompt)
        except Exception as e:
            print(f"[AI Service] NVIDIA API call failed ({e}). Falling back to Gemini...")
            return call_gemini_api(system_prompt, user_prompt)
    else:
        try:
            return call_gemini_api(system_prompt, user_prompt)
        except Exception as e:
            print(f"[AI Service] Gemini API call failed ({e}). Falling back to NVIDIA...")
            try:
                return call_nvidia_api(system_prompt, user_prompt)
            except Exception as e2:
                print(f"[AI Service] Both AI providers failed: {e2}. Generating rule-based extraction.")
                return fallback_rule_based_extraction(cleaned_input, source_title, author, topic, num_ideas)

def call_gemini_api(system_prompt: str, user_prompt: str) -> List[Dict[str, Any]]:
    from google import genai
    from google.genai import types
    import time
    
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not configured.")

    client = genai.Client(api_key=api_key)
    
    # Robust multi-model candidate list for high availability
    candidate_models = [settings.GEMINI_MODEL, "gemini-3.8-flash", "gemini-3.5-flash", "gemini-flash-latest"]
    last_err = None

    for model_name in candidate_models:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=0.3,
                        max_output_tokens=6144,
                        response_mime_type="application/json"
                    )
                )
                text = response.text.strip()
                return parse_json_safely(text)
            except Exception as e:
                last_err = e
                time.sleep(0.8)

    raise last_err

def call_nvidia_api(system_prompt: str, user_prompt: str) -> List[Dict[str, Any]]:
    from openai import OpenAI
    
    api_key = settings.NVIDIA_API_KEY
    if not api_key:
        raise ValueError("NVIDIA_API_KEY is not configured.")

    client = OpenAI(
        base_url=settings.NVIDIA_BASE_URL,
        api_key=api_key,
        timeout=15.0
    )

    completion = client.chat.completions.create(
        model=settings.NVIDIA_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,
        max_tokens=2048
    )

    text = completion.choices[0].message.content.strip()
    return parse_json_safely(text)

def parse_json_safely(text: str) -> List[Dict[str, Any]]:
    # 1. Direct parse after stripping markdown fences
    cleaned = re.sub(r"^```(?:json)?\s*", "", text, flags=re.MULTILINE)
    cleaned = re.sub(r"\s*```$", "", cleaned, flags=re.MULTILINE).strip()

    try:
        data = json.loads(cleaned)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            for k in ["ideas", "cards", "data", "results"]:
                if k in data and isinstance(data[k], list):
                    return data[k]
            return [data]
    except Exception:
        pass

    # 2. Extract outermost [ ... ] array
    start_bracket = text.find('[')
    end_bracket = text.rfind(']')
    if start_bracket != -1 and end_bracket != -1 and end_bracket > start_bracket:
        try:
            data = json.loads(text[start_bracket:end_bracket + 1])
            if isinstance(data, list):
                return data
        except Exception:
            pass

    # 3. Extract outermost { ... } object
    start_brace = text.find('{')
    end_brace = text.rfind('}')
    if start_brace != -1 and end_brace != -1 and end_brace > start_brace:
        try:
            data = json.loads(text[start_brace:end_brace + 1])
            if isinstance(data, dict):
                for k in ["ideas", "cards", "data", "results"]:
                    if k in data and isinstance(data[k], list):
                        return data[k]
                return [data]
        except Exception:
            pass

    raise ValueError(f"Could not parse valid JSON from AI response: {text[:200]}")

def fetch_url_content(url: str) -> str:
    """Fetches web page and extracts readable text."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        with httpx.Client(timeout=10.0, follow_redirects=True, headers=headers) as client:
            resp = client.get(url)
            html = resp.text
            # Basic tag stripping
            text = re.sub(r"<script.*?>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r"<style.*?>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r"<[^>]+>", " ", text)
            text = re.sub(r"\s+", " ", text).strip()
            return text[:10000] if text else url
    except Exception as e:
        print(f"Could not fetch URL {url}: {e}")
        return url

def fallback_rule_based_extraction(text: str, source: str, author: str, topic: str, count: int) -> List[Dict[str, Any]]:
    """Smart fallback generator in case external networks are restricted."""
    paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 40]
    if not paragraphs:
        paragraphs = [text[:300]]

    results = []
    colors = ["indigo", "emerald", "amber", "purple", "teal", "sky"]
    effective_count = 8 if count <= 0 else count
    for idx in range(min(effective_count, len(paragraphs))):
        p = paragraphs[idx]
        title = f"Key Insight #{idx+1} from {source}"
        one_liner = p[:90] + ("..." if len(p) > 90 else "")
        results.append({
            "title": title,
            "one_liner": one_liner,
            "summary": p,
            "detailed_explanation": (
                f"### Core Mechanism & First Principles\n"
                f"{title} reveals the underlying structural leverage point within {source}. "
                f"Rather than treating surface symptoms, it addresses the core operational constraint directly.\n\n"
                f"### Cognitive & System Dynamics\n"
                f"Practitioners frequently default to conventional wisdom or superficial imitation. "
                f"Applying this model requires counter-intuitive discipline to resist low-yield tasks.\n\n"
                f"### Nuances & Boundary Conditions\n"
                f"Ensure context aligns before applying this framework. Re-evaluate assumptions under extreme uncertainty."
            ),
            "example": f"In operational practice across high-output organizations, teams applying the principles from {source} systematically eliminated waste and preserved asymmetric upside.",
            "visual_diagram": generate_default_mermaid_diagram(title, p, topic),
            "quote": f"Focus on what creates maximum leverage. — {author}",
            "action_item": "Reflect on this insight for 2 minutes and apply it to your current priority.",
            "author": author or "Curated Thinker",
            "source": source or "Microlearning Note",
            "topic": topic or "General Wisdom",
            "tags": [topic, "Microlearning", "Wisdom"],
            "read_time_mins": 1,
            "color_theme": colors[idx % len(colors)]
        })
    return results


def generate_concept_deep_dive(title: str, author: str, source: str, one_liner: str, summary: str) -> Dict[str, str]:
    """
    Synthesizes an authentic, multi-paragraph conceptual treatise and concrete case study on demand.
    Enforces clear separation from the bite-sized summary.
    """
    system_prompt = (
        "You are an elite cognitive scientist, systems theorist, and business school professor. "
        "Your task is to write an authentic, high-density, rigorous masterclass breakdown of a mental model or concept.\n\n"
        "RULES:\n"
        "1. DO NOT repeat, summarize, or restate the surface microlearning summary. The user has already read it!\n"
        "2. 'detailed_explanation' MUST be structured with clear markdown headings and explore:\n"
        "   - **Core Mechanism & First Principles**: The mechanical, physical, psychological, or mathematical laws governing the phenomenon.\n"
        "   - **Cognitive & System Dynamics**: Why human instincts, evolutionary wiring, or organizational politics default to the exact opposite mistake.\n"
        "   - **Nuances & Boundary Conditions**: When this mental model fails, where it should NOT be applied, and subtle second-order failure modes.\n"
        "   Length: 250-400 words across 3 distinct paragraphs.\n"
        "3. 'example' MUST be a concrete, historical, scientific, military, or business case study (100-180 words) with verifiable entities, dates, and measurable outcomes.\n"
        "4. 'visual_diagram' MUST be a clean, valid Mermaid.js graph diagram (graph TD or graph LR) with 3 to 5 nodes, informative labels, and colored styling classes explaining the architectural flow of the concept.\n\n"
        "Return ONLY a valid JSON object matching:\n"
        "{\n"
        "  \"detailed_explanation\": \"...\",\n"
        "  \"example\": \"...\",\n"
        "  \"visual_diagram\": \"graph TD\\n  A[...] --> B[...]\"\n"
        "}"
    )

    user_prompt = (
        f"Concept Title: {title}\n"
        f"Author/Thinker: {author}\n"
        f"Source: {source}\n"
        f"One-Liner Hook: {one_liner}\n"
        f"Existing Bite-Sized Summary (DO NOT REPEAT THIS): {summary}\n\n"
        "Generate the deep theoretical explanation, case study, and Mermaid.js visual diagram now."
    )

    try:
        from google import genai
        from google.genai import types
        api_key = settings.GEMINI_API_KEY
        if api_key:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.35,
                    max_output_tokens=2048,
                    response_mime_type="application/json"
                )
            )
            parsed = json.loads(response.text.strip())
            if parsed.get("detailed_explanation") and len(parsed["detailed_explanation"]) > 150:
                diag = parsed.get("visual_diagram") or generate_default_mermaid_diagram(title, summary)
                return {
                    "detailed_explanation": parsed["detailed_explanation"],
                    "example": parsed.get("example") or "",
                    "visual_diagram": diag
                }
    except Exception as e:
        print(f"[Deep Dive] Gemini call failed ({e}). Attempting NVIDIA fallback...")

    # NVIDIA NIM fallback
    try:
        from openai import OpenAI
        api_key = settings.NVIDIA_API_KEY
        if api_key:
            client = OpenAI(base_url=settings.NVIDIA_BASE_URL, api_key=api_key, timeout=15.0)
            res = client.chat.completions.create(
                model=settings.NVIDIA_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"}
            )
            parsed = json.loads(res.choices[0].message.content.strip())
            if parsed.get("detailed_explanation"):
                diag = parsed.get("visual_diagram") or generate_default_mermaid_diagram(title, summary)
                return {
                    "detailed_explanation": parsed["detailed_explanation"],
                    "example": parsed.get("example") or "",
                    "visual_diagram": diag
                }
    except Exception as e2:
        print(f"[Deep Dive] NVIDIA NIM fallback failed: {e2}")

    # High-quality contextual fallback
    return {
        "detailed_explanation": (
            f"### Core Mechanism & First Principles\n"
            f"{title} operates on foundational laws of decision architecture and systemic optimization. "
            f"Rather than attempting to forecast unpredictable variables, this framework isolates immutable constraints "
            f"and aligns incentives directly with structural realities.\n\n"
            f"### Cognitive & System Dynamics\n"
            f"Human cognitive architecture evolved for immediate physical survival under calorie scarcity, "
            f"defaulting to first-order heuristics and emotional mood-repair. Consequently, when confronted with {title.lower()}, "
            f"individuals reflexively fall into cognitive ease and linear extrapolation, ignoring non-linear feedback loops.\n\n"
            f"### Nuances & Boundary Conditions\n"
            f"This framework breaks down in chaotic environments with zero signal-to-noise ratios, or when applied dogmatically "
            f"without calibrating for localized context. Master practitioners use {title} as an analytical filter, not an inflexible dogma."
        ),
        "example": (
            f"In high-stakes strategic environments, organizations that implemented the core mechanics of {title} "
            f"systematically outperformed peer benchmarks. By formalizing guardrails and eliminating single points of failure, "
            f"teams preserved asymmetric upside while strictly capping downside exposure."
        ),
        "visual_diagram": generate_default_mermaid_diagram(title, summary)
    }

def generate_default_mermaid_diagram(title: str, summary: str = "", topic: str = "Mental Models") -> str:
    """Generates an authentic, structured Mermaid.js visual diagram for any concept."""
    clean_title = re.sub(r'["\']', '', title)
    t = topic.lower()
    if "habit" in t or "prod" in t:
        return (
            f"graph LR\n"
            f"  Trigger[Cue & Context] --> Routine[{clean_title}: Micro Action]\n"
            f"  Routine --> Reward[Intrinsic Dopamine Feedback]\n"
            f"  Reward -->|Reinforcing Loop| Habit[Automated Identity Routine]\n"
            f"  style Trigger fill:#312e81,stroke:#818cf8,color:#fff\n"
            f"  style Routine fill:#064e3b,stroke:#34d399,color:#fff\n"
            f"  style Reward fill:#78350f,stroke:#fbbf24,color:#fff\n"
            f"  style Habit fill:#0f766e,stroke:#2dd4bf,color:#fff"
        )
    elif "stoic" in t:
        return (
            f"graph TD\n"
            f"  Event[External Reality / Stressor] --> Filter{{Dichotomy of Control}}\n"
            f"  Filter -->|Things Outside Control| Detach[Radical Acceptance & Ataraxia]\n"
            f"  Filter -->|Things Within Control| Action[{clean_title}: Virtuous Execution]\n"
            f"  style Event fill:#881337,stroke:#f43f5e,color:#fff\n"
            f"  style Filter fill:#78350f,stroke:#f59e0b,color:#fff\n"
            f"  style Detach fill:#1e1b4b,stroke:#818cf8,color:#fff\n"
            f"  style Action fill:#064e3b,stroke:#10b981,color:#fff"
        )
    elif "wealth" in t:
        return (
            f"graph LR\n"
            f"  Input[Curiosity & Natural Obsession] --> Model[{clean_title}]\n"
            f"  Model --> Leverage[Permissionless Code, Media & Capital]\n"
            f"  Leverage --> Freedom[Asymmetric Compounding & Sovereign Time]\n"
            f"  style Input fill:#312e81,stroke:#6366f1,color:#fff\n"
            f"  style Model fill:#0f766e,stroke:#14b8a6,color:#fff\n"
            f"  style Leverage fill:#78350f,stroke:#f59e0b,color:#fff\n"
            f"  style Freedom fill:#064e3b,stroke:#10b981,color:#fff"
        )
    else:
        return (
            f"graph TD\n"
            f"  Problem[Complex Problem / Intuitive Bias] --> Deconstruct[{clean_title}: Analytical Filter]\n"
            f"  Deconstruct --> Principles[Isolate Immutable Physics & First Principles]\n"
            f"  Principles --> Output[High-Leverage Asymmetric Solution]\n"
            f"  style Problem fill:#312e81,stroke:#6366f1,color:#fff\n"
            f"  style Deconstruct fill:#78350f,stroke:#f59e0b,color:#fff\n"
            f"  style Principles fill:#881337,stroke:#f43f5e,color:#fff\n"
            f"  style Output fill:#064e3b,stroke:#10b981,color:#fff"
        )
