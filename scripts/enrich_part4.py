import sys
from pathlib import Path
PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from app.database import get_connection

ENRICHMENTS_4 = {
    "idea_regret_minimization": {
        "detailed_explanation": """### 1. The Epistemology of Existential Time-Horizon Inversion
When individuals face high-stakes life and career crossroads, conventional decision-making matrices become paralyzed by immediate emotional static: social embarrassment, short-term reduction in cash flow, peer skepticism, and the acute pain of failure. Jeff Bezos formulated the **Regret Minimization Framework** to cleanly bypass these transient cognitive distortions. The model functions through temporal projection: you mentally project your consciousness to age 80, sitting on your porch looking back across the entirety of your biological existence, and ask: **'Which path minimizes the number of unlived regrets?'**

### 2. Symmetrical vs Asymmetrical Regrets: Omission vs Commission
Psychological research by Thomas Gilovich and Victoria Medvec reveals a profound divergence in human regret over time:
- In the short term (days to months), humans regret errors of **commission**—actions taken that failed, resulting in temporary embarrassment or monetary loss.
- In the long term (decades to end of life), humans overwhelmingly regret errors of **omission**—the businesses never started, the book never written, the risks never taken, the love never expressed.
At age 80, the sting of a failed startup or a rejected pitch is completely forgotten; what haunts the twilight of human life is the torturous question: *"What could have been if I had taken the shot?"*

### 3. Asymmetric Optionality at Scale
The Regret Minimization Framework works because it aligns decision-making with asymmetric optionality. Failing at an ambitious, high-agency venture has bounded downside (temporary career reset, minor savings loss, zero irreversible damage), while never attempting it guarantees 100% loss of the infinite upside optionality. By projecting to age 80, the psychological weight of short-term status anxiety drops to zero.

### 4. The 3-Step Horizon Execution Protocol
1. **The 80-Year Horizon Jump:** Close your eyes and visualize yourself at age 80 looking back at your current self.
2. **The Omission Filter:** Ask: *'If I try this bold move and it fails completely, will I regret it at age 80?'* (Almost always NO).
3. **The Haunting Question:** Ask: *'If I never try this because I stayed comfortable, will that omission haunt me at age 80?'* (If YES, execute immediately).""",
        "example": """In 1994, Jeff Bezos was a 30-year-old Senior Vice President at Wall Street quantitative hedge fund D.E. Shaw & Co. He enjoyed a lucrative six-figure salary, elite social status, and a massive annual bonus scheduled for distribution in just a few months. When he discovered that internet web activity was growing at an unprecedented 2,300% per year, he conceived the idea of an online bookstore selling millions of titles. His boss, David E. Shaw, listened to the proposal and counseled him: 'That sounds like a great idea, Jeff, but it would be a better idea for somebody who didn't already have a good job.' 

Bezos took a 48-hour walk in Central Park to decide. Applying the Regret Minimization Framework, he realized: 'I knew that when I was eighty, I was not going to regret having tried this. I knew that I would never regret participating in this thing called the Internet that I thought was going to be a world-altering event. Even if I failed completely and went bankrupt, I would be proud of the attempt. But I also knew that I would be forever haunted by the regret of never having tried at all.' He walked into Shaw's office, resigned, forfeited his year-end Wall Street bonus, packed his belongings into a Chevy Blazer, and drove to Seattle to incorporate Amazon in a suburban garage.

Similarly, in 1975, 19-year-old Bill Gates dropped out of Harvard University to co-found Microsoft with Paul Allen. When his parents expressed acute alarm at abandoning an elite Ivy League degree, Gates evaluated the decision through regret minimization: the microcomputer revolution (the Altair 8800 and the Intel 8080 chip) was happening right now. If he waited until graduation in 1977, the software operating system window would be permanently closed. At age 80, he would never regret having to re-enroll at Harvard, but he would forever regret missing the birth of personal computing.""",
        "boundary": """Do not use regret minimization to justify reckless, existential ruin bets (e.g. gambling your life savings on leveraged penny stocks or Russian roulette). The framework operates strictly on **calculated risks where failure is survivable**. If failing at age 30 produces irreversible catastrophic ruin (death, prison, bankruptcy that harms dependents), the framework must be checked by the Inversion Principle and margin of safety.""",
        "action_item": """The Age-80 Letter Drill: Take the boldest, most frightening crossroad decision currently facing you. Write a 1-paragraph letter from your 80-year-old self advising your current self on what to do. Sign it and take the first concrete step within 24 hours."""
    },

    "idea_ooda_loop": {
        "detailed_explanation": """### 1. Military Cybernetics & Cognitive Dominance
Developed by United States Air Force Colonel John Boyd—famed as 'Forty-Second Boyd' for his standing wager that he could defeat any pilot in simulated air-to-air dogfights within forty seconds—the **OODA Loop (Observe, Orient, Decide, Act)** is the premier cybernetic model of strategic competition under uncertainty. Boyd demonstrated that victory in combat, business, and evolutionary survival does not belong to the actor with the largest budget or heaviest armor, but to the actor whose cognitive loop cycles faster than the environment changes.

### 2. The Core Phases of The OODA Architecture
The OODA Loop consists of four continuous, dynamic feedback stages:
1. **Observe (Live Telemetry):** Sensing real-time environmental data, anomalies, adversary moves, and internal state.
2. **Orient (The Master Filter):** The decisive, most critical phase. Orientation is the genetic heritage, cultural traditions, previous experience, and cognitive models through which observation is filtered into meaning. Whoever has superior mental models orients accurately; whoever has rigid dogmas orients falsely.
3. **Decide (Hypothesis Generation):** Selecting an operational hypothesis from alternative pathways.
4. **Act (Probing Execution):** Executing a rapid, real-world probe that tests the environment and restarts the observation cycle.

### 3. Operating Inside the Adversary's Decision Cycle
The profound strategic genius of Boyd's model is **compression**. If you can execute your OODA loop inside your competitor's cycle time, your actions occur before they can even finish orienting to your previous move. Their observations become obsolete before they can decide; their plans address a reality that no longer exists. They become trapped in an unresolvable spiral of cognitive friction, disorientation, panic, and paralysis.

### 4. Agility Over Clout: The Fast Transient
Boyd demonstrated that agility is governed by the 'fast transient'—the speed at which a system can transition from one operational maneuver to another. In corporate strategy, large enterprises take 12 months to Observe, Orient, Decide, and Act through quarterly board committees. A lean startup that loops OODA every 72 hours runs 120 iterations in the time the corporate giant runs one, running circles around the incumbent.""",
        "example": """During the Korean War, American pilots flying the F-86 Sabre achieved an astonishing 10-to-1 kill ratio against Soviet pilots flying the MiG-15. This outcome baffled military analysts because the MiG-15 was aerodynamically superior: it possessed a higher climb rate, faster acceleration, tighter turning radius, and heavier cannon firepower. John Boyd analyzed the anomaly and discovered two subtle operational features:
1. The F-86 had a bubble canopy that provided 360-degree unobstructed visibility, whereas the MiG-15 pilot had restricted sightlines. The American pilot **Observed** the threat seconds earlier.
2. The F-86 possessed hydraulic flight controls, allowing the pilot to transition from a dive to a bank with minimal physical effort, whereas the MiG required immense manual stick force. The F-86 pilot could cycle the OODA loop and execute maneuvers three times faster, forcing the Soviet pilot into perpetual disorientation.

In modern business, Zara (Inditex) dominated global fast fashion by institutionalizing the OODA loop across its supply chain. While traditional fashion houses design collections 9 months in advance (slow OODA cycle), Zara store managers observe real-time sales telemetry daily. When a specific cut or fabric gains traction, Zara's decentralized design and manufacturing hubs in Spain produce and distribute fresh inventory to global stores within 15 days. By cycling OODA 15 times per season, Zara virtually eliminated inventory write-downs and pulverized traditional retailers.

In algorithmic trading, high-frequency market makers execute OODA loops in microseconds. Microwave transmission networks between Chicago and New York observe order-book imbalances, orient market depth, decide liquidity quotes, and execute trades before traditional institutional orders can clear fiber-optic cables.""",
        "boundary": """Do not sacrifice Orientation quality for reckless Action speed. Acting rapidly without accurate Observation and first-principles Orientation simply accelerates you off a cliff. The goal is not frantic activity; the goal is **cohesive, high-fidelity orientation paired with decisive execution**.""",
        "action_item": """Compress Your Feedback Loop: Identify the slowest phase in your team's current delivery cycle (e.g. waiting two weeks for customer feedback). Cut the cycle time in half this week by shipping a 48-hour prototype to 5 live users."""
    },

    "idea_sunk_cost_fallacy": {
        "detailed_explanation": """### 1. The Rationality Deficit of Honoring the Past
In neoclassical microeconomics, the fundamental axiom of rational decision-making asserts: **Sunk costs are unrecoverable historical outlays that must exert zero influence on forward-looking decisions.** Every rational choice must be evaluated strictly on expected future costs versus expected future benefits, and opportunity cost. Yet, across human psychology, politics, warfare, and corporate capital budgeting, human beings persistently violate this axiom, throwing good money, emotional energy, and human lives into failing enterprises simply because they have already spent resources on them.

### 2. Behavioral Foundations: Loss Aversion and Self-Justification
Nobel laureate Richard Thaler and behavioral economists Daniel Kahneman and Amos Tversky identified the deep psychological mechanisms driving the sunk cost fallacy:
- **Loss Aversion:** The psychological pain of realizing a loss is measured to be 2 to 2.5 times more intense than the pleasure of an equivalent gain. Halting a failing project forces an individual to publicly and internally acknowledge: *"I failed, and that $10 million is permanently gone."* Continuing the project preserves the comforting illusion that a turnaround might somehow redeem the past spend.
- **Ego Consistency & Self-Justification:** Humans have an obsessive need to appear consistent to their peers and to themselves (Leon Festinger's cognitive dissonance). Terminating a multi-year project feels like an indictment of their past intelligence.

### 3. The Concorde Effect: When Institutions Multiply Ruin
When the sunk cost fallacy infects organizations and nation-states, it transforms into the 'Concorde Effect'. Bureaucrats and politicians rationalize ongoing subsidies by invoking the memory of past sacrifices: *"We cannot retreat now; otherwise, our fallen soldiers will have died in vain."* Or: *"We have already invested $500 million in this software; we cannot scrap it now."* In reality, past sacrifices cannot be redeemed by future waste; continuing only ensures that more soldiers die in vain and more capital is incinerated.

### 4. Overcoming Sunk Cost: The Clean Slate Protocol
To insulate yourself from sunk cost bias:
1. **The Outsider Test (Andy Grove Heuristic):** Ask: *'If I were fired today and a brand-new CEO walked in with zero historical baggage, what is the very first project they would cancel?'* Then do it yourself immediately.
2. **Explicit Zero-Based Allocation:** Evaluate budgets from zero every fiscal quarter, requiring every dollar to defend its future ROI against cash holdings.""",
        "example": """The quintessential historical case study is the Concorde supersonic passenger jet developed jointly by the British and French governments. By the early 1970s, it was mathematically and commercially obvious that the aircraft was economically non-viable: supersonic sonic booms banned it from flying over overland flight paths, fuel consumption was exorbitant, and payload capacity was tiny. Private airlines canceled their purchase options. Yet, because the British and French governments had already poured billions into research and development, politicians from both nations refused to cancel the program, rationalizing that stopping would waste the investments already made. They continued pouring billions into Concorde operations for three decades, subsidizing ticket sales for wealthy transatlantic passengers until a catastrophic crash in Paris in 2000 finally forced its commercial retirement.

In corporate turnarounds, Intel's pivot in 1985 demonstrates heroic liberation from sunk cost. Intel had invented the dynamic random-access memory (DRAM) microchip industry and poured its entire corporate identity into memory manufacturing for 15 years. By 1985, Japanese conglomerates (Toshiba, Hitachi) flooded the global market with cheaper, higher-yield memory chips, plunging Intel into multi-million-dollar quarterly losses. CEO Gordon Moore and President Andy Grove sat in their Santa Clara office paralyzed by sunk cost. Grove looked at Moore and asked the legendary question: 'If we got kicked out and the board brought in a new CEO, what do you think he would do?' Moore answered without hesitation: 'He would get us out of memories.' Grove replied: 'Why shouldn't you and I walk out the door, come back in, and do it ourselves?' Intel immediately shut down its memory fabrication plants, fired thousands of workers, and reallocated 100% of capital to microprocessors, birthing the x86 chip empire that powered the PC revolution.

In everyday software development, engineering teams frequently spend six months building a complex proprietary ORM or authentication service that proves buggy and difficult to maintain. When a reliable open-source library arrives that solves the problem for free, junior leads often refuse to migrate: 'We spent six months building this custom code!' Senior architects understand that the six months are gone forever; the only relevant question is the maintenance cost over the next five years.""",
        "boundary": """Do not confuse overcoming sunk cost with lack of perseverance. Pivoting away from a failing hypothesis is intellectual discipline; quitting an initiative simply because the work is hard or currently experiencing temporary operational friction is laziness. Distinguish between **fundamental structural insolvency** (the investment thesis is definitively disproven) versus **ordinary execution friction** (the thesis remains sound, but requires grit).""",
        "action_item": """The Clean Slate Audit: Review your current active project portfolio. Identify the single project that drains the most time and capital relative to its future expected return. Apply the Andy Grove Test: 'If I took over this role today with zero emotional attachment to past efforts, would I fund this project?' If the answer is no, kill it this week."""
    }
}

def apply_part4():
    conn = get_connection()
    cursor = conn.cursor()
    print("[*] Applying Part 4 masterclass enrichments across database...")
    for idea_id, data in ENRICHMENTS_4.items():
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
    print("[SUCCESS] Part 4 mental models elevated successfully!")

if __name__ == "__main__":
    apply_part4()
