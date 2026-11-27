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
    },
    {
        "title": "The Scout Mindset",
        "author": "Julia Galef",
        "publisher": "Portfolio / Penguin",
        "topic": "Mental Models",
        "description": "Why some people see things clearly and others don't. Learning to seek truth instead of defending your ego.",
        "ideas": [
            {
                "title": "Soldier vs. Scout Mindset",
                "one_liner": "Stop defending what you already believe and start mapping what is actually true.",
                "summary": "Most of us think like soldiers: we attack facts that threaten our side and cheer for facts that support us. A scout's job isn't to win an argument—it's to draw an accurate map of the terrain.",
                "detailed_explanation": "### How It Works\nIn Soldier Mindset, your goal is to protect your beliefs, reputation, or team from feeling wrong. In Scout Mindset, your goal is to see reality as clearly as possible, even when the truth is uncomfortable.\n\n### Why We Get It Wrong\nChanging your mind feels like losing. Our brains treat an attack on our opinion the same way they treat a physical threat, triggering defensiveness.\n\n### When Not to Use It\nDon't stay in endless research mode when you already have enough facts and need to rally people to act.",
                "example": "In 1894, French officer Alfred Dreyfus was falsely convicted of treason. Colonel Georges Picquart initially believed Dreyfus was guilty too. When Picquart found evidence pointing to the real spy, he didn't bury it to protect the army's reputation—he fought to clear Dreyfus, showing true Scout Mindset.",
                "boundary": "Once a clear decision is made and action is underway, focus on execution rather than second-guessing every detail.",
                "action_item": "Pick one strong opinion you hold and ask: 'If I were wrong about this, what would be the clearest sign?'",
                "quote": "Judgment calls aren't about proving yourself right; they're about making sure you're seeing clearly.",
                "visual_diagram": "graph TD\n  Info[\"New Surprising Fact\"] --> Mode{\"Which Mindset?\"}\n  Mode -->|Soldier| Defend[\"Ignore or Attack Fact\"]\n  Mode -->|Scout| Map[\"Update Your Mental Map\"]\n  Defend --> Blind[\"Bigger Blindspots\"]\n  Map --> Clear[\"Better Decisions\"]"
            }
        ]
    },
    {
        "title": "Good Strategy Bad Strategy",
        "author": "Richard Rumelt",
        "publisher": "Crown Business",
        "topic": "Strategy",
        "description": "The difference between real strategy—focused action on a core obstacle—and empty corporate fluff.",
        "ideas": [
            {
                "title": "The Kernel of Good Strategy",
                "one_liner": "Real strategy isn't a wish list of goals; it's a clear plan to overcome your biggest obstacle.",
                "summary": "Bad strategy mistakes big goals ('grow revenue 20%') for a plan. Good strategy always has three parts: a clear diagnosis of the real problem, a guiding approach, and focused actions that work together.",
                "detailed_explanation": "### How It Works\nGreat strategy concentrates your limited energy on one critical bottleneck instead of spreading effort across twenty priorities. First name the core challenge, choose one smart way around it, and align your actions.\n\n### Why We Get It Wrong\nLeaders avoid hard choices because saying 'no' upsets people. Instead, they write vague slogans that try to please everyone and solve nothing.\n\n### When Not to Use It\nDon't lock into a rigid multi-year plan when the market is brand new and you still need to experiment.",
                "example": "When Steve Jobs returned to Apple in 1997, the company had dozens of confusing products and was weeks from bankruptcy. Instead of writing a 10-year vision statement, he diagnosed the bloat, cut 70% of the product line down to just four computers, and focused every engineer on those four.",
                "boundary": "In early-stage discovery before you know what works, run small experiments rather than committing everything to one bet.",
                "action_item": "Look at your top project today and write a 1-sentence diagnosis of the single biggest roadblock in its way.",
                "quote": "A good strategy honestly acknowledges the challenges being faced and provides an approach to overcoming them.",
                "visual_diagram": "graph TD\n  Problem[\"Complex Situation\"] --> Diag[\"1. Clear Diagnosis\"]\n  Diag --> Guide[\"2. Guiding Approach\"]\n  Guide --> Act[\"3. Focused Actions\"]\n  Act --> Win[\"Breakthrough Progress\"]"
            }
        ]
    },
    {
        "title": "Zero to One",
        "author": "Peter Thiel",
        "publisher": "Crown Business",
        "topic": "Strategy",
        "description": "Notes on startups and how to build the future by creating something genuinely new instead of copying.",
        "ideas": [
            {
                "title": "Competition Is for Losers",
                "one_liner": "Copying what already works leads to cutthroat price wars; creating something unique builds lasting value.",
                "summary": "Horizontal progress (1 to N) copies existing ideas and splits the same pie into smaller slices. Vertical progress (0 to 1) invents something new that gives customers no real substitute.",
                "detailed_explanation": "### How It Works\nIn a crowded market, companies fight over tiny margins just to survive. When you solve a problem 10x better in a completely new way, you escape the race and earn the breathing room to think long-term.\n\n### Why We Get It Wrong\nCompetition feels comforting because if others are doing it, the market must be real. So founders crowd into the same trendy spaces.\n\n### When Not to Use It\nDon't invent something weird just to be different—customers only care if it solves a real problem far better.",
                "example": "Restaurants in big cities compete fiercely on price and location, with most barely breaking even. Meanwhile, Google built a search algorithm 10x better than rivals, capturing massive profits without fighting endless price wars.",
                "boundary": "Don't try to invent a brand-new category if a proven, underserved local need just needs reliable execution.",
                "action_item": "Ask about your work: 'What valuable truth or problem am I solving that almost nobody else is looking at?'",
                "quote": "All happy companies are different: each one earns a monopoly by solving a unique problem.",
                "visual_diagram": "graph TD\n  Idea[\"New Venture\"] --> Path{\"1 to N or 0 to 1?\"}\n  Path -->|Copy Existing| Crowded[\"Price Wars & Thin Margins\"]\n  Path -->|Invent 10x Better| Unique[\"Unique Value & Lasting Edge\"]"
            }
        ]
    },
    {
        "title": "Superforecasting",
        "author": "Philip Tetlock",
        "publisher": "Crown",
        "topic": "Mental Models",
        "description": "The art and science of predicting the future better than experts using small, steady updates.",
        "ideas": [
            {
                "title": "Start with the Base Rate",
                "one_liner": "Before guessing what will happen in your special case, check how often it happens in general.",
                "summary": "We naturally zoom in on the details of our own story and forget the big picture. Starting with the outside statistical average ('base rate') keeps your predictions grounded in reality.",
                "detailed_explanation": "### How It Works\nTo predict any outcome accurately, split it into two steps: first ask 'How often does something like this succeed normally?' (the outside view), then adjust slightly based on your specific details (the inside view).\n\n### Why We Get It Wrong\nEvery founder, investor, or planner feels their project is special, so they ignore the fact that most similar projects run late or over budget.\n\n### When Not to Use It\nWhen a truly unprecedented shift changes the underlying rules, past averages carry less weight.",
                "example": "Nobel laureate Daniel Kahneman was writing a curriculum textbook with a team. Internally, they guessed it would take 2 years. When asked how long similar teams actually took, an expert said 7 to 10 years—and 40% never finished. It ended up taking Kahneman's team 8 years.",
                "boundary": "Use base rates as your starting anchor, then adjust when you have strong, verifiable reasons why this case differs.",
                "action_item": "For your next deadline or goal, look up how long similar projects actually took before setting your target date.",
                "quote": "Foresight isn't a mysterious gift; it's the product of particular ways of thinking and updating.",
                "visual_diagram": "graph TD\n  Guess[\"Need a Prediction\"] --> Outside[\"1. Check Base Rate\"]\n  Outside --> Inside[\"2. Adjust for Specifics\"]\n  Inside --> Update[\"3. Update with New Clues\"]\n  Update --> Sharp[\"Accurate Forecast\"]"
            }
        ]
    },
    {
        "title": "Range",
        "author": "David Epstein",
        "publisher": "Riverhead Books",
        "topic": "Productivity",
        "description": "Why generalists triumph in a specialized world by connecting ideas across different fields.",
        "ideas": [
            {
                "title": "The Sampling Period Advantage",
                "one_liner": "Trying many different paths early on isn't wasted time—it's how you find your true fit.",
                "summary": "Early specialization works in predictable games like chess or golf, but in messy real-world careers, people who explore widely first end up happier, more creative, and better at solving unfamiliar problems.",
                "detailed_explanation": "### How It Works\nBroad experience gives you a bigger toolkit of mental models. When you face a new problem, you can borrow solutions from another field that specialists never even look at.\n\n### Why We Get It Wrong\nWe worship the '10,000-hour head start' myth and panic if we feel behind peers who picked one narrow lane at age 18.\n\n### When Not to Use It\nIn fields with strict rules and unchanging patterns (like classical violin or surgery), early focused practice is still essential.",
                "example": "Roger Federer played soccer, basketball, skiing, and wrestling before focusing on tennis as a teenager. That broad athletic foundation gave him unmatched coordination and prevented early burnout compared to peers who played only tennis from age six.",
                "boundary": "Exploration is valuable, but eventually you still need to commit deeply once you find strong match quality.",
                "action_item": "Read one article or talk to someone completely outside your field this week and look for one idea you can borrow.",
                "quote": "Compare yourself to yourself yesterday, not to younger people who aren't you.",
                "visual_diagram": "graph TD\n  Start[\"Early Career\"] --> Path{\"Narrow Early vs Explore?\"}\n  Path -->|Narrow Too Soon| Stuck[\"Rigid Skills / Burnout\"]\n  Path -->|Sample Broadly| Range[\"Rich Toolkit & Better Fit\"]"
            }
        ]
    },
    {
        "title": "The Innovator's Dilemma",
        "author": "Clayton Christensen",
        "publisher": "Harvard Business Review Press",
        "topic": "Strategy",
        "description": "Why great companies fail when they listen too closely to their best customers and miss simple, cheaper disruptors.",
        "ideas": [
            {
                "title": "Disruption Starts at the Bottom",
                "one_liner": "Big winners rarely lose to better products—they lose to simpler, cheaper ones they ignored.",
                "summary": "Market leaders focus on serving their highest-paying customers with fancy features. That leaves the door open for newcomers to build simple, affordable tools for everyone else—and slowly climb upmarket.",
                "detailed_explanation": "### How It Works\nEvery successful company naturally chases higher profits. Improving a simple, cheap product for overlooked users looks unattractive at first, until that simple product gets good enough to steal the main market.\n\n### Why We Get It Wrong\nListening to your best customers feels like smart business—until their demands blind you to a simpler wave coming from below.\n\n### When Not to Use It\nDon't ignore quality in mission-critical fields like aviation or medicine where 'good enough' is unsafe.",
                "example": "Blockbuster ignored Netflix when it only mailed DVDs with limited selection to movie buffs. By the time streaming made Netflix fast and convenient, Blockbuster's store-based business couldn't pivot in time.",
                "boundary": "Not every cheap product is disruptive; it has to steadily improve until it meets mainstream needs.",
                "action_item": "Ask: 'What simple, clunky, or cheap tool are people using today that could replace our complex workflow in 5 years?'",
                "quote": "The very practices that keep a company successful are often the ones that cause it to miss disruption.",
                "visual_diagram": "graph TD\n  Leader[\"Market Leader\"] --> HighEnd[\"Chases High-Margin Customers\"]\n  Newcomer[\"Small Disruptor\"] --> LowEnd[\"Starts Simple & Affordable\"]\n  LowEnd --> Improves[\"Improves Rapidly\"]\n  Improves --> Wins[\"Captures Mainstream Market\"]"
            }
        ]
    },
    {
        "title": "Four Thousand Weeks",
        "author": "Oliver Burkeman",
        "publisher": "Farrar, Straus and Giroux",
        "topic": "Productivity",
        "description": "Time management for mortals: embracing your limits instead of trying to get everything done.",
        "ideas": [
            {
                "title": "Strategic Neglect",
                "one_liner": "You will never finish your to-do list, so choose carefully what you are willing to leave undone.",
                "summary": "Trying to squeeze more tasks into every day only creates an endless conveyor belt of new demands. Peace and real impact come from accepting your limits and deliberately ignoring low-value tasks.",
                "detailed_explanation": "### How It Works\nThe faster you clear your inbox, the faster people send you more emails. Instead of optimizing everything, limit your active projects to a few that truly matter and let the rest wait.\n\n### Why We Get It Wrong\nWe treat time like an infinite bucket we can master with better apps, rather than a short, finite life of roughly 4,000 weeks.\n\n### When Not to Use It\nDon't neglect urgent safety, legal, or health responsibilities—be picky about optional commitments.",
                "example": "Warren Buffett allegedly advised his pilot to list his top 25 career goals, circle the top 5, and treat the other 20 as an 'Avoid-At-All-Cost' list because those tempting #6–#25 goals steal time from the #1–#5 priorities.",
                "boundary": "Accepting limits doesn't mean giving up on ambition—it means channeling energy into fewer, deeper things.",
                "action_item": "Pick three non-essential tasks on your list today and consciously move them to a 'Not Doing This Week' list.",
                "quote": "The real measure of any time management technique is whether or not it helps you neglect the right things.",
                "visual_diagram": "graph TD\n  Tasks[\"Endless To-Do List\"] --> Choice{\"How Do You Handle It?\"}\n  Choice -->|Do Everything| Burnout[\"Busyness & Exhaustion\"]\n  Choice -->|Pick Top Few| Focus[\"Deep Work & Peace of Mind\"]"
            }
        ]
    },
    {
        "title": "Noise: A Flaw in Human Judgment",
        "author": "Daniel Kahneman",
        "publisher": "Little, Brown Spark",
        "topic": "Mental Models",
        "description": "Why human decisions vary wildly based on mood, weather, or timing—and how to make judgment fairer.",
        "ideas": [
            {
                "title": "Bias vs. Noise",
                "one_liner": "Sometimes our judgment isn't consistently tilted one way—it's just randomly scattered.",
                "summary": "Bias is when a scale is always off by 5 pounds in one direction. Noise is when the scale gives a different weight every time you step on it. Both ruin decisions, yet we rarely measure noise.",
                "detailed_explanation": "### How It Works\nEven trained experts give wildly different answers to the exact same case depending on whether they are tired, hungry, or saw a different case right before. Simple checklists and scoring rules cut noise dramatically.\n\n### Why We Get It Wrong\nPeople love trusting their gut in the moment and assume colleagues would make the same call they did.\n\n### When Not to Use It\nIn creative arts or brainstorming, variety is a feature, not a bug—save noise reduction for repeatable judgments.",
                "example": "Studies of judges and insurance underwriters found that two professionals looking at the exact same file often disagreed by over 50% on sentencing or pricing. Adding structured scoring checklists cut that random variation in half.",
                "boundary": "Structured rules shouldn't remove human empathy in rare, extraordinary cases—they just set a fair baseline.",
                "action_item": "Before your next hiring interview or review, write down 3 specific criteria and score each one independently before discussing.",
                "quote": "Wherever there is judgment, there is noise—and more of it than you think.",
                "visual_diagram": "graph TD\n  SameCase[\"Same Facts & Evidence\"] --> Unstructured[\"Gut Judgment Only\"]\n  SameCase --> Structured[\"Simple Scoring Checklist\"]\n  Unstructured --> Scattered[\"Wildly Different Outcomes\"]\n  Structured --> Fair[\"Consistent & Fair Decisions\"]"
            }
        ]
    },
    {
        "title": "Same as Ever",
        "author": "Morgan Housel",
        "publisher": "Portfolio",
        "topic": "Wealth",
        "description": "A guide to what never changes in a fast-moving world—human greed, fear, incentives, and patience.",
        "ideas": [
            {
                "title": "Bet on What Never Changes",
                "one_liner": "Predicting what will be different in 10 years is hard; betting on what will stay the same is far smarter.",
                "summary": "Technology and trends change every year, but human nature—fear, greed, status, and wanting things fast and easy—stays identical across centuries. Build around timeless human behaviors.",
                "detailed_explanation": "### How It Works\nJeff Bezos famously noted that nobody ever says 'I wish prices were higher and delivery took longer.' Focusing on permanent human desires compounds over decades without needing lucky guesses.\n\n### Why We Get It Wrong\nNovelty gets all the headlines. People love forecasting dramatic changes while overlooking permanent truths.\n\n### When Not to Use It\nStill watch for genuine shifts in tools and costs—timeless needs stay the same, even when delivery methods evolve.",
                "example": "Amazon built its entire empire around three things customers will always want in any decade: lower prices, wider selection, and faster delivery—letting the tools evolve while the core promise never changed.",
                "boundary": "Don't confuse timeless human desires with outdated business habits; how you deliver value still has to adapt.",
                "action_item": "List 2 things in your career or industry that customers will still want 10 years from now, and invest your energy there.",
                "quote": "Spend less time trying to predict what will change, and more time understanding what never will.",
                "visual_diagram": "graph TD\n  Future[\"Uncertain Future\"] --> Focus{\"Where to Build?\"}\n  Focus -->|Short-Lived Trends| Fragile[\"Fades Quickly\"]\n  Focus -->|Timeless Human Needs| Durable[\"Compounds Over Decades\"]"
            }
        ]
    },
    {
        "title": "The Art of Doing Science and Engineering",
        "author": "Richard Hamming",
        "publisher": "Stripe Press",
        "topic": "Productivity",
        "description": "Timeless lessons from a Bell Labs legend on doing great work and thinking independently.",
        "ideas": [
            {
                "title": "Work on the Important Problems",
                "one_liner": "If you don't work on important problems, you'll almost never do important work.",
                "summary": "Most talented people spend their whole lives solving small, safe puzzles instead of asking what truly matters in their field. Setting aside time each week for 'great thoughts' changes your trajectory.",
                "detailed_explanation": "### How It Works\nBell Labs pioneer Richard Hamming used to ask colleagues at lunch: 'What are the most important problems in your field, and why aren't you working on them?' Courage and problem selection matter as much as raw intelligence.\n\n### Why We Get It Wrong\nSmall, urgent tasks feel productive and safe, while big problems feel scary and uncertain.\n\n### When Not to Use It\nDon't neglect learning the basics—master your craft while keeping an eye on the biggest questions.",
                "example": "Hamming famously kept Friday afternoons free for 'Great Thoughts Time,' stepping back from daily coding tasks to ask big questions about error-correcting codes—work that later powered modern computing.",
                "boundary": "Big questions still require daily, patient craft; dreaming without shipping achieves nothing.",
                "action_item": "Block 30 minutes this Friday to ask: 'What is the most important problem in my work right now, and how can I take one step toward it?'",
                "quote": "Great work requires the courage to believe you can tackle important problems.",
                "visual_diagram": "graph TD\n  Week[\"Your Work Week\"] --> Choice{\"Problem Choice\"}\n  Choice -->|Only Small Safe Tasks| Average[\"Busy but Forgettable\"]\n  Choice -->|Important Questions| Great[\"Breakthrough Impact\"]"
            }
        ]
    },
    {
        "title": "Slow Productivity",
        "author": "Cal Newport",
        "publisher": "Portfolio",
        "topic": "Productivity",
        "description": "The lost art of accomplishment without burnout: do fewer things, work at a natural pace, and obsess over quality.",
        "ideas": [
            {
                "title": "Do Fewer Things",
                "one_liner": "Busyness is not productivity; doing fewer things better produces far greater results.",
                "summary": "Modern knowledge work mistakes constant Slack messages and packed calendars for real output. Cutting your active commitments in half frees up the focus needed to create work you're proud of.",
                "detailed_explanation": "### How It Works\nEvery extra project adds hidden coordination overhead—meetings, emails, and context switching. By capping active projects, you finish each one faster and at a much higher standard.\n\n### Why We Get It Wrong\nWe use visible busyness as a shortcut to prove we're working hard, even when it ruins our actual output.\n\n### When Not to Use It\nIn true short-term emergencies, all-hands responsiveness is temporarily needed—just don't make it your permanent lifestyle.",
                "example": "Jane Austen wrote her enduring novels in quiet morning bursts while living a calm, unhurried country life—producing masterpieces without constant meetings or frantic multitasking.",
                "boundary": "Working at a natural pace still requires steady daily discipline, not endless procrastination.",
                "action_item": "Put a hard cap on your active major projects today (max 2 or 3) and pause everything else until one finishes.",
                "quote": "Do fewer things. Work at a natural pace. Obsess over quality.",
                "visual_diagram": "graph TD\n  Load[\"Too Many Projects\"] --> Overhead[\"Meetings & Context Switching\"]\n  Overhead --> Burnout[\"Slow Progress & Burnout\"]\n  Cap[\"Cap at 2-3 Projects\"] --> Quality[\"Deep Focus & Great Work\"]"
            }
        ]
    },
    {
        "title": "Fooled by Randomness",
        "author": "Nassim Nicholas Taleb",
        "publisher": "Random House",
        "topic": "Wealth",
        "description": "The hidden role of chance in life and markets—and why lucky winners often look like geniuses.",
        "ideas": [
            {
                "title": "Beware Survivorship Bias",
                "one_liner": "Looking only at the winners hides all the people who took the exact same risks and failed.",
                "summary": "We hear endless stories from billionaires and hitmakers, but we rarely hear from the graveyard of thousands who followed the exact same playbook and lost everything. Always look at the silent graveyard.",
                "detailed_explanation": "### How It Works\nIf 1,000 people flip a coin ten times in a row, someone is almost guaranteed to get 10 heads in a row—not from skill, just from luck. Studying only the winner gives you false lessons.\n\n### Why We Get It Wrong\nFailures are quiet and invisible, while winners write books and give interviews, tricking us into copying reckless bets.\n\n### When Not to Use It\nIn repeatable skills like surgery or engineering, consistent track records over long periods really do prove genuine skill.",
                "example": "During WWII, engineers wanted to armor planes where returning planes had the most bullet holes. Statistician Abraham Wald realized they were looking at survivors—planes hit in the engines never made it back, so that's where the armor actually belonged.",
                "boundary": "Success stories are still inspiring, as long as you also ask how many failed doing the same thing.",
                "action_item": "Next time you read a 'how I succeeded' story, ask: 'How many people tried this exact move and failed quietly?'",
                "quote": "Reality is far more vicious than Russian roulette; the loser doesn't get to tell their story.",
                "visual_diagram": "graph TD\n  Many[\"1,000 Risk Takers\"] --> Luck[\"Random Luck & Skill\"]\n  Luck --> Winners[\"Few Visible Winners\"]\n  Luck --> Graveyard[\"Silent Failures\"]\n  Winners -->|Ignore Graveyard| Trap[\"False Confidence\"]"
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
            "title": f"The Almanack of Clear Thinking ({today_str})",
            "author": "Universal Knowledge Collective",
            "publisher": "Microstash Press",
            "topic": "Mental Models",
            "description": "Daily practical ideas for sharper decisions and clearer thinking.",
            "ideas": [
                {
                    "title": f"Daily Reality Check ({today_str})",
                    "one_liner": "Test your strongest beliefs against facts that could prove you wrong.",
                    "summary": "Good thinking goes stale if you never challenge it. Checking your assumptions against real-world feedback keeps your judgment sharp.",
                    "detailed_explanation": "### How It Works\nStaying sharp means testing your own ideas instead of just defending them. When things are uncertain, actively look for clues that you might be wrong rather than only collecting proof that makes you feel right.\n\n### Why We Get It Wrong\nOur brains naturally remember facts that back us up and quietly forget facts that challenge us.\n\n### When Not to Use It\nDon't throw away a solid, proven rule just because of one weird fluke—look for a real pattern first.",
                    "example": "Charles Darwin kept a special notebook just for observations that seemed to disprove his own theories. He wrote them down within 30 minutes because he knew how easily the human brain forgets facts it dislikes.",
                    "boundary": "Don't abandon a proven principle over a single noisy outlier—look for a real pattern first.",
                    "action_item": "Pick one strong opinion you held this morning and write down what real-world fact would change your mind.",
                    "quote": "Whenever you find yourself on the side of the majority, it is time to pause and reflect.",
                    "visual_diagram": "graph TD\n  Belief[\"Your Current Belief\"] --> Test{\"Test Against Real Facts\"}\n  Test -->|Proven Wrong| Adapt[\"Update Your Thinking\"]\n  Test -->|Holds Up| Retain[\"Stronger Confidence\"]"
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
