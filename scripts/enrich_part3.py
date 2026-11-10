import sys
from pathlib import Path
PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from app.database import get_connection

ENRICHMENTS_3 = {
    "idea_chestertons_fence": {
        "detailed_explanation": """### 1. The Epistemology of Reformed Restraint
In his 1929 essay collection *The Thing*, British philosopher G.K. Chesterton articulated the premier principle of institutional reform and systems architecture: **Chesterton's Fence**. The parable depicts a fence or gate erected across an ancient country road. The modern, naive reformer approaches and declares: *"I don't see the use of this; let us clear it away immediately."* The wise, seasoned philosopher counters: *"If you do not see the use of it, I certainly will not let you clear it away. Go away and think. Then, when you can come back and tell me that you do see the use of it, I may allow you to destroy it."*

### 2. Latent Function vs Manifest Design
Complex social, legal, biological, and software systems are not assembled in an afternoon by omniscient central planners; they co-evolve organically through centuries of conflict, environmental trauma, and unwritten cultural compromises. Anthropologists distinguish between **Manifest Function** (the stated, obvious reason for a rule) and **Latent Function** (the hidden, evolutionary stabilizing effect it exerts). Naive reformers evaluate rules solely by manifest function; when they cannot find an explicit memo explaining a procedure, they assume historical stupidity rather than historical survival.

### 3. The Tragedy of Blind De-Coupling
When an arrogant engineer deletes a 10-line 'legacy hack' or an executive eliminates a bureaucratic review board, they usually achieve an immediate, measurable first-order efficiency win (faster compile times, faster transaction throughput). However, within months, the catastrophic edge case that originally birthed that fence 10 years ago re-emerges, inflicting millions of dollars in damages. Fences are almost never built to annoy you; they are built because someone before you suffered a horrific disaster.

### 4. The Chesterton Deconstruction Protocol
Before removing, deprecating, or rewriting any established rule or code module:
1. **Historical Archaeology:** Consult commit histories, founding memos, or senior veterans. Answer: *What specific trauma, accident, or legal liability created this fence?*
2. **Failure Mode Re-Simulation:** Mentally simulate: *If this fence did not exist, what catastrophic scenario would occur during peak load or market crashes?*
3. **Earned Destruction:** Only when you can explain the original rationale better than its creators are you intellectually licensed to dismantle or refactor it.""",
        "example": """In 1958, during China's 'Great Leap Forward', central planners launched the 'Four Pests Campaign' to eliminate mosquitoes, flies, rats, and Eurasian tree sparrows. Planners observed sparrows eating grain seeds in rural fields and calculated that each sparrow consumed four pounds of grain annually. Applying naive first-order logic, the state mobilized millions of citizens to bang pots and pans, destroy nests, and shoot sparrows, driving the species to near extinction across China. 

The catastrophic second-order consequence: sparrows did not merely eat seeds; they were the primary biological predator of locusts and agricultural insects. With the ecological fence removed, massive swarms of locusts swept across China completely unmolested, decimating rice and grain harvests. The resulting Great Chinese Famine caused the starvation deaths of an estimated 15 to 45 million people over three years, forcing the government to secretly import 200,000 sparrows from the Soviet Union to re-establish the ecological boundary.

In software engineering, a newly hired senior architect at a major payment gateway identified a 500-millisecond artificial sleep delay in the transaction authorization worker queue. Deeming it amateurish legacy code, the architect deleted the sleep call and deployed to production. During the Black Friday shopping surge, concurrent database write locks spiked by 1,000x, deadlocking the primary PostgreSQL cluster and halting all credit card authorizations for four hours—causing $35 million in lost checkout transactions. The 500ms delay was a crude but brilliant jitter dampener designed four years earlier to prevent database connection pool exhaustion under sudden traffic spikes.""",
        "boundary": """Chesterton's Fence does not mean systems should never be reformed. In fact, many historical fences become obsolete when underlying environmental technologies fundamentally change (e.g. keeping physical signature stamps after introducing cryptographic public keys). The rule merely mandates that **understanding must precede destruction**. Once you have articulated the historical purpose and installed a superior modern alternative, you may tear down the fence.""",
        "action_item": """Run the Fence Audit: Identify one legacy procedure, bureaucratic sign-off, or code routine your team complains about. Forbid anyone from proposing its deletion until someone interviews its originators and produces a 1-page memo explaining its original necessity."""
    },

    "idea_goodharts_law": {
        "detailed_explanation": """### 1. The Breakdown of Proxy Metrics
Formulated by British central bank economist Charles Goodhart in 1975, the foundational law of institutional cybernetics asserts: **"When a measure becomes a target, it ceases to be a good measure."** In social, economic, and technical organizations, human beings are brilliant adaptive optimizers. When management selects a single quantifiable metric as a proxy for holistic organizational health, actors immediately decouple the metric from the underlying mission, optimizing solely for the score while corrupting the actual objective.

### 2. Campbell's Law and The Cobra Effect
Social psychologist Donald T. Campbell independently formulated the sociological equivalent: *"The more any quantitative social indicator is used for social decision-making, the more subject it will be to corruption pressures and the more apt it will be to distort the social processes it is intended to monitor."* If high school teachers are evaluated on standardized test scores, they stop teaching critical thinking and spend 100% of curriculum time drilling test answers (teaching to the test). The proxy metric (test score) improves while actual educational capability degrades.

### 3. The Mathematics of Gaming Incentives
Goodhart's Law operates through three predictable degeneration stages:
1. **Correlation Phase:** In a natural environment, Metric $M$ correlates positively with Quality $Q$ (e.g. enthusiastic lines of code correlate with an engaged programmer).
2. **Targeting Phase:** Management establishes a quota or financial bonus explicitly tied to Metric $M$.
3. **Exploitation & Decoupling:** Participants recognize that optimizing $M$ directly is orders of magnitude easier than generating true Quality $Q$. Scribes write verbose, repetitive code to inflate line counts; sales reps discount prices 90% on the final day of the quarter to hit gross volume targets, destroying company margin.

### 4. Counteracting Goodhart: Antagonistic KPI Pairs
To defend institutions against Goodhart degeneration:
- **Never Optimize a Single Metric in Isolation:** Always pair every primary velocity metric with an antagonistic quality or friction counter-metric.
  - *Speed / Velocity* must be paired with *Defect / Return Rate*.
  - *Customer Acquisition Volume* must be paired with *30-Day Churn & Net Retention*.
  - *Loan Origination Volume* must be paired with *Loan Default / Loss Reserves*.
- **Periodic Metric Rotation:** Rotate proxy evaluations periodically to prevent systemic gaming.""",
        "example": """In the Soviet Union's command economy, the Ministry of Heavy Industry evaluated nail manufacturing factories by gross weight of nails produced. Factory managers immediately responded to the incentive: they ceased producing small, useful carpentry nails and manufactured gigantic, multi-ton iron spikes that fulfilled their weight quota in two days, paralyzing domestic construction. When central planners realized the flaw and changed the quota to total number of nails produced, factories pivoted overnight: they manufactured millions of tiny, paper-thin, fragile pins that were completely unusable for structural building.

In Silicon Valley software startups, Customer Support teams are frequently graded on 'Average Ticket Resolution Time'. Customer agents quickly learned to game the proxy: whenever a customer submitted a complex, frustrating architectural question, agents sent a generic template response ('Please restart your router and clear your browser cache') and immediately marked the ticket as 'Resolved'. If the customer replied in frustration, it generated a new ticket, keeping resolution metrics pristine while leaving real customer satisfaction in ruins.

During the Vietnam War, United States Secretary of Defense Robert McNamara applied quantitative management metrics to military operations, using 'Enemy Body Count' as the definitive proxy metric for battlefield progress. Field commanders, incentivized by promotions and resources, began counting dead civilians, livestock, and unverified targets as enemy combatants, generating statistical reports claiming near-total victory while the actual strategic and political position in the theater deteriorated irreversibly.""",
        "boundary": """Goodhart's Law is not an excuse to abandon measurement and retreat into subjective ambiguity. Organizations need objective KPIs to align decentralized resources. Goodhart's Law mandates that **metrics must be treated as navigational instruments, not moral scorecards**. Pair metrics antagonistically, audit qualitative reality, and never allow a proxy to replace frontline human judgment.""",
        "action_item": """Audit Your Primary KPI: Look at the #1 number your team is evaluated on. Ask: 'If a cynical actor wanted to double this number in 30 days without doing any actual good work, how would they game it?' Install a counter-metric immediately to neutralize that specific loophole."""
    },

    "idea_galls_law": {
        "detailed_explanation": """### 1. The Fundamental Axiom of Systemantics
In his 1977 masterpiece *Systemantics: How Systems Work and Especially How They Fail*, physician and systems theorist John Gall formulated the premier law of complex engineering: **"A complex system that works is invariably found to have evolved from a simple system that worked. A complex system designed from scratch never works and cannot be patched up to make it work. You have to start over with a working simple system."**

### 2. The Non-Linear Failure Surface of Monoliths
Human hubris leads architects, politicians, and software engineers to believe that if they spend enough months drawing blueprints, writing specifications, and calculating edge cases, they can deploy a massive, highly integrated complex system de novo on Day 1. In reality, in any complex system with $N$ interacting subsystems, the number of potential combinatorial failure modes scales exponentially ($2^N$). No human brain, committee, or AI model can anticipate the emergent bugs, race conditions, latency bottlenecks, and feedback loops that ignite when these subsystems interact under real-world stress.

### 3. Evolutionary Survivability vs Theoretical Perfection
Working complex systems—from the human circulatory system to the global financial architecture—were never designed in an ivory tower. They began as crude, resilient, minimal viable loops that survived real-world entropy. The biological cell functioned for two billion years before multicellular organisms emerged; simple single-celled homeostasis was perfected before circulatory networks were layered on top. Complexity must be earned through evolutionary battle-testing, not decreed by architectural decree.

### 4. The Gallian Development Loop
To build monumental systems that actually survive:
1. **The Atomic Kernel:** Strip the entire vision down to a primitive, single-purpose system that works flawlessly end-to-end today.
2. **Stress-Testing the Baseline:** Expose that simple system to live hostile traffic, real user chaos, and operational load.
3. **Modular Expansion:** Layer additional capabilities onto the working core one discrete module at a time, verifying systemic stability before adding the next.""",
        "example": """The global Internet is the greatest technical triumph of Gall's Law in world history. In 1969, ARPANET began as a primitive four-node network connecting computers at UCLA, Stanford, UC Santa Barbara, and the University of Utah. The core protocol—TCP/IP—was designed with radical simplicity: break data into packets, route them independently, and reassemble them at destination. Because that primitive packet-switching protocol worked flawlessly, humanity spent the subsequent 50 years layering email, the World Wide Web, streaming video, mobile smartphones, cryptographic blockchains, and artificial intelligence on top of it, creating an interconnected planetary consciousness.

In contrast, the United Kingdom's National Health Service (NHS) launched the 'National Programme for IT' (NPfIT) in 2002—the largest civil information technology project in history. Central planners attempted to build a massive, fully integrated national electronic health record database, unified prescription routing system, and centralized hospital booking network from scratch. After ten years of bureaucratic delays, shifting software specifications, unresolvable integration bugs, and catastrophic cost overruns, the project was officially abandoned in 2011, incinerating over £10 billion ($12.5 billion) of taxpayer capital without delivering a single working nationwide system.

Similarly, Amazon Web Services (AWS) began in 2006 not as a complex multi-cloud enterprise platform, but as a single primitive service: Amazon S3 (Simple Storage Service). S3 did exactly one thing: put and get unstructured data objects via basic HTTP calls. Because S3 worked with 99.999999999% durability, Amazon layered EC2 (compute instances) on top, followed by databases, networking, and machine learning, evolving into a $100 billion annual cloud empire.""",
        "boundary": """Gall's Law is not an excuse to write sloppy, unmaintainable 'throwaway' code under the banner of moving fast. A simple system that works must be architected with clean, modular boundaries so that future complexity can be grafted onto it without collapsing the core. Simplicity is not carelessness; simplicity is the highest form of structural discipline.""",
        "action_item": """The Modular MVP Test: If your current project is slated to take 6 months before its first public release, stop. What is the stripped-down, 3-day version of the core loop that solves 80% of the customer's problem right now? Ship that first, verify survival, and iterate."""
    },

    "idea_lindy_effect": {
        "detailed_explanation": """### 1. The Survival Physics of Non-Perishable Goods
Named after Lindy's delicatessen in New York City—where Broadway actors and comedians gathered to observe that shows that had run for 100 nights possessed the statistical momentum to run for another 100 nights—the **Lindy Effect** formalizes the survival probability of non-perishable entities. Formulated mathematically by Benoit Mandelbrot and popularized by Nassim Nicholas Taleb, the law asserts: **For non-perishable concepts, technologies, ideas, and institutions, future life expectancy is proportional to their current age.**

### 2. Perishable vs Non-Perishable Decay
To understand Lindy, distinguish between two fundamentally different probability distributions:
- **Perishable Domain (Biological Aging):** Entities subject to physical wear-and-tear (humans, dogs, tomatoes, cars). Each passing day increases the conditional probability of death ($P(\\text{death} \\mid t)$ increases). An 80-year-old human has a much shorter remaining life expectancy than a 20-year-old human.
- **Non-Perishable Domain (Informational / Conceptual Survival):** Entities that are informational or conceptual (books, algorithms, tools, philosophies, recipes). These entities do not suffer mechanical degradation. Each passing century that an idea survives serves as an empirical proof of its robustness against cultural shifts, technological revolutions, and intellectual fads.

### 3. Time as the Ultimate Adversarial Filter
Humanity produces millions of new books, software libraries, scientific hypotheses, and business frameworks every decade. Over 99% of them are ephemeral noise, surviving only months before being washed away by the next cultural cycle. Time is the ultimate, impartial, non-corruptible filter. If a piece of writing (e.g. Homer's *Iliad*, Sun Tzu's *The Art of War*, or Marcus Aurelius's *Meditations*) has been read continuously for 2,000 years, it has survived the collapse of empires, religious wars, and the invention of printing, electricity, and the internet. It is almost mathematically guaranteed to be read 2,000 years from now.

### 4. Applied Lindy: Information Diet and Technical Stacks
- **Read Lindy Books:** Spend 80% of your reading hours on books that are older than 25 years. You automatically bypass 99.9% of intellectual garbage.
- **Build with Lindy Tech:** SQL was invented in 1974; relational databases will outlive 90% of trending modern JavaScript frameworks. Build mission-critical infrastructure on Lindy foundations.""",
        "example": """In software engineering, relational database management systems and SQL (Structured Query Language) were designed by Edgar F. Codd and IBM in the early 1970s. Over the past 50 years, the technology industry experienced dozens of revolutionary waves: object-oriented databases, XML databases, NoSQL, graph databases, and document stores. Yet today, PostgreSQL, MySQL, and SQLite power the core transactional infrastructure of every Fortune 500 bank, mobile operating system, and cloud provider. By virtue of surviving 50 years, SQL has demonstrated Lindy durability: it will likely remain foundational for another 50 years.

In literature and media consumption, consider the contrast between the *New York Times* Best Seller list of 2012 versus Seneca's *Letters from a Stoic* written in 65 AD. Almost none of the political commentary or business strategy books from 2012 are read today; their advice was contextual noise tailored to a fleeting macroeconomic moment. Seneca's letters on grief, ambition, friendship, and mortality, having survived two millennia, remain just as vital and psychologically incisive today as they were in Nero's Rome.

In consumer tools, physical knives, wooden spoons, glass cups, and wheels have remained structurally unchanged for thousands of years. While complex electronic kitchen gadgets (electric pasta makers, single-use fruit slicers) break and end up in thrift stores within three years, the simple chef's knife endures as an irreplaceable culinary primitive.""",
        "boundary": """The Lindy Effect applies strictly to **non-perishable informational or structural entities**, never to biological organisms. Furthermore, Lindy is a statistical heuristic, not an absolute guarantee: ancient institutions can still be obliterated by unprecedented step-function physical disruptions (e.g. horse transport being displaced by the internal combustion engine). Use Lindy to filter for quality, not to blindly dismiss emerging physical breakthroughs.""",
        "action_item": """The Lindy Information Filter: Before opening your next book or adding a dependency to your technical stack, check its age. Vow that for every modern book published this year, you will read one classic that has remained continuously in print for at least 50 years."""
    }
}

def apply_part3():
    conn = get_connection()
    cursor = conn.cursor()
    print("[*] Applying Part 3 masterclass enrichments across database...")
    for idea_id, data in ENRICHMENTS_3.items():
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
    print("[SUCCESS] Part 3 mental models elevated successfully!")

if __name__ == "__main__":
    apply_part3()
