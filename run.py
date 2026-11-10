"""
Microstash Launcher Script
Checks environment, verifies dependencies, initializes SQLite, and launches the FastAPI server.
"""

import sys
import os
import socket
import webbrowser
import uvicorn
from app.config import settings
from app.database import init_db

def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0

def find_available_port(start_port: int, max_attempts: int = 10) -> int:
    port = start_port
    for _ in range(max_attempts):
        if not is_port_in_use(port):
            return port
        port += 1
    return start_port

def main():
    print("=" * 68)
    print("  ✨ MICROSTASH — Replace Doomscrolling with Microlearning! ✨")
    print("  Deepstash-inspired bite-sized ideas, mental models & AI curator")
    print("=" * 68)

    # Initialize SQLite Database & seed cards
    print("• Initializing SQLite Database...")
    init_db()
    print("• Database initialized & seeded with 20+ mental models.")

    target_port = find_available_port(settings.PORT)
    if target_port != settings.PORT:
        print(f"⚠️  Port {settings.PORT} is busy. Switched to port {target_port}.")

    local_url = f"http://localhost:{target_port}"
    print(f"  • Local Server URL:    {local_url}")
    print(f"  • API Documentation:   {local_url}/docs")
    print(f"  • AI Multi-Engine:     Gemini 3.5 Flash & NVIDIA NIM")
    print(f"  • Neural Audio TTS:    Edge-TTS + Browser SpeechSynthesis")
    print("=" * 68)
    print("  Press Ctrl+C to stop the server at any time.\n")

    # Run uvicorn server
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=target_port,
        reload=True
    )

if __name__ == "__main__":
    main()
