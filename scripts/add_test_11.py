test_func = '''

def test_substack_ecosystem():
    print("[TEST 11/11] Verifying Substack Ecosystem (Notes, Restacks, Reader, Subscriptions & Discussions)...")
    # 1. Test listing notes
    res_notes = client.get("/api/substack/notes")
    assert res_notes.status_code == 200
    notes = res_notes.json()
    assert len(notes) >= 4
    print(f"      [OK] Substack Notes feed verified ({len(notes)} notes).")

    # 2. Test posting a new note
    res_post_note = client.post("/api/substack/notes", json={
        "content": "First-principles thinking deconstructs problems to immutable physics.",
        "author_name": "Test Scholar",
        "author_handle": "scholar"
    })
    assert res_post_note.status_code == 200
    new_note = res_post_note.json()
    assert new_note["content"] == "First-principles thinking deconstructs problems to immutable physics."
    print("      [OK] Substack Note creation verified.")

    # 3. Test liking a note
    res_like = client.post(f"/api/substack/notes/{new_note['id']}/like")
    assert res_like.status_code == 200
    assert res_like.json()["is_liked"] is True
    print("      [OK] Note like reaction operational.")

    # 4. Test restacking an idea card to Notes
    res_restack = client.post("/api/substack/ideas/idea_inversion/restack", json={
        "comment": "Restacking this foundational principle for my team.",
        "author_name": "Test Curator",
        "author_handle": "curator"
    })
    assert res_restack.status_code == 200
    restack_data = res_restack.json()
    assert restack_data["referenced_idea_id"] == "idea_inversion"
    assert restack_data["restack_comment"] == "Restacking this foundational principle for my team."
    print("      [OK] Quote Restack of mental model to Notes verified.")

    # 5. Test Threaded Discussions / Comments
    res_comments = client.get("/api/substack/ideas/idea_inversion/comments")
    assert res_comments.status_code == 200
    comments = res_comments.json()
    assert len(comments) >= 1
    print(f"      [OK] Substack discussions retrieved ({len(comments)} comments).")

    res_add_comm = client.post("/api/substack/ideas/idea_inversion/comments", json={
        "comment_text": "Inversion saved our release schedule last Friday.",
        "user_name": "Verified Builder"
    })
    assert res_add_comm.status_code == 200
    assert res_add_comm.json()["comment_text"] == "Inversion saved our release schedule last Friday."
    print("      [OK] Comment submission to Substack discussion operational.")

    # 6. Test Subscriptions & Publications
    res_subs = client.post("/api/substack/subscribe", json={
        "target_type": "publication",
        "target_name": "The Mental Model Review"
    })
    assert res_subs.status_code == 200
    assert "subscribed" in res_subs.json()
    print("      [OK] 1-Click Substack publication subscription operational.")

    res_pubs = client.get("/api/substack/publications")
    assert res_pubs.status_code == 200
    pubs = res_pubs.json()
    assert len(pubs) >= 1
    print(f"      [OK] Featured Substack publications verified ({len(pubs)} available).")
'''

with open('c:/LLM/deepstash_microlearning/scripts/run_test_suite.py', 'r', encoding='utf-8') as f:
    code = f.read()

target = "if __name__ == '__main__':"
if target not in code:
    target = 'if __name__ == "__main__":'

code = code.replace(target, test_func + "\n\n" + target)
code = code.replace("test_social_learning_and_notifications()", "test_social_learning_and_notifications()\n        test_substack_ecosystem()")
code = code.replace("ALL 10/10 TEST SUITES", "ALL 11/11 TEST SUITES")

with open('c:/LLM/deepstash_microlearning/scripts/run_test_suite.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("test_substack_ecosystem appended cleanly to test suite!")
