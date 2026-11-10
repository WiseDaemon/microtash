"""
Deep Model Enrichment Script for Microstash
Upgrades mental models with comprehensive, publication-grade first-principles treatises,
in-depth industrial & historical case studies, explicit boundary failure conditions,
and actionable multi-step execution protocols.
"""
import sys
import json
import sqlite3
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from app.database import get_connection, slugify, generate_copyright_attribution

ENRICHED_MODELS = {
    "idea_inversion": {
        "detailed_explanation": """### 1. Epistemological Asymmetry: The Logic of Non-Ruin
Human cognition is inherently vulnerable to overconfidence and teleological bias: when tasked with designing a successful venture, our intuition defaults to adding ambitious features, optimistic forecasts, and positive projections. However, probability theory reveals a profound asymmetry between success and failure. There are an infinite number of paths that terminate in catastrophe (leverage, fraud, exhaustion, fatal bugs), while the corridor to enduring success is narrow and heavily influenced by stochastic environmental factors. Inversion exploits this asymmetry: while predicting the exact sequence of moves that guarantees brilliant victory is near impossible, identifying and systematically neutralizing the deterministic failure vectors is remarkably tractable.

### 2. Jacobi's Mathematical Axiom & The Munger Heuristic
German mathematician Carl Gustav Jacob Jacobi pioneered algebraic inversion with his famous maxim: *"Man muss immer umkehren"* (invert, always invert). In complex analysis, intractable forward boundary integrals become trivial when inverted and evaluated backwards from the destination state. Charlie Munger ported this mathematical principle to capital allocation, mental hygiene, and strategic planning. Rather than attempting to divine brilliant investment plays, Munger and Warren Buffett focused their cognitive energy on avoiding standard pitfalls: leverage, envy, complexity, over-diversification, and personnel with compromised integrity. As Munger famously quipped: *"All I want to know is where I'm going to die so I'll never go there."*

### 3. Cognitive Biases Overridden by Inversion
Inversion directly counteracts three deeply ingrained psychological pathologies:
- **Planning Fallacy & Optimism Bias:** Daniel Kahneman and Amos Tversky proved that humans dramatically underestimate project completion times, failure probabilities, and budget overruns. Inversion forces a 'Pre-Mortem' mindset: assume the venture has failed catastrophically six months from now, then reconstruct the crime scene.
- **Confirmation Bias:** Strategists actively seek affirmative signals supporting their pet initiatives. Inversion demands an aggressive search for disconfirming evidence and self-sabotaging vulnerabilities.
- **Sunk Cost Rationalization:** By calculating forward anti-goals, practitioners can cleanly identify when an active initiative has entered a deterministic failure funnel and sever it without emotional attachment.

### 4. Operational Inversion Protocol
When applying inversion to high-stakes decisions, follow this structured execution loop:
1. **Explicit Terminal State Definition:** Explicitly write down the worst-case existential outcome with numerical specificity.
2. **Reverse Vulnerability Mapping:** Enumerate the top 5 operational actions or environmental conditions that would guarantee that exact failure.
3. **Guardrail Engineering:** Design immutable procedural safeguards, redundant backups, and tripwire metrics that make those failure modes physically or contractually impossible.""",
        "example": """Charlie Munger deployed inversion during World War II when serving as an Army Air Corps meteorologist in the Pacific theater. While other officers asked 'How do I map a safe flight path for these pilots?', Munger realized that benign weather could rapidly turn treacherous. He inverted the problem: 'What exact atmospheric conditions will kill these pilots, and how do I ensure no aircraft ever encounters them?' By identifying freezing air pockets, zero-visibility fog banks, and fuel exhaustion thresholds, he refused flight clearances whenever those specific death vectors appeared, maintaining an extraordinary safety record.

In corporate finance, John Bogle transformed asset management by inverting the entire mutual fund industry. While Wall Street firms competed frantically to predict winning stocks—generating huge trading turnover, massive commissions, and heavy management fees that systematically lagged the market—Bogle inverted the problem: 'What guarantees that an investor captures the gross return of the market minus the absolute minimum drag?' By eliminating trading turnover, firing active managers, and cutting expense ratios from 1.5% to 0.05%, Vanguard's index fund outperformed 85% of professional portfolio managers over two-decade horizons.

In software reliability engineering, Netflix implemented inversion through Chaos Engineering. Rather than hoping distributed microservices would survive unannounced AWS outages, engineers created 'Chaos Monkey'—an automated daemon that randomly terminates production servers during peak business hours. By inverting reliability into deliberate failure injection, engineers were forced to architect stateless failovers and self-healing services that withstand catastrophic infrastructure failures without customer interruption.""",
        "boundary": """Do not apply inversion dogmatically in early-stage greenfield exploration or artistic creation. Inversion is a risk-mitigation and downside-protection tool; when you are exploring open-ended possibility spaces with negligible downside and unlimited positive optionality, premature inversion induces risk-aversion, over-filtering, and paralysis. Use inversion after hypothesis validation, not before.""",
        "action_item": """Run a 30-Minute Pre-Mortem Protocol: Before signing off on your next major initiative, gather your core stakeholders. Announce: 'Imagine it is 12 months from now, and this initiative has failed catastrophically. What caused the disaster?' Write down every vulnerability and install 2 preventative guardrails today."""
    },

    "idea_first_principles": {
        "detailed_explanation": """### 1. Epistemological Roots: Aristotle to Descartes
First-principles thinking (reasoning from fundamental truths) represents the gold standard of scientific epistemology. Aristotle defined a first principle (*arche*) as the first basis from which a thing is known—an irreducible axiom that cannot be deduced from any other proposition. Centuries later, René Descartes formalized this in *Meditations on First Philosophy* through radical Cartesian doubt: systematically stripping away every received tradition, sensory perception, and social dogma until arriving at indubitable foundational bedrock (*Cogito, ergo sum*).

### 2. Analogy vs First-Principles: The Cognitive Trap
The human brain is an evolutionary energy-conservation engine. Reasoning by analogy—copying what competitors do with 5% cosmetic tweaks—burns minimal glucose and protects social conformity. If everyone else in an industry prices a service at $500, benchmarking sets your target at $475. While analogy works adequately in static environments, it creates systemic blindness in the face of technological inflection points. Analogy locks teams into local optima; first-principles reasoning deconstructs the problem to raw physics, thermodynamic limits, and unit economics, enabling global step-function breakthroughs.

### 3. The Deconstruction & Reconstruction Framework
Reasoning from first principles requires a disciplined two-phase mental procedure:
- **Phase A (Radical Deconstruction):** Strip away packaging, legal conventions, industry jargon, and supplier markups. Ask: *What are the immutable physical materials, energy requirements, and computational constraints of this problem?*
- **Phase B (Ground-Up Synthesis):** Starting strictly from those foundational truths, ask: *What is the most direct, thermodynamically efficient path to combine these atomic components into a solution?* Any delta between current market price and raw material cost is an opportunity for arbitrage or innovation.

### 4. Overcoming Social and Institutional Inertia
The primary barrier to first-principles thinking is not technical; it is institutional. In corporate and political structures, reasoning by analogy provides political cover: *"Nobody ever got fired for buying IBM."* Proposing a ground-up alternative exposes the innovator to acute career risk if it fails. Deploying first-principles requires combining intellectual rigor with organizational autonomy.""",
        "example": """When Elon Musk founded SpaceX in 2002, existing aerospace conglomerates (Boeing, Lockheed Martin) and Russian launch providers quoted rocket costs between $65 million and $130 million per mission. Instead of accepting the prevailing market price as an immutable constraint, Musk applied first-principles decomposition. He asked: 'What is a rocket physically made of?' The answer: aerospace-grade aluminum alloys, titanium, copper, carbon fiber, and rocket fuel. 

Musk looked up the spot commodity prices of each material on the London Metal Exchange and calculated that the raw materials comprised only about 2% of the total price of a finished rocket. The remaining 98% consisted of bureaucratic subcontractor markups, cost-plus contracting inefficiencies, and historical aerospace overhead. By bringing manufacturing, precision machining, software flight controls, and avionics completely in-house, SpaceX reduced launch manufacturing costs by over 70%, pioneered reusable orbital rocket boosters, and achieved dominant global market share in orbital mass delivery.

Similarly, in battery manufacturing, early electric vehicle skeptics claimed lithium-ion battery packs would never drop below $600 per kilowatt-hour because 'that was what they historically cost.' By breaking down the raw spot prices of cobalt, nickel, aluminum, carbon, and polymers on the open market ($80/kWh of raw materials), Tesla focused engineering solely on chemical refinement and manufacturing scale, driving battery pack costs below $120/kWh and making mass-market electric transit economically competitive with internal combustion engines.""",
        "boundary": """Do not apply first-principles thinking to every trivial everyday decision. Re-evaluating the physical chemistry of your morning coffee or questioning established municipal traffic conventions wastes vital cognitive bandwidth. Reserve first-principles exclusively for decisions where stakes are immense, conventional wisdom has plateaued, or you suspect a massive delta between actual cost and market convention.""",
        "action_item": """Isolate the single most expensive recurring cost or operational bottleneck in your business. Deconstruct it into its raw fundamental materials, human hours, and compute costs. Calculate the true physical floor cost and evaluate the delta."""
    },

    "idea_circle_competence": {
        "detailed_explanation": """### 1. The Geometry of Judgment
The Circle of Competence model, developed across decades by Warren Buffett and Charlie Munger, establishes that every decision-maker possesses a perimeter of authentic insight acquired through intense immersion, obsessive study, and hands-on trial-and-error. The central thesis of the model is counter-intuitive: **the absolute diameter of your circle is largely irrelevant; what matters catastrophically is knowing where the boundary lies.** Operating inside a small circle generates extraordinary asymmetric edge. Stepping even one millimeter outside that circle without realizing it transforms you from a disciplined expert into an unsuspecting mark.

### 2. Authentic Knowledge vs Chauffeur Knowledge
Max Planck, after winning the Nobel Prize in Physics, toured Germany giving identical lectures on quantum mechanics. His chauffeur memorized the lecture verbatim and offered to switch places for a session in Munich. The chauffeur delivered the lecture flawlessly. However, when a physicist in the audience asked an advanced question regarding quantum fluctuations, the chauffeur had zero mental model: he had surface fluency without structural comprehension. Charlie Munger uses this parable to distinguish between authentic expertise (earned through sweat and scars) and 'chauffeur knowledge' (parroting industry jargon, buzzwords, and executive summaries).

### 3. The Seduction of Extrapolation
The primary failure mode of successful individuals is competence spillover. Achieving monumental success in one specialized discipline (e.g. software engineering, neurosurgery, or real estate) breeds an intoxicating illusion of universal intellectual superiority. Founders and executives routinely extrapolate their domain edge into macroeconomic forecasting, currency speculation, or complex medical investments, where their actual predictive power is worse than random chance.

### 4. Disciplined Boundary Maintenance
Maintaining a sharp circle of competence requires three institutional practices:
- **The 'Too Hard' Pile:** Buffett maintains a physical tray on his desk labeled 'Too Hard.' If an investment thesis requires forecasting five uncertain variables outside his domain, it is immediately discarded regardless of hype.
- **Intellectual Humility as a Moat:** True experts say *"I don't know"* with calm confidence, whereas charlatans offer fluent opinions on every trending topic.
- **Continuous Perimeter Calibration:** Testing your beliefs against verifiable real-world outcomes to ensure your circle is expanding through deliberate practice rather than shrinking through obsolescence.""",
        "example": """During the frantic dot-com bubble of 1998-2000, Silicon Valley startups with zero revenues were trading at hundreds of times forward sales. Major financial publications ran cover stories questioning Warren Buffett's relevance, asking: 'What's Wrong, Warren?' and 'Has the Oracle of Omaha Lost His Touch?' High-profile investors ridiculed Berkshire Hathaway for sitting on tens of billions in cash while technology stocks doubled every quarter. 

Buffett refused to deploy capital into internet infrastructure and dot-com software, stating plainly: 'I don't invest in things I don't understand. It doesn't mean these companies won't succeed; it simply means their future cash flows lie outside my circle of competence.' When the NASDAQ collapsed 80% between 2000 and 2002, erasing trillions in market capitalization, Berkshire Hathaway suffered zero losses, preserved pristine liquidity, and utilized its dry powder to acquire distressed industrial, utility, and insurance assets at generational discounts.

In contrast, Long-Term Capital Management (LTCM)—a hedge fund founded by Nobel laureate economists and renowned Wall Street bond traders—possessed unparalleled mathematical edge in fixed-income arbitrage. However, in 1998, they stepped outside their circle by taking massive leveraged directional bets on Russian sovereign debt and equity volatility. When Russia unexpectedly defaulted on its domestic debt, LTCM lost $4.6 billion in six weeks and required a Federal Reserve-orchestrated bailout to prevent systemic Wall Street collapse.""",
        "boundary": """Do not mistake the circle of competence for intellectual stagnation. Having a defined perimeter is not an excuse to refuse learning new domains. It means acknowledging your current level of understanding honestly: when exploring a new field, recognize that you are a novice, reduce bet size, consult verified domain masters, and avoid making irreversible leveraged commitments.""",
        "action_item": """Draw two concentric circles on paper. In the inner circle, write the 3 domains where you possess verifiable, differentiated judgment. In the outer circle, write 3 trending domains where you have opinions but zero operational track record. Vow to make zero high-stakes bets in the outer ring this quarter."""
    },

    "idea_second_order": {
        "detailed_explanation": """### 1. The Physics of Complex Adaptive Systems
Human intuition evolved in the ancestral Pleistocene savannah, where cause and effect were immediate, local, and linear: hear a rustle in the grass, run away; throw a spear, hunt game. Modern civilization, however, operates within complex adaptive systems—interconnected economic, legal, biological, and technical networks where every intervention ripples through multiple orders of feedback. First-order thinking observes only the immediate, surface-level consequence of an action. Second-order thinking asks: *'And then what happens?'* Third-order thinking asks: *'What systemic adaptations will competitors, regulators, and nature make in response?'*

### 2. The Trap of First-Order Optimization
Almost every catastrophic policy, software architecture failure, and personal tragedy stems from optimizing solely for the first order. First-order consequences are universally obvious, immediate, and emotionally rewarding: eating cake tastes delicious; printing money stimulates short-term liquidity; adding code patches resolves a customer ticket. However, the second-order consequences are delayed, systemic, and frequently devastating: metabolic disease, currency debasement, and unmaintainable technical debt. As investor Howard Marks notes: *"First-order thinkers look for simple formulas and easy answers. Second-order thinkers know that success in any domain is counter-intuitive."*

### 3. Emergent Behavior and Feedback Delays
In dynamic systems, cause and effect are separated in both time and space. When an agent intervenes in a market, the participants do not remain passive: they adapt their incentives to game the new rules (Goodhart's Law). Second-order thinking requires mapping the reaction functions of all network nodes:
- How will adversaries adapt?
- What new equilibrium will emerge once the initial shock dissipates?
- Will the solution create a more resilient system or introduce hidden brittle dependencies?

### 4. Second-Order Decision Architecture
To systematically incorporate higher-order analysis into decision-making:
1. **Temporal Ripple Mapping:** Create a timeline matrix: Day 1 (Immediate), Month 6 (Adaptation), Year 3 (Equilibrium).
2. **Actor Reaction Functions:** For every key constituent (customers, rivals, regulators, employees), articulate their optimal selfish counter-move.
3. **Falsification Thresholds:** Define specific indicator metrics that alert you when second-order unintended consequences begin outpacing primary gains.""",
        "example": """In colonial British India, the administration in Delhi became alarmed by the infestation of venomous cobras. Applying naive first-order thinking, the governor established a generous cash bounty for every dead cobra skin delivered to authorities. First-order consequence: citizens caught and killed cobras, and the policy was hailed as an immediate triumph. Second-order consequence: enterprising entrepreneurs realized that hunting wild snakes was dangerous and inefficient compared to breeding cobras in captivity. Vast commercial cobra farms sprouted in basements across Delhi to harvest government bounties. When authorities realized the fraud and canceled the bounty, breeders released thousands of now-worthless venomous snakes into the streets, leaving Delhi with a vastly worse infestation than before the intervention.

In modern urban planning, the 'Braess's Paradox' and induced demand demonstrate second-order mechanics. When transportation authorities widen a congested four-lane highway into an eight-lane superhighway, first-order intuition assumes travel times will halve. In reality, the temporary drop in transit time incentivizes thousands of commuters who previously took trains or traveled at off-peak hours to drive cars, while encouraging real-estate developers to build exurban subdivisions. Within two years, the eight-lane highway is just as paralyzed as the original road, having consumed billions in capital while exacerbating total carbon emissions.

In monetary economics, zero-interest-rate policies (ZIRP) implemented after the 2008 financial crisis aimed to stimulate corporate capital investment (first-order). The second- and third-order consequences over the subsequent decade included massive asset price inflation in residential housing, an explosion of unprofitable 'zombie' companies kept alive by cheap debt, and an intense search for yield that fueled reckless speculation in speculative assets.""",
        "boundary": """Avoid 'paralysis by analysis' in trivial low-stakes decisions. Attempting to calculate the fifth-order consequences of what to order for lunch wastes precious mental energy. Second-order thinking is mandatory for high-stakes, asymmetric, irreversible decisions where complex human feedback and multi-year time horizons govern the outcome.""",
        "action_item": """Before approving any policy change, price shift, or strategic pivot, draw 3 columns: 'Immediate Consequence (1-30 Days)', 'Stakeholder Adaptation (3-12 Months)', and 'Compounding Equilibrium (2-5 Years)'. Force your team to defend the proposal under the third column."""
    },

    "idea_antifragility": {
        "detailed_explanation": """### 1. The Triad: Fragile, Robust, Antifragile
In *Antifragile*, scholar and risk-theorist Nassim Nicholas Taleb identified a glaring deficiency in human language: there was no direct antonym for the word 'fragile'. Words like 'robust', 'strong', or 'resilient' merely describe entities that resist stress and remain identical (like a granite boulder or a concrete bunker). Taleb coined the term **Antifragile** to describe things that *gain from disorder*—systems that actively improve, adapt, and grow stronger when exposed to volatility, randomness, stressors, and time.

| State | Metaphor | Reaction to Chaos / Stress | Asymmetry |
|---|---|---|---|
| **Fragile** | Porcelain Teacup, Damocles | Breaks, shatters, degrades | Negative asymmetry: small downside risk, zero upside |
| **Robust** | Granite Rock, Phoenix | Resists, stays equal | Symmetric: unaffected within design limits |
| **Antifragile** | Hydra, Muscle Tissue | Thrives, grows, evolves | Positive asymmetry: huge upside from volatility, bounded downside |

### 2. Hormesis and Overcompensation
The fundamental biological mechanism of antifragility is **hormesis**—the phenomenon where a low, non-lethal dose of a stressor or toxin stimulates beneficial overcompensation. When an athlete lifts a heavy barbell, muscle fibers experience mechanical micro-tears (localized trauma). In response, the body does not merely repair the damage to previous baseline; it overcompensates by synthesizing denser myofibrils and strengthening connective bone density in anticipation of future shocks. Conversely, placing an astronaut or patient on complete prolonged bed rest removes all gravitational stressors, causing rapid bone demineralization, muscle atrophy, and cardiovascular decay.

### 3. The Iatrogenics of Suppressing Volatility
Taleb warns of 'iatrogenics'—harm caused by the healer. When central planners, overprotective parents, or bureaucratic regulators attempt to smooth out all natural volatility (eliminating small forest fires, bailing out failing businesses, preventing minor childhood scrapes), they artificially prevent the system from testing its boundaries and purging hidden rot. By suppressing small, localized volatility, they transform natural distributed stress into massive, systemic, catastrophic fragility (producing mega-fires, financial panics, and fragile adults).

### 4. The Barbell Strategy for Asymmetric Upside
To architect an antifragile life or enterprise, Taleb advocates the **Barbell Strategy**:
- Place 85-90% of your resources in hyper-safe, ultra-conservative bastions completely immune to catastrophic ruin (cash equivalents, sovereign treasuries, boring core competencies).
- Place the remaining 10-15% in dozens of high-risk, open-ended bets with bounded downside (you can only lose the small capital invested) and unlimited non-linear upside (venture investments, patents, books, code).
- Completely eliminate the fragile middle: pseudo-safe assets with hidden catastrophic tail-risk.""",
        "example": """The evolution of the human immune system is the quintessence of antifragility. When a child plays in dirt and is exposed to diverse environmental bacteria, the adaptive immune system encounters foreign antigens, synthesizes specialized memory B-cells and T-cells, and builds long-term immunological resilience against virulent pathogens. In contrast, children raised in hyper-sterilized environments frequently develop autoimmune disorders and severe allergies (the hygiene hypothesis), because the immune system, starved of external stressors, turns inward and attacks the host's own tissues.

In financial architecture, the collapse of Lehman Brothers in 2008 demonstrated catastrophic fragility. Lehman leveraged its balance sheet over 30-to-1, primarily in illiquid subprime mortgage-backed securities. It had zero tolerance for volatility; a mere 3.3% decline in asset value wiped out 100% of its equity capital, triggering systemic bankruptcy. In contrast, Taleb's fund Universa Investments operates as an antifragile barbell: holding the vast majority of capital in short-term US Treasury bills, while continuously allocating small fractions to out-of-the-money put options on the stock market. During normal market conditions, the fund experiences tiny, predictable option bleed; during extreme market dislocations (like the 2008 crash or 2020 pandemic), the options explode non-linearly, delivering returns of over 3,000% from market chaos.

In software architecture, modern microservices platforms like Kubernetes utilize antifragile orchestrators. If a single microservice container experiences a memory leak or crash, the container runtime automatically kills the rogue instance, boots a fresh image on an alternate node, and shifts traffic seamlessly, making the overall distributed cluster stronger and more reliable through automated localized failure recovery.""",
        "boundary": """Antifragility requires two non-negotiable prerequisites: **absence of existential ruin** and **adequate recovery intervals**. A stressor that kills the host or completely obliterates an enterprise produces zero antifragile growth—only death. Furthermore, continuous chronic stress without recovery produces cumulative exhaustion and degradation (burnout). Stressors must be acute, survivable, and followed by adequate consolidation periods.""",
        "action_item": """Conduct an Antifragile Audit: Identify one area where you are over-optimizing for comfort or stability (e.g. relying on a single employer or single marketing channel). Construct a Barbell: protect your core survival with 6 months of liquid runway, and allocate 5 hours weekly to an open-ended asymmetric side-project."""
    },

    "idea_skin_in_the_game": {
        "detailed_explanation": """### 1. The Ethical and Risk Symmetry of Human History
*Skin in the Game* is not merely a modern business aphorism; it is the foundational ethical and evolutionary risk-management mechanism of civilization. Formulated rigorously by Nassim Nicholas Taleb, the core axiom asserts: **You must never separate decision-making authority from exposure to the downside consequences of those decisions.** When an individual or institution reaps the upside of a high-stakes gamble while transferring the downside onto others, moral hazard explodes, competence degrades, and the entire system becomes catastrophically fragile.

### 2. The Agency Problem & Moral Hazard
In corporate governance and political theory, the 'Principal-Agent Problem' arises when an agent acts on behalf of a principal but holds misaligned incentives. When corporate executives receive multimillion-dollar stock option bonuses for boosting short-term accounting earnings, but suffer zero clawbacks or personal bankruptcy when those aggressive accounting gimmicks unravel years later, they are incentivized to take reckless tail-risk with other people's capital. True credibility is not possessing fancy credentials, degrees, or polished rhetorical ability; credibility is having personal vulnerability to the outcome of your advice.

### 3. Historical Implementations of Skin in the Game
Ancient legal codes recognized that without symmetric penalties, human systems rot from within:
- **Hammurabi's Code (circa 1750 BC):** Law 229 decreed that if a builder constructs a house for someone, and the house collapses killing the owner, that builder shall be put to death. If the owner's son dies, the builder's son shall be put to death. This brutal symmetry ensured builders designed structures with extreme conservative safety margins.
- **Roman Bridge Engineers:** Roman military commanders required the chief architect and engineers of a bridge to stand beneath the archway while the first legion crossed over it.
- **Captains and Ships:** Naval maritime law traditionally mandated that the captain be the last soul to evacuate a sinking vessel, aligning the captain's personal survival with the safety of passengers and cargo.

### 4. Epistemological Filter: Filtering Gurus and Charlatans
Skin in the game serves as the ultimate epistemological bullshit filter. In academia and modern punditry, individuals face zero penalty for being wrong: an economic forecaster or political commentator can predict hyperinflation or market crashes five years in a row, be completely wrong, and still receive university tenure and television airtime. In the real world of entrepreneurs, traders, and surgeons, being persistently wrong results in bankruptcy, market exit, or revoked licenses. Taleb advises: *"Never ask a doctor what you should do. Ask him what he would do if he were in your shoes."*""",
        "example": """The 2007-2008 Global Financial Crisis was a textbook demonstration of the catastrophe caused by the absence of skin in the game. Investment bank executives packaged subprime mortgages into complex collateralized debt obligations (CDOs), generating billions in origination fees and cashing in hundreds of millions in personal performance bonuses. When the housing market cracked and subprime default rates spiked, institutions like Bear Stearns, Lehman Brothers, and Merrill Lynch faced insolvency. Because the financial system was deemed 'Too Big to Fail', the US federal government orchestrated hundreds of billions in taxpayer bailouts. The bankers retained their prior bonuses, suffered zero personal legal liability, and transferred the colossal financial ruin onto ordinary citizens and taxpayers.

In contrast, Warren Buffett and Charlie Munger constructed Berkshire Hathaway around maximum skin in the game. Over 99% of Buffett's personal net worth is invested directly in Berkshire shares. His annual salary has remained a modest $100,000 for over four decades, with zero stock options and zero executive performance bonuses. If Berkshire makes poor acquisitions or suffers underwriting losses, Buffett's personal fortune shrinks dollar-for-dollar alongside every individual retail shareholder.

In open-source software and venture capitalism, early-stage founders demonstrate skin in the game by investing their life savings and forgoing market salaries to build working prototypes. Investors recognize that a founder who has mortgaged their house and committed five years of sweat equity has skin in the game, whereas a corporate innovation consultant working on an hourly retainer incurs zero downside if the project is aborted.""",
        "boundary": """Skin in the game should not be confused with blind, reckless sacrifice. Demanding skin in the game does not mean that every mistake must be punished with termination. In innovative research and scientific experimentation, honest calculated failures must be permitted to encourage risk-taking. Skin in the game specifically targets **asymmetric transfers of risk**—where someone privatizes gains while socializing losses.""",
        "action_item": """Before accepting advice from any financial planner, consultant, or career coach, ask the Golden Question: 'Can you show me your personal portfolio/operating logs to verify you own this exact advice in your own life?' If they hold zero personal exposure, walk away."""
    }
}

def enrich_database():
    conn = get_connection()
    cursor = conn.cursor()
    print("[*] Updating database with long-form, rigorous mental model treatises...")

    try:
        cursor.execute("ALTER TABLE ideas ADD COLUMN boundary TEXT;")
        conn.commit()
    except Exception:
        pass

    for idea_id, data in ENRICHED_MODELS.items():
        cursor.execute("SELECT id, title FROM ideas WHERE id = ?", (idea_id,))
        row = cursor.fetchone()
        if not row:
            print(f"  [-] Idea '{idea_id}' not found in database, skipping.")
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
    print("[SUCCESS] Database mental models elevated successfully!")

if __name__ == "__main__":
    enrich_database()
