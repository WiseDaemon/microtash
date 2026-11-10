"""
Microstash App Launcher
Single-command startup script for Deepstash microlearning application.
"""
import os
import sys
import socket
import webbrowser
import uvicorn
from pathlib import Path

# Add current folder to sys.path so app module is discoverable
APP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(APP_DIR))

from app.config import settings

def find_available_port(starting_port=8000, max_attempts=20):
    for port in range(starting_port, starting_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', port)) != 0:
                return port
    return starting_port

def print_banner(port):
    print("=" * 68)
    print("  ✨ MICROSTASH — Replace Doomscrolling with Microlearning! ✨")
    print("  Deepstash-inspired bite-sized ideas, mental models & AI curator")
    print("=" * 68)
    print(f"  • Local Server URL:    http://localhost:{port}")
    print(f"  • API Documentation:   http://localhost:{port}/docs")
    print(f"  • AI Multi-Engine:     Gemini 3.5 Flash & NVIDIA NIM")
    print(f"  • Neural Audio TTS:    Edge-TTS + Browser SpeechSynthesis")
    print("=" * 68)
    print("  Press Ctrl+C to stop the server at any time.\n")

if __name__ == "__main__":
    port = find_available_port(settings.PORT)
    print_banner(port)
    
    # Launch browser after slight delay
    def open_browser():
        import time
        time.sleep(1.2)
        try:
            webbrowser.open(f"http://localhost:{port}")
        except Exception:
            pass

    import threading
    threading.Thread(target=open_browser, daemon=True).start()

    uvicorn.run("app.main:app", host="127.0.0.1", port=port, reload=True, log_level="info")
