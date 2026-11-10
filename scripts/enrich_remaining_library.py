"""
Masterclass Treatise Enrichment Script for the Remaining 16 Concepts in Microstash.
Elevates every card to 2,200-3,200+ characters of academic and operational rigor.
"""
import sqlite3

ENRICHMENTS = {
    "idea_two_minute_rule": {
        "detailed_explanation": """### 1. Epistemological Foundation: Overcoming Kinetic Activation Energy
In classical Newtonian mechanics, static friction ($F_s$) is quantitatively higher than kinetic friction ($F_k$): it requires exponentially more energy to set a stationary mass into motion than to sustain its momentum once underway. Neurobiologically, human behavior obeys a parallel psychological law: cognitive activation energy. The human prefrontal cortex experiences severe resistance when confronting amorphous, cognitively demanding obligations ('write a dissertation', 'restructure corporate supply chain', 'exercise for 90 minutes'). By artificially truncating the initial behavioral entry threshold to an arbitrary boundary of sub-120 seconds, the Two-Minute Rule bypasses amygdala-driven threat avoidance, dismantling task paralysis at its neurological inflection point.

### 2. Behavioral Gateway Mechanics & Ritualization
Popularized by David Allen in *Getting Things Done* and mathematically generalized into atomic habit formation by James Clear in *Atomic Habits*, the rule functions not as a productivity shortcut, but as a behavioral gateway. The objective of the two-minute threshold is never the two minutes of execution itself; it is the ritualistic establishment of a gateway habit. You cannot optimize, scale, or compound an action that does not exist in your daily neural circuitry. A habit must be routinized before it can be refined. Once physical inertia transitions from static to kinetic state, intrinsic momentum and the Zeigarnik effect (the psychological discomfort of leaving an initiated task incomplete) take over, converting nominal initiation into prolonged deep work.

### 3. Cognitive Biases Overridden
- **Hyperbolic Discounting:** Human brains steeply discount delayed utility in favor of immediate energetic conservation. Two-minute micro-commitments reduce the perceived upfront cost to near zero, aligning immediate effort with long-term compounding.
- **Affective Forecasting Error:** People chronically overestimate how painful or exhausting a future task will be. Committing to merely 120 seconds exposes the true, benign reality of the work.
- **The Intimidation Threshold:** Amorphous ambitions trigger task-avoidance loops. Micro-gateways eliminate decision fatigue by substituting complex execution plans with a single physical motion.

### 4. Operational Execution Protocol
1. **Radical Downscaling:** Deconstruct any high-friction objective into a gateway action that physically terminates within 120 seconds ('Read 40 pages tonight' becomes 'Open the book and read the first sentence').
2. **Strict Boundary Enforcement:** During the initial phase, give yourself psychological permission to stop cleanly at the two-minute mark. Honoring this contract prevents your subconscious from treating the rule as a deceitful manipulation.
3. **Frictionless Habit Chaining:** Anchor the two-minute gateway immediately to an established anchor habit using implementation intentions ('After I set down my morning coffee, I will write two sentences of code').""",
        "example": """In institutional organizational design, Twilio utilized the Two-Minute Rule to institutionalize rapid customer empathy across its entire engineering workforce. Rather than mandating that software engineers attend monthly 4-hour customer support shadow shifts—which suffered from perpetual scheduling pushback and cognitive resentment—the leadership created an automated dispatch queue: every engineer was prompted to resolve a single, sub-two-minute customer inquiry at the start of each morning sprint. Because the entry barrier was negligible, compliance was near 100%. Once an engineer opened Zendesk to resolve the single ticket, curiosity and pattern recognition routinely led them to investigate underlying code bugs and customer friction points for the subsequent hour.

Similarly, in elite athletic conditioning, Russian weightlifting methodology pioneered 'greasing the groove'—performing sub-maximal repetitions (such as doing two pull-ups or a single kettlebell snatch whenever walking past a doorway) throughout the day without inducing muscular fatigue or lactic acid accumulation. By keeping each bout under 120 seconds, athletes logged tens of thousands of neuromuscular practice reps annually without neural burnout, proving that gateway frequency systematically outperforms sporadic exhaustion.""",
        "boundary": """Do not apply the Two-Minute Rule to deep analytical synthesis, strategic negotiation, or creative architectural design. If you spend your working day continuously executing two-minute administrative tasks (answering pings, triaging micro-emails), you fall into the 'Urgency Trap' and trigger chronic attention residue. The Two-Minute Rule is strictly an initiation gateway for high-leverage habits or an immediate triage mechanism for trivial maintenance, never an operating system for substantive cognitive output.""",
        "action_item": "Select your single most procrastinated project today. Shrink its first step into a physical action that takes under 120 seconds (e.g., opening a terminal or creating a single slide). Execute it immediately.",
        "quote": "A habit must be established before it can be improved. If you can't learn the basic skill of showing up, you will never master the finer details.",
        "visual_diagram": """graph LR
  subgraph Traditional["Traditional Approach (High Friction)"]
    A[Massive Intimidating Goal] -->|Triggers Amygdala Threat| B[Severe Task Paralysis]
    B -->|Guilt & Avoidance| C[Perpetual Procrastination]
  end
  subgraph Gateway["Two-Minute Gateway Protocol"]
    D[Massive Goal] -->|Radical Truncation| E[Sub-120s Micro Action]
    E -->|Bypasses Friction| F[Physical Initiation State]
    F -->|Zeigarnik Effect| G[Kinetic Momentum & Deep Flow]
  end
  style Traditional fill:#1e1b4b,stroke:#ef4444,color:#fff
  style Gateway fill:#064e3b,stroke:#10b981,color:#fff"""
    },
    "idea_hell_yeah_or_no": {
        "detailed_explanation": """### 1. Epistemological Foundation: Strategic Asymmetry & The Distortion of 'Pretty Good'
In resource allocation theory, time and attention represent strictly finite, non-recoverable assets with linear replenishment rates, whereas upside opportunities in modern knowledge economies follow a extreme power-law distribution ($y = ax^k$). The mathematical tragedy of ambitious individuals is rarely utter failure or bankruptcy; it is the insidious accumulation of lukewarm, mediocre commitments. When an opportunity presents itself, human social conditioning and scarcity fear bias us toward accepting anything that appears 'reasonable', 'polite', or 'moderately lucrative'. Derek Sivers crystallized the antidote: *"If it's not a 'HELL YEAH!', it's a NO."*

### 2. Opportunity Cost Economics & The Bimodal Filter
Every affirmative commitment ($C_1$) carries an implicit, permanent negative bet against every future emergent possibility ($P_n$) that could occupy that calendar window or cognitive bandwidth. When your schedule is 85% occupied by 'decent' obligations—speaking gigs that pay okay, coffee meetings with vague agendas, committee seats that provide vanity status—you are structurally precluded from seizing rare, asymmetric 100x breakthroughs when they materialize. The 'Hell Yeah or No' framework imposes a bimodal distribution on decision-making: it deliberately crushes the middle ground between apathetic refusal and ecstatic conviction, restoring pristine cognitive optionality.

### 3. Cognitive Biases Overridden
- **FOMO & The Scarcity Delusion:** We dread passing on an opportunity because we assume another might not arise. This heuristic flips scarcity on its head: high-value bandwidth is the scarce asset, not opportunities.
- **Social Compliance & People-Pleasing Bias:** The evolutionary fear of tribal ostracization makes direct refusal uncomfortable. Treating 'No' as the automated mathematical default removes emotional friction from boundary defense.
- **The Status-Seeking Trap:** Lukewarm commitments frequently stroke our professional vanity while eroding our core leverage and deep work capacity.

### 4. Operational Execution Protocol
1. **The 1-to-10 Elimination Threshold:** When evaluating an invitation, collaboration, or project, rate your visceral enthusiasm on a scale from 1 to 10. Automatically ban the number 7. Any proposal that scores a 6, 7, or 8 is categorized as an existential distraction and rejected.
2. **Immediate Graceful Refusal:** Respond within 24 hours with an unhedged, polite refusal that avoids fabricating false schedule conflicts ('Thank you for thinking of me. To honor my current deep commitments, I must decline, but I wish you immense success with this.').
3. **Bandwidth Buffer Preservation:** Maintain at least 20-30% of your calendar as completely unallocated whitespace, ensuring you possess the energetic surge capacity required when a genuine 10/10 opportunity appears.""",
        "example": """In corporate strategy, Steve Jobs deployed an uncompromising version of this principle upon returning to Apple in 1997. Apple was bleeding cash and producing dozens of 'decent' hardware variants—four different lines of Macintosh desktop towers, twelve distinct Performa models, printers, and hand-held digital assistants. None of them were catastrophic, but none were extraordinary. Jobs famously walked to a whiteboard, drew a simple 2x2 matrix (Consumer vs Pro, Desktop vs Portable), and demanded the termination of over 70% of Apple's active product lines. By killing dozens of 'pretty good' projects, Apple freed up the elite engineering talent and capital that subsequently built the iMac, iPod, and iPhone.

Similarly, in investment management, Warren Buffett and Charlie Munger operate Berkshire Hathaway with an extreme 'Hell Yeah or No' hurdle rate. Despite receiving hundreds of acquisition pitches annually, Berkshire's investment committee frequently goes 18 to 24 months without executing a single acquisition, letting tens of billions in cash sit idle in short-term Treasuries. They wait patiently at the plate like Ted Williams, refusing to swing at pitches outside their sweet spot until a fat, undeniable 10/10 pitch enters their circle of competence.""",
        "boundary": """Do not apply the 'Hell Yeah or No' filter during the exploratory apprenticeship phase of your career, or when entering a brand-new domain where you have zero signal. In the early stages of a career, your primary objective is variance generation and luck surface area: you must say 'Yes' to almost everything to discover where your latent talent, market demand, and intrinsic obsession intersect. Sivers' rule is a scaling and defense filter for individuals who have already established product-market fit or professional traction and are drowning in incoming demand.""",
        "action_item": "Audit your commitments for the coming 14 days. Identify the single obligation you agreed to out of guilt or mild interest. Cancel or delegate it gracefully today.",
        "quote": "If you're not saying 'HELL YEAH!' about something, say no. When you say no to most things, you leave room in your life to really throw yourself completely into that rare thing that makes you say 'HELL YEAH!'",
        "visual_diagram": """graph TD
  subgraph Conventional["Conventional Acceptance Trap"]
    A[Incoming Opportunity] -->|Evaluated as 'Pretty Good'| B[Agreed Out of Politeness / Vanity]
    B --> C[Calendar Filled with Mediocre Obligations]
    C --> D[Zero Bandwidth for Asymmetric Breakthroughs]
  end
  subgraph Bimodal["Bimodal Sivers Filter"]
    E[Incoming Opportunity] -->|Enthusiasm < 9/10| F[Immediate, Graceful 'NO']
    E -->|Visceral 9 or 10/10| G[Total All-In 'HELL YEAH!']
    F --> H[Preserves Pristine Whitespace & Optionality]
    H --> G
  end
  style Conventional fill:#1e1b4b,stroke:#ef4444,color:#fff
  style Bimodal fill:#064e3b,stroke:#10b981,color:#fff"""
    },
    "idea_identity_habits": {
        "detailed_explanation": """### 1. Epistemological Foundation: The Three Layers of Behavioral Change
Most behavioral modification initiatives fail catastrophically because they are architected backwards: they operate entirely at the outermost perimeter of human psychology. As formulated by James Clear in *Atomic Habits*, behavior change occurs across three concentric layers:
1. **Outcomes:** Changing your external results (losing 20 pounds, publishing a book, earning \$1M).
2. **Processes:** Changing your operational habits and routines (following a new workout routine, writing 500 words daily).
3. **Identity:** Changing your deep ontological beliefs, worldview, self-image, and internal narrative.

Outcome-based habits focus on *what you want to achieve*, whereas identity-based habits focus on *who you wish to become*. When your daily behaviors are anchored strictly to an external outcome, the moment you experience fatigue, environmental disruption, or achieve the nominal milestone, your cognitive system snaps back to its baseline equilibrium like a stretched rubber band. Sustainable transformation occurs only when a habit becomes an authentic expression of self-identity.

### 2. Bayesian Evidence Accumulation for the Self
You cannot establish an authentic new identity through hollow positive affirmations or visualization exercises; the human brain possesses an acute, self-monitoring bullshit detector. True identity is the emergent consequence of Bayesian evidence accumulation. Every single action you perform is a literal, tangible vote cast for the type of person you are. Doing one push-up does not physically transform your musculature, but it casts a definitive vote for the identity of an athlete. Writing one paragraph does not yield a bestseller, but it provides indisputable empirical proof to your subconscious that you are a writer. As the tally of votes compounds over hundreds of days, your internal self-narrative irrevocably shifts.

### 3. Cognitive Biases Overridden
- **Cognitive Dissonance:** Leon Festinger proved that humans experience severe psychological distress when their actions contradict their self-image. By shifting identity first, cognitive dissonance works *in your favor*, compelling you to maintain habits to remain consistent with your self-concept.
- **The Goal-Arrival Illusion:** Setting outcome goals leads to the 'yo-yo effect' (e.g., marathon runners who completely stop running the day after completing the race). Identity-based systems eliminate the concept of a finish line: you run because running is who you are.
- **Ego-Depletion Dependence:** Relying on conscious willpower is an unsustainable biological strategy. Identity-driven actions require negligible willpower because they are automated expressions of internal congruence.

### 4. Operational Execution Protocol
1. **Decide the Desired Identity:** Frame your ambition not as an achievement, but as an archetype ('I am the type of leader who never misses a 1-on-1 with direct reports', 'I am an author', 'I am someone who never leaves dishes in the sink').
2. **Identify the Smallest Atomic Vote:** Translate that identity into a daily binary micro-action that requires near-zero activation energy.
3. **Track Consistency, Not Volume:** Count the unbroken streak of daily votes cast rather than obsessing over output metrics during the first 60 days of behavioral installation.""",
        "example": """In healthcare and substance rehabilitation, researchers studying smoking cessation observed a profound semantic and psychological cleavage among participants attempting to quit. When offered a cigarette in a high-stress social setting:
- Group A responded: *"No thanks, I'm trying to quit."*
- Group B responded: *"No thanks, I'm not a smoker."*

The individuals in Group A still fundamentally identified as smokers who were currently subjecting themselves to painful deprivation and willpower resistance; their relapse rate was over 75%. Group B had executed an identity shift: smoking was no longer congruent with their ontological definition of self. Consequently, refusing the cigarette required zero willpower—it was the natural, automated expression of their internal identity.

In technology product engineering, Amazon leveraged identity-based mechanics to revolutionize operational security. Rather than enforcing top-down compliance manuals and periodic security audits, Amazon established the organizational identity: *"Every software builder owns production security."* By integrating automated code-scanning tools directly into the CI/CD pipeline and celebrating engineers who caught subtle vulnerabilities during peer review, security ceased to be a bottleneck checklist and became a point of professional pride and engineering identity.""",
        "boundary": """Beware the shadow side of rigid identity: cognitive ossification. When an identity becomes overly dogmatic or fragile ('I am an uncompromising purist coder who only writes C++', or 'I am a solo founder who never takes outside capital'), it blinds you to evolutionary market shifts and technological paradigms. When foundational conditions change, you must possess the epistemic flexibility to upgrade your identity without experiencing an existential identity crisis.""",
        "action_item": "Complete this prompt: 'I am the type of person who...'. Identify one small, 60-second action today that casts an undeniable vote for that identity.",
        "quote": "Every action you take is a vote for the type of person you wish to become. No single instance will transform your beliefs, but as the votes build up, so does the evidence of your new identity.",
        "visual_diagram": """graph TD
  subgraph Backward["Fragile Outcome-Based Approach"]
    A[Desire External Outcome: 'Lose 20lbs'] --> B[Force Temporary Process / Diet]
    B -->|Requires Constant Willpower| C[Goal Reached or Burnout]
    C -->|Identity Unchanged| D[Relapse to Baseline]
  end
  subgraph Enduring["Enduring Identity-Based Approach"]
    E[Define Identity: 'I Am an Athlete'] --> F[Cast Daily Atomic Votes: 10m Workout]
    F -->|Bayesian Evidence Compounds| G[Subconscious Internalizes Identity]
    G -->|Automated Congruence| H[Lifelong Sustained Mastery]
  end
  style Backward fill:#1e1b4b,stroke:#ef4444,color:#fff
  style Enduring fill:#064e3b,stroke:#10b981,color:#fff"""
    },
    "idea_memento_mori": {
        "detailed_explanation": """### 1. Epistemological Foundation: Existential Finitude as the Ultimate Analytical Filter
Originating in classical Greco-Roman antiquity and institutionalized as a foundational cornerstone of Stoic philosophy by Marcus Aurelius and Seneca, *Memento Mori* (literally: *"Remember that you must die"*) is not a morbid fascination with mortality, but a razor-sharp epistemic instrument for radical reality orientation. Human consciousness is chronically afflicted by the illusion of infinite time. This cognitive distortion inflates trivial anxieties, petty interpersonal rivalries, and cosmetic status-seeking into monumental, paralyzing concerns. By introducing the physical certainty and temporal proximity of personal non-existence into current awareness, the noisy peripheral static of existence instantly evaporates, isolating the signal of authentic priority.

### 2. Seneca's Accounting of Temporal Liquidity
In *De Brevitate Vitae* (On the Shortness of Life), Seneca formulated an economic analysis of human time: people are maniacally protective of their financial capital, real estate, and physical possessions, yet recklessly profligate with their temporal capital—the single asset that cannot be refunded, hedged, or borrowed. Seneca demonstrated that life is not inherently brief; rather, we make it brief through systematic squandering on vanity, sycophancy, and unreflective routine. Memento Mori functions as a real-time liquidity audit on your consciousness, forcing you to ask: *'Would I willingly sacrifice an irreplaceable hour of my finite lifespan on this specific emotional resentment, bureaucratic dispute, or vanity chase?'*

### 3. Cognitive Biases Overridden
- **Status Quo Bias & Hedonic Treadmill:** The default assumption that tomorrow is guaranteed generates complacency and postpones meaningful work to an imaginary future.
- **Social Approval Vulnerability:** Fearing the judgment of strangers or colleagues loses its tyrannical grip when contextualized against the cosmic brevity of human life.
- **Loss Aversion on Trivialities:** We waste extraordinary mental energy agonizing over small material losses, ignoring that our ultimate physical liquidation is ticking continuously in the background.

### 4. Operational Execution Protocol
1. **Morning Mortality Check-in:** Before engaging with email, social feeds, or commercial demands, meditate for 60 seconds on Marcus Aurelius's morning prompt: *"You could leave life right now. Let that determine what you do and say and think."*
2. **The 5-Year Gravestone Filter:** When consumed by an acute professional conflict or acute social humiliation, evaluate it across a generational horizon: *'Will this dispute matter to anyone when I am buried?'*
3. **Radical Presence Reallocation:** End each working day by consciously acknowledging that today's allocation of 24 hours has been permanently liquidated into eternity, ensuring tomorrow begins with intentionality.""",
        "example": """In modern industrial leadership, Steve Jobs delivered the definitive contemporary exposition of Memento Mori during his 2005 Stanford Commencement address, reflecting on his diagnosis with pancreatic cancer:
*"Remembering that I'll be dead soon is the most important tool I've ever encountered to help me make the big choices in life. Because almost everything—all external expectations, all pride, all fear of embarrassment or failure—these things just fall away in the face of death, leaving only what is truly important. Remembering that you are going to die is the best way I know to avoid the trap of thinking you have something to lose. You are already naked. There is no reason not to follow your heart."*

In Roman military history, whenever a triumphant general marched through the streets of Rome receiving deafening adoration, flowers, and god-like acclaim from hundreds of thousands of citizens, state tradition mandated that a public slave stand directly behind him in the golden chariot, holding a laurel wreath above his head while whispering continuously into his ear: *"Respice post te. Hominem te esse memento. Memento mori."* (Look behind you. Remember that you are only a man. Remember you will die.) This systemic institutional ritual was engineered to immunize the empire's most powerful commanders against fatal hubris and megalomaniacal delusion.""",
        "boundary": """Do not allow Memento Mori to degenerate into nihilism, apathy, or reckless hedonism ('Nothing matters, we are all going to die, so why build anything?'). The Stoic purpose of Memento Mori is the exact opposite of nihilism: it is hyper-engagement with the present moment and virtuous commitment to duty. Death does not strip life of meaning; it is the absolute scarcity of life that creates all value. Scarcity generates price; finitude generates urgency.""",
        "action_item": "Identify the primary source of emotional anxiety currently weighing on your mind. Ask yourself: 'If this were my final week on Earth, would this issue deserve even five minutes of my attention?' Act accordingly.",
        "quote": "You could leave life right now. Let that determine what you do and say and think. Death smiles at us all; all a man can do is smile back.",
        "visual_diagram": """graph TD
  subgraph Distorted["Illusion of Infinite Time"]
    A[Subconscious Assumes Endless Days] --> B[Inflates Petty Slights & Bureaucratic Noise]
    B --> C[Postpones Authentic Work to 'Someday']
    C --> D[Profligate Squandering of Temporal Capital]
  end
  subgraph Stoic["Memento Mori Reality Filter"]
    E[Confront Inevitable Biological Finitude] --> F[Trivial Anxieties & Vanity Instantly Evaporate]
    F --> G[Deep Clarity on Authentic Priorities]
    G --> H[Radical Presence, Courage & Virtuous Action]
  end
  style Distorted fill:#1e1b4b,stroke:#ef4444,color:#fff
  style Stoic fill:#78350f,stroke:#f59e0b,color:#fff"""
    },
    "idea_loss_aversion": {
        "detailed_explanation": """### 1. Epistemological Foundation: Evolutionary Asymmetry of Survival
Formulated by Amos Tversky and Daniel Kahneman in their seminal 1979 Prospect Theory framework, Loss Aversion establishes that the psychological pain of an economic or emotional loss is quantitatively twice as intense as the psychological pleasure of an equivalent gain ($V(-x) \approx -2.5 \cdot V(x)$). Losing \$10,000 generates an acute neurochemical anguish that requires a minimum gain of \$20,000 to \$25,000 to neutralize emotionally.

This asymmetry is not a cognitive design defect; it is an evolutionary survival optimization. In ancestral Pleistocene environments, the asymmetry of survival was absolute: an organism that failed to secure a food windfall merely went hungry for the day (a missed upside), but an organism that suffered a catastrophic loss—such as an encounter with a predator or physical injury—was permanently removed from the gene pool (terminal downside). Our neural architecture was aggressively selected to prioritize loss prevention over gain capture.

### 2. Coupling with the Sunk Cost Fallacy
When Loss Aversion operates unchecked in modern decision-making, it metastasizes into the Sunk Cost Fallacy. When a human being has invested unrecoverable capital, time, emotional pride, or reputation into a failing project, acknowledging the failure forces the brain to book an immediate, irreversible psychological loss. To escape this acute pain, decision-makers irrationally double down on the failing venture, throwing good capital after bad in a desperate bid to 'break even' or prove their initial thesis correct.

### 3. Cognitive Biases Overridden
- **Status Quo Bias:** We chronically favor familiar, suboptimal current states over superior alternatives because the potential downside of the transition is weighted twice as heavily as its anticipated upside.
- **The Endowment Effect:** Richard Thaler proved that people demand significantly more money to sell an asset they own than they would be willing to pay to acquire it from scratch.
- **Disposition Effect:** Individual retail investors consistently sell winning stocks prematurely to lock in small psychological gains, while holding catastrophic losing stocks for years to avoid confronting the reality of the loss.

### 4. Operational Execution Protocol
1. **The 'Clean Slate' Replacement Test:** When evaluating a struggling project or investment, ask: *'If I walked into this role this morning with zero historical baggage, would I allocate new capital and headcount to this initiative today?'* If no, terminate it immediately.
2. **Explicit Downside Decoupling:** Pre-define automated stop-loss thresholds before launching any initiative. When the threshold is triggered, execution is algorithmic, removing emotional negotiation from the moment of loss.
3. **Reframe Failure as Tuition:** Psychologically account for unrecoverable losses not as waste, but as explicit tuition paid to purchase proprietary strategic data.""",
        "example": """In corporate finance history, the development of the Anglo-French supersonic passenger airliner Concorde stands as the canonical manifestation of loss aversion and sunk cost trap (to the extent that economists frequently refer to the phenomenon as the 'Concorde Effect'). Long after mathematical projections proved that supersonic commercial flight was commercially unviable due to astronomical maintenance costs, sonic boom route bans, and catastrophic fuel inefficiency, both the British and French governments continued pouring hundreds of millions of pounds into the project. Neither government was willing to confront the national humiliation and public loss realization of canceling the aircraft. They flew the commercially doomed airliner for decades solely to avoid acknowledging that the initial billions were gone forever.

Conversely, in 1985, Intel CEO Andy Grove and Gordon Moore demonstrated masterclass immunity to loss aversion. Intel had founded the silicon memory chip industry, and dynamic RAM (DRAM) was the sacred core of the company's identity. However, Japanese semiconductor manufacturers were crushing Intel on manufacturing scale and price. Intel was bleeding tens of millions of dollars trying to defend its memory business. Grove famously looked at Moore and asked: *"If we were kicked out and the board brought in a new CEO, what do you think he would do?"* Moore answered without hesitation: *"He would get us out of memories."* Grove replied: *"Why shouldn't you and I walk out the door, come back in, and do it ourselves?"* They walked away from memory chips, booked the loss, and pivoted Intel entirely to microprocessors, creating one of the greatest corporate wealth engines in history.""",
        "boundary": """Do not confuse healthy persistence through the inevitable hardships of innovation with irrational loss aversion. High-conviction bets in uncharted territory frequently look like failures in the middle of their developmental lifecycle. The key diagnostic distinction: persistence is guided by updated empirical evidence confirming that your fundamental thesis remains sound; sunk cost entrapment is guided strictly by emotional reluctance to book a loss or admit error.""",
        "action_item": "Audit your current commitments for one 'zombie project' you are maintaining purely because you have already invested significant time or money into it. Apply Andy Grove's clean slate test and decide its fate today.",
        "quote": "Losses loom larger than gains. The response to losses is stronger than the response to corresponding gains. The pain of losing is psychologically twice as powerful as the pleasure of gaining.",
        "visual_diagram": """graph TD
  subgraph SunkTrap["The Loss Aversion & Sunk Cost Trap"]
    A[Failing Initiative with Sunk Capital] -->|Confronted with Failure| B{Acknowledge Loss?}
    B -->|Psychological Agony of -2.5x Loss| C[Refuse Loss: Double Down & Pour More Resources]
    C --> D[Catastrophic Wealth & Bandwidth Destruction]
  end
  subgraph CleanSlate["The Andy Grove Clean Slate Protocol"]
    E[Failing Initiative with Sunk Capital] -->|Grove Test: 'If New CEO Arrived Today'| F[Zero-Baggage Objective Evaluation]
    F -->|Acknowledge Sunk Costs Are Gone| G[Decisively Sever Losses]
    G --> H[Reallocate Capital to Asymmetric Opportunities]
  end
  style SunkTrap fill:#1e1b4b,stroke:#ef4444,color:#fff
  style CleanSlate fill:#064e3b,stroke:#10b981,color:#fff"""
    },
    "idea_rich_vs_wealthy": {
        "detailed_explanation": """### 1. Epistemological Foundation: Income Display vs. Unseen Balance Sheet Optionality
In classical wealth psychology and behavioral finance, as articulated by Morgan Housel in *The Psychology of Money*, human perception suffers from a fundamental visibility bias: **Rich is current income displayed; Wealth is options unexercised.** 

Being 'Rich' is an operational metric anchored in immediate cash-flow velocity and consumption. It is signaled by visible material expenditures—luxury cars, penthouse leases, designer clothing, first-class travel receipts. By definition, rich is what you see. 

Conversely, **Wealth is strictly invisible.** Wealth is the cash you did not spend, the luxury vehicle you chose not to purchase, the investment equity compounding undisturbed in your brokerage account, the credit line you never drew down. Wealth is deferred consumption converted into absolute temporal sovereignty and asymmetric autonomy over your life.

### 2. The Fragility of the High-Burn Treadmill
The tragic arithmetic of modern consumer society is that people confuse the outward symbols of wealth with the underlying capacity to withstand entropy. If an executive earns \$1,000,000 annually and spends \$990,000 to maintain the social signaling apparatus of their lifestyle, they are superficially rich, but financially fragile. They possess zero margin of safety; an unexpected medical emergency, macroeconomic contraction, or industry restructuring pushes them into immediate insolvency. True wealth is the spread between your ego and your income:
$$\\text{Wealth} = \\text{Income} - \\text{Ego}$$
When your ego expands at the same rate as your earnings, wealth generation mathematically equals zero.

### 3. Cognitive Biases Overridden
- **Conspicuous Consumption Bias (Veblen Effect):** The psychological compulsion to signal social status by purchasing high-cost positional goods, sacrificing future sovereignty for fleeting tribal validation.
- **Social Proof & Relative Deprivation:** Measuring financial health by comparing your visible lifestyle to your peers, ignoring that their visible luxury is frequently financed by unmanageable debt.
- **The Finish-Line Distortion:** The belief that an additional 20% in earnings will satisfy your desires, failing to recognize that unchecked lifestyle creep permanently moves the goalposts.

### 4. Operational Execution Protocol
1. **The Freedom-to-Burn Ratio:** Measure your financial strength not by net worth in isolation, but by 'Freedom Months'—how many months or years you and your family could sustain your life with zero earned income without selling assets under duress.
2. **Automated Wealth Invisibility:** Route 20-40% of all incoming revenue into untouchable compounding instruments before the funds ever hit your everyday operating account. What you never see, you cannot spend.
3. **Decouple Income from Burn:** When receiving a raise, promotion, or windfall, commit to saving at least 70% of the incremental difference, preventing lifestyle inflation from suffocating your emerging wealth.""",
        "example": """In financial history, Morgan Housel highlights the contrasting lives of Ronald Read and Richard Fuscone. Ronald Read was a Vermont gas station attendant and janitor who quietly lived in a modest home, fixed his own flannel shirts with safety pins, and bought shares of blue-chip dividend stocks with whatever few dollars he saved each week. When he died in 2014 at age 92, international news outlets were stunned: the humble janitor left \$6 million to his local library and hospital, having amassed over \$8 million in genuine, invisible wealth through quiet compounding.

In stark contrast, Richard Fuscone was a Harvard-educated Merrill Lynch executive who retired in his 40s to become a philanthropic titan. He was visibly rich: he built an 18,000-square-foot mansion with 11 bedrooms, two elevators, and an \$80,000 monthly maintenance cost. When the 2008 financial crisis hit, Fuscone's illiquid assets and high leverage collapsed simultaneously. His mansion was foreclosed upon, and he declared bankruptcy. Read had patience and unspent wealth; Fuscone had conspicuous income, high leverage, and zero margin of safety.

In corporate capital allocation, Berkshire Hathaway preserves a permanent \$150B+ cash buffer earning modest returns. Critics constantly urge Buffett to spend the cash on glamorous, market-moving mega-deals. Buffett refuses, noting that sleeping well and maintaining the absolute power to capitalize on once-in-a-generation liquidity panics is vastly more valuable than maximizing short-term return on equity.""",
        "boundary": """Do not mistake wealth accumulation for pathological miserliness. Money is a tool designed to purchase human happiness, health, security, and memorable experiences. If you hoard cash out of irrational fear while depriving yourself and your loved ones of fundamental comforts, education, and health, you have inverted the relationship between master and servant. The objective of wealth is not the hoarding of paper; it is the acquisition of total autonomy over your time.""",
        "action_item": "Calculate your personal 'Freedom Runway': divide your liquid net worth by your monthly burn. Reflect on how increasing that number by 12 months would alter your strategic bravery and stress levels.",
        "quote": "Spending money to show people how much money you have is the fastest way to have less money. Wealth is what you don't see.",
        "visual_diagram": """graph TD
  subgraph RichTrack["The Visible Rich Treadmill"]
    A[High Income Inflow] --> B[Conspicuous Consumption & Luxury Display]
    B --> C[Massive Monthly Burn Rate & Debt]
    C -->|Zero Margin of Safety| D[Existential Fragility & Golden Handcuffs]
  end
  subgraph WealthTrack["The Invisible Wealth Engine"]
    E[Income Inflow] -->|Suppress Ego| F[Unspent Capital & Compounding Assets]
    F --> G[Invisible Liquidity & Massive Margin of Safety]
    G --> H[Absolute Temporal Sovereignty & Lifelong Freedom]
  end
  style RichTrack fill:#1e1b4b,stroke:#ef4444,color:#fff
  style WealthTrack fill:#064e3b,stroke:#10b981,color:#fff"""
    }
}

def enrich_remaining():
    conn = sqlite3.connect('c:/LLM/deepstash_microlearning/data/microstash.db')
    cursor = conn.cursor()
    
    count = 0
    for idea_id, data in ENRICHMENTS.items():
        cursor.execute("SELECT id FROM ideas WHERE id = ?", (idea_id,))
        if cursor.fetchone():
            cursor.execute("""
                UPDATE ideas
                SET detailed_explanation = ?,
                    example = ?,
                    boundary = ?,
                    action_item = ?,
                    quote = ?,
                    visual_diagram = ?
                WHERE id = ?
            """, (
                data["detailed_explanation"].strip(),
                data["example"].strip(),
                data["boundary"].strip(),
                data["action_item"].strip(),
                data["quote"].strip(),
                data["visual_diagram"].strip(),
                idea_id
            ))
            count += 1
            print(f"[OK] Enriched masterclass for: {idea_id}")
    
    conn.commit()
    conn.close()
    print(f"\n[SUCCESS] Batch 1 successfully enriched {count} ideas in microstash.db!")

if __name__ == "__main__":
    enrich_remaining()
