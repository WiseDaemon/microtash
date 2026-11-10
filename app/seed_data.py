"""
Comprehensive seed knowledge base for Deepstash microlearning.
Contains atomic insights, key takeaways, quotes, and action items from renowned books and thinkers.
"""

DEFAULT_STASHES = [
    {
        "id": "stash_mental_models",
        "title": "Mental Models for Clear Thinking",
        "description": "Powerful frameworks from Charlie Munger, Daniel Kahneman, and Richard Feynman to make better decisions.",
        "icon": "brain",
        "color": "indigo"
    },
    {
        "id": "stash_habits_productivity",
        "title": "High Performance & Atomic Habits",
        "description": "Bite-sized behavioral hacks from James Clear, Cal Newport, and Greg McKeown.",
        "icon": "zap",
        "color": "emerald"
    },
    {
        "id": "stash_stoic_armor",
        "title": "Stoic Armor for Modern Chaos",
        "description": "Timeless resilience, emotional mastery, and clarity from Marcus Aurelius and Seneca.",
        "icon": "shield",
        "color": "amber"
    },
    {
        "id": "stash_wealth_psychology",
        "title": "The Psychology of Wealth & Leverage",
        "description": "Building freedom and asymmetric upside with Naval Ravikant and Morgan Housel.",
        "icon": "trending-up",
        "color": "teal"
    }
]

DEFAULT_IDEAS = [
    # Mental Models
    {
        "id": "idea_inversion",
        "title": "The Inversion Principle",
        "one_liner": "Avoid stupidity rather than striving for brilliant moves.",
        "summary": "Most problems are easier to solve when you flip them upside down. Instead of asking 'How do I succeed?', ask 'How could I guarantee absolute failure?' and systematically eliminate those failure vectors.",
        "detailed_explanation": "Inversion was popularized by German mathematician Carl Jacobi, who famously advised 'man muss immer umkehren' (invert, always invert). In cognitive psychology and decision science, human beings are notoriously terrible at predicting the exact sequences required for brilliant success, but exceptionally good at identifying obvious traps and pitfalls that lead to disaster. By identifying the root causes of failure—such as leverage, hubris, lack of sleep, or procrastination—and systematically removing them, success becomes the natural default residue.",
        "example": "Charlie Munger used inversion during World War II when he was a meteorologist clearing military flights. Instead of asking 'How do I keep these pilots safe?', he asked 'What weather conditions will kill these pilots and how do I avoid sending anyone into those conditions?' In business, Vanguard's John Bogle didn't try to pick the hottest winning stocks; he inverted the problem by minimizing fees, turnover, and trading costs—which guaranteed beating 85% of active fund managers over 20 years.",
        "visual_diagram": """graph LR
  subgraph Standard["Standard Approach (Fragile)"]
    A[Strive for Brilliance] --> B[Complex Forecasting] --> C[Hidden Landmines & Failure]
  end
  subgraph Inversion["Inversion Approach (Robust)"]
    D[Define Absolute Catastrophe] --> E[Systematically Eliminate Traps] --> F[Success as Default Residue]
  end
  style Standard fill:#1e1b4b,stroke:#6366f1,color:#fff
  style Inversion fill:#064e3b,stroke:#10b981,color:#fff""",
        "quote": "Invert, always invert: Turn a situation or problem upside down. What happens if all our assumptions are wrong?",
        "action_item": "Before starting your next major project, write down the 3 fastest ways it could fail. Put guardrails on each immediately.",
        "author": "Charlie Munger",
        "source": "Poor Charlie's Almanack",
        "topic": "Mental Models",
        "tags": ["Decision Making", "Thinking", "Strategy"],
        "read_time_mins": 1,
        "color_theme": "indigo",
        "likes": 142,
        "saved_count": 89
    },
    {
        "id": "idea_first_principles",
        "title": "First-Principles Thinking",
        "one_liner": "Boil problems down to their fundamental truths instead of reasoning by analogy.",
        "summary": "Reasoning by analogy means copying what others are doing with minor tweaks. First-principles reasoning deconstructs a reality into its most basic physical truths and builds a conclusion up from scratch.",
        "detailed_explanation": "First principles thinking is the practice of actively questioning every assumption you think you know about a given problem or scenario, then creating new knowledge and solutions from the ground up. Most people navigate life reasoning by analogy—copying what someone else did with slight cosmetic tweaks. While analogy saves cognitive energy, it blinds you to step-function breakthroughs. First principles thinking forces you to isolate the immutable physical laws or fundamental axioms and build upwards without dogmatic precedent.",
        "example": "When Elon Musk founded SpaceX, aerospace contractors quoted rocket costs at $65 million each. Instead of accepting this price, Musk broke down what a rocket is physically made of: aerospace-grade aluminum alloys, titanium, copper, and carbon fiber. The raw material cost was only about 2% of the typical rocket price. SpaceX built their manufacturing in-house, cutting launch costs by over 70% and creating the world's most successful space transportation company.",
        "visual_diagram": """graph TD
  A[Complex Problem / Convention] -->|Deconstruct Assumptions| B[Foundational Truths & Physics]
  B -->|Reason Upwards from Scratch| C[Original Step-Function Solution]
  style A fill:#312e81,stroke:#6366f1,color:#fff
  style B fill:#831843,stroke:#f43f5e,color:#fff
  style C fill:#064e3b,stroke:#10b981,color:#fff""",
        "quote": "First principles is a physics way of looking at the world. You boil things down to the most fundamental truths and say, 'What are we sure is true?'",
        "action_item": "Take one expensive recurring cost in your business or life. Ask 'What are the raw components of this?' Re-evaluate the price from ground up.",
        "author": "Elon Musk & Aristotle",
        "source": "Foundational Physics & Philosophy",
        "topic": "Mental Models",
        "tags": ["Innovation", "Problem Solving", "Physics"],
        "read_time_mins": 2,
        "color_theme": "sky",
        "likes": 210,
        "saved_count": 134
    },
    {
        "id": "idea_circle_competence",
        "title": "The Circle of Competence",
        "one_liner": "Knowing the perimeter of what you don't know is vastly more important than the size of the circle.",
        "summary": "Inside your circle of competence, you have real edge and genuine understanding. Outside it, you are simply gambling. True expertise is having the discipline to say 'I do not know' whenever you step beyond your perimeter.",
        "detailed_explanation": "The Circle of Competence model, developed by Warren Buffett and Charlie Munger, dictates that each person accumulates genuine insight into certain narrow areas through years of experience, natural curiosity, and rigorous trial-and-error. The critical insight of the model is that the absolute size of your circle does not matter at all. What matters catastrophically is knowing where the boundary lies. Stepping outside that circle without realizing it leads to overconfidence, disastrous financial bets, and ego-driven blindness.",
        "example": "Buffett famously avoided investing in dot-com tech stocks during the late 1990s bull run despite intense public ridicule and headlines asking 'Has Warren Lost His Touch?'. He stated simply that software code and tech valuations fell outside his circle of competence. When the NASDAQ crashed 80% in 2000, Berkshire Hathaway preserved its capital entirely and used cash reserves to buy distressed bargains.",
        "visual_diagram": """graph TD
  subgraph Competence_Map["Boundary of Competence"]
    Inside["INSIDE CIRCLE<br/>Authentic Edge & Mastery<br/>(Bet Confidently)"]
    Perimeter["PERIMETER<br/>Intellectual Honesty<br/>('I Do Not Know')"]
    Outside["OUTSIDE PERIMETER<br/>Blind Spots & Noise<br/>(Pass / Delegate)"]
    Inside --> Perimeter --> Outside
  end
  style Inside fill:#064e3b,stroke:#10b981,color:#fff
  style Perimeter fill:#78350f,stroke:#f59e0b,color:#fff
  style Outside fill:#881337,stroke:#f43f5e,color:#fff""",
        "quote": "It is not a competency if you don't know the edge of it.",
        "action_item": "Identify the 2 domains where you possess authentic judgment. Say 'No' this week to any opportunity outside that boundary.",
        "author": "Warren Buffett",
        "source": "Berkshire Hathaway Shareholder Letters",
        "topic": "Mental Models",
        "tags": ["Competence", "Focus", "Self-Awareness"],
        "read_time_mins": 1,
        "color_theme": "purple",
        "likes": 98,
        "saved_count": 67
    },
    {
        "id": "idea_second_order",
        "title": "Second-Order Thinking",
        "one_liner": "Ask 'And then what?' to foresee the delayed consequences of quick fixes.",
        "summary": "First-order thinking looks only at immediate gratification and direct effects. Second-order thinking evaluates the ripple effects, secondary reactions, and counter-intuitive outcomes over 6 months, 2 years, and 5 years.",
        "detailed_explanation": "First-order consequences are immediate, direct, and obvious. Second-order consequences are indirect, delayed, and often counter-intuitive. In complex adaptive systems (economies, ecosystems, organizations), every action causes reactions, feedback loops, and unintended adaptations. People who think only in the first order make decisions that feel great in the moment but create systemic catastrophe down the road. Second-order thinkers always ask: 'And then what happens next?'",
        "example": "The 'Cobra Effect' in colonial Delhi: The British government wanted to reduce venomous cobras, so they offered a cash bounty for every dead cobra brought in. First-order result: people killed cobras. Second-order result: enterprising locals realized they could breed cobras in their basements to collect more bounty money. When the government canceled the program, breeders released thousands of worthless snakes into the streets, leaving Delhi with more cobras than when they started.",
        "visual_diagram": """graph LR
  Decision[Decision / Policy] -->|Immediate| R1[1st Order: Direct Gratification]
  R1 -->|6-12 Months| R2[2nd Order: Systemic Adaptations & Feedback]
  R2 -->|2-5 Years| R3[3rd Order: Compounding Asymmetric Outcome]
  style Decision fill:#312e81,stroke:#6366f1,color:#fff
  style R1 fill:#78350f,stroke:#f59e0b,color:#fff
  style R2 fill:#064e3b,stroke:#10b981,color:#fff
  style R3 fill:#1e1b4b,stroke:#818cf8,color:#fff""",
        "quote": "Failing to consider second- and third-order consequences is the cause of a great many painfully bad decisions.",
        "action_item": "Next time you are tempted by a shortcut, draw a 3-column table: Immediate effect, 6-month effect, 2-year effect.",
        "author": "Howard Marks & Ray Dalio",
        "source": "The Most Important Thing",
        "topic": "Mental Models",
        "tags": ["Long Term", "Strategy", "Consequences"],
        "read_time_mins": 2,
        "color_theme": "indigo",
        "likes": 184,
        "saved_count": 115
    },

    # Habits & Productivity
    {
        "id": "idea_two_minute_rule",
        "title": "The Two-Minute Rule",
        "one_liner": "When you start a new habit, it should take less than two minutes to do.",
        "summary": "The objective of a new habit isn't to master the entire routine on day one; it's simply to establish the ritual of showing up. You have to standardize before you can optimize. Make the barrier to entry microscopic.",
        "detailed_explanation": "The Two-Minute Rule from James Clear's Atomic Habits leverages behavioral momentum and friction reduction. Human brains are biologically wired to conserve metabolic energy, triggering resistance and procrastination whenever a task feels daunting. By shrinking any desired behavior down to an action that requires less than 120 seconds, you bypass the amygdala's threat response. The primary objective of habit formation is not optimal performance; it is behavioral standardization. Once a habit is established, it can easily be optimized.",
        "example": "A runner who struggled with consistency made a rule: he was only allowed to put on his running shoes and step outside for 2 minutes. Once the two minutes were up, he was permitted to stop and go back inside. For weeks he simply went out for 2 minutes. Soon, the friction of starting was completely gone, and running 5 miles became as frictionless as brushing his teeth.",
        "visual_diagram": """graph LR
  BigGoal[Intimidating Habit<br/>E.g. 1-Hour Workout] -->|Shrink to < 120s| Gateway[2-Minute Ritual<br/>Tie Running Shoes & Step Out]
  Gateway -->|Bypasses Amygdala Friction| Flow[Standardized Behavioral Ritual]
  Flow -->|Habit Standardized| Scale[Optimization & Compounding Scale]
  style BigGoal fill:#881337,stroke:#f43f5e,color:#fff
  style Gateway fill:#064e3b,stroke:#10b981,color:#fff
  style Flow fill:#312e81,stroke:#6366f1,color:#fff
  style Scale fill:#0f766e,stroke:#14b8a6,color:#fff""",
        "quote": "A habit must be established before it can be improved.",
        "action_item": "Downscale your hardest goal into a 2-minute version: 'Read 30 pages' becomes 'Open book and read 1 page'; 'Workout 1 hour' becomes 'Tie running shoes'.",
        "author": "James Clear",
        "source": "Atomic Habits",
        "topic": "Productivity",
        "tags": ["Habits", "Friction", "Discipline"],
        "read_time_mins": 1,
        "color_theme": "emerald",
        "likes": 320,
        "saved_count": 210
    },
    {
        "id": "idea_attention_residue",
        "title": "Attention Residue",
        "one_liner": "Switching tasks leaves a toxic mental residue that destroys cognitive output.",
        "summary": "When you switch from Task A to Task B, your attention does not immediately follow. A thick residue of cognitive bandwidth remains stuck thinking about the previous task. Rapid multitasking reduces your effective IQ by up to 10 points.",
        "detailed_explanation": "Dr. Sophie Leroy's research at the University of Minnesota uncovered that when people switch between tasks, their brain does not cleanly shift focus. Instead, a cognitive residue remains fixated on the unresolved elements of the previous task. This attention residue clogs working memory, slows processing speed, and drastically degrades analytical depth. Checking your inbox or a Slack message for just 15 seconds can disrupt deep focus for up to 23 minutes.",
        "example": "Software engineers at companies that implemented 'No-Meeting Wednesdays' and strict asynchronous communication reported a 44% increase in delivered code velocity and higher code quality. By eliminating the constant task-switching between Zoom calls, emails, and code reviews, their brains entered flow state without cognitive drag.",
        "visual_diagram": """graph TD
  TaskA[Deep Work Project A] -->|10-Second Inbox / Slack Glance| TaskB[Task B Interrupt]
  TaskB -->|Attempt to Return| Residue[Cognitive Residue Clogs Working Memory]
  Residue -->|20+ Minutes Cognitive Drag| Frag[Degraded Processing Speed & Surface Work]
  style TaskA fill:#064e3b,stroke:#10b981,color:#fff
  style TaskB fill:#78350f,stroke:#f59e0b,color:#fff
  style Residue fill:#881337,stroke:#f43f5e,color:#fff
  style Frag fill:#1e1b4b,stroke:#6366f1,color:#fff""",
        "quote": "To produce at your peak level you need to work for extended periods with full concentration on a single task free from distraction.",
        "action_item": "Batch check emails and Slack in two designated 20-minute windows per day (e.g., 11:30 AM and 4:30 PM). Close tabs in between.",
        "author": "Cal Newport",
        "source": "Deep Work",
        "topic": "Productivity",
        "tags": ["Deep Work", "Focus", "Cognition"],
        "read_time_mins": 2,
        "color_theme": "teal",
        "likes": 265,
        "saved_count": 190
    },
    {
        "id": "idea_hell_yeah_or_no",
        "title": "If It's Not a 'Hell Yeah!', It's a 'No'",
        "one_liner": "Eliminate lukewarm commitments to protect space for the truly extraordinary.",
        "summary": "We often say yes to opportunities simply because they are polite, easy, or mildly flattering. But every mediocre yes steals energy from your highest-conviction pursuits. If an invite doesn't evoke an enthusiastic 'Hell yeah!', decline gracefully.",
        "detailed_explanation": "Derek Sivers proposed this heuristic for anyone feeling overwhelmed by opportunities and obligations. As you gain skill and reputation, the world inundates you with mediocre invitations, speaking gigs, partnerships, and coffee chats. If you evaluate opportunities with a low threshold, your schedule quickly fills with lukewarm commitments that leave zero room for game-changing breakthroughs. If an opportunity doesn't evoke an immediate, visceral 'HELL YEAH!', your default answer must be an unapologetic 'No'.",
        "example": "Steve Jobs returned to Apple in 1997 when the company was 90 days from bankruptcy. Apple had dozens of product lines, printers, cameras, and computer variations. Jobs drew a simple 2x2 grid on a whiteboard: Consumer vs. Pro, Desktop vs. Portable. He slashed 70% of Apple's existing projects to focus exclusively on 4 products that were undeniable 'Hell Yeahs', saving Apple and launching the iMac and iPod.",
        "visual_diagram": """graph TD
  Request[Opportunity / Invitation] --> Triage{Does it spark a visceral<br/>'HELL YEAH!'?}
  Triage -->|Yes! 9/10 or 10/10| Accept[ACCEPT: Dedicate 100% Focus & Excellence]
  Triage -->|Lukewarm / Polite / 6-8| Decline[DECLINE: Preserve High-Leverage Bandwidth]
  style Request fill:#312e81,stroke:#6366f1,color:#fff
  style Triage fill:#78350f,stroke:#f59e0b,color:#fff
  style Accept fill:#064e3b,stroke:#10b981,color:#fff
  style Decline fill:#881337,stroke:#f43f5e,color:#fff""",
        "quote": "Saying yes to one thing means saying no to everything else you could have done with that time.",
        "action_item": "Audit your calendar for the coming week. Find at least one meeting or obligation that is merely lukewarm and politely cancel or delegate it.",
        "author": "Derek Sivers",
        "source": "Hell Yeah or No",
        "topic": "Productivity",
        "tags": ["Prioritization", "Time Management", "Boundaries"],
        "read_time_mins": 1,
        "color_theme": "amber",
        "likes": 178,
        "saved_count": 102
    },
    {
        "id": "idea_identity_habits",
        "title": "Identity-Based Habits",
        "one_liner": "The goal is not to read a book, the goal is to become a reader.",
        "summary": "Outcome-based habits focus on what you want to achieve (e.g. lose 10 lbs). Identity-based habits focus on who you want to become (e.g. I am the type of person who never misses a workout). Every action is a vote for the person you wish to be.",
        "detailed_explanation": "Most people attempt to change their behavior from the outside in: they focus on outcomes (losing 15 pounds, publishing a book) or processes (dieting, writing daily). But research shows sustainable behavior change only occurs when anchored in identity—your underlying beliefs about who you are. When a behavior aligns with your self-image, you no longer need willpower. Every small decision you make is either a vote confirming your chosen identity or a vote against it.",
        "example": "When offered a cigarette, Person A says, 'No thanks, I'm trying to quit.' Person B says, 'No thanks, I am not a smoker.' Person A still views themselves as a smoker struggling against temptation; Person B has changed their core identity. Consequently, Person B is 4x more likely to remain smoke-free over the long haul.",
        "visual_diagram": """graph TD
  subgraph Identity_Engine["Three Layers of Behavior Change"]
    Identity["CORE: Identity<br/>(Who you believe you are)"] --> Process["PROCESS: Daily Systems<br/>(What you consistently do)"]
    Process --> Outcome["OUTCOME: Temporary Result<br/>(What you temporarily get)"]
  end
  style Identity fill:#064e3b,stroke:#10b981,color:#fff
  style Process fill:#312e81,stroke:#6366f1,color:#fff
  style Outcome fill:#78350f,stroke:#f59e0b,color:#fff""",
        "quote": "True behavior change is identity change. You might start a habit because of motivation, but the only reason you'll stick with one is that it becomes part of your identity.",
        "action_item": "Decide on one identity statement today: 'I am a disciplined creator'. Every time you resist checking social media, mentally say: 'Vote cast.'",
        "author": "James Clear",
        "source": "Atomic Habits",
        "topic": "Productivity",
        "tags": ["Identity", "Habits", "Psychology"],
        "read_time_mins": 1,
        "color_theme": "emerald",
        "likes": 298,
        "saved_count": 175
    },

    # Stoicism & Philosophy
    {
        "id": "idea_dichotomy_control",
        "title": "The Dichotomy of Control",
        "one_liner": "Suffering arises when we demand that external events obey our internal desires.",
        "summary": "Epictetus divided the universe into two buckets: things up to us (our opinions, intentions, values, and actions) and things not up to us (the weather, politics, economic shifts, reputation, and other people's behavior). Master the former; accept the latter.",
        "detailed_explanation": "The bedrock principle of Epictetan Stoicism divides everything in existence into two categories: things within our control (our thoughts, decisions, virtues, responses, and values) and things outside our control (weather, economy, algorithms, other people's opinions, and the past). Anxiety and suffering are born from misallocating emotional energy to external factors that we cannot govern. True inner tranquility (ataraxia) comes from pouring 100% of our energy into our internal choices while practicing radical acceptance of the rest.",
        "example": "Admiral James Stockdale, held as a prisoner of war in Vietnam for over seven years and tortured over twenty times, survived by practicing the dichotomy of control daily. He realized he could not control whether his captors beat him, what food he was given, or when the war would end. But he retained absolute control over his internal dignity, his loyalty to fellow prisoners, and his determination not to break.",
        "visual_diagram": """graph LR
  subgraph In_Control["WITHIN MY CONTROL"]
    C1[My Beliefs & Judgments]
    C2[My Decisions & Responses]
    C3[My Ethical Character]
  end
  subgraph Not_In_Control["OUTSIDE MY CONTROL"]
    O1[Other People's Opinions]
    O2[Macro Economic Cycles]
    O3[The Past & Weather]
  end
  In_Control -.->|100% Emotional Investment| Peace[Inner Freedom & Ataraxia]
  Not_In_Control -.->|Radical Acceptance & Detachment| Peace
  style In_Control fill:#064e3b,stroke:#10b981,color:#fff
  style Not_In_Control fill:#881337,stroke:#f43f5e,color:#fff
  style Peace fill:#1e1b4b,stroke:#818cf8,color:#fff""",
        "quote": "Make the best use of what is in your power, and take the rest as it happens.",
        "action_item": "Draw two circles on paper. In the center, write today's stressors that you control. In the outer ring, list the uncontrollable factors. Draw an 'X' over the outer ring.",
        "author": "Epictetus & Marcus Aurelius",
        "source": "The Enchiridion & Meditations",
        "topic": "Stoicism",
        "tags": ["Control", "Equanimity", "Resilience"],
        "read_time_mins": 2,
        "color_theme": "amber",
        "likes": 340,
        "saved_count": 240
    },
    {
        "id": "idea_obstacle_is_way",
        "title": "The Obstacle is the Way",
        "one_liner": "The impediment to action advances action. What stands in the way becomes the way.",
        "summary": "Adversity is not an interruption to your purpose; it is the raw fuel for it. When an obstacle blocks your original trajectory, it forces you to develop patience, humility, ingenuity, or grit that you would never have uncovered on a smooth road.",
        "detailed_explanation": "From Marcus Aurelius's Meditations: 'The impediment to action advances action. What stands in the way becomes the way.' Rather than viewing roadblocks, economic crashes, or personal crises as interruptions to your path, Stoicism teaches that the obstacle IS the path. Obstacles present an irreplaceable arena to forge courage, resilience, patience, and inventiveness that could never be cultivated in tranquil, easy times.",
        "example": "In 1914, Thomas Edison's massive West Orange laboratory caught fire. Ten buildings burned to the ground, destroying years of irreplaceable experiments and millions of dollars in equipment. Instead of falling into despair, the 67-year-old Edison called his family and employees to watch the flames, saying: 'All our mistakes are burned up. Now we can start anew.' Within three weeks, he had rebuilt enough to resume manufacturing and turned a profit the following year.",
        "visual_diagram": """graph LR
  Path[Intended Journey Path] -->|Unforeseen Roadblock| Block[Severe Crisis / Obstacle]
  Block -->|Stoic Mental Inversion| Catalyst[Catalyst: Demands Grit, Ingenuity & Virtue]
  Catalyst -->|Elevated Trajectory| Triumph[What Stood in the Way BECOMES The Way]
  style Path fill:#312e81,stroke:#6366f1,color:#fff
  style Block fill:#881337,stroke:#f43f5e,color:#fff
  style Catalyst fill:#78350f,stroke:#f59e0b,color:#fff
  style Triumph fill:#064e3b,stroke:#10b981,color:#fff""",
        "quote": "The mind adapts and converts to its own purposes the obstacle to our acting.",
        "action_item": "Take the single most irritating obstacle you face right now. Ask: 'What rare virtue does this obstacle force me to practice today?'",
        "author": "Marcus Aurelius",
        "source": "Meditations (Book 5)",
        "topic": "Stoicism",
        "tags": ["Mindset", "Adversity", "Resilience"],
        "read_time_mins": 1,
        "color_theme": "amber",
        "likes": 412,
        "saved_count": 310
    },
    {
        "id": "idea_memento_mori",
        "title": "Memento Mori: Death as Clarity",
        "one_liner": "Remember that your time is finite; let it determine what you do, say, and think.",
        "summary": "Contemplating mortality is not morbid; it is the ultimate clarifying lens. It instantly strips away petty slights, vanity, artificial anxieties, and consumerist distractions, leaving only what genuinely matters right now.",
        "detailed_explanation": "Memento Mori—Latin for 'remember you must die'—was practiced by Roman generals and philosophers not as a depressing obsession with death, but as an energizing wake-up call to life. When you deeply acknowledge that today might be your final turn on this planet, trivial grievances vanish, vanity loses its power, procrastination melts, and present-moment gratitude becomes your default state of mind.",
        "example": "Steve Jobs famously reflected on Memento Mori in his 2005 Stanford Commencement speech: 'Remembering that I'll be dead soon is the most important tool I've ever encountered to help me make the big choices in life. Because almost everything—all external expectations, all pride, all fear of embarrassment or failure—these things just fall away in the face of death, leaving only what is truly important.'",
        "visual_diagram": """graph TD
  Noise[Petty Insults, Vanity & Synthetic Worries] --> Lens[MEMENTO MORI: Awareness of Mortality]
  Lens -->|Burn Away Non-Essentials| Reality[Essential Presence, Authentic Kindness & Deep Work]
  style Noise fill:#881337,stroke:#f43f5e,color:#fff
  style Lens fill:#4c1d95,stroke:#c084fc,color:#fff
  style Reality fill:#064e3b,stroke:#10b981,color:#fff""",
        "quote": "You could leave life right now. Let that determine what you do and say and think.",
        "action_item": "Take 30 seconds of quiet stillness. Acknowledge that today could be your last evening on earth. Treat the next person you talk to with complete kindness.",
        "author": "Seneca",
        "source": "Letters from a Stoic",
        "topic": "Stoicism",
        "tags": ["Perspective", "Mortality", "Presence"],
        "read_time_mins": 1,
        "color_theme": "rose",
        "likes": 220,
        "saved_count": 145
    },

    # Psychology & Human Behavior
    {
        "id": "idea_system1_system2",
        "title": "System 1 vs System 2 Thinking",
        "one_liner": "Your fast, intuitive brain runs on autopilot while your slow, logical brain is lazy.",
        "summary": "System 1 operates automatically, fast, and with little effort, but is riddled with cognitive biases and emotional heuristics. System 2 allocates attention to effortful mental operations, but tires easily. Great thinkers know when to deliberately wake up System 2.",
        "detailed_explanation": "In Thinking, Fast and Slow, Nobel laureate Daniel Kahneman maps human cognition into two complementary modes. System 1 is fast, automatic, emotional, stereotypic, and unconscious. It is essential for survival (jumping away from a snake, reading facial expressions), but prone to cognitive biases like confirmation bias and availability heuristics. System 2 is slow, deliberative, logical, and effortful. Because System 2 requires high glucose and energy, the brain is a cognitive miser that defaults to System 1 heuristics whenever possible.",
        "example": "Retailers take advantage of System 1 by placing items on sale with a crossed-out 'anchor' price of $99 marked down to $69. System 1 perceives an urgent bargain. System 2 is required to pause, calculate actual utility, and ask: 'Do I actually need this item at all, regardless of the discount?'",
        "visual_diagram": """graph TD
  Input[Daily Decisions & Biases] --> S1[System 1: Fast, Intuitive, Cognitive Miser]
  S1 -->|Default Shortcuts| FastErr[Heuristic Reactions & Cognitive Biases]
  Input -->|Deliberate Reflection| S2[System 2: Slow, Deliberate, Effortful]
  S2 -->|Analytical Calculation| SoundJudg[Calibrated Strategic Judgment]
  style Input fill:#312e81,stroke:#6366f1,color:#fff
  style S1 fill:#78350f,stroke:#f59e0b,color:#fff
  style S2 fill:#064e3b,stroke:#10b981,color:#fff
  style FastErr fill:#881337,stroke:#f43f5e,color:#fff
  style SoundJudg fill:#0f766e,stroke:#14b8a6,color:#fff""",
        "quote": "Thinking is to humans as swimming is to cats; they can do it, but they'd prefer not to.",
        "action_item": "Whenever you feel an impulsive urge to buy, send an angry email, or make a quick trade, enforce a 24-hour mandatory cooling period.",
        "author": "Daniel Kahneman",
        "source": "Thinking, Fast and Slow",
        "topic": "Psychology",
        "tags": ["Cognition", "Biases", "Decision Making"],
        "read_time_mins": 2,
        "color_theme": "purple",
        "likes": 280,
        "saved_count": 195
    },
    {
        "id": "idea_loss_aversion",
        "title": "Loss Aversion & Sunk Cost",
        "one_liner": "The pain of losing $100 is psychologically twice as intense as the joy of gaining $100.",
        "summary": "Evolutionary psychology wired us to defend against losses fiercely. This causes people to hold losing investments, stay in toxic relationships, or cling to failing projects because 'I've already invested so much'. That past investment is gone forever.",
        "detailed_explanation": "Discovered through Amos Tversky and Daniel Kahneman's Prospect Theory, loss aversion demonstrates that the emotional pain of losing an asset or sum of money is psychologically roughly twice as impactful as the pleasure of gaining the exact same amount. This evolutionary asymmetry leads to irrational decision-making, such as the sunk cost fallacy—refusing to abandon a doomed project because of the time or money already spent.",
        "example": "Investors frequently hold onto losing stocks that have plummeted 60%, refusing to sell because 'it's only a paper loss until I sell'. They will sell winning stocks prematurely to lock in small gains, starving their winners and feeding their losers, which severely underperforms the broader market over time.",
        "visual_diagram": """graph LR
  Gain["Gain of $100<br/>(+1x Joy)"]
  Loss["Loss of $100<br/>(-2x to -2.5x Psychological Pain)"]
  Loss --> Result["Sunk Cost Trap: Clinging to Losing Bets & Toxic Sunk Costs"]
  style Gain fill:#064e3b,stroke:#10b981,color:#fff
  style Loss fill:#881337,stroke:#f43f5e,color:#fff
  style Result fill:#1e1b4b,stroke:#818cf8,color:#fff""",
        "quote": "Organizations that don't tolerate failure end up tolerating mediocrity, because people only make safe, incremental bets.",
        "action_item": "Ask yourself: 'If I were not already invested in this project today, would I start it from scratch with fresh capital?' If no, exit now.",
        "author": "Amos Tversky & Daniel Kahneman",
        "source": "Prospect Theory",
        "topic": "Psychology",
        "tags": ["Economics", "Biases", "Rationality"],
        "read_time_mins": 1,
        "color_theme": "rose",
        "likes": 195,
        "saved_count": 122
    },

    # Wealth & Leverage
    {
        "id": "idea_permissionless_leverage",
        "title": "Permissionless Leverage",
        "one_liner": "Code and media are the new leverage: they work while you sleep without asking anyone's permission.",
        "summary": "Traditional leverage required managing human beings (labor) or convincing bankers (capital). Modern leverage is permissionless: software code and digital media. An algorithm or a great article replicates infinitely at marginal cost near zero.",
        "detailed_explanation": "Naval Ravikant categorizes human leverage into four eras. The first was labor (having people work for you), which requires immense management and social politics. The second was capital (having money work for you), which requires convincing bankers and investors. The modern era introduced permissionless leverage: code and media. You don't need anyone's permission to write code or publish content. A piece of software or an audio narration can work for millions of people simultaneously across the globe at zero marginal cost.",
        "example": "In 2012, Instagram had just 13 employees when it was acquired by Facebook for $1 billion while serving over 30 million active users. In contrast, Kodak employed over 140,000 people at its peak. The Instagram team wielded pure permissionless software leverage—each engineer's code reached millions of people without requiring an army of physical workers.",
        "visual_diagram": """graph TD
  L1[1. Labor: Human Headcount<br/>High Politics, Requires Permission] --> L2[2. Capital: Money / Debt<br/>Requires Gatekeepers & Investors]
  L2 --> L3[3. Code & Media: PERMISSIONLESS<br/>Zero Marginal Cost, Works Infinitely While You Sleep]
  style L1 fill:#881337,stroke:#f43f5e,color:#fff
  style L2 fill:#78350f,stroke:#f59e0b,color:#fff
  style L3 fill:#064e3b,stroke:#10b981,color:#fff""",
        "quote": "Forget rich versus poor, white-collar versus blue-collar. It's now leveraged versus un-leveraged.",
        "action_item": "Build or write one digital asset this week (a script, a guide, a video, a template) that can deliver value to 1,000 people without requiring 1,000 hours of your time.",
        "author": "Naval Ravikant",
        "source": "The Almanack of Naval Ravikant",
        "topic": "Wealth",
        "tags": ["Leverage", "Code", "Media", "Freedom"],
        "read_time_mins": 2,
        "color_theme": "teal",
        "likes": 480,
        "saved_count": 360
    },
    {
        "id": "idea_rich_vs_wealthy",
        "title": "Rich vs. Wealthy",
        "one_liner": "Rich is current income; wealth is the income not spent, the options you keep open.",
        "summary": "Rich is a sports car and a flashy lifestyle designed to broadcast status to strangers. Wealth is the money you don't see: the investments quietly compounding, the emergency fund, and the sovereign freedom to wake up and do whatever you want.",
        "detailed_explanation": "In The Psychology of Money, Morgan Housel makes a vital distinction between being rich and being wealthy. Being rich is current income and visible consumption—fancy watches, expensive cars, lavish vacations designed to telegraph status to strangers. Wealth, however, is the money you do NOT spend. Wealth is optionality, financial runway, unexercised freedom, and the peace of mind knowing you control your own time and calendar.",
        "example": "Housel recounts a story of a brilliant tech executive who loved buying expensive cars and throwing $1,000 cash bills into the Pacific Ocean for fun. He went bankrupt within a few years after an economic downturn. Meanwhile, Ronald Read, a Vermont janitor and gas station attendant, quietly invested his modest savings in dividend stocks and lived simply. When he died at age 92, he had amassed over $8 million, leaving the majority to his local hospital and library.",
        "visual_diagram": """graph LR
  subgraph Rich_State["RICH (Visible Consumption)"]
    R1[High Current Income] --> R2[Expensive Cars & Watches] --> R3[Telegraphed Status to Strangers]
  end
  subgraph Wealth_State["WEALTHY (Hidden Sovereignty)"]
    W1[Income Not Spent] --> W2[Compounding Assets & Emergency Runway] --> W3[100% Control Over Your Own Time]
  end
  style Rich_State fill:#881337,stroke:#f43f5e,color:#fff
  style Wealth_State fill:#064e3b,stroke:#10b981,color:#fff""",
        "quote": "Spending money to show people how much money you have is the fastest way to have less money.",
        "action_item": "Next time you want to spend to impress someone, remember: nobody is admiring your possession as much as you imagine; they are merely imagining themselves owning it.",
        "author": "Morgan Housel",
        "source": "The Psychology of Money",
        "topic": "Wealth",
        "tags": ["Money", "Freedom", "Ego"],
        "read_time_mins": 1,
        "color_theme": "teal",
        "likes": 390,
        "saved_count": 270
    },
    {
        "id": "idea_specific_knowledge",
        "title": "Specific Knowledge",
        "one_liner": "Arm yourself with specific knowledge that cannot be trained in a classroom.",
        "summary": "If society can train someone else to do what you do via a standardized curriculum, it will eventually replace you or commoditize your rate. Specific knowledge is found by pursuing your genuine curiosity and natural obsessions. To you it feels like play, to others it looks like hard work.",
        "detailed_explanation": "Specific knowledge is the unique synthesis of your authentic curiosities, personality traits, and obsessive interests. Because it cannot be acquired in an off-the-shelf course, it cannot be automated or easily outsourced. The ultimate career moat is not working 80 hours a week doing what everyone else is doing; it is doing what feels effortless to you but impossible to everyone else.",
        "example": "Steve Jobs auditing a calligraphy class at Reed College had no commercial purpose at the time. A decade later, that exact idiosyncratic knowledge was woven into the Macintosh computer as beautiful typography and proportional fonts—creating Apple's foundational design differentiation against IBM and Microsoft.",
        "visual_diagram": """graph LR
  Curiosity[Authentic Childhood Curiosities & Obsessions] --> Moat[Specific Knowledge: Cannot Be Taught in a School]
  Moat --> Leverage[Permissionless Leverage: Code & Content]
  Leverage --> Asymmetry[Feels Like Play to You, Looks Like Hard Work to Others]
  style Curiosity fill:#312e81,stroke:#6366f1,color:#fff
  style Moat fill:#064e3b,stroke:#10b981,color:#fff
  style Leverage fill:#78350f,stroke:#f59e0b,color:#fff
  style Asymmetry fill:#0f766e,stroke:#14b8a6,color:#fff""",
        "quote": "Specific knowledge cannot be taught, but it can be learned through apprenticeship and intense obsession.",
        "action_item": "List 3 things you loved doing effortlessly between ages 12 and 18 that your peers found tedious or difficult. That is your specific knowledge clue.",
        "author": "Naval Ravikant",
        "source": "How to Get Rich Without Getting Lucky",
        "topic": "Wealth",
        "tags": ["Career", "Curiosity", "Uniqueness"],
        "read_time_mins": 2,
        "color_theme": "indigo",
        "likes": 345,
        "saved_count": 230
    },

    # Antifragility & Resilience
    {
        "id": "idea_antifragility",
        "title": "The Antifragile Principle",
        "one_liner": "Some things benefit from shocks; they thrive and grow when exposed to volatility, randomness, and stress.",
        "summary": "Fragile breaks under stress (like porcelain). Robust resists stress (like a boulder). Antifragile improves under stress (like the human immune system, bone density, or entrepreneurship). Design your life to gain from uncertainty, not fear it.",
        "detailed_explanation": "Nassim Taleb created the term 'antifragile' because there was no true opposite of fragile in any major language. Robust or resilient simply means staying the same when hit. Antifragile means actively getting stronger and more capable when exposed to chaos, volatility, and stress (within lethal limits). In career, health, and software systems, eliminating all volatility actually creates catastrophic fragility.",
        "example": "Weightlifting (hypertrophy): When you lift a heavy barbell, you cause micro-tears in muscle fibers (stress and trauma). In response, the body over-compensates during recovery by building denser, stronger muscle fibers to prepare for future shocks. Conversely, complete bed rest destroys bone density and weakens the heart.",
        "visual_diagram": """graph TD
  subgraph Volatility_Triad["The Triad Under Chaos & Volatility"]
    F["FRAGILE (Porcelain)<br/>Breaks Under Stress"]
    R["ROBUST (Granite)<br/>Resists Stress, Stays Equal"]
    A["ANTIFRAGILE (Immune System/Hydra)<br/>Thrives and Grows Stronger from Stress"]
  end
  style F fill:#881337,stroke:#f43f5e,color:#fff
  style R fill:#312e81,stroke:#6366f1,color:#fff
  style A fill:#064e3b,stroke:#10b981,color:#fff""",
        "quote": "Wind extinguishes a candle and energizes fire. You want to be the fire and wish for the wind.",
        "action_item": "Expose yourself to small, controlled stressors (cold showers, lifting heavy weights, public speaking, fast feedback loops) to stimulate antifragile growth.",
        "author": "Nassim Nicholas Taleb",
        "source": "Antifragile: Things That Gain from Disorder",
        "topic": "Mental Models",
        "tags": ["Resilience", "Volatility", "Growth"],
        "read_time_mins": 2,
        "color_theme": "rose",
        "likes": 275,
        "saved_count": 182
    },
    {
        "id": "idea_skin_in_the_game",
        "title": "Skin in the Game",
        "one_liner": "Never take advice or trust forecasts from people who incur zero penalty for being wrong.",
        "summary": "Knowledge without downside risk is reckless. True credibility is not having academic credentials or a polished pitch; it is having personal exposure to the negative fallout if your thesis fails. Don't tell me what you think, show me what you own.",
        "detailed_explanation": "The concept of 'Skin in the Game' is the oldest evolutionary and ethical risk-management mechanism known to civilization. Hammurabi's Code decreed that if a builder constructs a house and it collapses killing the owner, the builder shall be put to death. When decision-makers are insulated from the downside consequences of their decisions (agency problem), they systematically take asymmetric risks with other people's money and lives.",
        "example": "During the 2008 financial crisis, Wall Street bank executives pocketed tens of millions in bonuses for generating high-risk subprime mortgage securities. When the mortgage market crashed, the banks were bailed out with taxpayer money while executives kept their previous bonuses—a total absence of skin in the game that created moral hazard.",
        "visual_diagram": """graph LR
  subgraph No_Skin["NO SKIN IN THE GAME (Moral Hazard)"]
    N1[High Risk Decisions] --> N2[Keep Private Upside] --> N3[Socialize Downside to Others]
  end
  subgraph Real_Skin["SKIN IN THE GAME (Ethical Symmetry)"]
    S1[High Conviction Thesis] --> S2[Direct Downside Penalty if Wrong] --> S3[True Credibility & Tested Wisdom]
  end
  style No_Skin fill:#881337,stroke:#f43f5e,color:#fff
  style Real_Skin fill:#064e3b,stroke:#10b981,color:#fff""",
        "quote": "If you give an opinion, and someone follows it, you should share in the consequences.",
        "action_item": "Before taking any consultant, advisor, or guru's advice, ask: 'What do you personally lose if this recommendation blows up?'",
        "author": "Nassim Nicholas Taleb",
        "source": "Skin in the Game",
        "topic": "Mental Models",
        "tags": ["Accountability", "Ethics", "Wisdom"],
        "read_time_mins": 1,
        "color_theme": "purple",
        "likes": 188,
        "saved_count": 118
    }
]
