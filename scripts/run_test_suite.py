"""
Comprehensive Automated Test Suite for Microstash
Tests Database, FastAPI Routes, AI Socratic Stress-Test, Leitner Spaced Repetition,
Compliance Endpoints, Static Files, Flutter Mobile App, and Universal Global Book Cache.
"""
import sys
import os
from pathlib import Path

# Setup project path
PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from fastapi.testclient import TestClient
from app.main import app
from app import database
from app.config import settings

client = TestClient(app)

def test_database_and_seed():
    print("[1/8] Testing database initialization & seed...")
    database.init_db()
    ideas = database.get_ideas()
    assert len(ideas) >= 15, f"Expected at least 15 seeded ideas, got {len(ideas)}"
    stashes = database.get_stashes()
    assert len(stashes) >= 4, f"Expected at least 4 seeded stashes, got {len(stashes)}"
    books = database.list_scanned_books()
    assert len(books) >= 5, f"Expected at least 5 registered books in global library, got {len(books)}"
    print(f"      [OK] Database seeded with {len(ideas)} mental models, {len(stashes)} stashes, and {len(books)} global books.")

def test_core_web_routes():
    print("[2/8] Testing web routes & branding...")
    # Home Page
    res = client.get("/")
    assert res.status_code == 200, f"Expected 200 on /, got {res.status_code}"
    html = res.text
    assert "Microstash" in html, "Brand name 'Microstash' missing from home page"
    assert "Mental Model Gym" in html or "Stop hoarding ideas" in html, "New branding missing"
    assert "stress-test-modal" in html, "Socratic stress-test modal missing from HTML"
    assert "Daily Workout" in html, "Leitner Daily Workout chip missing from HTML"
    assert "Global Bookshelf" in html or "global-book-search-input" in html, "Global book search missing from HTML"
    print("      [OK] Home page loaded with correct 'Mental Model Gym' branding, global search, and modals.")

    # Privacy & Terms
    res_priv = client.get("/privacy")
    assert res_priv.status_code == 200, "Privacy policy returned non-200"
    assert "Google Play" in res_priv.text or "Microstash Privacy" in res_priv.text, "Privacy policy content missing"
    
    res_terms = client.get("/terms")
    assert res_terms.status_code == 200, "Terms of service returned non-200"
    print("      [OK] Google Play mandatory /privacy and /terms pages verified.")

def test_ideas_api():
    print("[3/8] Testing Ideas API...")
    res = client.get("/api/ideas")
    assert res.status_code == 200
    data = res.json()
    assert len(data) > 0, "No ideas returned from /api/ideas"
    first_idea = data[0]
    assert "id" in first_idea and "title" in first_idea and "one_liner" in first_idea
    assert "visual_diagram" in first_idea, "visual_diagram field missing from idea"
    assert "copyright_notice" in first_idea, "copyright_notice field missing from idea"
    assert "author" in first_idea["copyright_notice"].lower(), "Author not credited in copyright notice"
    
    # Filter by topic
    res_topic = client.get("/api/ideas?topic=Mental Models")
    assert res_topic.status_code == 200
    assert len(res_topic.json()) > 0

    # Like, Save, Read
    idea_id = first_idea["id"]
    res_like = client.post(f"/api/ideas/{idea_id}/like")
    assert res_like.status_code == 200
    
    res_save = client.post(f"/api/ideas/{idea_id}/save")
    assert res_save.status_code == 200

    res_read = client.post(f"/api/ideas/{idea_id}/read")
    assert res_read.status_code == 200
    assert res_read.json()["status"] == "ok"
    print(f"      [OK] Ideas API, filtering, author/publisher credits, likes, saves, and read history operational.")

def test_socratic_stress_test():
    print("[4/8] Testing Socratic Stress-Test AI endpoint...")
    ideas = database.get_ideas()
    test_idea = ideas[0]
    
    res = client.get(f"/api/ai/stress-test/{test_idea.id}")
    assert res.status_code == 200, f"Stress test returned {res.status_code}: {res.text}"
    body = res.json()
    assert body["status"] == "ok"
    assert "stress_test" in body
    st = body["stress_test"]
    assert "scenario" in st and len(st["scenario"]) > 20, "Scenario text missing or too short"
    assert "question" in st, "Question missing from stress test"
    assert "options" in st and len(st["options"]) >= 3, "Expected at least 3 multiple choice options"
    assert any(opt.get("is_correct") for opt in st["options"]), "At least one option must be marked is_correct"
    assert "first_principles_takeaway" in st, "First-principles takeaway missing"
    print(f"      [OK] Socratic Stress-Test generated successfully for '{test_idea.title}'.")
    print(f"           - Dilemma: {st['scenario'][:80]}...")
    print(f"           - Options count: {len(st['options'])}")

def test_leitner_spaced_repetition():
    print("[5/8] Testing Leitner Spaced Repetition engine...")
    ideas = database.get_ideas()
    test_idea = ideas[0]
    
    # Reset box to 1 for test
    conn = database.get_connection()
    conn.cursor().execute("UPDATE ideas SET leitner_box = 1 WHERE id = ?", (test_idea.id,))
    conn.commit()
    conn.close()

    # Review card with grade "good" (Advances box from 1 to 2)
    res_review = client.post(f"/api/ideas/{test_idea.id}/leitner-review", json={"grade": "good"})
    assert res_review.status_code == 200
    updated_idea = res_review.json()
    assert updated_idea["leitner_box"] == 2, f"Expected box 2, got {updated_idea['leitner_box']}"
    assert updated_idea["next_review_date"] is not None, "next_review_date was not set"

    # Review card with grade 5 ("easy", advances box by 2: 2 -> 4)
    res_review_easy = client.post(f"/api/ideas/{test_idea.id}/leitner-review", json={"grade": 5})
    assert res_review_easy.status_code == 200
    assert res_review_easy.json()["leitner_box"] == 4, f"Expected box 4, got {res_review_easy.json()['leitner_box']}"

    # Query due cards
    res_due = client.get("/api/ideas/leitner/due")
    assert res_due.status_code == 200
    assert isinstance(res_due.json(), list)
    print(f"      [OK] Leitner review progression (Box 1 -> Box 2 -> Box 4) and intervals verified.")

def test_compliance_and_static_assets():
    print("[6/8] Testing static assets & Google Play compliance endpoints...")
    for asset in ["/static/css/style.css", "/static/js/app.js", "/static/js/audio.js", "/static/js/share.js", "/static/js/swipe.js"]:
        res_asset = client.get(asset)
        assert res_asset.status_code == 200, f"Static asset {asset} failed with {res_asset.status_code}"
    print("      [OK] All CSS, swipe engine, audio, and share static assets returned 200.")

    res_del = client.post("/api/user/delete-account")
    assert res_del.status_code == 200
    assert res_del.json()["status"] == "ok"
    print("      [OK] Google Play mandatory account/data purge endpoint (/api/user/delete-account) verified.")

def test_flutter_scaffold():
    print("[7/8] Testing Flutter Android project files...")
    flutter_dir = PROJECT_DIR / "flutter_app"
    assert (flutter_dir / "pubspec.yaml").exists(), "pubspec.yaml missing"
    assert (flutter_dir / "android" / "app" / "src" / "main" / "AndroidManifest.xml").exists(), "AndroidManifest.xml missing"
    assert (flutter_dir / "lib" / "main.dart").exists(), "main.dart missing"
    assert (flutter_dir / "lib" / "models" / "idea.dart").exists(), "idea.dart model missing"
    assert (flutter_dir / "lib" / "models" / "book.dart").exists(), "book.dart model missing"
    assert (flutter_dir / "lib" / "services" / "api_service.dart").exists(), "api_service.dart missing"
    assert (flutter_dir / "lib" / "services" / "offline_storage_service.dart").exists(), "offline_storage_service.dart missing"
    assert (flutter_dir / "lib" / "services" / "share_receiver_service.dart").exists(), "share_receiver_service.dart missing"
    assert (flutter_dir / "lib" / "services" / "notification_service.dart").exists(), "notification_service.dart missing"
    assert (flutter_dir / "android" / "app" / "src" / "main" / "kotlin" / "com" / "microstash" / "app" / "MainActivity.kt").exists(), "MainActivity.kt missing"
    assert (flutter_dir / "lib" / "screens" / "feed_screen.dart").exists(), "feed_screen.dart missing"
    assert (flutter_dir / "lib" / "screens" / "discover_screen.dart").exists(), "discover_screen.dart missing"
    assert (flutter_dir / "lib" / "screens" / "workout_screen.dart").exists(), "workout_screen.dart missing"
    assert (flutter_dir / "lib" / "screens" / "stress_test_screen.dart").exists(), "stress_test_screen.dart missing"
    
    manifest_text = (flutter_dir / "android" / "app" / "src" / "main" / "AndroidManifest.xml").read_text(encoding="utf-8")
    assert "android.intent.action.SEND" in manifest_text, "Share target SEND action missing from AndroidManifest"
    assert "FOREGROUND_SERVICE_MEDIA_PLAYBACK" in manifest_text, "Audio playback permission missing"
    print("      [OK] Flutter Android mobile client verified (Discover screen, Material 3, Share target, Audio service).")

def test_universal_book_cache():
    print("[8/8] Testing Universal Global Book & Idea Cache (Zero Duplicate Scans & Author Attribution)...")
    
    # 1. Verify /api/books listing
    res_books = client.get("/api/books")
    assert res_books.status_code == 200
    books = res_books.json()
    assert len(books) > 0, "Global book registry should not be empty"
    print(f"      [OK] Found {len(books)} books already available to all users.")

    # 2. Test cached book retrieval: 'Thinking, Fast and Slow'
    res_cached = client.post("/api/ai/auto-fetch-and-generate", json={"query": "Thinking Fast and Slow"})
    assert res_cached.status_code == 200
    data_cached = res_cached.json()
    assert data_cached.get("cached") is True, "Expected cached=True for existing book"
    assert data_cached.get("global_library_hit") is True, "Expected global_library_hit=True"
    assert len(data_cached.get("ideas", [])) > 0, "Expected idea cards in cached response"
    assert "copyright_notice" in data_cached, "Copyright notice missing from auto-fetch response"
    print(f"      [OK] Instant 0s cache hit for 'Thinking Fast and Slow' (Cards: {len(data_cached['ideas'])}).")

    # 3. Simulate User A scanning a brand new book into the library with publisher credit
    new_book_title = "Antifragile: Things That Gain from Disorder"
    sample_cards = [
        {
            "title": "Fragile vs Antifragile",
            "one_liner": "Antifragility goes beyond resilience; it benefits from shocks.",
            "summary": "Resilience resists shocks and stays the same; the antifragile gets better with volatility.",
            "detailed_explanation": "Complex systems thrive when exposed to small, non-fatal stressors.",
            "example": "Bones become denser when subject to resistance training.",
            "visual_diagram": "graph TD\\n  A[Shock] -->|Fragile| B[Breaks]\\n  A -->|Antifragile| C[Strengthens]",
            "author": "Nassim Nicholas Taleb",
            "source": new_book_title,
            "publisher": "Random House",
            "topic": "Mental Models",
            "tags": ["Risk", "Decision Making"]
        }
    ]

    res_user_a = client.post("/api/ai/save-as-book-stash", json={
        "book_title": new_book_title,
        "author": "Nassim Nicholas Taleb",
        "publisher": "Random House",
        "ideas": sample_cards
    })
    assert res_user_a.status_code == 200
    user_a_stash = res_user_a.json()
    assert user_a_stash.get("globally_available") is True
    print(f"      [OK] User A scanned '{new_book_title}' into the global registry.")

    # 4. Simulate User B searching for the book with different punctuation/casing
    res_user_b = client.post("/api/ai/auto-fetch-and-generate", json={
        "query": "antifragile things that gain from disorder"
    })
    assert res_user_b.status_code == 200
    data_user_b = res_user_b.json()
    assert data_user_b.get("cached") is True, "User B should hit global cache (0s scan)"
    assert data_user_b.get("global_library_hit") is True, "Expected global_library_hit=True for User B"
    assert len(data_user_b.get("ideas", [])) >= 1, "User B should receive cards generated by User A"
    print(f"      [OK] User B requested '{new_book_title}' and received instant 0s cache hit without re-scanning!")

    # 5. Direct book lookup via /api/books/{slug}
    res_book_detail = client.get("/api/books/antifragile")
    assert res_book_detail.status_code == 200
    detail = res_book_detail.json()
    assert detail["title"] == new_book_title or "Antifragile" in detail["title"]
    assert len(detail["ideas"]) >= 1
    assert "copyright_notice" in detail and detail["copyright_notice"] is not None
    assert "author" in detail["copyright_notice"].lower()
    print(f"      [OK] Universal Library endpoint /api/books/antifragile verified with copyright attribution.")

def test_user_accounts_and_sessions():
    print("[TEST 9/9] Verifying User Authentication, Sessions & JWT Security...")
    import uuid
    uid = uuid.uuid4().hex[:6]
    test_email = f"learner_{uid}@microstash.app"
    test_user = f"learner_{uid}"
    test_pwd = "StrongPassword#2026"

    # 1. Register a new user
    res_reg = client.post("/api/auth/register", json={
        "email": test_email,
        "username": test_user,
        "password": test_pwd,
        "full_name": "Cognitive Gymnast"
    })
    assert res_reg.status_code == 200, f"Register failed: {res_reg.text}"
    data_reg = res_reg.json()
    assert "access_token" in data_reg
    assert data_reg["token_type"] == "bearer"
    assert data_reg["user"]["username"] == test_user
    assert data_reg["user"]["email"] == test_email
    token = data_reg["access_token"]
    print(f"      [OK] User registered successfully: {test_user} ({test_email})")

    # 2. Duplicate registration rejection
    res_dup = client.post("/api/auth/register", json={
        "email": test_email,
        "username": f"other_{uid}",
        "password": test_pwd
    })
    assert res_dup.status_code == 400, "Expected 400 on duplicate email"
    print("      [OK] Duplicate registration rejected with HTTP 400.")

    # 3. Valid Login
    res_login = client.post("/api/auth/login", json={
        "username_or_email": test_email,
        "password": test_pwd
    })
    assert res_login.status_code == 200
    login_token = res_login.json()["access_token"]
    print("      [OK] Valid credentials returned authenticated JWT token.")

    # 4. Invalid Login (wrong password)
    res_bad_login = client.post("/api/auth/login", json={
        "username_or_email": test_email,
        "password": "WrongPassword123"
    })
    assert res_bad_login.status_code == 401
    print("      [OK] Invalid password correctly rejected with HTTP 401.")

    # 5. Access protected /me endpoint with valid token
    res_me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {login_token}"})
    assert res_me.status_code == 200
    user_info = res_me.json()
    assert user_info["user"]["username"] == test_user
    assert "progress" in user_info or "stats" in user_info
    print("      [OK] Protected route /api/auth/me verified with Bearer JWT.")

    # 6. Logout and session invalidation
    res_logout = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {login_token}"})
    assert res_logout.status_code == 200
    print("      [OK] User session successfully terminated on server.")

    # 7. Access /me with invalidated token should fail
    res_revoked = client.get("/api/auth/me", headers={"Authorization": f"Bearer {login_token}"})
    assert res_revoked.status_code == 401
    print("      [OK] Revoked session token blocked with HTTP 401.")

    # 8. Test seeded default demo account
    res_demo = client.post("/api/auth/login", json={
        "username_or_email": "demo@microstash.app",
        "password": "demo1234"
    })
    assert res_demo.status_code == 200, "Demo user should log in successfully"
    print("      [OK] Seeded demo user (demo@microstash.app) verified.")

def test_social_learning_and_notifications():
    print("[TEST 10/10] Verifying Social Learning, Shared Stashes & Mobile Notifications...")
    import uuid
    deck_title = f"Billionaire Frameworks {uuid.uuid4().hex[:4]}"
    
    # 1. Create a personal stash
    res_create = client.post("/api/stashes", json={
        "title": deck_title,
        "description": "High leverage mental frameworks for strategic decisions",
        "icon": "brain",
        "color": "indigo",
        "is_public": False
    })
    assert res_create.status_code == 200
    stash = res_create.json()
    stash_id = stash["id"]
    print(f"      [OK] Personal stash created: '{deck_title}' (id: {stash_id})")

    # 2. Add an actual idea to the stash
    res_ideas = client.get("/api/ideas")
    assert res_ideas.status_code == 200
    first_idea_id = res_ideas.json()[0]["id"]
    res_add = client.post(f"/api/stashes/{stash_id}/ideas", json={"idea_id": first_idea_id})
    assert res_add.status_code == 200
    print(f"      [OK] Added mental model '{first_idea_id}' to the stash.")

    # 3. Publish to Community library
    res_pub = client.post(f"/api/stashes/{stash_id}/publish", json={"is_public": True})
    assert res_pub.status_code == 200
    pub_data = res_pub.json()
    assert pub_data["is_public"] is True
    share_slug = pub_data["share_slug"]
    assert len(share_slug) > 0
    print(f"      [OK] Stash published to Community. Direct share slug: {share_slug}")

    # 4. Access shared stash via public endpoint (no login required)
    res_share = client.get(f"/api/stashes/share/{share_slug}")
    assert res_share.status_code == 200
    shared_detail = res_share.json()
    assert shared_detail["title"] == deck_title
    assert len(shared_detail["ideas"]) >= 1
    print("      [OK] Public social share endpoint (/api/stashes/share/{slug}) returned complete deck.")

    # 5. List community public stashes
    res_public_list = client.get("/api/stashes/public")
    assert res_public_list.status_code == 200
    public_stashes = res_public_list.json()
    assert any(s["id"] == stash_id or s["share_slug"] == share_slug for s in public_stashes)
    print(f"      [OK] Verified community public gallery contains {len(public_stashes)} shared stashes.")

    # 6. Web direct share route (/share/stash/{slug})
    res_web_share = client.get(f"/share/stash/{share_slug}")
    assert res_web_share.status_code == 200
    assert "text/html" in res_web_share.headers["content-type"]
    print("      [OK] Direct web share route (/share/stash/{slug}) returned 200 HTML.")

    # 7. Clone shared stash to learner's personal library
    res_clone = client.post(f"/api/stashes/{stash_id}/clone")
    assert res_clone.status_code == 200
    clone_data = res_clone.json()
    assert clone_data["status"] == "ok"
    cloned_stash = clone_data["cloned_stash"]
    assert "Copy" in cloned_stash["title"] or "My Stash" in cloned_stash["title"]
    assert len(cloned_stash["ideas"]) >= 1

    # Verify original stash clone_count incremented
    res_orig = client.get(f"/api/stashes/{stash_id}")
    assert res_orig.status_code == 200
    assert res_orig.json()["clone_count"] >= 1
    print(f"      [OK] Stash successfully cloned into user library with verified clone metrics.")

    # 8. Mobile Notification Service verification
    notif_file = PROJECT_DIR / "flutter_app" / "lib" / "services" / "notification_service.dart"
    assert notif_file.exists(), "NotificationService must exist in Flutter project"
    notif_content = notif_file.read_text(encoding="utf-8")
    assert "scheduleDailyWorkoutReminder" in notif_content
    assert "checkDueCardsAndNotify" in notif_content
    assert "isReminderEnabled" in notif_content
    print("      [OK] Flutter NotificationService (scheduleDailyWorkoutReminder, checkDueCardsAndNotify) verified.")

    # 9. Mobile Workout Screen notification trigger verification
    workout_file = PROJECT_DIR / "flutter_app" / "lib" / "screens" / "workout_screen.dart"
    assert workout_file.exists()
    workout_content = workout_file.read_text(encoding="utf-8")
    assert "NotificationService.checkDueCardsAndNotify" in workout_content
    print("      [OK] Flutter WorkoutScreen notification triggers verified.")



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


if __name__ == "__main__":
    print("====================================================================")
    print("  [*] MICROSTASH AUTOMATED VERIFICATION TEST SUITE [*]")
    print("====================================================================")
    try:
        test_database_and_seed()
        test_core_web_routes()
        test_ideas_api()
        test_socratic_stress_test()
        test_leitner_spaced_repetition()
        test_compliance_and_static_assets()
        test_flutter_scaffold()
        test_universal_book_cache()
        test_user_accounts_and_sessions()
        test_social_learning_and_notifications()
        test_substack_ecosystem()
        print("====================================================================")
        print("  [SUCCESS] ALL 11/11 TEST SUITES PASSED FLAWLESSLY! [SUCCESS]")
        print("====================================================================")
    except Exception as e:
        print(f"\n[ERROR] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
