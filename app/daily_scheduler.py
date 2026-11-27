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
    },
    {
        "title": "The Black Swan",
        "author": "Nassim Nicholas Taleb",
        "publisher": "Random House",
        "topic": "Mental Models",
        "description": "The impact of the highly improbable—why rare, unexpected events shape history and how to prepare for them.",
        "ideas": [
            {
                "title": "Prepare for Rare Shocks, Don't Predict Them",
                "one_liner": "The biggest events in history are almost impossible to predict—so build resilience instead of forecasts.",
                "summary": "A Black Swan is a rare surprise with massive impact that everyone claims was obvious afterward. Instead of trying to guess the next crisis, build a life and portfolio that won't break when surprises hit.",
                "detailed_explanation": "### How It Works\nTraditional forecasts assume tomorrow looks like yesterday. In reality, a handful of sudden shocks—pandemics, breakthroughs, crashes—drive most of the change.\n\n### Why We Get It Wrong\nHumans love tidy stories after the fact and mistake past stability for future safety.\n\n### When Not to Use It\nIn stable physical systems like bridge weight limits, normal averages still work reliably.",
                "example": "Before 2008, major banks used models built on recent calm years that treated a nationwide housing crash as practically impossible—and went bankrupt when the rare shock arrived.",
                "boundary": "Don't let fear of rare events stop you from taking small, smart risks with capped downside.",
                "action_item": "Ask: 'If my biggest source of income or traffic disappeared for 3 months, what backup would keep me safe?'",
                "quote": "Readiness beats prediction every single time.",
                "visual_diagram": "graph TD\n  Event[\"Rare Shock\"] --> Fragile[\"Over-Leveraged Plan\"]\n  Event --> Robust[\"Built-In Cushion\"]\n  Fragile --> Crash[\"Breaks Completely\"]\n  Robust --> Survive[\"Survives & Adapts\"]"
            }
        ]
    },
    {
        "title": "Essentialism",
        "author": "Greg McKeown",
        "publisher": "Crown Business",
        "topic": "Productivity",
        "description": "The disciplined pursuit of less—saying no to almost everything so you can give your best to what truly matters.",
        "ideas": [
            {
                "title": "Less, But Better",
                "one_liner": "If you don't prioritize your own life, someone else will gladly prioritize it for you.",
                "summary": "Saying yes to every good opportunity leaves you stretched thin across twenty average projects. Essentialism means trading popularity for real progress on the vital few things.",
                "detailed_explanation": "### How It Works\nImagine pushing 1 millimeter in 20 directions vs. pushing 20 millimeters in 1 direction. Focusing your energy creates real breakthroughs.\n\n### Why We Get It Wrong\nWe fear missing out and hate saying no, so we pack our calendars with polite obligations.\n\n### When Not to Use It\nEarly in your career when you're still discovering what you're great at, say yes more to explore.",
                "example": "Steve Jobs famously cut Apple's messy product lineup down to just four products in 1997—and turned a dying company into the most valuable firm on earth.",
                "boundary": "Saying no works best when you say it clearly and kindly, not by ghosting people.",
                "action_item": "Say a polite 'no' to one non-essential meeting or favor this week to protect your deep focus time.",
                "quote": "Remember that if you don't prioritize your life, someone else will.",
                "visual_diagram": "graph TD\n  Energy[\"Your Energy\"] --> Spread[\"20 Average Tasks\"]\n  Energy --> Focus[\"1 Vital Goal\"]\n  Spread --> Thin[\"Tiny Progress\"]\n  Focus --> Big[\"Breakthrough Results\"]"
            }
        ]
    },
    {
        "title": "The 7 Habits of Highly Effective People",
        "author": "Stephen R. Covey",
        "publisher": "Free Press",
        "topic": "Productivity",
        "description": "Timeless principles for personal effectiveness, responsibility, and working well with others.",
        "ideas": [
            {
                "title": "Circle of Concern vs. Circle of Influence",
                "one_liner": "Put your energy into what you can actually change, not what you can only worry about.",
                "summary": "Everyone has things they care about (weather, politics, past mistakes) and things they can directly control (their attitude, skills, daily habits). Proactive people focus on their Circle of Influence—and watch it grow.",
                "detailed_explanation": "### How It Works\nEvery hour spent complaining about things outside your control drains energy from the things you can actually improve today.\n\n### Why We Get It Wrong\nBlaming outside forces feels comforting in the moment because it removes responsibility.\n\n### When Not to Use It\nFocusing on what you can control doesn't mean ignoring real injustice—it means choosing effective action over helpless venting.",
                "example": "During a severe industry downturn, one sales team spent hours complaining about the economy while another rebuilt their outreach script and landed 30% more demos.",
                "boundary": "Still stay aware of major external trends so you can adapt early.",
                "action_item": "Write down one problem bugging you today and circle only the part you can personally act on in the next 24 hours.",
                "quote": "I am not a product of my circumstances. I am a product of my decisions.",
                "visual_diagram": "graph TD\n  Worry[\"Worries & Problems\"] --> Split{\"Can You Control It?\"}\n  Split -->|No| Concern[\"Let It Go\"]\n  Split -->|Yes| Influence[\"Take Direct Action\"]\n  Influence --> Grow[\"Your Influence Grows\"]"
            }
        ]
    },
    {
        "title": "Man's Search for Meaning",
        "author": "Viktor E. Frankl",
        "publisher": "Beacon Press",
        "topic": "Stoicism",
        "description": "A psychiatrist's lessons from surviving the Holocaust on finding purpose and choosing your response in any situation.",
        "ideas": [
            {
                "title": "The Space Between Stimulus and Response",
                "one_liner": "Between what happens to you and how you react, there is a pause—and in that pause lies your freedom.",
                "summary": "You can't always control what happens to you, but you always own the gap between the event and your reaction. Even a two-second pause turns knee-jerk anger into deliberate choice.",
                "detailed_explanation": "### How It Works\nMost people react automatically like a reflex—insult triggers anger, delay triggers panic. Training yourself to pause for one breath restores control over your next move.\n\n### Why We Get It Wrong\nStrong emotions hijack attention and make instant reaction feel urgent.\n\n### When Not to Use It\nIn immediate physical danger, trust fast reflexes first and reflect later.",
                "example": "Viktor Frankl observed that even in brutal concentration camps, a few prisoners kept their dignity and helped others—proving that environment doesn't dictate character.",
                "boundary": "Pausing doesn't mean suppressing feelings forever—it means choosing wise action instead of exploding.",
                "action_item": "Next time an annoying email or comment hits, wait 60 seconds and take two slow breaths before replying.",
                "quote": "Everything can be taken from a person but one thing: the freedom to choose one's attitude.",
                "visual_diagram": "graph TD\n  Event[\"Triggering Event\"] --> Pause[\"1-Breath Pause\"]\n  Pause --> Choice[\"Choose Your Response\"]\n  Choice --> Peace[\"Strength & Self-Control\"]"
            }
        ]
    },
    {
        "title": "Never Split the Difference",
        "author": "Chris Voss",
        "publisher": "HarperBusiness",
        "topic": "Strategy",
        "description": "Former FBI hostage negotiator shares practical tactics for high-stakes conversations and everyday deals.",
        "ideas": [
            {
                "title": "Tactical Empathy & Mirroring",
                "one_liner": "People don't agree with you until they feel you truly understand where they're coming from.",
                "summary": "Pushing harder with logic rarely wins a tense negotiation. Simply repeating the other person's last few key words ('mirroring') and naming their emotion ('It sounds like...') lowers their guard and opens real dialogue.",
                "detailed_explanation": "### How It Works\nWhen someone feels heard, their defensive brain calms down and they start volunteering helpful details you'd never get by arguing.\n\n### Why We Get It Wrong\nWe spend the whole time they're talking rehearsing our own counterargument.\n\n### When Not to Use It\nEmpathy must be genuine—fake robotic repeating feels manipulative.",
                "example": "FBI negotiator Chris Voss used simple mirroring and calm labeling during bank hostage standoffs, getting armed suspects to release hostages peacefully without firing a shot.",
                "boundary": "Understanding someone's feelings doesn't mean agreeing to an unfair deal.",
                "action_item": "In your next tricky conversation, start a sentence with 'It seems like...' or 'It sounds like...' before pitching your point.",
                "quote": "He who has learned to disagree without being disagreeable has discovered the most valuable secret of negotiation.",
                "visual_diagram": "graph TD\n  Tense[\"Tense Disagreement\"] --> Listen[\"Mirror & Label Emotion\"]\n  Listen --> Safe[\"Other Side Feels Heard\"]\n  Safe --> Open[\"Better Deal Together\"]"
            }
        ]
    },
    {
        "title": "The Checklist Manifesto",
        "author": "Atul Gawande",
        "publisher": "Metropolitan Books",
        "topic": "Productivity",
        "description": "How simple 5-step checklists prevent catastrophic errors even for world-class surgeons and pilots.",
        "ideas": [
            {
                "title": "Checklists Beat Memory Under Pressure",
                "one_liner": "Smart people still make silly mistakes under stress—a short checklist catches what memory drops.",
                "summary": "Modern work is too complex to hold in your head when things get busy. A short, clear checklist of critical steps frees your brain to focus on hard judgment calls.",
                "detailed_explanation": "### How It Works\nChecklists aren't about dumbing down experts; they handle the obvious routine checks automatically so experts have full brainpower for surprises.\n\n### Why We Get It Wrong\nExperienced pros often feel checklists are insulting—until a skipped basic step causes a disaster.\n\n### When Not to Use It\nDon't build 80-item bureaucratic checklists that nobody reads; keep them to 5–9 crucial items.",
                "example": "When the World Health Organization introduced a 90-second surgical safety checklist across hospitals worldwide, major surgical complications dropped by over 35% and deaths fell nearly in half.",
                "boundary": "Checklists verify the essentials, not every tiny detail.",
                "action_item": "Write a 5-item pre-launch checklist for a task you repeat every week (like sending a report or deploying code).",
                "quote": "Under conditions of complexity, not only are checklists a help, they are required for success.",
                "visual_diagram": "graph TD\n  Stress[\"High-Pressure Task\"] --> Memory[\"Rely on Memory Only\"]\n  Stress --> List[\"5-Item Checklist\"]\n  Memory --> Miss[\"Avoidable Errors\"]\n  List --> Safe[\"Consistent Excellence\"]"
            }
        ]
    },
    {
        "title": "7 Powers: The Foundations of Business Strategy",
        "author": "Hamilton Helmer",
        "publisher": "Deep Strategy",
        "topic": "Strategy",
        "description": "The seven durable advantages that let great businesses earn lasting profits without getting copied.",
        "ideas": [
            {
                "title": "Scale Economies & Switching Costs",
                "one_liner": "A real business moat makes it painful for rivals to copy you—not just nice to have.",
                "summary": "Being slightly better isn't a strategy because competitors copy features quickly. Lasting business power comes from structural advantages like lower cost at scale, network effects, or high switching costs.",
                "detailed_explanation": "### How It Works\nTrue business power has two parts: a clear benefit (higher prices or lower costs) and a real barrier stopping competitors from matching it.\n\n### Why We Get It Wrong\nTeams mistake 'working hard' or 'great customer service' for a moat when any funded rival can copy both.\n\n### When Not to Use It\nEarly startups need product-market fit before worrying about long-term moats.",
                "example": "Netflix spent billions on original shows; because it had over 200 million subscribers, the cost per viewer was tiny compared to smaller streaming rivals.",
                "boundary": "Moats protect existing value, but you still must keep delighting customers.",
                "action_item": "Ask about your product or career: 'What gets stronger and harder to copy the bigger or more experienced I get?'",
                "quote": "Strategy is the study of the fundamental determinants of potential business value.",
                "visual_diagram": "graph TD\n  Growth[\"Company Grows\"] --> Moat{\"Real Barrier?\"}\n  Moat -->|No| Copy[\"Rivals Copy Fast\"]\n  Moat -->|Yes| Power[\"Lasting Advantage\"]"
            }
        ]
    },
    {
        "title": "Seeking Wisdom: From Darwin to Munger",
        "author": "Peter Bevelin",
        "publisher": "PCA Publications",
        "topic": "Mental Models",
        "description": "A clear field guide to how human thinking goes wrong—and the mental tools that keep judgment sharp.",
        "ideas": [
            {
                "title": "Incentives Drive Behavior",
                "one_liner": "Show me the incentive, and I will show you the outcome.",
                "summary": "People rarely act purely on what you ask them to do—they act on what gets rewarded. Before blaming someone's character, look at what the system pays or praises them for.",
                "detailed_explanation": "### How It Works\nEven honest people bend their judgment without realizing it when their paycheck or status depends on a certain answer.\n\n### Why We Get It Wrong\nWe assume good intentions or training will override badly designed rewards.\n\n### When Not to Use It\nDon't become cynical—intrinsic pride and fairness matter too, just align rewards with them.",
                "example": "FedEx used to pay night-shift cargo loaders by the hour, and planes constantly left late. The moment FedEx switched to paying a flat shift rate and letting crews go home once planes were loaded, delays vanished overnight.",
                "boundary": "Money isn't the only incentive—status, autonomy, and pride often motivate even more.",
                "action_item": "Look at a frustrating recurring problem at work and ask: 'How is our current setup accidentally rewarding this behavior?'",
                "quote": "Never think about something else when you should be thinking about the power of incentives.",
                "visual_diagram": "graph TD\n  System[\"Rules & Rewards\"] --> Behavior[\"What People Actually Do\"]\n  Behavior --> Result[\"Real Outcome\"]"
            }
        ]
    },
    {
        "title": "The Mom Test",
        "author": "Rob Fitzpatrick",
        "publisher": "CreateSpace",
        "topic": "Strategy",
        "description": "How to talk to customers and learn if your idea is actually good when everyone is trying to be polite.",
        "ideas": [
            {
                "title": "Ask About Past Behavior, Not Future Opinions",
                "one_liner": "Never ask 'Would you use this?'—ask 'When was the last time you tried to solve this problem?'",
                "summary": "People lie to be nice when you pitch your idea ('Sounds awesome!'). Ask specific questions about their actual past habits, frustrations, and what they've already paid for instead.",
                "detailed_explanation": "### How It Works\nFacts about the past ('I spent 3 hours fixing this yesterday') are real; promises about the future ('Sure, I'd totally buy that!') are cheap.\n\n### Why We Get It Wrong\nWe want compliments and validation, so we pitch our idea first and trap people into being polite.\n\n### When Not to Use It\nOnce you're selling a finished product, clear pitching matters—during discovery, just listen.",
                "example": "A founder building a digital cookbook app asked friends 'Do you like cooking?' and got enthusiastic yeses—then launched to zero sales because nobody actually paid for recipes when YouTube was free.",
                "boundary": "For brand-new inventions people have never seen, watch how they struggle today rather than asking them to design your product.",
                "action_item": "In your next user chat, go 10 minutes without mentioning your idea—only ask about how they handle the problem right now.",
                "quote": "The measure of usefulness of an early customer conversation is whether it gives us concrete facts about our users' lives.",
                "visual_diagram": "graph TD\n  Chat[\"Customer Chat\"] --> Ask{\"What Do You Ask?\"}\n  Ask -->|Future Opinion| Fluff[\"Polite Compliments\"]\n  Ask -->|Past Behavior| Truth[\"Real Problem & Proof\"]"
            }
        ]
    },
    {
        "title": "Designing Your Life",
        "author": "Bill Burnett & Dave Evans",
        "publisher": "Knopf",
        "topic": "Productivity",
        "description": "Using Stanford design thinking to build a meaningful career through small, low-risk prototypes.",
        "ideas": [
            {
                "title": "Prototype Your Next Chapter",
                "one_liner": "Don't try to think your way to the perfect career—run small, cheap real-world experiments.",
                "summary": "You can't figure out if you'll love a job by staring at a spreadsheet. Have two coffee chats, shadow someone for an afternoon, or try a tiny weekend project to test reality first.",
                "detailed_explanation": "### How It Works\nDesigners never build a final product on the first try; they build quick, cheap prototypes to see what actually works.\n\n### Why We Get It Wrong\nWe wait until we're 100% certain before making a move, which keeps us stuck for years.\n\n### When Not to Use It\nDon't treat life like endless dabbling—once a test excites you, commit for real.",
                "example": "An executive convinced she wanted to open a cafe spent two weekends working shifts at a friend's bakery—and quickly realized she loved baking at home, not 5 AM retail management, saving her life savings.",
                "boundary": "Prototype to learn fast, not to procrastinate.",
                "action_item": "Pick one career or creative idea you're curious about and message one person doing it today for a 15-minute chat.",
                "quote": "You can't know where you're going until you start testing where you might want to be.",
                "visual_diagram": "graph TD\n  Idea[\"Curious Idea\"] --> Test[\"Small 1-Week Prototype\"]\n  Test --> Learn[\"Real Experience & Feedback\"]\n  Learn --> Next[\"Smart Next Step\"]"
            }
        ]
    },
    {
        "title": "How to Win Friends and Influence People",
        "author": "Dale Carnegie",
        "publisher": "Simon & Schuster",
        "topic": "Psychology",
        "description": "The timeless guide to genuine connection, persuasion, and getting people on your side without friction.",
        "ideas": [
            {
                "title": "Be Genuinely Interested, Not Interesting",
                "one_liner": "You make more friends in two months by being interested in others than in two years trying to impress them.",
                "summary": "People care far more about their own goals, worries, and stories than yours. Asking thoughtful questions and remembering small details builds instant trust and goodwill.",
                "detailed_explanation": "### How It Works\nTrue warmth comes from curiosity about the other person's world rather than performing to look smart.\n\n### Why We Get It Wrong\nNervousness makes us talk about ourselves to prove our worth.\n\n### When Not to Use It\nCuriosity only works when it's sincere; fake flattery is spotted instantly.",
                "example": "Theodore Roosevelt stayed up late reading about whatever topic his next morning's guest loved—from ranching to botany—so every visitor left feeling deeply understood.",
                "boundary": "Still share your own honest thoughts when asked; connection is a two-way street.",
                "action_item": "In your next conversation, ask two follow-up questions about the other person before talking about yourself.",
                "quote": "Talk to someone about themselves and they'll listen for hours.",
                "visual_diagram": "graph TD\n  Meet[\"Meet Someone\"] --> Ask[\"Ask Thoughtful Questions\"]\n  Ask --> Trust[\"Genuine Warmth & Trust\"]"
            }
        ]
    },
    {
        "title": "The Obstacle Is the Way",
        "author": "Ryan Holiday",
        "publisher": "Portfolio",
        "topic": "Stoicism",
        "description": "The ancient Stoic art of turning trials, setbacks, and frustration into your greatest advantage.",
        "ideas": [
            {
                "title": "Flip Every Setback Into Fuel",
                "one_liner": "What stands in the way becomes the way.",
                "summary": "Every obstacle is an unasked-for training ground. When a plan breaks, you can either complain about how unfair it is or use the constraint to build strength, creativity, and grit.",
                "detailed_explanation": "### How It Works\nMarcus Aurelius wrote that obstacles don't stop action—they become the new raw material for action. Separate what happened (objective fact) from the story you tell about it.\n\n### Why We Get It Wrong\nSetbacks bruise our ego and make us wish reality were easier.\n\n### When Not to Use It\nDon't ignore real burnout or genuine danger—rest and smart pivots are also forms of strength.",
                "example": "When Thomas Edison's laboratory burned down in 1914, destroying years of prototypes, he told his son to fetch his mother because she'd never see a fire like this again—and used the fresh start to rebuild a better, stronger lab.",
                "boundary": "Accepting what happened doesn't mean tolerating bad treatment; it means responding cleanly without self-pity.",
                "action_item": "Take one annoying roadblock from today and write down one useful skill or backup plan it is forcing you to build.",
                "quote": "The impediment to action advances action. What stands in the way becomes the way.",
                "visual_diagram": "graph TD\n  Block[\"Unexpected Setback\"] --> Lens{\"How Do You View It?\"}\n  Lens -->|Victim| Stuck[\"Frustration & Quit\"]\n  Lens -->|Stoic| Fuel[\"Fuel for Growth\"]"
            }
        ]
    },
    {
        "title": "Ego Is the Enemy",
        "author": "Ryan Holiday",
        "publisher": "Portfolio",
        "topic": "Stoicism",
        "description": "Why pride and needing to look smart quietly ruin ambition, success, and recovery.",
        "ideas": [
            {
                "title": "Stay a Student, Even After Winning",
                "one_liner": "Confidence is earned through real work; ego is needing to feel superior before or after.",
                "summary": "Ego makes you ignore feedback when starting out, get sloppy after winning, and blame everyone else when you fail. Staying humble keeps you learning faster than everyone around you.",
                "detailed_explanation": "### How It Works\nThe moment you think you've 'arrived,' you stop practicing the basics that got you there. Treating every room like a classroom keeps your edge sharp.\n\n### Why We Get It Wrong\nPraise feels good, and admitting you don't know feels vulnerable.\n\n### When Not to Use It\nHumility shouldn't turn into self-doubt—know your strengths while staying hungry to learn.",
                "example": "After winning championship rings, basketball coach Bill Walsh still studied game film obsessively and welcomed harsh critiques from junior assistants, refusing to rest on past glory.",
                "boundary": "Don't confuse humility with letting others walk over you.",
                "action_item": "Ask one teammate or mentor today: 'What is one blindspot I'm missing right now?' and just listen without defending.",
                "quote": "Impress yourself with your work, not others with your talk.",
                "visual_diagram": "graph TD\n  Success[\"Early Win\"] --> Ego[\"Think You Know Everything\"]\n  Success --> Student[\"Stay Hungry & Humble\"]\n  Ego --> Decline[\"Sloppy Habits\"]\n  Student --> Mastery[\"Long-Term Mastery\"]"
            }
        ]
    },
    {
        "title": "The Lean Startup",
        "author": "Eric Ries",
        "publisher": "Crown Business",
        "topic": "Strategy",
        "description": "How modern teams test risky ideas fast with minimal waste using Build-Measure-Learn loops.",
        "ideas": [
            {
                "title": "Build-Measure-Learn Loop",
                "one_liner": "Don't spend six months building something nobody wants—ship the simplest test this week.",
                "summary": "The biggest risk for any new project isn't building it wrong; it's building something nobody actually cares about. Launch a Minimum Viable Product (MVP) fast to learn from real behavior.",
                "detailed_explanation": "### How It Works\nTurn your biggest assumption into a quick experiment, put it in front of real users, measure what they actually do, and decide whether to pivot or double down.\n\n### Why We Get It Wrong\nPolishing features in secret feels safe because nobody can reject you yet.\n\n### When Not to Use It\nIn safety-critical fields like medical devices or aviation, never ship unfinished hardware.",
                "example": "Dropbox founder Drew Houston didn't build full sync infrastructure first—he recorded a 3-minute demo video showing how it would work, and 75,000 people joined the waitlist overnight.",
                "boundary": "MVP means minimum *viable*—it still has to solve one real problem cleanly.",
                "action_item": "Take a project you're planning and ask: 'How could we test the core idea in 48 hours without building the full thing?'",
                "quote": "The only way to win is to learn faster than anyone else.",
                "visual_diagram": "graph TD\n  Idea[\"Core Assumption\"] --> Build[\"Smallest Possible Test\"]\n  Build --> Measure[\"Real User Behavior\"]\n  Measure --> Learn[\"Pivot or Double Down\"]"
            }
        ]
    },
    {
        "title": "Hooked: How to Build Habit-Forming Products",
        "author": "Nir Eyal",
        "publisher": "Portfolio",
        "topic": "Psychology",
        "description": "The four-step loop behind products people return to naturally—and how to use it for good habits.",
        "ideas": [
            {
                "title": "The Hook Model (Trigger-Action-Reward-Investment)",
                "one_liner": "Habits form when a clear cue leads to an easy action, a surprising reward, and a small personal investment.",
                "summary": "Products and personal habits stick when they follow four steps: a clear Trigger, a tiny Action, a Variable Reward that keeps things interesting, and an Investment that makes next time even better.",
                "detailed_explanation": "### How It Works\nEvery cycle you complete—like saving a note or logging a workout—makes you slightly more invested in coming back tomorrow.\n\n### Why We Get It Wrong\nWe try to force habits through pure willpower instead of making the first action tiny and the reward immediate.\n\n### When Not to Use It\nUse habit design to help people live healthier, smarter lives—never to trap them in mindless scrolling.",
                "example": "Duolingo sends a friendly daily reminder (Trigger), offers a 3-minute lesson (Action), celebrates with streaks and XP (Reward), and builds your word streak (Investment).",
                "boundary": "Don't add gamified streaks if the core activity doesn't deliver real value.",
                "action_item": "Design one good habit today by pairing a clear daily cue with a 2-minute version of the habit and a small reward.",
                "quote": "Habits are formed by frequent, rewarding repetition—not by sheer willpower.",
                "visual_diagram": "graph TD\n  Trigger[\"1. Trigger\"] --> Action[\"2. Easy Action\"]\n  Action --> Reward[\"3. Reward\"]\n  Reward --> Invest[\"4. Small Investment\"]\n  Invest --> Trigger"
            }
        ]
    },
    {
        "title": "Made to Stick",
        "author": "Chip Heath & Dan Heath",
        "publisher": "Random House",
        "topic": "Psychology",
        "description": "Why some ideas survive and spread effortlessly while others are forgotten five minutes later.",
        "ideas": [
            {
                "title": "Curse of Knowledge",
                "one_liner": "Once you know something well, it's surprisingly hard to remember what it felt like not to know it.",
                "summary": "Experts pack presentations with jargon and abstract stats because they forgot how confusing those words are to newcomers. Concrete stories, simple language, and vivid visuals make ideas stick.",
                "detailed_explanation": "### How It Works\nOur brains remember concrete images ('a man on the moon by 1969') far better than vague slogans ('optimize aerospace leadership').\n\n### Why We Get It Wrong\nUsing complex buzzwords makes speakers feel smart, even when the audience tunes out.\n\n### When Not to Use It\nWhen talking solely with fellow specialists who need exact technical precision, shorthand is fine.",
                "example": "In a famous Stanford study, 'tappers' tapped the rhythm of 'Happy Birthday' on a table and guessed listeners would recognize it 50% of the time—listeners guessed right only 2.5% of the time because the tappers heard the full tune in their heads.",
                "boundary": "Simple doesn't mean dumbed-down—find the sharpest core truth.",
                "action_item": "Read your last email or slide deck and replace two abstract buzzwords with one concrete real-world example.",
                "quote": "The difference between a great idea and a forgotten one is how concretely it is told.",
                "visual_diagram": "graph TD\n  Message[\"Your Idea\"] --> Style{\"How Is It Shared?\"}\n  Style -->|Abstract Jargon| Forget[\"Forgotten Fast\"]\n  Style -->|Simple & Concrete| Stick[\"Remembered & Shared\"]"
            }
        ]
    },
    {
        "title": "The Creative Act: A Way of Being",
        "author": "Rick Rubin",
        "publisher": "Penguin Press",
        "topic": "Productivity",
        "description": "Legendary producer Rick Rubin's reflections on creativity, noticing details, and finishing meaningful work.",
        "ideas": [
            {
                "title": "Separate Creating from Judging",
                "one_liner": "Never edit while you create—let ideas flow freely first, and judge them tomorrow.",
                "summary": "Your inner critic is essential for polishing good work, but if it shows up while you're brainstorming or drafting, it kills good ideas before they can breathe.",
                "detailed_explanation": "### How It Works\nCreative flow requires playful experimentation. Put your editor in another room during the first draft, then bring the editor back with fresh eyes later.\n\n### Why We Get It Wrong\nFear of making something bad makes us critique every single sentence before finishing a page.\n\n### When Not to Use It\nDon't skip the editing phase entirely—great work needs both wild creation and sharp pruning.",
                "example": "Rick Rubin encouraged bands like the Red Hot Chili Peppers and Johnny Cash to record raw, unfiltered acoustic takes in a living room before worrying about studio perfection.",
                "boundary": "Finish and polish before shipping—freedom is for drafting, standards are for publishing.",
                "action_item": "Set a 15-minute timer today to write or sketch freely without hitting backspace or judging quality.",
                "quote": "The best work happens when you turn off the judge and just pay attention.",
                "visual_diagram": "graph TD\n  Draft[\"1. Free Creation (No Judging)\"] --> Rest[\"2. Short Break\"]\n  Rest --> Edit[\"3. Sharp Editing\"]\n  Edit --> Ship[\"Original Work\"]"
            }
        ]
    },
    {
        "title": "Start with Why",
        "author": "Simon Sinek",
        "publisher": "Portfolio",
        "topic": "Strategy",
        "description": "How great leaders inspire lasting loyalty by leading with purpose before features.",
        "ideas": [
            {
                "title": "The Golden Circle (Why -> How -> What)",
                "one_liner": "People don't buy what you do; they buy why you do it.",
                "summary": "Most companies communicate from the outside in ('Here is our product and features'). Inspiring leaders communicate from the inside out: start with why it matters, then how you do it, then what you built.",
                "detailed_explanation": "### How It Works\nFeatures attract bargain hunters; a clear, authentic purpose attracts loyal believers who stick with you through ups and downs.\n\n### Why We Get It Wrong\nListing specs and bullet points feels concrete and safe, while talking about purpose feels vulnerable.\n\n### When Not to Use It\nA strong 'Why' never excuses a broken product—your 'What' still has to work great.",
                "example": "In 1903, Samuel Langley had huge government funding and press to build the first airplane, chasing fame and money. The Wright brothers had zero funding—just a deep belief in flight—and inspired their small bike-shop team to fly first.",
                "boundary": "Purpose has to be backed by real action, not empty marketing posters.",
                "action_item": "Write one clear sentence explaining *why* your current project should matter to the person using it.",
                "quote": "Working hard for something we don't care about is called stress; working hard for something we love is called passion.",
                "visual_diagram": "graph TD\n  Why[\"1. WHY (Purpose)\"] --> How[\"2. HOW (Process)\"]\n  How --> What[\"3. WHAT (Product)\"]\n  What --> Loyal[\"Deep Trust & Loyalty\"]"
            }
        ]
    },
    {
        "title": "Grit",
        "author": "Angela Duckworth",
        "publisher": "Scribner",
        "topic": "Productivity",
        "description": "The power of passion and perseverance—why sticking with one craft beats raw talent over time.",
        "ideas": [
            {
                "title": "Effort Counts Twice",
                "one_liner": "Talent × Effort = Skill, and Skill × Effort = Achievement.",
                "summary": "Raw talent gives you a head start, but consistent daily effort counts twice: first it turns talent into real skill, and then it turns skill into meaningful results over years.",
                "detailed_explanation": "### How It Works\nTalent without practice stays an unrealized hint. Steady, deliberate effort compounds every month into mastery that natural talent alone can't touch.\n\n### Why We Get It Wrong\nWe worship effortless geniuses in movies and quit the moment something feels hard.\n\n### When Not to Use It\nGrit isn't stubbornly sticking with a dead-end job—keep adjusting your method while staying committed to your long-term goal.",
                "example": "West Point cadets who survived the grueling first summer ('Beast Barracks') weren't the ones with the highest SAT scores or athletic rankings—they were the ones scoring highest on grit.",
                "boundary": "Be gritty about your big direction, flexible about your daily tactics.",
                "action_item": "Pick one skill you want to master this year and commit to 20 minutes of focused daily practice—no skipping two days in a row.",
                "quote": "Enthusiasm is common. Endurance is rare.",
                "visual_diagram": "graph TD\n  Talent[\"Starting Talent\"] --> Effort1[\"Daily Effort\"]\n  Effort1 --> Skill[\"Real Skill\"]\n  Skill --> Effort2[\"More Effort Over Time\"]\n  Effort2 --> Mastery[\"Lasting Achievement\"]"
            }
        ]
    },
    {
        "title": "The War of Art",
        "author": "Steven Pressfield",
        "publisher": "Black Irish Entertainment",
        "topic": "Productivity",
        "description": "Winning the inner creative battle against procrastination, fear, and self-doubt.",
        "ideas": [
            {
                "title": "Turn Pro & Beat Resistance",
                "one_liner": "The amateur waits for inspiration; the professional sits down and works every day.",
                "summary": "The closer you get to doing work you truly care about, the louder procrastination and distraction ('Resistance') scream. Showing up on a schedule defeats Resistance before it starts.",
                "detailed_explanation": "### How It Works\nResistance is invisible fear disguised as 'let me clean my desk first' or 'I'll start Monday.' Treating your craft like a daily job removes the drama.\n\n### Why We Get It Wrong\nWe wait to feel motivated before starting, when in reality starting creates the motivation.\n\n### When Not to Use It\nShowing up daily doesn't mean ignoring real rest—professionals schedule recovery just like athletes do.",
                "example": "Author Somerset Maugham was asked if he wrote on a schedule or only when inspired: 'I write only when inspiration strikes. Fortunately it strikes every morning at nine o'clock sharp.'",
                "boundary": "Discipline works best on a sustainable daily rhythm, not frantic all-nighters.",
                "action_item": "Set a specific start time tomorrow morning for your hardest task—and start even if you don't feel ready.",
                "quote": "The professional shows up every day, no matter how they feel.",
                "visual_diagram": "graph TD\n  Start[\"Want to Do Great Work\"] --> Fear[\"Procrastination / Resistance\"]\n  Fear --> Amateur[\"Wait for Mood\"]\n  Fear --> Pro[\"Start on Schedule\"]\n  Pro --> Flow[\"Momentum Follows\"]"
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
