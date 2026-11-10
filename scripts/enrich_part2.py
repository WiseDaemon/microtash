import sys
from pathlib import Path
PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from app.database import get_connection

ENRICHMENTS = {
    "idea_obstacle_is_way": {
        "detailed_explanation": """### 1. Epictetus, Marcus Aurelius, and The Alchemical Mind
In Book 5 of *Meditations*, Roman Emperor Marcus Aurelius penned the quintessential maxim of Stoic resilience: *"The impediment to action advances action. What stands in the way becomes the way."* Stoicism is not passive resignation, emotional repression, or fatalism; it is active psychological alchemy. When external events disrupt your plans, the Stoic mind does not lament the disruption. Instead, it reclassifies the obstacle as the exact training apparatus designed to forge virtue, strategic ingenuity, and emotional sovereignty.

### 2. The Internal Objective Observer (The Hegemonikon)
Marcus Aurelius describes the *Hegemonikon*—the ruling governing center of human consciousness. While you cannot control external reality (wars, economic collapses, betrayals, weather), you retain absolute, unassailable dominion over the judgment you project onto that reality. Events themselves are morally neutral; only your perception labels them as 'bad' or 'ruinous'. By stripping away catastrophic emotional adjectives, the mind perceives the obstacle with crystalline, surgical objectivity: an engineering challenge to be dismantled.

### 3. Turning Adversity into Fuel: The Fire Metaphor
Marcus used the metaphor of a blazing furnace: a fragile candle flame is easily snuffed out by a gust of wind; a roaring bonfire, however, consumes the gale, consumes the heavy logs thrown upon it, and burns all the brighter using the obstacle as fuel. When a supplier breaches a contract or a software server crashes, a fragile executive panics; a Stoic strategist utilizes the crisis to fireproof their supplier redundancy and harden their infrastructure against catastrophic future collapse.

### 4. The 3-Stage Stoic Alchemy Protocol
1. **Objective Perception (Apatheia):** Strip emotional drama from the raw data. State only facts without self-pity.
2. **Directed Action (Energeia):** Pivot immediately from 'Why did this happen to me?' to 'What is the highest-integrity action available right now?'
3. **Internal Will (Amor Fati):** Love the fate that arrives, embracing the struggle as your personal cognitive gym.""",
        "example": """In 1914, Thomas Edison's vast West Orange laboratory complex—comprising 10 buildings representing his life's work, prototypes, and millions of dollars in uninsurable chemistry equipment—caught fire. Fueled by volatile chemicals, the inferno consumed the campus. Instead of weeping or falling into despair, the 67-year-old Edison reportedly called his family over, saying: 'Go get your mother and all her friends. They'll never see a fire like this again.' The next morning, amidst smoking ruins, Edison surveyed the ash and declared: 'There is great value in disaster. All our mistakes are burned up. Thank God we can start anew.' Within three weeks, he had secured temporary facilities, re-employed his workforce, and within months, his operations generated over $10 million in revenue.

In the military theater, General George S. Patton utilized German counter-offensives not as defensive crises, but as strategic traps. During the Battle of the Bulge in December 1944, when the German army launched a massive surprise blitzkrieg through the Ardennes forest, surrounded the 101st Airborne at Bastogne, and created a dangerous bulge in Allied lines, Allied high command panicked. Patton saw the inverted opportunity: 'The kraut has stuck his head inside the meat grinder, and I have hold of the handle.' Within 72 hours, Patton executed an unprecedented 90-degree pivot of his entire Third Army through blizzards, relieving Bastogne and crushing the German offensive.

In modern business, Steve Jobs's humiliating public firing from Apple in 1985 seemed like a career execution. Years later, Jobs reflected: 'I didn't see it then, but it turned out that getting fired from Apple was the best thing that could have ever happened to me. The heaviness of being successful was replaced by the lightness of being a beginner again.' During his exile, he founded NeXT (whose operating system became macOS) and acquired Pixar (revolutionizing computer animation), returning to Apple in 1997 with the mature executive wisdom that built the most valuable enterprise in human history.""",
        "boundary": """The obstacle is the way is not a license for toxic positivity or reckless masochism. You should not deliberately engineer catastrophic failures or tolerate abusive environments under the guise of 'building character.' It is an emergency operational heuristic to be deployed when an unavoidable, immutable external shock hits.""",
        "action_item": """Perform Marcus's Reframing Drill: Write down your biggest current professional headache or roadblock. Cross out the complaint and write: 'This obstacle is giving me the rare chance to practice [Patience / Redundancy / First-Principles Engineering]. My next concrete move is...'"""
    },

    "idea_attention_residue": {
        "detailed_explanation": """### 1. The Superpower of the 21st-Century Economy
In *Deep Work*, computer science professor Cal Newport establishes that the ability to perform deep work—professional activities performed in a state of distraction-free concentration that push your cognitive capabilities to their limit—is becoming increasingly rare at the exact same time it is becoming increasingly valuable. Those who cultivate this skill, and make it the core of their working life, will systematically outperform peers who swim in fragmented shallows.

### 2. The Neurological Cost of Attention Residue
Sophie Leroy, a business professor at the University of Minnesota, discovered the phenomenon of **Attention Residue**. When you switch from Task A (writing code, drafting strategy) to quickly glance at Task B (checking Slack, skimming an email notification), your attention does not cleanly transition. A significant portion of your cognitive processing remains stranded on Task B, leaving you in a state of fractured cognitive efficiency. Even if the glance took only 15 seconds, full neurological refocusing on Task A requires 15 to 25 minutes. Workers who toggle communication tools every 6 minutes never enter the prefrontal neurological state required for high-yield breakthroughs.

### 3. The Deep Work Equation
Newport formalizes the law of intellectual productivity:
$$\\text{High-Quality Work Produced} = (\\text{Time Spent}) \\times (\\text{Intensity of Focus})$$
If your Intensity of Focus is compromised by ambient multitasking, increasing Time Spent merely leads to burnout without generating depth. Doubling your focus intensity allows you to produce in 3 hours what an unfocused peer struggles to finish in an 8-hour workday.

### 4. Architectural Philosophies of Deep Work
Practitioners must select an intentional scheduling philosophy:
- **Monastic:** Ruthlessly eliminating all secondary communication to dedicate months to a single magnum opus.
- **Bimodal:** Dividing time into multi-day blocks of pure isolation followed by days of open coordination.
- **Rhythmic:** Establishing a daily, unbreakable morning block (e.g. 8:00 AM - 11:30 AM) of sacred, phone-free immersion.
- **Journalistic:** Shifting rapidly into deep focus whenever a free 90-minute window appears (requires high mental discipline).""",
        "example": """Carl Jung built a physical stone tower in Bollingen, Switzerland, in 1922 to establish monastic deep work. Without electricity, running water, or telephone communication, Jung locked himself inside his private stone study each morning to write foundational psychological treatises and analyze the collective unconscious, emerging in the afternoon to chop wood and cook simple meals. This deep isolation enabled him to revolutionize 20th-century psychiatry while maintaining a demanding clinical practice in Zurich.

In software engineering, Bill Gates famously took bi-annual 'Think Weeks' throughout his tenure as CEO of Microsoft. Gates retreated to a secluded lakeside cottage with zero internet access, zero corporate meetings, and boxes of technical whitepapers, research studies, and academic manuscripts. During his 1995 Think Week, Gates authored the famed 'The Internet Tidal Wave' memo, which completely pivoted Microsoft's strategy to incorporate internet protocols across Windows, Office, and server infrastructure, defending its software monopoly into the new millennium.

Theoretical physicist Peter Higgs, who predicted the existence of the Higgs boson particle, attributed his Nobel Prize-winning breakthrough to a complete absence of modern communication interruptions. Higgs famously worked without a telephone, refused to use computers, and never checked email, stating: 'Today I wouldn't get an academic job. It's as simple as that. I wouldn't be regarded as productive enough because I wrote only a handful of papers.' Yet his deep immersion cracked one of the greatest riddles in the Standard Model of particle physics.""",
        "boundary": """Deep work is metabolically exhausting. Empirical neuroscience indicates that even elite performers (concert violinists, grandmasters, mathematicians) can sustain at most 3 to 4 hours of true deep work per day. Attempting to force 8 continuous hours of deep work leads to cognitive degradation. The remainder of the workday should be allocated to low-friction administrative coordination, exercise, and deep biological recovery.""",
        "action_item": """Institute a 'Bunker Block' Tomorrow Morning: Set your phone in another room on airplane mode. Block out 90 minutes on your calendar from 9:00 AM to 10:30 AM. Work on your single highest-leverage strategic problem with zero browser tabs open except the active document."""
    },

    "idea_dichotomy_control": {
        "detailed_explanation": """### 1. Epictetus and the Enchiridion Axiom
In the opening line of the *Enchiridion*, Stoic philosopher Epictetus—who spent his youth as a physically crippled slave in Rome before establishing his philosophical academy—posited the fundamental boundary of human sanity: *"Some things are within our power, while others are not."* The **Dichotomy of Control** divides all phenomena in the universe into two mutually exclusive sets:
1. **Things Up To Us (*Ep' hemin*):** Our opinions, aims, desires, aversions, voluntary choices, and integrity.
2. **Things Not Up To Us (*Ouk ep' hemin*):** Body, property, reputation, external macroeconomic events, weather, stock prices, and the behavior of other human beings.

### 2. The Internal Locus of Sovereign Tranquility
Epictetus observed that 100% of human psychological torment, anxiety, envy, and despair stems from a single cognitive category error: attempting to exert control over external variables, or staking your self-worth on outcomes that depend on outside forces. When you desire an external outcome (e.g. 'I must win this contract' or 'That person must respect me'), you become an enslaved hostage to fortune. When you anchor your satisfaction strictly on internal execution (e.g. 'I will prepare the most rigorous, honest proposal possible'), you achieve emotional invulnerability (*Ataraxia*).

### 3. The Archer Metaphor: Internal Execution vs External Target
Stoic philosopher Antipater of Tarsus formulated the classic analogy of the archer:
- The archer controls the tension of the bowstring, the fletching of the arrow, the sight alignment, the muscle calibration, and the moment of release. All of this is entirely within the archer's control.
- However, the moment the arrow leaves the bow, whether it strikes the target is fundamentally **not** up to the archer: a sudden gust of wind, an earthquake, or an unexpected movement by the target can deflect the arrow.
- The Stoic archer strives with absolute excellence to shoot well, but remains completely detached from the final landing spot of the arrow.

### 4. The Daily Stoic Filter
To operationalize the dichotomy of control:
1. **Active Sifting:** Whenever anxiety strikes, pause and ask: *'Does this matter belong to Set A (my actions) or Set B (external reactions)?'*
2. **Radical Surrender:** If it belongs to Set B, whisper the Stoic release: *"This is nothing to me."*
3. **Hyper-Focus on Set A:** Redirect 100% of your metabolic and cognitive energy into your immediate next voluntary action.""",
        "example": """Admiral James Stockdale, the highest-ranking naval officer held prisoner of war in the 'Hanoi Hilton' during the Vietnam War, survived over seven years of solitary confinement, brutal physical torture, and complete starvation by rigorously applying Epictetus. Stockdale had memorized the *Enchiridion* as a student. In prison, with zero control over his food, medical treatment, or release date, he realized: 'They could control my body, my clothes, and my environment, but they could never control my moral purpose (*prohairesis*) unless I surrendered it.' While optimistic prisoners who set arbitrary dates ('We'll be out by Christmas') died of broken hearts when deadlines passed, Stockdale focused strictly on day-to-day survival and upholding the military code of conduct, eventually earning the Medal of Honor.

In modern competitive athletics, legendary UCLA basketball coach John Wooden never mentioned winning games or defeating opponents to his players. Wooden's entire coaching philosophy was an application of the dichotomy of control: 'Success is peace of mind, which is a direct result of self-satisfaction in knowing you made the effort to become the best of which you are capable.' By focusing entirely on fundamental execution (footwork, conditioning, passing) rather than scoreboards, Wooden led UCLA to an unprecedented 10 NCAA national championships in 12 years.

In financial trading, George Soros demonstrated the dichotomy of control by detaching his ego from investment forecasts. When asked how he survived extreme market crashes, Soros noted: 'I'm not an expert at predicting the future; I'm an expert at recognizing when I am wrong.' Soros treated market prices as external Set B variables; his only internal Set A control was rapid position sizing and immediate stop-loss execution.""",
        "boundary": """Do not use the dichotomy of control to justify apathy, social withdrawal, or neglect of duty. Acknowledging that the future of an organization is not completely within your control is not an excuse to work carelessly. It demands that you care intensely about your duty and personal performance, while abandoning neurotic attachment to external praise or arbitrary guarantees.""",
        "action_item": """The Two-Column Anxiety Triage: Take your biggest active worry right now. Divide a sheet into 'Things I Can Directly Influence Today' and 'Things Governed by External Circumstances'. Cross out the second column completely and execute the first item on the left."""
    },

    "idea_specific_knowledge": {
        "detailed_explanation": """### 1. The Economics of Uniqueness and Irreplaceability
In *How to Get Rich Without Getting Lucky*, Naval Ravikant identifies **Specific Knowledge** as the cornerstone of individual economic sovereignty. Specific knowledge is defined as knowledge that **cannot be trained for in a standardized school or curriculum**. If society can train a human being through a standardized curriculum, bootcamp, or certification course, society can also train thousands of others to replace them—and will eventually write a software algorithm or train an AI model to automate the function entirely.

### 2. Authentic Curiosity as a Protective Moat
Specific knowledge cannot be acquired through extrinsic, forced motivation. It is found by pursuing your genuine, idiosyncratic curiosity and innate childhood obsessions. What feels like effortless play to you looks like exhausting, grueling labor to anyone else. Because nobody can compete with you on being you, building a career around authentic curiosity creates an unassailable moat: you can sustain 80-hour weeks of experimentation simply because you find the domain intrinsically fascinating, while competitors burning willpower burn out within months.

### 3. The Apprenticeship Model vs Institutional Credentials
Specific knowledge is edge-of-the-art knowledge. It is passed down through direct mentorship, personal experimentation, open-source hacking, and scars from failed ventures. It lives in tacit judgment, pattern recognition, and gut heuristics rather than textbook equations. When Steve Jobs audited calligraphy classes, or when John Carmack experimented with 3D graphics rendering in binary assembly, there was no university degree for their craft; their unique synthesis created entirely new economic industries.

### 4. Turning Specific Knowledge into Asymmetric Moats
To package specific knowledge for maximum leverage:
- **Build Under Your Own Name:** Take accountability and personal risk (Skin in the Game).
- **Arm with Leverage:** Connect your unique insight to code, media, or capital so your judgment scales globally.
- **Own Equity:** Never sell specific knowledge by the hour; own fractional upside in the enterprise or IP.""",
        "example": """When Steve Jobs was 19, he dropped out of Reed College but chose to audit classes that interested him purely out of curiosity. He wandered into a calligraphy course taught by Trappist monk Robert Palladino, learning about serif and sans-serif typefaces, variable letter kerning, and what makes great typography artistic. At the time, calligraphy had zero commercial applicability or career trajectory. Ten years later, when designing the original Macintosh computer, Jobs wove that exact specific knowledge into the operating system as beautiful proportional typography, creating Apple's legendary design aesthetic and establishing desktop publishing as an entire industry.

In finance, Jim Simons was an elite mathematician who cracked cryptographic codes for the National Security Agency and won the Oswald Veblen Prize in Geometry. When he founded Renaissance Technologies in 1982, Wall Street firms analyzed balance sheets and visited corporate CEOs. Simons applied his specific knowledge—stochastic differential equations, non-linear pattern recognition, and automated statistical arbitrage. Renaissance's flagship Medallion Fund generated average annual gross returns of 66% over 30 years ($100 billion in net trading profits)—the greatest investing track record in world history—because no traditional MBA or financial analyst possessed his mathematical weaponry.

In modern internet culture, Marques Brownlee (MKBHD) started uploading YouTube videos reviewing HP laptop remote controls and smartphone webcams as a 15-year-old high school student in his bedroom in 2008. Over 15 years of uninterrupted weekly video production, he accumulated specific knowledge in consumer electronics ergonomics, 8K video cinematography, and consumer taste. Today, with over 18 million subscribers, major tech CEOs (including Tim Cook and Satya Nadella) personally debut products on his channel, because his authentic credibility cannot be replicated by traditional advertising agencies.""",
        "boundary": """Specific knowledge must solve real human problems or create genuine economic utility. Having obsessive specific knowledge in an entirely useless, self-indulgent niche with zero market demand (e.g. memorizing obscure movie trivia) generates zero leverage. Specific knowledge becomes economically valuable when it intersects with high societal demand and emerging technological leverage.""",
        "action_item": """The Childhood Archaeology Exercise: Ask your parents or childhood friends: 'What was I obsessively doing between ages 10 and 16 that seemed strange or effortless to me?' Cross-reference that innate curiosity with modern technological leverage (Code, AI, Media)."""
    },

    "idea_system1_system2": {
        "detailed_explanation": """### 1. Dual-Process Cognitive Architecture
In *Thinking, Fast and Slow*, Nobel laureate Daniel Kahneman synthesized decades of behavioral economics and cognitive psychology into a foundational dual-process model of human cognition:
- **System 1 (Fast Thinking):** Operates automatically, instinctively, and rapidly with little or no conscious effort. It governs facial emotion recognition, driving on an empty highway, detecting hostility in a voice, and reflexive fight-or-flight reactions. System 1 runs on heuristics, associative memory, and pattern-matching.
- **System 2 (Slow Thinking):** Allocates attention to effortful mental operations, including complex calculations, logical deductions, statistical probability, strategic planning, and self-control. System 2 is deliberate, analytical, and metabolically expensive.

### 2. The Cognitive Miser Axiom
The central vulnerability of human judgment is that **System 2 is lazy**. The human brain consumes 20% of the body's metabolic glucose despite comprising only 2% of total mass. To conserve energy, the brain defaults to System 1 heuristics whenever possible, allowing intuitive biases (availability heuristic, anchoring, substitution, halo effect) to masquerade as rigorous conclusions. System 2 rarely verifies; it primarily rationalizes decisions that System 1 made instinctively milliseconds earlier.

### 3. Attribute Substitution: The Core Bias Engine
When faced with a complex, intractable question (e.g. *'Is this $100M infrastructure investment financially viable over a 10-year horizon?'*), System 1 automatically executes **attribute substitution**: it silently swaps the hard question for an easy question it can answer immediately (e.g. *'Do I like the charismatic CEO who presented this pitch?'*). Unless System 2 is consciously engaged through formal checklists and analytical friction, executives make multi-million-dollar decisions based on emotional intuition while convincing themselves they performed thorough due diligence.

### 4. Designing Institutional Circuit Breakers
To prevent catastrophic System 1 failures in strategic planning:
1. **Mandatory Cooling Periods:** Enforce an immutable 24-hour delay between high-emotion pitch meetings and capital commitments.
2. **Algorithmic Checklists:** Replace intuitive interview impressions with standardized, blind scoring rubrics (reducing halo bias).
3. **Devil's Advocate Challenge:** Explicitly assign a senior executive to construct the adversarial case against high-consensus proposals.""",
        "example": """In medical trauma centers, emergency room physicians operating under severe sleep deprivation and sensory overload routinely suffer from System 1 heuristic traps (anchoring on the first diagnosis suggested by paramedics, or availability bias from a patient treated earlier that night). World Health Organization surgeon Atul Gawande introduced a simple 19-item Surgical Safety Checklist. By forcing System 2 verification before anesthesia and surgical incision (verifying patient identity, site marking, antibiotic administration), major surgical complications plummeted by 36% and post-operative deaths dropped by 47% across eight global hospitals—not through new surgical technology, but by installing a System 2 circuit breaker over System 1 intuition.

In venture capital investing, SoftBank's Masayoshi Son committed $4.4 billion to WeWork in 2017 after a 12-minute walk with founder Adam Neumann. Son famously asked Neumann: 'In a fight, who wins—the smart guy or the crazy guy?' When Neumann replied 'the crazy guy,' Son declared: 'You are not crazy enough.' This was a quintessential System 1 failure: attribute substitution (swapping complex commercial real-estate lease valuation for charismatic founder energy). When WeWork's IPO collapsed two years later, SoftBank was forced to write down over $14 billion in losses.

In aviation, following the catastrophic crash of United Airlines Flight 173 in 1978 (where the crew became so fixated on an apparent landing gear malfunction that they allowed the DC-8 aircraft to run completely out of fuel and crash in a suburb), the airline industry pioneered Crew Resource Management (CRM). CRM trains junior copilots to actively challenge captains when System 1 fixation occurs, transforming cockpit hierarchy into distributed System 2 verification.""",
        "boundary": """Do not attempt to run System 2 for every mundane daily encounter. Attempting to statistically calculate the expected utility of every handshake, meal choice, or casual conversation will cause acute cognitive exhaustion and social awkwardness. System 1 intuition is extraordinarily powerful in domain environments with high regularity and immediate valid feedback (chess masters, experienced firefighters, tennis players). Reserve System 2 for low-validity, high-noise environments (financial markets, long-term strategy, geopolitical forecasting).""",
        "action_item": """Institute a 'Checklist Filter' on Major Decisions: Identify your top recurring decision (hiring a candidate, buying stock, committing to a vendor). Draft a 5-point non-negotiable checklist that must be scored numerically before any emotional 'gut feeling' is permitted to approve the deal."""
    }
}

def apply_all():
    conn = get_connection()
    cursor = conn.cursor()
    print("[*] Applying deep masterclass enrichments across database...")
    for idea_id, data in ENRICHMENTS.items():
        cursor.execute("SELECT id, title FROM ideas WHERE id = ?", (idea_id,))
        row = cursor.fetchone()
        if not row:
            print(f"  [-] Missing '{idea_id}'")
            continue
        cursor.execute("""
            UPDATE ideas 
            SET detailed_explanation = ?,
                example = ?,
                boundary = ?,
                action_item = ?
            WHERE id = ?
        """, (
            data["detailed_explanation"].strip(),
            data["example"].strip(),
            data["boundary"].strip(),
            data["action_item"].strip(),
            idea_id
        ))
        print(f"  [+] Enriched '{row['title']}' (Words: {len(data['detailed_explanation'].split())})")
    conn.commit()
    conn.close()
    print("[SUCCESS] All targeted models upgraded to 300+ word masterclass treatises!")

if __name__ == "__main__":
    apply_all()
