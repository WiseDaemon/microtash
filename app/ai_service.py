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
    provider: str = "nvidia",
    num_ideas: int = 3
) -> List[Dict[str, Any]]:
    """
    Deconstructs raw text, article content, or a book chapter into structured Deepstash-style idea cards.
    Defaults to NVIDIA Nemotron 70B, falling back seamlessly to Gemini or rule-based synthesis.
    """
    # If input looks like an HTTP URL, attempt to scrape the main text
    cleaned_input = input_text.strip()
    if cleaned_input.startswith("http://") or cleaned_input.startswith("https://"):
        cleaned_input = fetch_url_content(cleaned_input)

    # Prompt design for atomic microlearning cards
    system_prompt = (
        "You are an expert editor and clear communicator for Microstash, a microlearning app that helps everyday readers learn and apply powerful ideas. "
        "Your mission is to pull out clear, practical, memorable ideas from the provided book or material.\n\n"
        "PLAIN-ENGLISH STYLE RULE:\n"
        "- Write in clear, natural, everyday English (8th-10th grade reading level). Avoid academic jargon, buzzwords, and overly formal phrasing.\n"
        "- Keep sentences punchy, direct, and vivid—explain big ideas simply without losing their depth or impact.\n\n"
        "CONTENT SEPARATION RULE:\n"
        "- 'summary' is a quick, punchy overview (50-80 words, 1-2 short paragraphs for fast reading).\n"
        "- 'detailed_explanation' MUST be a clear, practical deep dive (220-350 words, in 3 short sections) that does NOT repeat the summary:\n"
        "  1. How It Works (the core idea explained simply)\n"
        "  2. Why People Miss This (common mistakes our brains or teams naturally make)\n"
        "  3. When Not to Use It (the limits and exceptions to watch out for)\n"
        "- 'example' MUST be a concrete, real-world story (100-160 words) with specific people, companies, or events and clear results.\n\n"
        "Return ONLY a valid JSON array of objects with the exact following schema:\n"
        "[\n"
        "  {\n"
        "    \"title\": \"Punchy Headline Concept (e.g. The Two-Minute Rule)\",\n"
        "    \"one_liner\": \"Bold, memorable 1-sentence hook in plain English\",\n"
        "    \"summary\": \"Quick, clear overview (50-80 words).\",\n"
        "    \"detailed_explanation\": \"Clear, practical deep dive (220-350 words) across How It Works, Why People Miss This, and When Not to Use It. MUST NOT REPEAT THE SUMMARY.\",\n"
        "    \"example\": \"Concrete real-world story (100-160 words) with real people/companies and clear results.\",\n"
        "    \"visual_diagram\": \"Valid Mermaid.js graph code (e.g. graph TD or graph LR with 3-4 short, clear nodes) showing how the idea works.\",\n"
        "    \"quote\": \"Memorable quote or key line from the author.\",\n"
        "    \"action_item\": \"Simple 'Try it today' step the reader can do right away.\",\n"
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

    # Execution order based on provider preference & available keys
    # NVIDIA Nemotron is the primary AI engine
    prefer_nvidia = (provider.lower() == "nvidia") or (not settings.GEMINI_API_KEY and bool(settings.NVIDIA_API_KEY))

    if prefer_nvidia:
        try:
            return call_nvidia_api(system_prompt, user_prompt)
        except Exception as e:
            print(f"[AI Service] NVIDIA API call failed ({e}). Falling back to Gemini or rules...")
            if settings.GEMINI_API_KEY:
                try:
                    return call_gemini_api(system_prompt, user_prompt)
                except Exception as e_gemini:
                    print(f"[AI Service] Gemini fallback also failed ({e_gemini}).")
            return fallback_rule_based_extraction(cleaned_input, source_title, author, topic, num_ideas)
    else:
        try:
            if settings.GEMINI_API_KEY:
                return call_gemini_api(system_prompt, user_prompt)
            else:
                return call_nvidia_api(system_prompt, user_prompt)
        except Exception as e:
            print(f"[AI Service] Primary AI call failed ({e}). Falling back to NVIDIA...")
            try:
                if settings.NVIDIA_API_KEY:
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
        max_tokens=4096
    )

    text = (completion.choices[0].message.content or "").strip()
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
        "You are a gifted teacher who explains complex ideas in crystal-clear, everyday English. "
        "Your task is to write a helpful, engaging deep dive into a mental model so any reader can grasp it immediately without losing its full power.\n\n"
        "RULES:\n"
        "1. Write in plain, conversational English (8th-10th grade reading level). Avoid academic jargon, buzzwords, and stiff wording.\n"
        "2. DO NOT repeat or paraphrase the quick summary. Go deeper with fresh, concrete insight.\n"
        "3. 'detailed_explanation' MUST use clear markdown headings across 3 short sections:\n"
        "   - **How It Works**: The core logic explained simply and clearly.\n"
        "   - **Why We Get It Wrong**: Why our natural instincts or habits lead us into the opposite mistake.\n"
        "   - **When Not to Use It**: Real limits, exceptions, and when this rule can backfire.\n"
        "   Length: 220-350 words.\n"
        "4. 'example' MUST be a vivid, real-world story from history, business, or everyday life (100-160 words) with specific names and outcomes.\n"
        "5. 'visual_diagram' MUST be clean, valid Mermaid.js graph code (graph TD) with 3 to 5 short nodes explaining how the idea works.\n\n"
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

    # 1. Try NVIDIA Nemotron 70B (primary engine)
    if settings.NVIDIA_API_KEY:
        try:
            from openai import OpenAI
            client = OpenAI(base_url=settings.NVIDIA_BASE_URL, api_key=settings.NVIDIA_API_KEY, timeout=15.0)
            res = client.chat.completions.create(
                model=settings.NVIDIA_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"}
            )
            parsed = json.loads(res.choices[0].message.content.strip())
            if parsed.get("detailed_explanation") and len(parsed["detailed_explanation"]) > 100:
                diag = parsed.get("visual_diagram") or generate_default_mermaid_diagram(title, summary)
                return {
                    "detailed_explanation": parsed["detailed_explanation"],
                    "example": parsed.get("example") or "",
                    "visual_diagram": diag
                }
        except Exception as e_nv:
            print(f"[Deep Dive] NVIDIA call failed ({e_nv}). Attempting Gemini fallback...")

    # 2. Try Gemini fallback if configured
    if settings.GEMINI_API_KEY:
        try:
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
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
            if parsed.get("detailed_explanation") and len(parsed["detailed_explanation"]) > 100:
                diag = parsed.get("visual_diagram") or generate_default_mermaid_diagram(title, summary)
                return {
                    "detailed_explanation": parsed["detailed_explanation"],
                    "example": parsed.get("example") or "",
                    "visual_diagram": diag
                }
        except Exception as e:
            print(f"[Deep Dive] Gemini call failed ({e}).")

    # High-quality contextual fallback
    return {
        "detailed_explanation": (
            f"### How It Works\n"
            f"{title} works by focusing on what actually moves the needle instead of trying to predict every detail. "
            f"Rather than guessing the future, it helps you spot the few real constraints that control the outcome.\n\n"
            f"### Why We Get It Wrong\n"
            f"Our brains are wired for quick survival, not careful long-term thinking. Under stress or time pressure, "
            f"we naturally fall back on gut feelings, habit, and short-term comfort instead of stepping back to see the bigger picture.\n\n"
            f"### When Not to Use It\n"
            f"This approach can backfire in completely unpredictable situations or if followed like a rigid rule without "
            f"paying attention to what is happening right in front of you. Use {title} as a helpful lens, not a strict dogma."
        ),
        "example": (
            f"In high-pressure situations, teams and leaders who applied {title} consistently outperformed those who relied on guesswork. "
            f"By setting clear guardrails and fixing weak spots early, they protected their downside while leaving plenty of room for big wins."
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


def generate_socratic_stress_test(title: str, summary: str, detailed_explanation: str = "", author: str = "") -> Dict[str, Any]:
    """
    Synthesizes a realistic high-stakes scenario dilemma that tests the user's ability
    to correctly apply the mental model versus falling into a common cognitive trap.
    """
    prompt = (
        f"You are a friendly, practical coach at Microstash. "
        f"Create a relatable, everyday work or life scenario to test whether someone knows how to apply '{title}' in plain English.\n\n"
        f"Summary of Concept: {summary}\n"
        f"Context/Details: {detailed_explanation[:300] if detailed_explanation else 'N/A'}\n\n"
        f"STYLE RULE: Write in simple, clear, everyday English (no academic jargon or buzzwords).\n\n"
        f"Return ONLY a valid JSON object with this exact structure:\n"
        f"{{\n"
        f"  \"scenario\": \"A clear, relatable work or life situation (60-100 words) presenting a real choice.\",\n"
        f"  \"question\": \"Using {title}, what is the smartest next move?\",\n"
        f"  \"options\": [\n"
        f"    {{\n"
        f"      \"id\": \"A\",\n"
        f"      \"text\": \"A common knee-jerk reaction or intuitive mistake.\",\n"
        f"      \"is_correct\": false,\n"
        f"      \"feedback\": \"Why this backfires: explains the trap in simple terms.\"\n"
        f"    }},\n"
        f"    {{\n"
        f"      \"id\": \"B\",\n"
        f"      \"text\": \"The smart, practical choice that applies {title}.\",\n"
        f"      \"is_correct\": true,\n"
        f"      \"feedback\": \"Spot on! Explains clearly why {title} works best here.\"\n"
        f"    }},\n"
        f"    {{\n"
        f"      \"id\": \"C\",\n"
        f"      \"text\": \"A middle-ground compromise that misses the point.\",\n"
        f"      \"is_correct\": false,\n"
        f"      \"feedback\": \"Why splitting the difference leads to a weak result here.\"\n"
        f"    }}\n"
        f"  ],\n"
        f"  \"first_principles_takeaway\": \"One punchy, memorable 1-sentence rule of thumb.\"\n"
        f"}}"
    )

    # 1. Primary Engine: NVIDIA Nemotron 70B
    if settings.NVIDIA_API_KEY:
        try:
            from openai import OpenAI
            client = OpenAI(
                base_url=settings.NVIDIA_BASE_URL,
                api_key=settings.NVIDIA_API_KEY,
                timeout=15.0
            )
            completion = client.chat.completions.create(
                model=settings.NVIDIA_MODEL,
                messages=[
                    {"role": "system", "content": "You are a cognitive psychologist and Socratic trainer. Output strictly valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.35,
                max_tokens=3000
            )
            text_resp = (completion.choices[0].message.content or "").strip()
            parsed = parse_json_safely(text_resp)
            if isinstance(parsed, list) and len(parsed) > 0:
                return parsed[0]
            elif isinstance(parsed, dict) and "scenario" in parsed:
                return parsed
        except Exception as e_nv:
            print(f"[Socratic] NVIDIA Nemotron call failed ({e_nv}). Attempting fallback...")

    # 2. Secondary fallback: Gemini
    if settings.GEMINI_API_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
            payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.4}}
            with httpx.Client(timeout=20.0) as client:
                resp = client.post(url, json=payload)
                if resp.status_code == 200:
                    text_resp = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                    parsed = parse_json_safely(text_resp)
                    if isinstance(parsed, list) and len(parsed) > 0:
                        return parsed[0]
                    elif isinstance(parsed, dict):
                        return parsed
        except Exception as e:
            print(f"Gemini Socratic stress-test failed, falling back: {e}")

    return {
        "scenario": (
            f"Your team is facing a tough, messy decision with competing priorities and a tight deadline. "
            f"Everyone is pushing to move fast based on gut instinct, even though several warning signs are popping up. "
            f"How do you use '{title}' to handle the uncertainty?"
        ),
        "question": f"Using {title}, what is the smartest next step?",
        "options": [
            {
                "id": "A",
                "text": "Rush forward right away to see what happens, ignoring the warning signs for now.",
                "is_correct": False,
                "feedback": f"Trap: Jumping into action without checking the real risks goes against the core lesson of {title}."
            },
            {
                "id": "B",
                "text": f"Strip the problem down to the basic facts, fix the biggest weak spots first, and focus on the 20% of actions that drive 80% of the result.",
                "is_correct": True,
                "feedback": f"Spot on! You're using {title} to cut through the noise and focus on what actually matters."
            },
            {
                "id": "C",
                "text": "Call a meeting to split the budget and time evenly across everyone's favorite ideas.",
                "is_correct": False,
                "feedback": "Trap: Trying to please everyone usually dilutes your focus and leads to weak results."
            }
        ],
        "first_principles_takeaway": f"When things feel uncertain, use {title} to protect against big mistakes first, then focus on what works best."
    }
