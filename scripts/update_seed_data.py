import sqlite3
import json
import re

def update_seed_file():
    conn = sqlite3.connect('c:/LLM/deepstash_microlearning/data/microstash.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM ideas")
    db_ideas = {r["id"]: dict(r) for r in cur.fetchall()}
    conn.close()

    seed_path = 'c:/LLM/deepstash_microlearning/app/seed_data.py'
    with open(seed_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # We want to replace each idea dictionary in DEFAULT_IDEAS with the enriched data
    # Let's inspect which ideas exist in db_ideas and have enriched detailed_explanation
    enriched_count = 0
    for idea_id, data in db_ideas.items():
        if not data.get("boundary") and len(data.get("detailed_explanation") or "") < 1000:
            continue
        
        # Regex search for the idea block in seed_data.py
        # Match from "id": "{idea_id}" until the next item or end of dictionary
        pattern = re.compile(rf'(\{{\s*"id":\s*"{idea_id}".*?\n\s*\}})', re.DOTALL)
        match = pattern.search(content)
        if match:
            old_block = match.group(1)
            # Build new block with all updated fields
            # Parse tags
            tags_list = json.loads(data["tags"]) if isinstance(data["tags"], str) and data["tags"].startswith("[") else (data["tags"] or [])
            tags_repr = json.dumps(tags_list)
            
            # Escape strings safely for python dict
            def escape_str(s):
                if not s:
                    return '""'
                # Use triple quotes for multiline or long text
                if '\n' in s or len(s) > 100:
                    escaped = s.replace('\\', '\\\\').replace('"""', '\\"\\"\\"')
                    return f'"""{escaped}"""'
                else:
                    escaped = s.replace('\\', '\\\\').replace('"', '\\"')
                    return f'"{escaped}"'

            new_block = f'''{{
        "id": "{idea_id}",
        "title": {escape_str(data["title"])},
        "one_liner": {escape_str(data["one_liner"])},
        "summary": {escape_str(data["summary"])},
        "detailed_explanation": {escape_str(data["detailed_explanation"])},
        "example": {escape_str(data["example"])},
        "boundary": {escape_str(data.get("boundary") or "")},
        "visual_diagram": {escape_str(data.get("visual_diagram") or "")},
        "quote": {escape_str(data.get("quote") or "")},
        "action_item": {escape_str(data.get("action_item") or "")},
        "author": {escape_str(data.get("author") or "")},
        "source": {escape_str(data.get("source") or "")},
        "topic": {escape_str(data.get("topic") or "")},
        "tags": {tags_repr},
        "read_time_mins": {data.get("read_time_mins") or 2},
        "color_theme": "{data.get("color_theme") or "indigo"}",
        "likes": {data.get("likes") or 100},
        "saved_count": {data.get("saved_count") or 50}
    }}'''
            content = content[:match.start()] + new_block + content[match.end():]
            enriched_count += 1

    with open(seed_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Successfully updated {enriched_count} ideas in app/seed_data.py with masterclass treatises!")

if __name__ == "__main__":
    update_seed_file()
