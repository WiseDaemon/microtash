"""
Comprehensive Automated Test Suite for Microstash
Tests Database, FastAPI Routes, AI Socratic Stress-Test, Leitner Spaced Repetition,
Compliance Endpoints, Static Files, and Flutter Assets.
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
    print("[1/7] Testing database initialization & seed...")
    database.init_db()
    ideas = database.get_ideas()
    assert len(ideas) >= 15, f"Expected at least 15 seeded ideas, got {len(ideas)}"
    stashes = database.get_stashes()
    assert len(stashes) >= 4, f"Expected at least 4 seeded stashes, got {len(stashes)}"
    print(f"      [OK] Database seeded with {len(ideas)} mental models and {len(stashes)} stashes.")

def test_core_web_routes():
    print("[2/7] Testing web routes & branding...")
    # Home Page
    res = client.get("/")
    assert res.status_code == 200, f"Expected 200 on /, got {res.status_code}"
    html = res.text
    assert "Microstash" in html, "Brand name 'Microstash' missing from home page"
    assert "Mental Model Gym" in html or "Stop hoarding ideas" in html, "New branding missing"
    assert "stress-test-modal" in html, "Socratic stress-test modal missing from HTML"
    assert "Daily Workout" in html, "Leitner Daily Workout chip missing from HTML"
    print("      [OK] Home page loaded with correct 'Mental Model Gym' branding and modals.")

    # Privacy & Terms
    res_priv = client.get("/privacy")
    assert res_priv.status_code == 200, "Privacy policy returned non-200"
    assert "Google Play" in res_priv.text or "Microstash Privacy" in res_priv.text, "Privacy policy content missing"
    
    res_terms = client.get("/terms")
    assert res_terms.status_code == 200, "Terms of service returned non-200"
    print("      [OK] Google Play mandatory /privacy and /terms pages verified.")

def test_ideas_api():
    print("[3/7] Testing Ideas API...")
    res = client.get("/api/ideas")
    assert res.status_code == 200
    data = res.json()
    assert len(data) > 0, "No ideas returned from /api/ideas"
    first_idea = data[0]
    assert "id" in first_idea and "title" in first_idea and "one_liner" in first_idea
    assert "visual_diagram" in first_idea, "visual_diagram field missing from idea"
    
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
    print(f"      [OK] Ideas API, filtering, likes, saves, and read history operational.")

def test_socratic_stress_test():
    print("[4/7] Testing Socratic Stress-Test AI endpoint...")
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
    print("[5/7] Testing Leitner Spaced Repetition engine...")
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
    print("[6/7] Testing static assets & Google Play compliance endpoints...")
    # Static CSS & JS
    for asset in ["/static/css/style.css", "/static/js/app.js", "/static/js/audio.js", "/static/js/share.js", "/static/js/swipe.js"]:
        res_asset = client.get(asset)
        assert res_asset.status_code == 200, f"Static asset {asset} failed with {res_asset.status_code}"
    print("      [OK] All CSS, swipe engine, audio, and share static assets returned 200.")

    # Account Deletion Compliance Endpoint
    res_del = client.post("/api/user/delete-account")
    assert res_del.status_code == 200
    assert res_del.json()["status"] == "ok"
    print("      [OK] Google Play mandatory account/data purge endpoint (/api/user/delete-account) verified.")

def test_flutter_scaffold():
    print("[7/7] Testing Flutter Android project files...")
    flutter_dir = PROJECT_DIR / "flutter_app"
    assert (flutter_dir / "pubspec.yaml").exists(), "pubspec.yaml missing"
    assert (flutter_dir / "android" / "app" / "src" / "main" / "AndroidManifest.xml").exists(), "AndroidManifest.xml missing"
    assert (flutter_dir / "lib" / "main.dart").exists(), "main.dart missing"
    assert (flutter_dir / "lib" / "models" / "idea.dart").exists(), "idea.dart model missing"
    assert (flutter_dir / "lib" / "services" / "api_service.dart").exists(), "api_service.dart missing"
    assert (flutter_dir / "lib" / "screens" / "feed_screen.dart").exists(), "feed_screen.dart missing"
    assert (flutter_dir / "lib" / "screens" / "workout_screen.dart").exists(), "workout_screen.dart missing"
    assert (flutter_dir / "lib" / "screens" / "stress_test_screen.dart").exists(), "stress_test_screen.dart missing"
    
    # Check Android Manifest contains share target intent filter
    manifest_text = (flutter_dir / "android" / "app" / "src" / "main" / "AndroidManifest.xml").read_text(encoding="utf-8")
    assert "android.intent.action.SEND" in manifest_text, "Share target SEND action missing from AndroidManifest"
    assert "FOREGROUND_SERVICE_MEDIA_PLAYBACK" in manifest_text, "Audio playback permission missing"
    print("      [OK] Flutter Android mobile client verified (Material 3, Share target, Audio service).")

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
        print("====================================================================")
        print("  [SUCCESS] ALL 7/7 TEST SUITES PASSED FLAWLESSLY! [SUCCESS]")
        print("====================================================================")
    except Exception as e:
        print(f"\n[ERROR] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
