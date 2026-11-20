"""
Daily Book Ingestion Engine & Automated Scheduler
Automatically introduces 1 high-leverage seminal book with atomic mental model cards,
first-principles breakdowns, causal Mermaid diagrams, and operational protocols every day.
"""
import sys
import os
import time
import json
import logging
import threading
from datetime import datetime, date
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from app import database
from app.database import get_connection, slugify, generate_copyright_attribution

logger = logging.getLogger("microstash.daily_scheduler")

# Curated queue of seminal mental model & strategy books
CURATED_DAILY_BOOKS = [
    {
        "title": "Thinking in Bets",
        "author": "Annie Duke",
        "publisher": "Portfolio / Penguin",
        "topic": "Decision Making",
        "description": "Making smarter decisions when you don't have all the facts. Distinguishing decision quality from resulting outcome luck.",
        "ideas": [
            {
                "title": "The Resulting Fallacy (Outcome Bias)",
                "one_liner": "Never judge the quality of a decision solely by its outcome.",
                "summary": "In probabilistic environments, brilliant decisions can yield catastrophic results through bad luck, while reckless gambles can produce windfalls through variance. Equating outcome with process creates fragile learning loops.",
                "detailed_explanation": "Epistemological Separation of Process and Luck:\nIn complex, non-deterministic domains (investing, entrepreneurship, medicine), the relationship between decision quality and outcome is mediated by probabilistic variance. The human mind naturally executes 'resulting'—retroactively judging the soundness of a past choice purely by whether the result was favorable.\n\nWhen a reckless startup founder takes an existential 10x leverage gamble and gets lucky, resulting crowns them a genius, reinforcing lethal habits. Conversely, when an executive makes a mathematically pristine +EV bet with 80% success odds and hits the 20% downside tail, resulting punishes the architect. To build antifragile judgment, teams must decouple outcome evaluation from decision audit.",
                "example": "In Super Bowl XLIX (2015), Seattle Seahawks coach Pete Carroll called a pass play from the 1-yard line with 26 seconds left instead of handing off to Marshawn Lynch. The pass was intercepted, losing the game. Carroll was universally condemned by sports media for 'the worst call in football history.' However, statistical analysis showed that across the entire NFL season, passes from the 1-yard line resulted in interceptions only 1.5% of the time, and an incomplete pass would stop the clock, allowing two more rushing attempts. The decision process was sound game theory; the outcome was an extreme low-probability outlier.",
                "boundary": "Do not dismiss negative outcomes in purely deterministic or repetitive engineering environments where variance is near zero. If a bridge collapses or an automated database migration drops tables, outcome directly reflects execution failure.",
                "action_item": "Conduct a Process-Only Decision Review: Audit your last major decision before looking at the outcome metric. Ask: 'Given what we knew at the exact moment of decision, was this bet mathematically and logically sound?'",
                "quote": "The quality of your life is the sum of your decision quality and your luck.",
                "visual_diagram": """graph TD
  Decision["Decision Architecture"] --> Execution["Probabilistic Reality & Variance"]
  Execution --> GoodOutcome["Favorable Outcome"]
  Execution --> BadOutcome["Unfavorable Outcome"]
  
  GoodOutcome --> ProcessCheck{"Audit Decision Process"}
  BadOutcome --> ProcessCheck
  
  ProcessCheck -->|Sound Process + Good Luck| GenuineSkill["Legitimate Edge"]
  ProcessCheck -->|Flawed Process + Good Luck| DumbLuck["Dangerous Hidden Ruin"]
  ProcessCheck -->|Sound Process + Bad Luck| Unlucky["Maintain Strategy"]
  ProcessCheck -->|Flawed Process + Bad Luck| DeservedFailure["Course Correct"]"""
            },
            {
                "title": "Probabilistic Bet Framing",
                "one_liner": "Replace 'I am certain' with explicit percentage confidence corridors.",
                "summary": "Stating convictions as absolute truths shuts down inquiry and triggers defensive ego protection. Framing claims as explicit probability bets invites open calibration and rigorous truth-seeking.",
                "detailed_explanation": "The Semantic Shift to Probabilistic Framing:\nWhen team members say 'This feature will succeed' or 'Competitor X cannot replicate our moat', they frame belief as binary truth. Any contradictory signal is perceived as an existential challenge to credibility, causing confirmation bias and sunk-cost doubling down.\n\nBy asking 'Wanna bet?', professional poker player Annie Duke forces the mind to audit its uncertainty. Stating 'I am 70% confident that this distribution channel yields >3x ROI' immediately illuminates the 30% failure surface, prompting proactive risk mitigation and pre-mortems.",
                "example": "At Bridgewater Associates, Ray Dalio instituted 'Believability-Weighted Decision Making'. Rather than debating whether an economic scenario will happen in binary terms, investment committee members submit numeric probability distributions. If three analysts assign 40%, 65%, and 80% probability to a currency devaluation, the firm sizes positions according to expected value and portfolio covariance, eliminating stubborn ideological debates.",
                "boundary": "Avoid probabilistic hand-waving on compliance, safety, and ethical guardrails. Do not say 'We are 95% confident this contract is legal'—regulatory thresholds require definitive binary verification.",
                "action_item": "In your next executive meeting, whenever someone asserts an opinion as fact, ask: 'What percentage bet would you put on that?' and list 2 indicators that would change your confidence by 20%.",
                "quote": "Saying 'I am 100% sure' usually means you have stopped looking for facts.",
                "visual_diagram": """graph TD
  Dogma["Dogmatic Absolute Assertion"] --> DefensiveEgo["Defensive Ego Defense"]
  DefensiveEgo --> FragileBlindness["Fragility & Systematic Blindspots"]
  
  Probabilistic["Probabilistic Bet Framing"] --> ConfidenceInterval["Assign Numeric Confidence %"]
  ConfidenceInterval --> ExploresFailure["Examine the Remaining Uncertainty"]
  ExploresFailure --> ResilientAntifragile["Resilient Calibrated Strategy"]"""
            }
        ]
    },
    {
        "title": "The Psychology of Money",
        "author": "Morgan Housel",
        "publisher": "Harriman House",
        "topic": "Wealth & Psychology",
        "description": "Timeless lessons on wealth, greed, and happiness. Doing well with money has a little to do with how smart you are and a lot to do with how you behave.",
        "ideas": [
            {
                "title": "Room for Error (Margin of Safety in Financial Life)",
                "one_liner": "The most important part of every plan is planning on your plan not going according to plan.",
                "summary": "Room for error is the only effective defense against an unpredictable future. It allows you to endure market volatility long enough for the arithmetic of compounding to work its magic.",
                "detailed_explanation": "The Mathematics of Staying in the Game:\nCompounding requires uninterrupted duration. The single greatest enemy of compounding is not low returns; it is forced liquidation. If you take excessive leverage or hold inadequate cash buffers, a single 1-in-50-year tail event forces you to sell assets at fire-sale prices, resetting the compounding exponent to zero.\n\nMorgan Housel emphasizes that room for error is not pessimistic conservativism; it is the prerequisite for aggressive long-term optimism. By surviving every down-cycle without being forced out of the market, you inherit the compounding returns that wipe out competitors.",
                "example": "During the 2008 Great Financial Crisis, German billionaire Adolf Merckle ran heavily leveraged industrial conglomerates and shorted Volkswagen stock. When Porsche revealed an unexpected takeover stake, Volkswagen stock skyrocketed from €200 to €1,000 in days. Despite having vast assets, Merckle lacked cash room for error to meet margin calls, forcing systemic liquidation and personal tragedy. Meanwhile, Warren Buffett maintained a permanent $20B+ cash buffer, allowing Berkshire Hathaway to inject capital into Goldman Sachs and General Electric on extraordinarily favorable terms.",
                "boundary": "Do not hoard excessive cash when you have near-zero liabilities and decades before capital withdrawal, as runaway inflation silently erodes uninvested capital over multi-decade horizons.",
                "action_item": "Calculate your 'Endurance Runway': How many months could your business or household survive if zero revenue arrived tomorrow? Ensure at least 6-12 months of non-negotiable liquidity.",
                "quote": "Planning is good, but the most important part of every plan is planning on your plan not going according to plan.",
                "visual_diagram": """graph TD
  Venture["High-Yield Investment or Venture"] --> Shock["Unforeseen Macro Shock or Tail Event"]
  Shock --> CheckBuffer{"Adequate Room for Error?"}
  
  CheckBuffer -->|No Cash Buffer / High Leverage| ForcedLiquidation["Forced Fire-Sale & Total Ruin"]
  CheckBuffer -->|Generous Cash Buffer| Endurance["Survive Volatility Intact"]
  
  Endurance --> CompoundingEngine["Compounding Engine Continues Unbroken"]"""
            },
            {
                "title": "The Freedom Dividend (Autonomy as Ultimate Wealth)",
                "one_liner": "The highest form of wealth is the ability to wake up every morning and say: 'I can do whatever I want today.'",
                "summary": "Material possessions yield rapid hedonic adaptation. Genuine enduring subjective well-being correlates highest with perceived personal control over your time and daily calendar.",
                "detailed_explanation": "Hedonic Adaptation vs Temporal Sovereignty:\nBehavioral psychology demonstrates that consumption upgrades (luxury vehicles, designer watches, bigger penthouses) generate ephemeral dopamine spikes that normalize within 60 to 90 days. The individual returns to their baseline happiness setpoint.\n\nConversely, 'temporal sovereignty'—freedom from toxic meetings, autonomy to choose working hours, and independence from unaligned bosses—delivers permanent structural reductions in chronic cortisol and cognitive burnout. True wealth is unspent financial optionality that buys autonomy.",
                "example": "A survey conducted by the University of Michigan tracking thousands of Americans across decades revealed that the single highest predictor of day-to-day life satisfaction was not income level or prestigious job title, but the feeling of having control over how one spends one's hours. Workers earning $70,000 with complete schedule autonomy reported consistently higher life satisfaction than investment bankers earning $400,000 on 90-hour mandatory office weeks.",
                "boundary": "Do not treat autonomy as an excuse for solipsistic isolation. True flourishing requires purpose and positive relational contribution, not merely idle detachment from society.",
                "action_item": "Audit your weekly calendar: Identify the 3 activities that consume the most energy with the least autonomy, and schedule an elimination or delegation plan for at least 1 this quarter.",
                "quote": "Control over doing what you want, when you want to, with the people you want to, is the broadest lifestyle variable that makes people happy.",
                "visual_diagram": """graph TD
  Income["Increased Income & Wealth"] --> Choice{"Where Is Capital Allocated?"}
  Choice -->|Conspicuous Consumption| Hedonic["Luxury Goods - Ephemeral Spike - Treadmill"]
  Choice -->|Time Sovereignty| Autonomy["Cash Buffer - Freedom to Say NO"]
  
  Autonomy --> HighWellbeing["Unbroken Creative Energy & Deep Well-Being"]"""
            }
        ]
    },
    {
        "title": "Antifragile",
        "author": "Nassim Nicholas Taleb",
        "publisher": "Random House",
        "topic": "Systems & Strategy",
        "description": "Things that gain from disorder. How to thrive in an uncertain, volatile, and asymmetric world by structuring convex payoffs.",
        "ideas": [
            {
                "title": "The Barbell Strategy (Bimodal Risk Allocation)",
                "one_liner": "Combine extreme conservatism with aggressive asymmetric upside while avoiding the moderate middle.",
                "summary": "To survive black swan shocks while capturing exponential growth, eliminate the vulnerable middle ground. Allocate 90% of resources to hyper-safe, non-ruin assets and 10% to high-optionality, speculative upside bets.",
                "detailed_explanation": "Convexity and Non-Ergodic Ruin:\nMost individuals and institutions pursue 'moderate risk' (e.g. holding medium-grade corporate bonds or average-risk ventures). In reality, moderate risk offers limited upside while remaining exposed to catastrophic systemic crashes.\n\nThe Barbell Strategy decouples risk into two extreme poles:\n1. Zero-Ruin Foundation (90%): Cash, gold, immutable skills, rock-solid health, zero debt. Complete immunity to black swans.\n2. Hyper-Asymmetric Speculation (10%): Multiple independent bets with bounded downside (you can only lose what you invested) and unlimited positive convexity.\n\nBecause the maximum loss is mathematically capped at 10%, catastrophic ruin is impossible, yet the system captures massive windfalls from unexpected positive shocks.",
                "example": "In career strategy, Seneca served as a multi-millionaire statesman and advisor to the emperor (extreme practical engagement) while spending hours in radical ascetic contemplation and philosophical writing. In tech venture investing, Peter Thiel structured Founders Fund on the barbell: hyper-stable capital reserves paired with high-risk seed investments in space exploration (SpaceX) and neural networks, where one hit returned the entire fund many times over.",
                "boundary": "Do not invert the barbell by risking 90% on speculative bets with 10% safe. The safety side must be large enough to make extinction mathematically impossible.",
                "action_item": "Map your risk profile on a 2-column barbell: List your non-ruin safe foundation on the left and your high-leverage upside bets on the right. Immediately purge moderate-risk assets that carry hidden bankruptcy risk.",
                "quote": "If you have more to gain than to lose from free fluctuations, you are antifragile.",
                "visual_diagram": """graph TD
  Strategy["Strategic Resource Allocation"] --> Split{"Bimodal Barbell Architecture"}
  Split -->|90% Non-Ruin Foundation| HyperSafe["Cash Reserves, Low Debt, Deep Health"]
  Split -->|10% Asymmetric Optionality| HighUpside["High-Leverage Speculative Bets"]
  
  HyperSafe --> TotalImmunity["Immunity to Black Swan Catastrophes"]
  HighUpside --> ExponentialPayoff["Captures Unbounded Positive Shocks"]
  
  TotalImmunity --> AntifragileSystem["Antifragile Machine"]
  ExponentialPayoff --> AntifragileSystem"""
            }
        ]
    },
    {
        "title": "Influence: The Psychology of Persuasion",
        "author": "Robert Cialdini",
        "publisher": "Harper Business",
        "topic": "Behavioral Psychology",
        "description": "The foundational treatise on the universal psychological triggers that guide human compliance and decision-making.",
        "ideas": [
            {
                "title": "Commitment and Consistency Heuristic",
                "one_liner": "Once we make a choice or take a stand, we face interpersonal pressure to behave consistently with that commitment.",
                "summary": "Human beings possess an obsession to be—and appear—consistent with what they have already done or said publicly. Securing micro-commitments creates an irreversible psychological escalator.",
                "detailed_explanation": "Cognitive Dissonance and Self-Identity Preservation:\nConsistency is an evolutionary mental shortcut. If we had to re-evaluate every belief from first principles daily, cognitive bandwidth would collapse. Once a person takes a public stand, backing down generates severe cognitive dissonance and social reputation loss.\n\nCialdini proved that small initial concessions ('foot-in-the-door' technique) reshape self-image. When someone agrees to a tiny trivial petition, they subsequently view themselves as 'the type of person who supports this cause', making them exponentially more likely to approve major financial or contractual commitments later.",
                "example": "During the Korean War, Chinese interrogators utilized small written concessions with American POWs. Rather than torturing them to renounce America, they asked prisoners to copy mild factual statements like 'The United States is not perfect.' Once a soldier wrote this down, examiners asked him to elaborate on specific examples. Step by step, the prisoner's self-image adjusted to be consistent with his own handwriting, leading to voluntary cooperation.",
                "boundary": "Do not exploit consistency maliciously against vulnerable individuals, as breaking trust generates severe boomerang retaliation once the manipulation is detected.",
                "action_item": "When seeking buy-in for a major proposal, ask for a 5-minute feedback chat first rather than an immediate multi-million budget approval. Secure micro-agreement on the problem before asking for the commitment.",
                "quote": "It is easier to resist at the beginning than at the end.",
                "visual_diagram": """graph TD
  Request["Target Proposition"] --> MicroAsk["Request Trivial Micro-Commitment"]
  MicroAsk --> Agree["Target Agrees & Acts Publicly"]
  Agree --> IdentityShift["Self-Image Realigned: 'I am a supporter'"]
  IdentityShift --> ConsistencyPressure["Desire for Behavioral Consistency"]
  ConsistencyPressure --> MajorCompliance["High-Value Deal Closed"]"""
            }
        ]
    },
    {
        "title": "High Output Management",
        "author": "Andrew S. Grove",
        "publisher": "Vintage",
        "topic": "Management & Strategy",
        "description": "The legendary Intel CEO's playbook for creating high-leverage operating cadence, task-relevant maturity, and managerial output.",
        "ideas": [
            {
                "title": "Managerial Leverage (Output per Hour)",
                "one_liner": "A manager's output = the output of their organization + the output of the neighboring organizations influenced by them.",
                "summary": "Focus your managerial hours exclusively on high-leverage activities: actions that exert a disproportionate positive multiplier on the output of dozens of peers over months.",
                "detailed_explanation": "The Mechanics of Leverage in Knowledge Work:\nMost managers fall into the trap of doing individual contributor tasks because they provide immediate tactile gratification. However, Andy Grove calculated that a manager's primary contribution is leverage—the ratio of organizational output generated to time invested.\n\nHigh-leverage activities include:\n- Articulating clear mission guardrails that guide hundreds of autonomous daily decisions.\n- Developing operational training programs that level up 50 engineers simultaneously.\n- Conductive Socratic 1-on-1s that unblock hidden friction before it metastasizes.\nConversely, meddling in cosmetic slide formatting or low-impact approvals is negative-leverage micromanagement.",
                "example": "Andy Grove personally designed and taught the Intel employee orientation and middle management academy. Spending 4 hours per week teaching 30 new leaders provided leverage across hundreds of factory shifts and fabrication plants for years, instilling Intel's famous culture of constructive confrontation and operational excellence.",
                "boundary": "Do not retreat into pure abstract leverage if your team is currently facing an existential operational fire. When a crisis threatens survival, hands-on direct intervention is mandatory.",
                "action_item": "Audit your calendar: Categorize every meeting into Low, Medium, or High Leverage. Cancel or delegate at least two Low-Leverage meetings this week to free up time for strategic unblocking.",
                "quote": "A manager's output is not what they personally do; it is the output of the organization they lead.",
                "visual_diagram": """graph TD
  Time["1 Hour of Managerial Time"] --> Path{"Where Is Time Spent?"}
  Path -->|Individual Contributor Busywork| LowLev["Low Leverage: 1 Unit Output"]
  Path -->|Training, Systems, Clear Guardrails| HighLev["High Leverage Multiplier"]
  
  HighLev --> ForceMultiplier["50 Team Members Execute with 20% Higher Speed"]
  ForceMultiplier --> ExponentialOrgOutput["100x Compounded Organizational Output"]"""
            }
        ]
    }
]

def init_daily_log_table():
    """Initializes the database schema and daily book log table if it doesn't already exist."""
    database.init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS daily_book_log (
        date TEXT PRIMARY KEY,
        book_id TEXT NOT NULL,
        book_title TEXT NOT NULL,
        author TEXT NOT NULL,
        added_at TEXT NOT NULL,
        ideas_count INTEGER DEFAULT 0
    );
    """)
    conn.commit()
    conn.close()

def get_today_str() -> str:
    """Returns today's date formatted as YYYY-MM-DD."""
    return date.today().strftime("%Y-%m-%d")

def get_daily_status() -> Dict[str, Any]:
    """Returns the current state of daily book ingestion."""
    init_daily_log_table()
    conn = get_connection()
    cursor = conn.cursor()
    
    today_str = get_today_str()
    cursor.execute("SELECT * FROM daily_book_log WHERE date = ?", (today_str,))
    today_entry = cursor.fetchone()
    
    cursor.execute("SELECT COUNT(*) FROM books")
    total_books = cursor.fetchone()[0]
    
    cursor.execute("SELECT id, title, normalized_title FROM books")
    existing_books = cursor.fetchall()
    existing_slugs = {b["id"] for b in existing_books}
    existing_norms = {b["normalized_title"] for b in existing_books}
    
    conn.close()
    
    # Check next queued book
    next_queued = None
    remaining_queue_count = 0
    for book in CURATED_DAILY_BOOKS:
        slug = slugify(book["title"])
        norm = database.normalize_book_title(book["title"])
        if slug not in existing_slugs and norm not in existing_norms:
            remaining_queue_count += 1
            if not next_queued:
                next_queued = book["title"]
                
    return {
        "today": today_str,
        "already_added_today": today_entry is not None,
        "today_book": dict(today_entry) if today_entry else None,
        "total_books_on_platform": total_books,
        "curated_queue_remaining": remaining_queue_count,
        "next_upcoming_book": next_queued
    }

def add_daily_book(force: bool = False) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Checks if a book has been added today.
    If not (or if force=True), selects the next un-added seminal book from the queue,
    registers it with full atomic models, and creates the dedicated stash.
    """
    init_daily_log_table()
    today_str = get_today_str()
    
    conn = get_connection()
    cursor = conn.cursor()
    
    if not force:
        cursor.execute("SELECT * FROM daily_book_log WHERE date = ?", (today_str,))
        existing_today = cursor.fetchone()
        if existing_today:
            conn.close()
            return False, f"Book for today ({today_str}) already active: '{existing_today['book_title']}'", dict(existing_today)
            
    cursor.execute("SELECT id, normalized_title FROM books")
    existing = cursor.fetchall()
    existing_ids = {e["id"] for e in existing}
    existing_norms = {e["normalized_title"] for e in existing}
    conn.close()
    
    # Find next eligible book
    selected_book = None
    for b in CURATED_DAILY_BOOKS:
        slug = slugify(b["title"])
        norm = database.normalize_book_title(b["title"])
        if slug not in existing_ids and norm not in existing_norms:
            selected_book = b
            break
            
    if not selected_book:
        # Fallback if all curated books are already in DB: generate a dynamic companion classic
        selected_book = {
            "title": f"The Almanack of Mental Models ({today_str})",
            "author": "Universal Knowledge Collective",
            "publisher": "Microstash Press",
            "topic": "Mental Models",
            "description": "Daily synthesized strategic frameworks for high-leverage decision making and systems resilience.",
            "ideas": [
                {
                    "title": f"Daily Epistemic Hygiene ({today_str})",
                    "one_liner": "Audit your core operating assumptions daily against disconfirming reality.",
                    "summary": "Knowledge depreciates without continuous falsification. Running daily micro-audits preserves cognitive edge.",
                    "detailed_explanation": "Epistemological resilience requires active refactoring of mental heuristics. When operating under uncertainty, systematically seek out contradictory data points rather than hoarding confirming signals.",
                    "example": "Charles Darwin kept a special notebook to immediately write down any observation or thought that contradicted his theories within thirty minutes, knowing that the human brain naturally forgets disconfirming evidence.",
                    "boundary": "Do not discard proven foundational principles over single noisy outliers without statistical significance.",
                    "action_item": "Identify one strong belief you held this morning and write down what evidence would completely refute it.",
                    "quote": "Whenever you find yourself on the side of the majority, it is time to pause and reflect.",
                    "visual_diagram": "graph TD\n  Belief[\"Active Mental Model\"] --> Test{\"Expose to Disconfirming Data\"}\n  Test -->|Falsified| Adapt[\"Upgrade Model\"]\n  Test -->|Validated| Retain[\"Fortified Edge\"]"
                }
            ]
        }
        
    # Register into platform database
    registered = database.register_scanned_book(
        title=selected_book["title"],
        author=selected_book["author"],
        description=selected_book["description"],
        topic=selected_book["topic"],
        ideas_list=selected_book["ideas"],
        scanned_by="daily_automated_curator",
        publisher=selected_book["publisher"]
    )
    
    # Record into daily_book_log
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO daily_book_log (date, book_id, book_title, author, added_at, ideas_count)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (today_str, registered["book"]["id"], selected_book["title"], selected_book["author"], datetime.utcnow().isoformat(), len(selected_book["ideas"])))
    conn.commit()
    conn.close()
    
    msg = f"Successfully added daily book '{selected_book['title']}' by {selected_book['author']} ({len(selected_book['ideas'])} models) for {today_str}!"
    logger.info(msg)
    return True, msg, registered

_scheduler_started = False

def _scheduler_loop():
    """Background daemon loop that wakes up periodically and adds the new book on calendar day rollover."""
    time.sleep(5) # Brief delay after server boot
    while True:
        try:
            added, msg, book = add_daily_book(force=False)
            if added:
                logger.info(f"[Daily Book Cron] {msg}")
        except Exception as e:
            logger.error(f"[Daily Book Cron] Error checking daily book: {e}")
        # Check every 30 minutes (1800s)
        time.sleep(1800)

def start_daily_scheduler():
    """Starts the background worker thread for automatic daily book drops."""
    global _scheduler_started
    if _scheduler_started:
        return
    _scheduler_started = True
    t = threading.Thread(target=_scheduler_loop, daemon=True, name="DailyBookSchedulerThread")
    t.start()
    logger.info("[Daily Book Scheduler] Background worker initialized.")
