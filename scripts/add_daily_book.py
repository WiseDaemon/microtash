#!/usr/bin/env python3
"""
Daily Book Ingestion CLI Script
Usage:
    python scripts/add_daily_book.py           # Adds today's book if not already added
    python scripts/add_daily_book.py --force   # Adds the next seminal book immediately
    python scripts/add_daily_book.py --status  # Checks current daily book status
"""
import sys
import argparse
from pathlib import Path

# Setup project root path
PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from app import database
from app.daily_scheduler import add_daily_book, get_daily_status

def main():
    parser = argparse.ArgumentParser(description="Microstash Daily Book Ingestion CLI")
    parser.add_argument("--force", action="store_true", help="Force addition of the next seminal book even if already added today")
    parser.add_argument("--status", action="store_true", help="Display current status of daily books on the platform")
    args = parser.parse_args()

    print("=" * 68)
    print("  📚 MICROSTASH — Automated Daily Book Ingestion 📚")
    print("=" * 68)

    status = get_daily_status()
    if args.status:
        print(f"  • Date:                     {status['today']}")
        print(f"  • Book Added Today:         {'YES' if status['already_added_today'] else 'NO'}")
        if status['today_book']:
            print(f"  • Today's Active Book:      \"{status['today_book']['book_title']}\" by {status['today_book']['author']}")
        print(f"  • Total Books on Platform:  {status['total_books_on_platform']}")
        print(f"  • Curated Backlog In Queue: {status['curated_queue_remaining']}")
        print(f"  • Next Book in Line:        {status['next_upcoming_book'] or 'None (All Curated Books Added)'}")
        print("=" * 68)
        return

    print(f"[*] Processing daily book drop for {status['today']}...")
    added, msg, data = add_daily_book(force=args.force)

    if added:
        book_info = data["book"] if "book" in data else data
        print(f"\n[SUCCESS] New book unlocked on platform!")
        print(f"  • Title:        {book_info.get('title')}")
        print(f"  • Author:       {book_info.get('author')}")
        print(f"  • Topic:        {book_info.get('topic')}")
        print(f"  • Atomic Models: {book_info.get('ideas_count', 0)}")
        print(f"  • Platform URL:  http://localhost:8000")
        print(f"  • Public Ngrok:  https://uncrown-washbowl-glucose.ngrok-free.dev")
    else:
        print(f"\n[INFO] {msg}")
        print(f"  (Tip: Pass --force to add another book immediately!)")

    print("=" * 68)

if __name__ == "__main__":
    main()
