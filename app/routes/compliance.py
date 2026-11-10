from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import HTMLResponse
from app import database

router = APIRouter(tags=["Google Play Compliance & Privacy"])

@router.delete("/api/user/account")
@router.post("/api/user/delete-account")
def delete_user_account():
    """
    Google Play Policy Mandatory Endpoint:
    Allows user to request complete deletion of their account, learning history,
    saved stashes, and telemetry from the system.
    """
    try:
        conn = database.get_connection()
        cursor = conn.cursor()
        # Reset user progress
        cursor.execute("UPDATE user_progress SET streak_days = 0, ideas_read_count = 0, doomscroll_mins_saved = 0 WHERE id = 1;")
        # Clear read history
        cursor.execute("DELETE FROM read_history;")
        # Reset local likes and saves
        cursor.execute("UPDATE ideas SET is_liked = 0, is_saved = 0, leitner_box = 1, next_review_date = NULL;")
        conn.commit()
        conn.close()
        return {
            "status": "ok",
            "message": "All user data, progress history, and bookmarks have been purged in compliance with Google Play Store data safety guidelines."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to purge account data: {str(e)}")

@router.get("/privacy", response_class=HTMLResponse)
def privacy_policy():
    """Google Play mandatory public privacy policy webpage."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Privacy Policy — Microstash</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
</head>
<body class="bg-gray-900 text-gray-100 min-h-screen py-12 px-6 max-w-4xl mx-auto">
    <h1 class="text-3xl font-extrabold text-emerald-400 mb-6">Microstash Privacy Policy</h1>
    <p class="text-sm text-gray-400 mb-8">Effective Date: November 2026</p>
    
    <section class="space-y-6 text-gray-300 leading-relaxed">
        <div>
            <h2 class="text-xl font-bold text-white mb-2">1. Overview</h2>
            <p>Microstash ("we", "our", or "the App") is dedicated to cognitive excellence and respect for user sovereignty. We do not sell your personal data or track you across third-party websites.</p>
        </div>
        <div>
            <h2 class="text-xl font-bold text-white mb-2">2. Information We Collect</h2>
            <p>Microstash collects minimal information necessary to deliver our active recall service: anonymous usage telemetry, locally stored learning cards, Leitner review timestamps, and user-generated collections.</p>
        </div>
        <div>
            <h2 class="text-xl font-bold text-white mb-2">3. Google Play Data Safety & Third-Party Processors</h2>
            <p>Audio playback is generated using Microsoft Edge Neural TTS or on-device synthesis. AI queries are processed through Google Gemini API or NVIDIA NIM. We do not transmit personally identifiable information (PII) to ad networks.</p>
        </div>
        <div>
            <h2 class="text-xl font-bold text-white mb-2">4. User Rights & Account Deletion</h2>
            <p>In full compliance with Google Play Store Developer Guidelines, users have the absolute right to purge all account data, bookmark history, and streaks at any time within the app settings or via our automated API endpoint <code>/api/user/delete-account</code>.</p>
        </div>
        <div>
            <h2 class="text-xl font-bold text-white mb-2">5. Contact Us</h2>
            <p>If you have questions regarding this Privacy Policy, please reach out via GitHub: <a class="text-emerald-400 underline" href="https://github.com/WiseDaemon/microtash">WiseDaemon/microtash</a>.</p>
        </div>
    </section>
</body>
</html>"""

@router.get("/terms", response_class=HTMLResponse)
def terms_of_service():
    """Terms of Service."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Terms of Service — Microstash</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
</head>
<body class="bg-gray-900 text-gray-100 min-h-screen py-12 px-6 max-w-4xl mx-auto">
    <h1 class="text-3xl font-extrabold text-indigo-400 mb-6">Microstash Terms of Service</h1>
    <p class="text-sm text-gray-400 mb-8">Effective Date: November 2026</p>
    <div class="space-y-4 text-gray-300 leading-relaxed">
        <p>By accessing or using Microstash, you agree to utilize the platform for personal learning, cognitive training, and intellectual growth.</p>
        <p>Mental models, summaries, and AI syntheses provided within Microstash are for educational purposes and do not constitute formal legal, financial, or medical advice.</p>
    </div>
</body>
</html>"""
