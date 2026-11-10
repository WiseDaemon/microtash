/**
 * Main Microstash Application Controller
 * Deepstash-inspired microlearning, swipe deck, feed, stashes, and AI Stashifier
 */

window.state = {
  ideas: [],
  stashes: [],
  leitnerIdeas: [],
  currentIdeaIndex: 0,
  currentLeitnerIndex: 0,
  isLeitnerRevealed: false,
  diagramViewMode: localStorage.getItem('microstash_diagram_mode') || 'canvas',
  activeTab: 'swipe',
  selectedTopic: 'All',
  searchQuery: '',
  stats: {
    streak_days: 1,
    doomscroll_mins_saved: 0,
    ideas_read_count: 0
  }
};

let searchDebounceTimeout = null;
let lastExtractedIdeas = [];
let lastExtractedBookTitle = "";
let lastExtractedAuthor = "";
let targetIdeaForStash = null;
let currentDeepDiveIdea = null;

document.addEventListener("DOMContentLoaded", async () => {
  await loadStats();
  await loadStashes();
  await loadIdeas();
  await loadLeitnerDue();
  if (typeof initSwipeEngine === 'function') {
    initSwipeEngine();
  }

  // Auto-Fetch enter key & button listeners
  const queryInput = document.getElementById("autofetch-query");
  if (queryInput) {
    queryInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        runAutoFetchAndGenerate();
      }
    });
  }

  const btnAuto = document.getElementById("btn-run-autofetch");
  if (btnAuto) {
    btnAuto.addEventListener("click", (e) => {
      e.preventDefault();
      runAutoFetchAndGenerate();
    });
  }

  const btnManual = document.getElementById("btn-run-ai");
  if (btnManual) {
    btnManual.addEventListener("click", (e) => {
      e.preventDefault();
      runAIExtraction();
    });
  }

  // Keyboard navigation shortcuts
  document.addEventListener("keydown", (e) => {
    if (['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) return;

    // Daily Recall Gym specific shortcuts
    if (window.state.activeTab === 'leitner') {
      if (e.key === " " || e.code === "Space") {
        if (!window.state.isLeitnerRevealed) {
          e.preventDefault();
          revealLeitnerAnswer();
          return;
        }
      } else if (window.state.isLeitnerRevealed) {
        if (e.key === "1" || e.key === "h" || e.key === "H") {
          e.preventDefault();
          submitLeitnerGrade('hard');
          return;
        } else if (e.key === "2" || e.key === "g" || e.key === "G") {
          e.preventDefault();
          submitLeitnerGrade('good');
          return;
        } else if (e.key === "3" || e.key === "e" || e.key === "E") {
          e.preventDefault();
          submitLeitnerGrade('easy');
          return;
        }
      }
    }

    if (e.key === "ArrowRight") {
      e.preventDefault();
      if (typeof handleSwipe === 'function') handleSwipe('right');
    } else if (e.key === "ArrowLeft" || (e.key === " " && window.state.activeTab === 'swipe')) {
      e.preventDefault();
      if (typeof handleSwipe === 'function') handleSwipe('left');
    } else if (e.key === "f" || e.key === "F") {
      e.preventDefault();
      if (typeof flipCard === 'function') flipCard();
    } else if (e.key === "l" || e.key === "L") {
      e.preventDefault();
      toggleLikeCurrentCard();
    } else if (e.key === "s" || e.key === "S") {
      e.preventDefault();
      toggleSaveCurrentCard();
    } else if (e.key === "a" || e.key === "A") {
      e.preventDefault();
      if (typeof playCurrentCardAudio === 'function') playCurrentCardAudio();
    } else if (e.key === "d" || e.key === "D") {
      e.preventDefault();
      openDeepDiveModal();
    } else if (e.key === "Escape") {
      closeDeepDiveModal();
      closeStashModal();
      closeCreateStashModal();
      if (typeof closeShareModal === 'function') closeShareModal();
    }
  });
});

// --- Tab Navigation ---
function switchTab(tabId) {
  window.state.activeTab = tabId;
  const tabs = ['swipe', 'leitner', 'feed', 'stashes', 'ai'];

  tabs.forEach(t => {
    const el = document.getElementById(`tab-${t}`);
    const navBtn = document.getElementById(`nav-btn-${t}`);
    const mNavBtn = document.getElementById(`m-nav-${t}`);

    if (t === tabId) {
      if (el) el.classList.remove('hidden');
      if (navBtn) {
        navBtn.classList.add('bg-indigo-600', 'text-white', 'shadow');
        navBtn.classList.remove('text-slate-300', 'hover:bg-slate-700/50');
      }
      if (mNavBtn) {
        mNavBtn.classList.add('text-indigo-400');
        mNavBtn.classList.remove('text-slate-400');
      }
    } else {
      if (el) el.classList.add('hidden');
      if (navBtn) {
        navBtn.classList.remove('bg-indigo-600', 'text-white', 'shadow');
        navBtn.classList.add('text-slate-300', 'hover:bg-slate-700/50');
      }
      if (mNavBtn) {
        mNavBtn.classList.remove('text-indigo-400');
        mNavBtn.classList.add('text-slate-400');
      }
    }
  });

  if (tabId === 'feed') {
    renderFeedGrid();
  } else if (tabId === 'stashes') {
    renderStashesGrid();
  } else if (tabId === 'leitner') {
    renderLeitnerCard();
  }

  if (window.lucide) lucide.createIcons();
}

// --- Data Fetchers ---
async function loadIdeas() {
  try {
    let url = '/api/ideas';
    if (window.state.selectedTopic === 'leitner-workout') {
      url = '/api/ideas/leitner/due';
    } else {
      const params = new URLSearchParams();
      if (window.state.selectedTopic && window.state.selectedTopic !== 'All' && window.state.selectedTopic !== 'all') {
        params.append('topic', window.state.selectedTopic);
      }
      if (window.state.searchQuery) {
        params.append('q', window.state.searchQuery);
      }
      url = `/api/ideas?${params.toString()}`;
    }

    const res = await fetch(url);
    const data = await res.json();
    window.state.ideas = data;

    if (window.state.currentIdeaIndex >= data.length) {
      window.state.currentIdeaIndex = 0;
    }

    updateSwipeCardDisplay();
    renderFeedGrid();
  } catch (err) {
    console.error("Failed to load ideas:", err);
  }
}

async function loadStashes() {
  try {
    const res = await fetch('/api/stashes');
    const data = await res.json();
    window.state.stashes = data;
    renderStashesGrid();
  } catch (err) {
    console.error("Failed to load stashes:", err);
  }
}

async function loadStats() {
  try {
    const res = await fetch('/api/stats');
    const data = await res.json();
    window.state.stats = data;

    const streakEl = document.getElementById("streak-counter");
    const doomscrollEl = document.getElementById("doomscroll-saved");

    if (streakEl) streakEl.textContent = `${data.streak_days} Day${data.streak_days > 1 ? 's' : ''}`;
    if (doomscrollEl) doomscrollEl.textContent = `${data.doomscroll_mins_saved}m Saved`;
  } catch (err) {
    console.error("Failed to load stats:", err);
  }
}

// --- Topic Theming Helpers ---
function getTopicBadgeClass(topic) {
  const t = (topic || '').toLowerCase();
  if (t.includes('model')) return 'badge-mental-models';
  if (t.includes('prod')) return 'badge-productivity';
  if (t.includes('stoic')) return 'badge-stoicism';
  if (t.includes('wealth') || t.includes('finan') || t.includes('money')) return 'badge-wealth';
  if (t.includes('psych')) return 'badge-psychology';
  if (t.includes('tech') || t.includes('ai')) return 'badge-tech';
  if (t.includes('health') || t.includes('bio')) return 'badge-health';
  return 'badge-mental-models';
}

function getTopicBorderClass(topic) {
  const t = (topic || '').toLowerCase();
  if (t.includes('model')) return 'border-t-mental-models';
  if (t.includes('prod')) return 'border-t-productivity';
  if (t.includes('stoic')) return 'border-t-stoicism';
  if (t.includes('wealth') || t.includes('finan') || t.includes('money')) return 'border-t-wealth';
  if (t.includes('psych')) return 'border-t-psychology';
  if (t.includes('tech') || t.includes('ai')) return 'border-t-tech';
  if (t.includes('health') || t.includes('bio')) return 'border-t-health';
  return 'border-t-mental-models';
}

function getTopicGlowColor(topic) {
  const t = (topic || '').toLowerCase();
  if (t.includes('model')) return 'rgba(99, 102, 241, 0.25)';
  if (t.includes('prod')) return 'rgba(16, 185, 129, 0.25)';
  if (t.includes('stoic')) return 'rgba(245, 158, 11, 0.25)';
  if (t.includes('wealth') || t.includes('finan')) return 'rgba(20, 184, 166, 0.25)';
  if (t.includes('psych')) return 'rgba(168, 85, 247, 0.25)';
  if (t.includes('tech') || t.includes('ai')) return 'rgba(14, 165, 233, 0.25)';
  if (t.includes('health')) return 'rgba(244, 63, 94, 0.25)';
  return 'rgba(99, 102, 241, 0.25)';
}

// --- Visual Explanation & Interactive Mermaid Engine ---
let mermaidInitialized = false;
let diagramRenderCounter = 0;
let currentDiagramZoom = 1.0;
let currentDiagramStepIndex = -1;
let activeDiagramNodes = [];
let currentPanX = 0;
let currentPanY = 0;
let isPanningDiagram = false;
let panStartX = 0;
let panStartY = 0;

function initMermaidIfNeeded() {
  if (mermaidInitialized) return;
  if (window.mermaid) {
    try {
      mermaid.initialize({
        startOnLoad: false,
        theme: 'dark',
        securityLevel: 'loose',
        themeVariables: {
          darkMode: true,
          background: 'transparent',
          primaryColor: '#312e81',
          primaryTextColor: '#ffffff',
          primaryBorderColor: '#6366f1',
          lineColor: '#818cf8',
          secondaryColor: '#064e3b',
          tertiaryColor: '#78350f',
          fontFamily: 'Inter, system-ui, sans-serif'
        }
      });
      mermaidInitialized = true;
    } catch (e) {
      console.warn("Mermaid init warning:", e);
    }
  }
}

async function renderIdeaVisualDiagram(idea, targetElId) {
  const container = document.getElementById(targetElId);
  if (!container || !idea) return;

  // In modal, if user selected Adaptive Step Flow, render directly
  if (targetElId === 'modal-diagram-render' && window.state.diagramViewMode === 'flow') {
    container.innerHTML = renderStyledStepFlow(idea);
    if (window.lucide) lucide.createIcons();
    return;
  }

  initMermaidIfNeeded();
  const rawDiagram = idea.visual_diagram || generateClientFallbackDiagram(idea);

  if (window.mermaid && rawDiagram) {
    try {
      diagramRenderCounter++;
      const uniqueId = `mermaid-svg-${diagramRenderCounter}-${Date.now()}`;
      const cleanDiag = rawDiagram.trim().replace(/^```mermaid\s*/i, '').replace(/```\s*$/, '').trim();
      const { svg } = await mermaid.render(uniqueId, cleanDiag);
      container.innerHTML = svg;
      
      const svgEl = container.querySelector('svg');
      if (svgEl) {
        svgEl.style.maxWidth = '100%';
        svgEl.style.height = 'auto';
        svgEl.style.overflow = 'visible';
        svgEl.classList.add('transition-all', 'duration-300');

        // Make nodes and edges genuinely interactive!
        if (targetElId === 'modal-diagram-render') {
          setupModalInteractiveDiagram(svgEl, idea);
        } else if (targetElId === 'card-back-diagram-render') {
          setupCardBackInteractiveDiagram(svgEl, idea);
        }
      }
      return;
    } catch (err) {
      console.warn("[Mermaid] Render failed, falling back to structured flow:", err);
    }
  }

  container.innerHTML = renderStyledStepFlow(idea);
  if (window.lucide) lucide.createIcons();
}

function setupModalInteractiveDiagram(svgEl, idea) {
  // Query all node elements generated by Mermaid
  const rawNodes = svgEl.querySelectorAll('.node, g[id*="flowchart-"]');
  // Deduplicate and filter out nested labels
  const uniqueNodes = Array.from(rawNodes).filter((n, i, arr) => {
    return !arr.some(parent => parent !== n && parent.contains(n));
  });

  activeDiagramNodes = uniqueNodes;
  currentDiagramStepIndex = -1;
  currentDiagramZoom = 1.0;
  currentPanX = 0;
  currentPanY = 0;
  applyDiagramTransform();

  const stepLabel = document.getElementById("diagram-step-label");
  if (stepLabel) {
    stepLabel.textContent = `Step 1 of ${uniqueNodes.length || 3}`;
  }

  // Attach interactive click and hover to each node
  uniqueNodes.forEach((node, index) => {
    node.setAttribute('role', 'button');
    node.setAttribute('tabindex', '0');
    node.classList.add('cursor-pointer');

    node.addEventListener('click', (e) => {
      e.stopPropagation();
      selectDiagramNode(node, index, uniqueNodes.length, idea);
    });

    node.addEventListener('mouseenter', () => {
      node.style.cursor = 'pointer';
    });
  });

  // Attach drag-to-pan handlers on modal-diagram-container
  const panContainer = document.getElementById("modal-diagram-container");
  if (panContainer && !panContainer.dataset.panSetup) {
    panContainer.dataset.panSetup = "true";

    panContainer.addEventListener('mousedown', (e) => {
      // Don't drag if clicking buttons
      if (e.target.closest('button')) return;
      isPanningDiagram = true;
      panStartX = e.clientX - currentPanX;
      panStartY = e.clientY - currentPanY;
    });

    window.addEventListener('mousemove', (e) => {
      if (!isPanningDiagram) return;
      currentPanX = e.clientX - panStartX;
      currentPanY = e.clientY - panStartY;
      applyDiagramTransform();
    });

    window.addEventListener('mouseup', () => {
      isPanningDiagram = false;
    });

    // Mouse wheel zoom
    panContainer.addEventListener('wheel', (e) => {
      e.preventDefault();
      const delta = e.deltaY < 0 ? 0.08 : -0.08;
      zoomDiagram(delta);
    }, { passive: false });
  }
}

function setupCardBackInteractiveDiagram(svgEl, idea) {
  const nodes = svgEl.querySelectorAll('.node, g[id*="flowchart-"]');
  nodes.forEach((node) => {
    node.classList.add('cursor-pointer');
    node.addEventListener('click', (e) => {
      e.stopPropagation();
      nodes.forEach(n => n.classList.remove('active-step-node'));
      node.classList.add('active-step-node');
      const text = extractNodeText(node);
      const actionEl = document.getElementById("card-back-action");
      if (actionEl && text) {
        actionEl.innerHTML = `<strong class="text-sky-300">Active Node [${text}]:</strong> Observe how this stage governs the overall mental model.`;
      }
    });
  });
}

function applyDiagramTransform() {
  const canvas = document.getElementById("modal-diagram-render");
  if (canvas) {
    canvas.style.transform = `translate(${currentPanX}px, ${currentPanY}px) scale(${currentDiagramZoom})`;
  }
  const badge = document.getElementById("diagram-zoom-badge");
  if (badge) {
    badge.textContent = `${Math.round(currentDiagramZoom * 100)}%`;
  }
}

function zoomDiagram(delta) {
  currentDiagramZoom = Math.max(0.6, Math.min(2.4, currentDiagramZoom + delta));
  applyDiagramTransform();
}

function resetDiagramZoom() {
  currentDiagramZoom = 1.0;
  currentPanX = 0;
  currentPanY = 0;
  applyDiagramTransform();
}

function stepDiagram(delta) {
  if (!activeDiagramNodes || !activeDiagramNodes.length) return;
  const total = activeDiagramNodes.length;
  
  if (currentDiagramStepIndex === -1 && delta > 0) {
    currentDiagramStepIndex = 0;
  } else {
    currentDiagramStepIndex = (currentDiagramStepIndex + delta + total) % total;
  }

  const targetNode = activeDiagramNodes[currentDiagramStepIndex];
  if (targetNode) {
    selectDiagramNode(targetNode, currentDiagramStepIndex, total, currentDeepDiveIdea);
  }
}

function resetDiagramStep() {
  currentDiagramStepIndex = -1;
  activeDiagramNodes.forEach(n => n.classList.remove('active-step-node'));
  const svgEl = document.querySelector('#modal-diagram-render svg');
  if (svgEl) svgEl.classList.remove('focus-mode');
  
  const stepLabel = document.getElementById("diagram-step-label");
  if (stepLabel) {
    stepLabel.textContent = `Step 1 of ${activeDiagramNodes.length || 3}`;
  }
  dismissNodeInspector();
  resetDiagramZoom();
}

function extractNodeText(node) {
  if (!node) return "";
  // Check foreignObject or text element
  const textEl = node.querySelector('.nodeLabel, foreignObject, text') || node;
  return (textEl.textContent || "").replace(/\s+/g, ' ').trim();
}

function selectDiagramNode(node, index, total, idea) {
  currentDiagramStepIndex = index;
  
  // Update visual node classes
  activeDiagramNodes.forEach(n => n.classList.remove('active-step-node'));
  node.classList.add('active-step-node');

  const svgEl = document.querySelector('#modal-diagram-render svg');
  if (svgEl) svgEl.classList.add('focus-mode');

  // Update step pill label
  const stepLabel = document.getElementById("diagram-step-label");
  if (stepLabel) {
    stepLabel.textContent = `Step ${index + 1} of ${total}`;
  }

  // Extract clean node text
  const rawText = extractNodeText(node);
  const cleanTitle = rawText.length > 50 ? rawText.substring(0, 48) + '...' : rawText;

  // Update Live Node Inspector Card
  const titleEl = document.getElementById("inspector-node-title");
  const descEl = document.getElementById("inspector-node-desc");
  const ruleEl = document.getElementById("inspector-rule-text");
  const badgeEl = document.getElementById("inspector-badge");

  if (titleEl) titleEl.textContent = cleanTitle || `Stage ${index + 1}`;
  if (badgeEl) badgeEl.textContent = `Step ${index + 1} / ${total}`;

  // Generate contextual explanation based on position in flow
  let roleDesc = "";
  let ruleText = "";

  const textLower = cleanTitle.toLowerCase();
  if (textLower.includes("problem") || textLower.includes("context") || textLower.includes("standard") || textLower.includes("cue") || index === 0) {
    roleDesc = `Initiating Condition: Captures the raw intuitive default, environmental trigger, or status quo assumptions before applying ${idea ? idea.title : 'the mental model'}.`;
    ruleText = "Notice the cognitive trap or immediate shortcut your brain wants to take here.";
  } else if (textLower.includes("invert") || textLower.includes("principles") || textLower.includes("filter") || textLower.includes("action") || textLower.includes("routine")) {
    roleDesc = `The Transformative Operator: This is where ${idea ? idea.title : 'the model'} actively intervenes. By imposing counter-intuitive constraints, you filter signal from noise and isolate fundamental physics.`;
    ruleText = idea && idea.action_item ? idea.action_item : "Eliminate failure modes and reason upwards from immutable axioms.";
  } else if (textLower.includes("catastrophe") || textLower.includes("residue") || textLower.includes("trap") || textLower.includes("loss")) {
    roleDesc = `Critical Failure Vector: The hidden downside or systemic penalty that un-inverted or distracted thinkers walk into unknowingly.`;
    ruleText = "Pre-mortems and margin-of-safety guardrails neutralize this exact landmine.";
  } else {
    roleDesc = `Compounding Output & Asymmetric Payoff: The sustainable strategic advantage produced when the model runs to completion. Success becomes the natural residue.`;
    ruleText = "Preserves infinite upside while strictly capping downside exposure.";
  }

  if (descEl) descEl.textContent = roleDesc;
  if (ruleEl) ruleEl.textContent = ruleText;

  if (window.lucide) lucide.createIcons();
}

function dismissNodeInspector() {
  const titleEl = document.getElementById("inspector-node-title");
  const descEl = document.getElementById("inspector-node-desc");
  const ruleEl = document.getElementById("inspector-rule-text");
  const badgeEl = document.getElementById("inspector-badge");

  if (titleEl) titleEl.textContent = "Select a node to inspect";
  if (badgeEl) badgeEl.textContent = "Active Node";
  if (descEl) descEl.textContent = "Click on any stage in the flow above to see its role in the mental model, cognitive dynamics, and strategic heuristic.";
  if (ruleEl) ruleEl.textContent = "Interactive mental model simulation ready.";

  activeDiagramNodes.forEach(n => n.classList.remove('active-step-node'));
  const svgEl = document.querySelector('#modal-diagram-render svg');
  if (svgEl) svgEl.classList.remove('focus-mode');
}

function generateClientFallbackDiagram(idea) {
  const title = (idea.title || 'Mental Model').replace(/["']/g, '');
  const t = (idea.topic || '').toLowerCase();
  if (t.includes('prod') || t.includes('habit')) {
    return `graph LR\n  Cue[Context & Trigger] --> Action[${title}: Micro Action]\n  Action --> Reward[Intrinsic Dopamine]\n  Reward -->|Compounding Loop| Habit[Identity Routine]\n  style Cue fill:#312e81,stroke:#818cf8,color:#fff\n  style Action fill:#064e3b,stroke:#34d399,color:#fff\n  style Reward fill:#78350f,stroke:#fbbf24,color:#fff\n  style Habit fill:#0f766e,stroke:#2dd4bf,color:#fff`;
  } else if (t.includes('stoic')) {
    return `graph TD\n  Event[External Reality / Stressor] --> Filter{Dichotomy of Control}\n  Filter -->|Things Outside Control| Detach[Radical Acceptance & Peace]\n  Filter -->|Things Within Control| Action[${title}: Virtuous Action]\n  style Event fill:#881337,stroke:#f43f5e,color:#fff\n  style Filter fill:#78350f,stroke:#f59e0b,color:#fff\n  style Detach fill:#1e1b4b,stroke:#818cf8,color:#fff\n  style Action fill:#064e3b,stroke:#10b981,color:#fff`;
  } else {
    return `graph TD\n  Problem[Conventional Assumption / Bias] --> Deconstruct[${title}: Analytical Filter]\n  Deconstruct --> Principles[Foundational First Principles]\n  Principles --> Output[High-Leverage Asymmetric Solution]\n  style Problem fill:#312e81,stroke:#6366f1,color:#fff\n  style Deconstruct fill:#78350f,stroke:#f59e0b,color:#fff\n  style Principles fill:#881337,stroke:#f43f5e,color:#fff\n  style Output fill:#064e3b,stroke:#10b981,color:#fff`;
  }
}

function renderStyledStepFlow(idea) {
  const title = idea.title || 'Mental Model';
  const hook = idea.one_liner || 'Core Challenge';
  const action = idea.action_item || 'Execute asymmetric high-leverage action.';
  const example = idea.example || 'Applied across high-stakes domains to minimize systematic failure.';

  return `
    <div class="w-full flex flex-col space-y-3 py-1 text-xs">
      <!-- Step 1: Trigger / Problem -->
      <div class="p-3.5 rounded-2xl bg-indigo-950/40 border border-indigo-500/30 flex items-start space-x-3 transition hover:border-indigo-400">
        <div class="w-7 h-7 rounded-xl bg-indigo-500/20 text-indigo-300 border border-indigo-500/40 flex items-center justify-center font-bold text-xs shrink-0 mt-0.5">
          1
        </div>
        <div class="flex-1">
          <div class="flex items-center justify-between mb-1">
            <span class="text-[10px] text-indigo-400 font-bold uppercase tracking-wider">Trigger / Problem State</span>
            <span class="text-[10px] text-slate-500">Context</span>
          </div>
          <p class="text-xs sm:text-sm font-semibold text-slate-100">${hook}</p>
        </div>
      </div>

      <!-- Arrow Down Connector -->
      <div class="flex items-center justify-center text-slate-600 -my-1">
        <i data-lucide="arrow-down" class="w-4 h-4 text-slate-500"></i>
      </div>

      <!-- Step 2: Mental Model Filter -->
      <div class="p-3.5 rounded-2xl bg-emerald-950/40 border border-emerald-500/30 flex items-start space-x-3 transition hover:border-emerald-400">
        <div class="w-7 h-7 rounded-xl bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 flex items-center justify-center font-bold text-xs shrink-0 mt-0.5">
          2
        </div>
        <div class="flex-1">
          <div class="flex items-center justify-between mb-1">
            <span class="text-[10px] text-emerald-400 font-bold uppercase tracking-wider">Mental Model / First Principles</span>
            <span class="text-[10px] text-emerald-500/80 font-mono">Algorithm</span>
          </div>
          <p class="text-xs sm:text-sm font-bold text-white">${title}</p>
          <p class="text-xs text-slate-300 mt-1 leading-relaxed">${idea.summary || ''}</p>
        </div>
      </div>

      <!-- Arrow Down Connector -->
      <div class="flex items-center justify-center text-slate-600 -my-1">
        <i data-lucide="arrow-down" class="w-4 h-4 text-slate-500"></i>
      </div>

      <!-- Step 3: High-Leverage Payoff -->
      <div class="p-3.5 rounded-2xl bg-purple-950/40 border border-purple-500/30 flex items-start space-x-3 transition hover:border-purple-400">
        <div class="w-7 h-7 rounded-xl bg-purple-500/20 text-purple-300 border border-purple-500/40 flex items-center justify-center font-bold text-xs shrink-0 mt-0.5">
          3
        </div>
        <div class="flex-1">
          <div class="flex items-center justify-between mb-1">
            <span class="text-[10px] text-purple-400 font-bold uppercase tracking-wider">Practical Payoff & Asymmetric Execution</span>
            <span class="text-[10px] text-purple-400 font-mono">Impact</span>
          </div>
          <p class="text-xs sm:text-sm font-semibold text-slate-100">${action}</p>
          <div class="mt-2 pt-2 border-t border-purple-500/20 text-[11px] text-purple-200/80">
            <span class="font-bold text-purple-300">Case Example:</span> ${example}
          </div>
        </div>
      </div>
    </div>
  `;
}

function setDiagramViewMode(mode) {
  window.state.diagramViewMode = mode;
  try {
    localStorage.setItem('microstash_diagram_mode', mode);
  } catch (e) {}

  const canvasBtn = document.getElementById('view-mode-canvas-btn');
  const flowBtn = document.getElementById('view-mode-flow-btn');
  const stepperToolbar = document.getElementById('diagram-stepper-toolbar');

  if (mode === 'flow') {
    if (canvasBtn) {
      canvasBtn.classList.remove('bg-indigo-600', 'text-white', 'shadow');
      canvasBtn.classList.add('text-slate-400');
    }
    if (flowBtn) {
      flowBtn.classList.add('bg-indigo-600', 'text-white', 'shadow');
      flowBtn.classList.remove('text-slate-400');
    }
    if (stepperToolbar) stepperToolbar.classList.add('opacity-40', 'pointer-events-none');
  } else {
    if (canvasBtn) {
      canvasBtn.classList.add('bg-indigo-600', 'text-white', 'shadow');
      canvasBtn.classList.remove('text-slate-400');
    }
    if (flowBtn) {
      flowBtn.classList.remove('bg-indigo-600', 'text-white', 'shadow');
      flowBtn.classList.add('text-slate-400');
    }
    if (stepperToolbar) stepperToolbar.classList.remove('opacity-40', 'pointer-events-none');
  }

  if (currentDeepDiveIdea) {
    renderIdeaVisualDiagram(currentDeepDiveIdea, 'modal-diagram-render');
  }
}

// --- Swipe Card Display ---
function updateSwipeCardDisplay() {
  const ideas = window.state.ideas;
  if (!ideas.length) {
    document.getElementById("card-title").textContent = "All caught up!";
    document.getElementById("card-one-liner").textContent = "You've absorbed all microlearning cards in this filter.";
    document.getElementById("card-summary").textContent = "Switch topics or use the AI Stashifier to generate more bite-sized wisdom from any book or article!";
    document.getElementById("deck-progress").textContent = "(0 of 0)";
    return;
  }

  const idx = window.state.currentIdeaIndex;
  const idea = ideas[idx];
  if (!idea) return;

  const progressEl = document.getElementById("deck-progress");
  if (progressEl) progressEl.textContent = `(${idx + 1} of ${ideas.length})`;

  // Front face elements & Dynamic Topic Theming
  const topicEl = document.getElementById("card-topic");
  if (topicEl) {
    topicEl.textContent = idea.topic;
    topicEl.className = `px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${getTopicBadgeClass(idea.topic)}`;
  }

  // Dynamic ambient glow
  const glowEl = document.getElementById("card-glow");
  if (glowEl) {
    glowEl.style.background = `radial-gradient(circle, ${getTopicGlowColor(idea.topic)} 0%, rgba(0,0,0,0) 70%)`;
  }

  document.getElementById("card-read-time").textContent = `${idea.read_time_mins || 1} min read`;
  document.getElementById("card-title").textContent = idea.title;
  document.getElementById("card-one-liner").textContent = idea.one_liner;
  document.getElementById("card-summary").textContent = idea.summary;
  document.getElementById("card-author").textContent = idea.author;
  document.getElementById("card-source").textContent = idea.source;
  document.getElementById("card-likes-val").textContent = idea.likes;

  // Like button visual
  const likeBtn = document.getElementById("icon-like");
  if (likeBtn) {
    likeBtn.classList.toggle("text-rose-500", !!idea.is_liked);
    likeBtn.classList.toggle("fill-rose-500", !!idea.is_liked);
  }

  // Save button visual
  const saveBtn = document.getElementById("icon-save");
  if (saveBtn) {
    saveBtn.classList.toggle("fill-white", !!idea.is_saved);
  }

  // Back face elements (Detailed / Flip)
  document.getElementById("card-back-quote").textContent = idea.quote ? `“${idea.quote.replace(/^["“”]|["“”]$/g, '')}”` : `“${idea.one_liner}”`;
  document.getElementById("card-back-action").textContent = idea.action_item || "Reflect on this mental model and observe how it applies in your decisions today.";

  const exampleEl = document.getElementById("card-back-example");
  if (exampleEl) {
    exampleEl.textContent = idea.example || idea.detailed_explanation || "Focus first on identifying and removing major failure vectors and inefficiencies.";
  }

  const tagsContainer = document.getElementById("card-back-tags");
  if (tagsContainer) {
    tagsContainer.innerHTML = (idea.tags || []).map(t => `
      <span class="px-2.5 py-1 rounded-md bg-slate-800 text-xs text-slate-300 border border-slate-700">${t}</span>
    `).join('');
  }

  // Render Visual Architecture Diagram on Card Back
  renderIdeaVisualDiagram(idea, 'card-back-diagram-render');

  if (window.lucide) lucide.createIcons();
}

function advanceCard() {
  if (!window.state.ideas.length) return;
  window.state.currentIdeaIndex = (window.state.currentIdeaIndex + 1) % window.state.ideas.length;
  updateSwipeCardDisplay();
}

async function recordCurrentIdeaRead() {
  const idea = window.state.ideas[window.state.currentIdeaIndex];
  if (!idea) return;
  try {
    await fetch(`/api/ideas/${idea.id}/read`, { method: 'POST' });
    loadStats();
  } catch (err) {
    console.error("Failed to record read:", err);
  }
}

async function toggleLikeCurrentCard() {
  const idea = window.state.ideas[window.state.currentIdeaIndex];
  if (!idea) return;
  try {
    const res = await fetch(`/api/ideas/${idea.id}/like`, { method: 'POST' });
    const updated = await res.json();
    idea.likes = updated.likes;
    idea.is_liked = updated.is_liked;
    updateSwipeCardDisplay();
  } catch (err) {
    console.error("Failed to like:", err);
  }
}

async function toggleSaveCurrentCard(silent = false) {
  const idea = window.state.ideas[window.state.currentIdeaIndex];
  if (!idea) return;
  if (!silent) {
    openStashModal(idea.id);
  } else {
    try {
      const res = await fetch(`/api/ideas/${idea.id}/save`, { method: 'POST' });
      const updated = await res.json();
      idea.is_saved = updated.is_saved;
      idea.saved_count = updated.saved_count;
      updateSwipeCardDisplay();
      loadStats();
    } catch (err) {
      console.error("Failed to save:", err);
    }
  }
}

// --- Feed Tab ---
function filterByTopic(topic) {
  window.state.selectedTopic = topic;
  
  document.querySelectorAll(".topic-pill").forEach(pill => {
    if (pill.textContent.trim().toLowerCase() === topic.toLowerCase()) {
      pill.classList.add("bg-indigo-600", "text-white");
      pill.classList.remove("bg-slate-800", "text-slate-300");
    } else {
      pill.classList.remove("bg-indigo-600", "text-white");
      pill.classList.add("bg-slate-800", "text-slate-300");
    }
  });

  loadIdeas();
}

function debounceFeedSearch() {
  clearTimeout(searchDebounceTimeout);
  searchDebounceTimeout = setTimeout(() => {
    const input = document.getElementById("feed-search-input");
    window.state.searchQuery = input ? input.value.trim() : '';
    loadIdeas();
  }, 250);
}

function renderFeedGrid() {
  const container = document.getElementById("feed-grid");
  if (!container) return;

  const ideas = window.state.ideas;
  if (!ideas.length) {
    container.innerHTML = `
      <div class="col-span-full py-16 text-center text-slate-500">
        <i data-lucide="inbox" class="w-12 h-12 mx-auto mb-3 opacity-40"></i>
        <p class="text-base font-semibold">No microlearning cards match your search</p>
        <p class="text-xs text-slate-500 mt-1">Try another keyword or generate new cards with the AI Stashifier</p>
      </div>
    `;
    if (window.lucide) lucide.createIcons();
    return;
  }

  container.innerHTML = ideas.map((idea, index) => {
    const hasDeepDive = idea.detailed_explanation && idea.detailed_explanation.trim().length >= 100;
    return `
    <div class="group glass-card border border-slate-800/80 ${getTopicBorderClass(idea.topic)} hover:border-indigo-500/50 rounded-3xl p-6 flex flex-col justify-between shadow-lg transition-all duration-300 hover:-translate-y-1.5 hover:shadow-2xl">
      <div>
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center space-x-2">
            <span class="px-2.5 py-0.5 rounded-full text-[11px] font-bold uppercase tracking-wider ${getTopicBadgeClass(idea.topic)}">
              ${idea.topic}
            </span>
            ${hasDeepDive ? `
              <span class="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full bg-purple-500/15 text-purple-300 border border-purple-500/25 text-[10px] font-semibold" title="Includes authentic in-depth theoretical breakdown and case study">
                <i data-lucide="sparkles" class="w-2.5 h-2.5"></i>
                <span>Deep Dive</span>
              </span>
            ` : ''}
          </div>
          <span class="text-xs text-slate-400 flex items-center space-x-1">
            <i data-lucide="clock" class="w-3 h-3"></i>
            <span>${idea.read_time_mins || 1}m</span>
          </span>
        </div>

        <h3 class="text-lg font-bold text-white mb-1.5 leading-snug group-hover:text-indigo-300 transition">
          ${idea.title}
        </h3>
        
        <p class="text-xs text-indigo-300/80 font-medium mb-3">
          ${idea.one_liner}
        </p>

        <p class="text-xs text-slate-300 leading-relaxed line-clamp-4 mb-4">
          ${idea.summary}
        </p>
      </div>

      <div class="pt-4 border-t border-slate-800 flex items-center justify-between">
        <div class="text-[11px]">
          <span class="font-semibold text-slate-200 block truncate max-w-[120px]">${idea.author}</span>
          <span class="text-slate-500 block truncate max-w-[120px]">${idea.source}</span>
        </div>

        <div class="flex items-center space-x-1">
          <button onclick="openStressTestModal('${idea.id}')" class="px-2.5 py-1.5 rounded-xl bg-amber-500/10 hover:bg-amber-600 text-amber-300 hover:text-white border border-amber-500/20 text-xs font-semibold flex items-center space-x-1 transition shadow-sm" title="Socratic Dilemma Stress-Test">
            <i data-lucide="zap" class="w-3.5 h-3.5 text-amber-400"></i>
            <span class="hidden sm:inline">Stress Test</span>
          </button>
          <button onclick="openDeepDiveModal('${idea.id}')" class="px-2.5 py-1.5 rounded-xl bg-indigo-500/10 hover:bg-indigo-600 text-indigo-300 hover:text-white border border-indigo-500/20 text-xs font-semibold flex items-center space-x-1 transition shadow-sm" title="Detailed explanation and example">
            <i data-lucide="book-open" class="w-3.5 h-3.5"></i>
            <span>Detailed</span>
          </button>
          <button onclick="playIdeaAudioById('${idea.id}')" class="p-2 rounded-xl text-slate-400 hover:text-sky-400 hover:bg-slate-800 transition" title="Listen">
            <i data-lucide="volume-2" class="w-4 h-4"></i>
          </button>
          <button onclick="openStashModal('${idea.id}')" class="p-2 rounded-xl text-slate-400 hover:text-indigo-400 hover:bg-slate-800 transition" title="Save to Stash">
            <i data-lucide="bookmark" class="w-4 h-4 ${idea.is_saved ? 'fill-indigo-400 text-indigo-400' : ''}"></i>
          </button>
          <button onclick="jumpToSwipeCard(${index})" class="px-2.5 py-1.5 rounded-xl bg-slate-800 hover:bg-indigo-600 text-slate-300 hover:text-white text-xs font-semibold flex items-center space-x-1 transition" title="Open in Swipe Deck">
            <span>Swipe</span>
            <i data-lucide="chevron-right" class="w-3.5 h-3.5"></i>
          </button>
        </div>
      </div>
    </div>
    `;
  }).join('');

  if (window.lucide) lucide.createIcons();
}

function jumpToSwipeCard(index) {
  window.state.currentIdeaIndex = index;
  updateSwipeCardDisplay();
  switchTab('swipe');
}

async function playIdeaAudioById(id) {
  let idea = (window.state.ideas || []).find(i => String(i.id) === String(id));
  if (!idea && lastExtractedIdeas.length) {
    idea = lastExtractedIdeas.find(i => String(i.id) === String(id));
  }
  if (!idea) {
    try {
      const res = await fetch(`/api/ideas/${id}`);
      if (res.ok) idea = await res.json();
    } catch (e) {
      console.warn("Could not fetch idea for audio:", e);
    }
  }

  if (idea && typeof startAudioForIdea === 'function') {
    startAudioForIdea(idea);
  }
}

// --- Stashes Tab ---
function renderStashesGrid() {
  const container = document.getElementById("stashes-grid");
  if (!container) return;

  const stashes = window.state.stashes;
  if (!stashes.length) {
    container.innerHTML = `<div class="col-span-full py-12 text-center text-slate-500">No stashes created yet.</div>`;
    return;
  }

  container.innerHTML = stashes.map(stash => `
    <div onclick="viewStashDetail('${stash.id}')" class="cursor-pointer group bg-slate-900 border border-slate-800 hover:border-indigo-500/60 rounded-3xl p-6 shadow-xl transition-all duration-200 hover:-translate-y-1">
      <div class="flex items-center justify-between mb-4">
        <div class="w-12 h-12 rounded-2xl bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 flex items-center justify-center text-lg">
          <i data-lucide="${stash.icon || 'sparkles'}" class="w-6 h-6"></i>
        </div>
        <span class="px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-800 text-slate-400 border border-slate-700">
          ${stash.ideas_count} ideas
        </span>
      </div>

      <h3 class="text-xl font-bold text-white mb-2 group-hover:text-indigo-300 transition">
        ${stash.title}
      </h3>
      <p class="text-xs text-slate-400 line-clamp-2 leading-relaxed">
        ${stash.description}
      </p>

      <div class="mt-6 pt-4 border-t border-slate-800 flex items-center justify-between text-xs text-indigo-400 font-semibold">
        <span>Open Collection</span>
        <i data-lucide="arrow-right" class="w-4 h-4 transition-transform group-hover:translate-x-1"></i>
      </div>
    </div>
  `).join('');

  if (window.lucide) lucide.createIcons();
}

async function viewStashDetail(stashId) {
  try {
    const res = await fetch(`/api/stashes/${stashId}`);
    const stash = await res.json();

    document.getElementById("stashes-grid").classList.add("hidden");
    const detailView = document.getElementById("stash-detail-view");
    const detailContent = document.getElementById("stash-detail-content");
    detailView.classList.remove("hidden");

    detailContent.innerHTML = `
      <div class="bg-slate-900 p-6 rounded-3xl border border-slate-800 mb-6">
        <div class="flex items-center space-x-3 mb-2">
          <div class="w-10 h-10 rounded-2xl bg-indigo-500/20 text-indigo-400 flex items-center justify-center">
            <i data-lucide="${stash.icon || 'bookmark'}" class="w-5 h-5"></i>
          </div>
          <div>
            <h2 class="text-2xl font-bold text-white">${stash.title}</h2>
            <p class="text-xs text-slate-400">${stash.ideas_count} curated atomic ideas</p>
          </div>
        </div>
        <p class="text-sm text-slate-300 mt-2">${stash.description}</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        ${(stash.ideas || []).map(idea => `
          <div class="bg-slate-900 border border-slate-800 rounded-3xl p-6 flex flex-col justify-between">
            <div>
              <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                ${idea.topic}
              </span>
              <h4 class="text-base font-bold text-white mt-2">${idea.title}</h4>
              <p class="text-xs text-indigo-300/80 font-medium mb-2">${idea.one_liner}</p>
              <p class="text-xs text-slate-300 leading-relaxed mb-4">${idea.summary}</p>
            </div>
            <div class="pt-3 border-t border-slate-800 flex items-center justify-between text-xs">
              <span class="text-slate-400 font-medium truncate max-w-[120px]">${idea.author}</span>
              <div class="flex items-center space-x-1.5">
                <button onclick="openDeepDiveModal('${idea.id}')" class="px-2.5 py-1 rounded-lg bg-indigo-500/10 hover:bg-indigo-600 text-indigo-300 hover:text-white text-xs font-semibold flex items-center space-x-1 transition" title="Detailed explanation and example">
                  <i data-lucide="book-open" class="w-3 h-3"></i>
                  <span>Detailed</span>
                </button>
                <button onclick="playIdeaAudioById('${idea.id}')" class="p-1.5 rounded-lg text-slate-400 hover:text-sky-400 hover:bg-slate-800 transition" title="Listen">
                  <i data-lucide="volume-2" class="w-3.5 h-3.5"></i>
                </button>
                <button onclick="removeIdeaFromStash('${stash.id}', '${idea.id}')" class="text-rose-400 hover:text-rose-300 text-xs p-1">Remove</button>
              </div>
            </div>
          </div>
        `).join('')}
      </div>
    `;

    if (window.lucide) lucide.createIcons();
  } catch (err) {
    console.error("Failed to load stash detail:", err);
  }
}

function closeStashDetail() {
  document.getElementById("stash-detail-view").classList.add("hidden");
  document.getElementById("stashes-grid").classList.remove("hidden");
}

async function removeIdeaFromStash(stashId, ideaId) {
  try {
    await fetch(`/api/stashes/${stashId}/ideas/${ideaId}`, { method: 'DELETE' });
    viewStashDetail(stashId);
    loadStashes();
  } catch (err) {
    console.error("Failed to remove idea:", err);
  }
}

// --- Stash Picker Modal ---
function openStashModal(ideaId) {
  targetIdeaForStash = ideaId;
  const modal = document.getElementById("stash-modal");
  const list = document.getElementById("stash-picker-list");
  if (!modal || !list) return;

  const stashes = window.state.stashes;
  list.innerHTML = stashes.map(stash => `
    <button onclick="saveIdeaToSpecificStash('${stash.id}')" class="w-full p-3 rounded-2xl bg-slate-800 hover:bg-slate-700/80 border border-slate-700 text-left flex items-center justify-between transition">
      <div class="flex items-center space-x-3">
        <div class="w-8 h-8 rounded-xl bg-indigo-500/20 text-indigo-400 flex items-center justify-center">
          <i data-lucide="${stash.icon || 'bookmark'}" class="w-4 h-4"></i>
        </div>
        <div>
          <span class="text-sm font-semibold text-white block">${stash.title}</span>
          <span class="text-[11px] text-slate-400 block">${stash.ideas_count} ideas</span>
        </div>
      </div>
      <i data-lucide="plus" class="w-4 h-4 text-slate-400"></i>
    </button>
  `).join('');

  modal.classList.remove("hidden");
  if (window.lucide) lucide.createIcons();
}

function closeStashModal() {
  const modal = document.getElementById("stash-modal");
  if (modal) modal.classList.add("hidden");
}

async function saveIdeaToSpecificStash(stashId) {
  if (!targetIdeaForStash) return;
  try {
    await fetch(`/api/stashes/${stashId}/ideas`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ idea_id: targetIdeaForStash })
    });
    closeStashModal();
    alert("Saved to stash!");
    loadStashes();
    loadIdeas();
  } catch (err) {
    console.error("Failed to add to stash:", err);
  }
}

// --- Create New Stash Modal ---
function openCreateStashModal() {
  document.getElementById("create-stash-modal").classList.remove("hidden");
}

function closeCreateStashModal() {
  document.getElementById("create-stash-modal").classList.add("hidden");
}

async function submitNewStash() {
  const title = document.getElementById("new-stash-title").value.trim();
  const desc = document.getElementById("new-stash-desc").value.trim();
  const color = document.querySelector('input[name="stash-color"]:checked')?.value || 'indigo';

  if (!title) {
    alert("Please enter a title for your stash.");
    return;
  }

  try {
    await fetch('/api/stashes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: title,
        description: desc || "Personal collection of microlearning nuggets.",
        icon: "bookmark",
        color: color
      })
    });
    closeCreateStashModal();
    loadStashes();
  } catch (err) {
    console.error("Failed to create stash:", err);
  }
}

function formatMarkdownInline(str) {
  if (!str) return "";
  // Bold **text**
  let res = str.replace(/\*\*(.*?)\*\*/g, '<strong class="text-white font-semibold">$1</strong>');
  // Italic *text*
  res = res.replace(/(?<!\*)\*(?!\*)(.*?)(?<!\*)\*(?!\*)/g, '<em class="text-indigo-200/90 font-medium">$1</em>');
  // Code `code`
  res = res.replace(/`([^`]+)`/g, '<code class="px-1.5 py-0.5 rounded bg-slate-800 text-indigo-300 font-mono text-[11px]">$1</code>');
  return res;
}

function renderMarkdownDetailed(text) {
  if (!text) return "";
  const lines = text.split("\n");
  let html = "";
  let inParagraph = false;

  for (let line of lines) {
    const trimmed = line.trim();
    if (!trimmed) {
      if (inParagraph) {
        html += "</p>";
        inParagraph = false;
      }
      continue;
    }

    if (trimmed.startsWith("### ") || trimmed.startsWith("## ")) {
      if (inParagraph) {
        html += "</p>";
        inParagraph = false;
      }
      const title = trimmed.replace(/^#+\s*/, "");
      html += `<div class="deep-dive-section-heading">
        <span class="deep-dive-bullet-dot"></span>
        <span>${formatMarkdownInline(title)}</span>
      </div>`;
    } else if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
      if (inParagraph) {
        html += "</p>";
        inParagraph = false;
      }
      html += `<div class="deep-dive-bullet-item">
        <span class="deep-dive-bullet-dot"></span>
        <span>${formatMarkdownInline(trimmed.substring(2))}</span>
      </div>`;
    } else if (trimmed.startsWith("> ")) {
      if (inParagraph) {
        html += "</p>";
        inParagraph = false;
      }
      html += `<blockquote class="border-l-3 border-indigo-500/70 bg-slate-950/40 rounded-r-xl pl-3.5 py-2 my-2 text-xs sm:text-sm text-slate-300 italic font-serif">
        ${formatMarkdownInline(trimmed.substring(2))}
      </blockquote>`;
    } else {
      if (!inParagraph) {
        html += `<p class="text-xs sm:text-sm text-slate-200 leading-relaxed my-2">`;
        inParagraph = true;
      } else {
        html += " ";
      }
      html += formatMarkdownInline(trimmed);
    }
  }
  if (inParagraph) html += "</p>";
  return html;
}

// --- Deep Dive / Detailed Concept Modal ---
async function openDeepDiveModal(ideaId = null) {
  let idea = null;
  if (ideaId !== null && ideaId !== undefined) {
    idea = (window.state.ideas || []).find(i => String(i.id) === String(ideaId));
    if (!idea && lastExtractedIdeas && lastExtractedIdeas.length) {
      if (typeof ideaId === 'number' || (!isNaN(Number(ideaId)) && Number(ideaId) < lastExtractedIdeas.length)) {
        idea = lastExtractedIdeas[Number(ideaId)];
      } else {
        idea = lastExtractedIdeas.find(i => String(i.id) === String(ideaId));
      }
    }
    if (!idea) {
      try {
        const res = await fetch(`/api/ideas/${ideaId}`);
        if (res.ok) idea = await res.json();
      } catch (e) {
        console.warn("Could not fetch idea detail:", e);
      }
    }
  }

  if (!idea) {
    idea = (window.state.ideas || [])[window.state.currentIdeaIndex];
  }

  if (!idea) return;
  currentDeepDiveIdea = idea;

  const modal = document.getElementById("deep-dive-modal");
  if (!modal) return;
  modal.dataset.ideaId = idea.id || '';

  const topicEl = document.getElementById("modal-topic");
  if (topicEl) {
    topicEl.textContent = idea.topic || "Mental Model";
    topicEl.className = `px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${getTopicBadgeClass(idea.topic)}`;
  }

  const authorEl = document.getElementById("modal-author");
  if (authorEl) authorEl.textContent = idea.author || "Curated Thinker";

  const sourceEl = document.getElementById("modal-source");
  if (sourceEl) sourceEl.textContent = idea.source || "Insight";

  const titleEl = document.getElementById("modal-title");
  if (titleEl) titleEl.textContent = idea.title;

  const oneLinerEl = document.getElementById("modal-one-liner");
  if (oneLinerEl) oneLinerEl.textContent = idea.one_liner;

  // Section 1: The Core Mental Model (Bite-sized microlearning summary)
  const summaryEl = document.getElementById("modal-summary");
  if (summaryEl) summaryEl.textContent = idea.summary;

  // Section: Visual Architecture Diagram Flow
  renderIdeaVisualDiagram(idea, 'modal-diagram-render');

  // Section 2: In-Depth Explanation & Theoretical Mechanics
  const detailedEl = document.getElementById("modal-detailed");
  const exampleEl = document.getElementById("modal-example");

  const hasGenuineDeepDive = idea.detailed_explanation && 
                             idea.detailed_explanation.trim().length >= 120 && 
                             idea.detailed_explanation.trim() !== idea.summary.trim();

  if (hasGenuineDeepDive) {
    if (detailedEl) detailedEl.innerHTML = renderMarkdownDetailed(idea.detailed_explanation);
    if (exampleEl) exampleEl.textContent = idea.example || "Historical and operational practitioners apply this model to reduce systematic failure modes.";
  } else {
    // Show active synthesis skeleton
    if (detailedEl) {
      detailedEl.innerHTML = `
        <div class="space-y-3 py-2 animate-pulse" id="deep-dive-loader">
          <div class="flex items-center space-x-2 text-indigo-400 font-semibold text-xs">
            <span class="animate-spin text-base">⚙️</span>
            <span>Synthesizing authentic in-depth theoretical mechanics & first principles...</span>
          </div>
          <div class="h-3 bg-slate-800 rounded w-full"></div>
          <div class="h-3 bg-slate-800 rounded w-5/6"></div>
          <div class="h-3 bg-slate-800 rounded w-4/6"></div>
        </div>
      `;
    }
    if (exampleEl) {
      exampleEl.innerHTML = `<span class="text-amber-300/70 text-xs italic">Retrieving verified case study...</span>`;
    }

    // Trigger on-demand synthesis from backend
    if (idea.id) {
      fetch(`/api/ideas/${idea.id}/deep-dive`, { method: 'POST' })
        .then(res => res.json())
        .then(updated => {
          if (updated && updated.detailed_explanation && updated.detailed_explanation.trim() !== idea.summary.trim()) {
            idea.detailed_explanation = updated.detailed_explanation;
            idea.example = updated.example || idea.example;
            
            // Update in window.state.ideas cache
            const cachedItem = (window.state.ideas || []).find(i => String(i.id) === String(idea.id));
            if (cachedItem) {
              cachedItem.detailed_explanation = updated.detailed_explanation;
              cachedItem.example = updated.example;
            }

            if (currentDeepDiveIdea && currentDeepDiveIdea.id === idea.id) {
              if (detailedEl) detailedEl.innerHTML = renderMarkdownDetailed(updated.detailed_explanation);
              if (exampleEl) exampleEl.textContent = updated.example || "Case study synthesized.";
              if (updated.visual_diagram) {
                idea.visual_diagram = updated.visual_diagram;
                renderIdeaVisualDiagram(updated, 'modal-diagram-render');
              }
              if (window.lucide) lucide.createIcons();
            }
          }
        })
        .catch(err => {
          console.warn("[Deep Dive] Auto-synthesis error:", err);
          if (detailedEl) {
            detailedEl.innerHTML = `
              <div class="text-xs text-slate-300 space-y-2">
                <p><strong>First Principles Breakdown:</strong> ${idea.title} addresses the fundamental divergence between short-term intuition and systemic reality.</p>
                <p><strong>System Dynamics:</strong> Human psychology defaults to immediate feedback loops. This mental model establishes counter-intuitive guardrails to preserve long-term asymmetric advantage.</p>
              </div>
            `;
          }
        });
    }
  }

  const actionEl = document.getElementById("modal-action");
  if (actionEl) {
    actionEl.textContent = idea.action_item || "Apply this principle to one critical decision today.";
  }

  const quoteEl = document.getElementById("modal-quote");
  const quoteContainer = document.getElementById("modal-quote-container");
  if (quoteEl && quoteContainer) {
    if (idea.quote) {
      quoteEl.textContent = `“${idea.quote.replace(/^["“”]|["“”]$/g, '')}”`;
      quoteContainer.classList.remove("hidden");
    } else {
      quoteContainer.classList.add("hidden");
    }
  }

  const tagsEl = document.getElementById("modal-tags");
  if (tagsEl) {
    tagsEl.innerHTML = (idea.tags || []).map(t => `
      <span class="px-2.5 py-1 rounded-lg bg-slate-800 text-xs font-medium text-slate-300 border border-slate-700/80">#${t}</span>
    `).join('');
  }

  modal.classList.remove("hidden");
  if (window.lucide) lucide.createIcons();
}

async function regenerateCurrentDeepDive() {
  if (!currentDeepDiveIdea || !currentDeepDiveIdea.id) return;
  const idea = currentDeepDiveIdea;

  const btn = document.getElementById("modal-btn-regenerate");
  const detailedEl = document.getElementById("modal-detailed");
  const exampleEl = document.getElementById("modal-example");

  if (btn) {
    btn.disabled = true;
    btn.innerHTML = `<span class="animate-spin mr-1">⚙️</span><span>Deepening...</span>`;
  }

  if (detailedEl) {
    detailedEl.innerHTML = `
      <div class="space-y-3 py-2 animate-pulse">
        <div class="flex items-center space-x-2 text-purple-400 font-semibold text-xs">
          <span class="animate-spin text-base">⚙️</span>
          <span>Synthesizing deeper theoretical mechanics & nuanced boundary conditions...</span>
        </div>
        <div class="h-3 bg-slate-800 rounded w-full"></div>
        <div class="h-3 bg-slate-800 rounded w-5/6"></div>
      </div>
    `;
  }

  try {
    const res = await fetch(`/api/ideas/${idea.id}/deep-dive?force=true`, { method: 'POST' });
    const updated = await res.json();
    if (updated && updated.detailed_explanation) {
      idea.detailed_explanation = updated.detailed_explanation;
      idea.example = updated.example || idea.example;

      const cachedItem = (window.state.ideas || []).find(i => String(i.id) === String(idea.id));
      if (cachedItem) {
        cachedItem.detailed_explanation = updated.detailed_explanation;
        cachedItem.example = updated.example;
      }

      if (detailedEl) detailedEl.innerHTML = renderMarkdownDetailed(updated.detailed_explanation);
      if (exampleEl) exampleEl.textContent = updated.example || "Case study refreshed.";
      if (updated.visual_diagram) {
        idea.visual_diagram = updated.visual_diagram;
        renderIdeaVisualDiagram(updated, 'modal-diagram-render');
      }
    }
  } catch (err) {
    console.error("Failed to deepen:", err);
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = `<i data-lucide="sparkles" class="w-3.5 h-3.5"></i><span>Deepen</span>`;
    }
    if (window.lucide) lucide.createIcons();
  }
}

function closeDeepDiveModal() {
  const modal = document.getElementById("deep-dive-modal");
  if (modal) modal.classList.add("hidden");
}

function copyCurrentDeepDive() {
  if (!currentDeepDiveIdea) return;
  const idea = currentDeepDiveIdea;
  const text = `📖 ${idea.title.toUpperCase()}\n${idea.one_liner}\n\n💡 SUMMARY:\n${idea.summary}\n\n🔬 DEEP DIVE:\n${idea.detailed_explanation || ''}\n\n🏆 REAL-WORLD EXAMPLE:\n${idea.example || ''}\n\n⚡ ACTION STEP:\n${idea.action_item || ''}\n\n— ${idea.author} (${idea.source})\nCurated on Microstash`;

  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).then(() => {
      alert("Detailed concept copied to clipboard!");
    }).catch(() => {
      prompt("Copy detailed concept:", text);
    });
  } else {
    prompt("Copy detailed concept:", text);
  }
}

function modalSaveToStash() {
  if (currentDeepDiveIdea && currentDeepDiveIdea.id) {
    openStashModal(currentDeepDiveIdea.id);
  } else {
    alert("Please save this card to your feed first to add it to a stash.");
  }
}

function modalShareCard() {
  if (currentDeepDiveIdea && typeof openShareStudioModal === 'function') {
    openShareStudioModal(currentDeepDiveIdea);
  }
}

// --- AI Stashifier Mode & Auto-Fetch ---
function setAIMode(mode) {
  const autofetchSec = document.getElementById("ai-section-autofetch");
  const manualSec = document.getElementById("ai-section-manual");
  const btnAuto = document.getElementById("ai-mode-btn-autofetch");
  const btnManual = document.getElementById("ai-mode-btn-manual");

  if (mode === 'autofetch') {
    if (autofetchSec) autofetchSec.classList.remove("hidden");
    if (manualSec) manualSec.classList.add("hidden");
    if (btnAuto) {
      btnAuto.classList.add("bg-indigo-600", "text-white", "shadow");
      btnAuto.classList.remove("text-slate-400", "hover:bg-slate-800");
    }
    if (btnManual) {
      btnManual.classList.remove("bg-indigo-600", "text-white", "shadow");
      btnManual.classList.add("text-slate-400", "hover:bg-slate-800");
    }
  } else {
    if (autofetchSec) autofetchSec.classList.add("hidden");
    if (manualSec) manualSec.classList.remove("hidden");
    if (btnManual) {
      btnManual.classList.add("bg-indigo-600", "text-white", "shadow");
      btnManual.classList.remove("text-slate-400", "hover:bg-slate-800");
    }
    if (btnAuto) {
      btnAuto.classList.remove("bg-indigo-600", "text-white", "shadow");
      btnAuto.classList.add("text-slate-400", "hover:bg-slate-800");
    }
  }
}

function setQueryAndFetch(query) {
  const input = document.getElementById("autofetch-query");
  if (input) input.value = query;
  runAutoFetchAndGenerate();
}

async function runAutoFetchAndGenerate() {
  const input = document.getElementById("autofetch-query");
  const query = input ? input.value.trim() : "";
  if (!query) {
    alert("Please enter a book name, author, or idea/concept.");
    return;
  }

  const topic = document.getElementById("autofetch-topic")?.value || "Mental Models";
  const count = parseInt(document.getElementById("autofetch-count")?.value || "3", 10);
  const provider = document.querySelector('input[name="autofetch-engine"]:checked')?.value || 'gemini';

  const btn = document.getElementById("btn-run-autofetch");
  const resultsArea = document.getElementById("ai-results-area");
  const webContextBox = document.getElementById("ai-web-context-box");

  if (btn) {
    btn.disabled = true;
    btn.innerHTML = `<span class="animate-spin mr-2">🌐</span> Auto-fetching web info & synthesizing...`;
  }

  if (webContextBox) webContextBox.classList.add("hidden");

  resultsArea.innerHTML = `
    <div class="bg-slate-900 border border-slate-800 p-8 rounded-3xl text-center space-y-4">
      <div class="inline-block p-4 rounded-2xl bg-indigo-500/10 text-indigo-400 animate-pulse">
        <i data-lucide="globe" class="w-8 h-8"></i>
      </div>
      <div>
        <h3 class="text-base font-bold text-white">Live Web Search & Deep Knowledge Synthesis</h3>
        <p class="text-xs text-slate-400 mt-1 max-w-md mx-auto">
          Querying Firecrawl, Wikipedia, and OpenLibrary for "${query}" to extract core chapters and ideas...
        </p>
      </div>
    </div>
  `;
  if (window.lucide) lucide.createIcons();

  try {
    const res = await fetch('/api/ai/autofetch-extract', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: query,
        topic: topic,
        provider: provider,
        num_ideas: count
      })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Auto-fetch failed");

    const webInfo = data.web_info;
    if (webInfo && webContextBox) {
      document.getElementById("web-resolved-title").textContent = webInfo.resolved_title || query;
      document.getElementById("web-resolved-author").textContent = webInfo.resolved_author || "Identified from web";
      document.getElementById("web-description-preview").textContent = webInfo.description || "Synthesized from web knowledge.";
      
      const sourcesBadge = document.getElementById("web-sources-badge");
      if (sourcesBadge) {
        sourcesBadge.textContent = `${(webInfo.sources || []).length} sources verified`;
      }

      const sourcesList = document.getElementById("web-sources-list");
      if (sourcesList && webInfo.sources) {
        sourcesList.innerHTML = webInfo.sources.map(s => `
          <a href="${s.url}" target="_blank" rel="noopener noreferrer" class="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-indigo-300 hover:text-white border border-slate-700 flex items-center space-x-1 transition">
            <i data-lucide="external-link" class="w-3 h-3"></i>
            <span class="truncate max-w-[140px]">${s.title}</span>
          </a>
        `).join('');
      }

      webContextBox.classList.remove("hidden");
    }

    lastExtractedIdeas = data.ideas;
    lastExtractedBookTitle = webInfo ? (webInfo.resolved_title || query) : query;
    lastExtractedAuthor = webInfo ? (webInfo.resolved_author || "Curated Thinker") : "Curated Thinker";
    renderAIExtractionResults(data.ideas);
  } catch (err) {
    console.error("Auto-fetch error:", err);
    resultsArea.innerHTML = `
      <div class="p-6 rounded-2xl bg-rose-950/40 border border-rose-800 text-rose-200 text-sm space-y-2">
        <div class="flex items-center space-x-2 font-bold text-rose-300">
          <i data-lucide="alert-triangle" class="w-5 h-5"></i>
          <span>Auto-Fetch / Generation Notice</span>
        </div>
        <p>${err.message}</p>
        <p class="text-xs text-rose-300/80">Please ensure the server is active on http://127.0.0.1:8000.</p>
      </div>
    `;
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = `<i data-lucide="sparkles" class="w-4 h-4"></i><span>Auto-Fetch & Generate Ideas</span>`;
    }
    if (window.lucide) lucide.createIcons();
  }
}

// --- Manual AI Stashifier ---
function fillSampleAI(choice) {
  const textarea = document.getElementById("ai-input-text");
  const title = document.getElementById("ai-source-title");
  const author = document.getElementById("ai-author");
  const topic = document.getElementById("ai-topic");

  if (choice === 1) {
    textarea.value = "Daniel Kahneman reveals that our minds have two systems: System 1 operates automatically and quickly with little effort. System 2 allocates attention to effortful mental operations like complex computations. Cognitive ease reduces vigilance, whereas cognitive strain activates System 2. Prospect theory shows losses loom larger than gains, which leads to irrational risk aversion.";
    title.value = "Thinking, Fast and Slow";
    author.value = "Daniel Kahneman";
    topic.value = "Psychology";
  } else if (choice === 2) {
    textarea.value = "Charlie Munger champions the latticework of mental models: 1. Inversion - avoid stupidity rather than seeking brilliance. 2. Circle of competence - know where your edge ends. 3. Incentive-caused bias - never, ever think about something else when you should be thinking about the power of incentives.";
    title.value = "Poor Charlie's Almanack";
    author.value = "Charlie Munger";
    topic.value = "Mental Models";
  } else {
    textarea.value = "Procrastination is an emotional regulation problem, not a time management defect. When a task triggers negative emotions like fear of failure or boredom, the amygdala seeks immediate mood repair by scrolling social media. Solutions: The 5-Minute Rule to lower starting friction, and self-compassion which lowers cortisol.";
    title.value = "The Science of Overcoming Procrastination";
    author.value = "Dr. Tim Pychyl";
    topic.value = "Productivity";
  }
}

async function runAIExtraction() {
  const text = document.getElementById("ai-input-text").value.trim();
  if (!text) {
    alert("Please provide some text, a URL, or a topic to extract ideas from.");
    return;
  }

  const sourceTitle = document.getElementById("ai-source-title").value.trim();
  const author = document.getElementById("ai-author").value.trim();
  const topic = document.getElementById("ai-topic").value;
  const provider = document.querySelector('input[name="ai-engine"]:checked')?.value || 'gemini';

  const btn = document.getElementById("btn-run-ai");
  const resultsArea = document.getElementById("ai-results-area");

  btn.disabled = true;
  btn.innerHTML = `<span class="animate-spin mr-2">⚙️</span> Synthesizing Microlearning Cards...`;
  resultsArea.innerHTML = `
    <div class="bg-slate-900 border border-slate-800 p-8 rounded-3xl text-center space-y-3">
      <div class="inline-block p-4 rounded-2xl bg-indigo-500/10 text-indigo-400 animate-pulse">
        <i data-lucide="sparkles" class="w-8 h-8"></i>
      </div>
      <h3 class="text-base font-bold text-white">Extracting Core Mental Models & Action Steps</h3>
      <p class="text-xs text-slate-400">Distilling noise into high-density atomic wisdom...</p>
    </div>
  `;
  if (window.lucide) lucide.createIcons();

  try {
    const res = await fetch('/api/ai/extract', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        input_text: text,
        source_title: sourceTitle,
        author: author,
        topic: topic,
        provider: provider,
        num_ideas: 3
      })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Extraction failed");

    lastExtractedIdeas = data.ideas;
    renderAIExtractionResults(data.ideas);
  } catch (err) {
    resultsArea.innerHTML = `
      <div class="p-6 rounded-2xl bg-rose-950/40 border border-rose-800 text-rose-200 text-sm">
        <strong>Extraction Error:</strong> ${err.message}
      </div>
    `;
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<i data-lucide="sparkles" class="w-4 h-4"></i><span>Generate from Custom Text</span>`;
    if (window.lucide) lucide.createIcons();
  }
}

function renderAIExtractionResults(ideas) {
  const container = document.getElementById("ai-results-area");
  if (!container) return;

  const bookTitle = lastExtractedBookTitle || (ideas.length ? ideas[0].source : "Book");
  const author = lastExtractedAuthor || (ideas.length ? ideas[0].author : "Author");

  container.innerHTML = `
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
      <div>
        <h3 class="text-lg font-bold text-white flex items-center space-x-2">
          <span>${ideas.length} Complete Ideas Generated</span>
          <span class="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">Complete Breakdown</span>
        </h3>
        <p class="text-xs text-slate-400 mt-0.5">Covering core chapters and mental models from <strong>${bookTitle}</strong> by ${author}</p>
      </div>

      <div class="flex items-center space-x-2">
        <button onclick="saveAsDedicatedBookStash()" class="px-4 py-2.5 rounded-xl bg-gradient-to-r from-amber-500 to-rose-600 hover:from-amber-400 hover:to-rose-500 text-white font-bold text-xs flex items-center space-x-1.5 shadow-lg shadow-rose-600/20 transition active:scale-95" title="Create a dedicated stash collection for this book">
          <i data-lucide="bookmark-plus" class="w-4 h-4"></i>
          <span>Create "${bookTitle.length > 18 ? bookTitle.slice(0, 16) + '...' : bookTitle}" Stash</span>
        </button>
        <button onclick="saveAllExtractedCards()" class="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white font-semibold text-xs flex items-center space-x-1.5 border border-slate-700 transition" title="Add all cards to your general feed">
          <i data-lucide="check" class="w-4 h-4 text-emerald-400"></i>
          <span>Add to Feed</span>
        </button>
      </div>
    </div>

    <div class="space-y-4 pt-2">
      ${ideas.map((card, idx) => `
        <div class="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-3">
          <div class="flex items-center justify-between">
            <span class="px-2.5 py-0.5 rounded-full text-xs font-bold uppercase bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
              #${idx+1} • ${card.topic}
            </span>
            <span class="text-xs text-slate-400">${card.author} — ${card.source}</span>
          </div>

          <h4 class="text-lg font-extrabold text-white">${card.title}</h4>
          <p class="text-xs text-indigo-300 font-medium">${card.one_liner}</p>
          <p class="text-xs text-slate-300 leading-relaxed">${card.summary}</p>

          ${card.detailed_explanation ? `
            <div class="bg-slate-950/60 border border-slate-800 rounded-2xl p-4 text-xs text-slate-300 space-y-1.5">
              <span class="font-bold text-indigo-400 uppercase tracking-wider block">Detailed Concept Breakdown:</span>
              <p class="leading-relaxed">${card.detailed_explanation}</p>
            </div>
          ` : ''}

          ${card.example ? `
            <div class="bg-amber-950/30 border border-amber-800/40 rounded-2xl p-4 text-xs text-amber-200/90 space-y-1">
              <span class="font-bold text-amber-400 uppercase tracking-wider block">Real-World Case Study / Example:</span>
              <p class="leading-relaxed">${card.example}</p>
            </div>
          ` : ''}

          ${card.quote ? `
            <blockquote class="border-l-2 border-indigo-500 pl-3 text-xs italic text-slate-300">
              "${card.quote}"
            </blockquote>
          ` : ''}

          ${card.action_item ? `
            <div class="bg-emerald-950/40 border border-emerald-800/40 rounded-xl p-3 text-xs text-emerald-200">
              <span class="font-bold uppercase tracking-wider block mb-1">Try It Today:</span>
              ${card.action_item}
            </div>
          ` : ''}

          <div class="pt-2 flex items-center justify-between border-t border-slate-800/60">
            <button onclick="openDeepDiveModal(${idx})" class="text-xs font-semibold text-indigo-400 hover:text-white flex items-center space-x-1 transition px-3 py-1.5 rounded-xl bg-indigo-500/10 hover:bg-indigo-600">
              <i data-lucide="book-open" class="w-3.5 h-3.5"></i>
              <span>Open in Deep Dive Reader</span>
            </button>
            <span class="text-[11px] text-slate-500">Atomic Card #${idx+1}</span>
          </div>
        </div>
      `).join('')}
    </div>
  `;

  if (window.lucide) lucide.createIcons();
}

async function saveAsDedicatedBookStash() {
  if (!lastExtractedIdeas.length) return;
  const bookTitle = lastExtractedBookTitle || (lastExtractedIdeas[0] ? lastExtractedIdeas[0].source : "Book");
  const author = lastExtractedAuthor || (lastExtractedIdeas[0] ? lastExtractedIdeas[0].author : "Author");

  try {
    const res = await fetch('/api/ai/save-as-book-stash', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ideas: lastExtractedIdeas,
        book_title: bookTitle,
        author: author,
        color: "indigo"
      })
    });
    const data = await res.json();
    alert(`Success! Created "${data.stash_title}" with ${data.saved_count} atomic ideas.`);
    await loadStashes();
    await loadIdeas();
    switchTab('stashes');
    viewStashDetail(data.stash_id);
  } catch (err) {
    console.error("Failed to save book stash:", err);
    alert("Could not save book stash: " + err.message);
  }
}

async function saveAllExtractedCards() {
  if (!lastExtractedIdeas.length) return;
  try {
    await fetch('/api/ai/save-batch', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ideas: lastExtractedIdeas })
    });
    alert(`Successfully added ${lastExtractedIdeas.length} ideas to your Microstash feed!`);
    loadIdeas();
    switchTab('swipe');
  } catch (err) {
    console.error("Failed to save batch:", err);
  }
}

// --- Theme Toggle ---
function toggleTheme() {
  const html = document.documentElement;
  const isDark = html.classList.contains("dark");
  const icon = document.getElementById("theme-icon");

  if (isDark) {
    html.classList.remove("dark");
    if (icon) icon.setAttribute("data-lucide", "sun");
    localStorage.setItem("theme", "light");
  } else {
    html.classList.add("dark");
    if (icon) icon.setAttribute("data-lucide", "moon");
    localStorage.setItem("theme", "dark");
  }
  if (window.lucide) lucide.createIcons();
}

// --- Daily Recall Gym & Leitner Spaced Repetition Engine ---
async function loadLeitnerDue() {
  try {
    const res = await fetch('/api/ideas/leitner/due');
    if (res.ok) {
      window.state.leitnerIdeas = await res.json();
      window.state.currentLeitnerIndex = 0;
      window.state.isLeitnerRevealed = false;
    }
  } catch (err) {
    console.warn("Could not load due Leitner ideas:", err);
  }
  updateLeitnerStatsUI();
}

function updateLeitnerStatsUI() {
  const dueCount = (window.state.leitnerIdeas || []).length;
  const badge = document.getElementById('leitner-due-badge');
  if (badge) {
    badge.textContent = dueCount;
    if (dueCount > 0) {
      badge.classList.remove('bg-slate-700/50', 'text-slate-400');
      badge.classList.add('bg-emerald-500/20', 'text-emerald-300');
    } else {
      badge.classList.remove('bg-emerald-500/20', 'text-emerald-300');
      badge.classList.add('bg-slate-700/50', 'text-slate-400');
    }
  }

  // Count distribution across all loaded ideas
  const allIdeas = window.state.ideas || [];
  for (let b = 1; b <= 5; b++) {
    const count = allIdeas.filter(i => (i.leitner_box || 1) === b).length;
    const el = document.getElementById(`box-count-${b}`);
    if (el) el.textContent = count;
  }

  // Session progress counter
  const counterEl = document.getElementById('leitner-session-counter');
  if (counterEl) {
    if (dueCount === 0 || window.state.currentLeitnerIndex >= dueCount) {
      counterEl.textContent = `${dueCount} / ${dueCount} Done`;
    } else {
      counterEl.textContent = `${window.state.currentLeitnerIndex + 1} / ${dueCount}`;
    }
  }
}

function renderLeitnerCard() {
  const container = document.getElementById('leitner-card-container');
  if (!container) return;

  const dueList = window.state.leitnerIdeas || [];
  const currIdx = window.state.currentLeitnerIndex || 0;

  if (dueList.length === 0 || currIdx >= dueList.length) {
    // Session Complete or All caught up screen
    container.innerHTML = `
      <div class="bg-gradient-to-b from-slate-900 to-slate-950 border border-emerald-500/30 rounded-3xl p-8 sm:p-10 text-center shadow-2xl space-y-6 max-w-xl mx-auto">
        <div class="w-16 h-16 rounded-3xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center mx-auto text-emerald-400 shadow-inner">
          <i data-lucide="trophy" class="w-8 h-8"></i>
        </div>
        <div class="space-y-2">
          <h3 class="text-xl sm:text-2xl font-bold text-white">Daily Recall Gym Cleared!</h3>
          <p class="text-xs sm:text-sm text-slate-300 leading-relaxed">
            You've completed all scheduled active recall reviews for today. Spaced repetition intervals have shifted forward.
          </p>
        </div>
        <div class="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 text-xs text-slate-400 flex items-center justify-around">
          <div>
            <span class="block text-slate-500 font-semibold uppercase text-[10px]">Cards Reviewed</span>
            <span class="text-base font-bold text-emerald-400 font-mono">${dueList.length}</span>
          </div>
          <div class="h-6 w-px bg-slate-800"></div>
          <div>
            <span class="block text-slate-500 font-semibold uppercase text-[10px]">Retention Schedule</span>
            <span class="text-base font-bold text-indigo-400 font-mono">1d → 30d</span>
          </div>
          <div class="h-6 w-px bg-slate-800"></div>
          <div>
            <span class="block text-slate-500 font-semibold uppercase text-[10px]">Streak</span>
            <span class="text-base font-bold text-amber-400 font-mono">${window.state.stats.streak_days || 1} 🔥</span>
          </div>
        </div>
        <div class="pt-2 flex flex-col sm:flex-row items-center justify-center gap-3">
          <button onclick="restartLeitnerPractice()" class="w-full sm:w-auto px-5 py-3 rounded-2xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs sm:text-sm flex items-center justify-center space-x-2 transition shadow-lg shadow-indigo-600/30 cursor-pointer">
            <i data-lucide="rotate-ccw" class="w-4 h-4"></i>
            <span>Practice All Cards Anyway</span>
          </button>
          <button onclick="switchTab('swipe')" class="w-full sm:w-auto px-5 py-3 rounded-2xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-xs sm:text-sm flex items-center justify-center space-x-2 transition cursor-pointer">
            <i data-lucide="layers" class="w-4 h-4"></i>
            <span>Back to Swipe Deck</span>
          </button>
        </div>
      </div>
    `;
    if (window.lucide) lucide.createIcons();
    updateLeitnerStatsUI();
    return;
  }

  const idea = dueList[currIdx];
  const boxNum = idea.leitner_box || 1;
  const isRevealed = window.state.isLeitnerRevealed;

  if (!isRevealed) {
    // FRONT: Active Retrieval Challenge
    container.innerHTML = `
      <div class="bg-gradient-to-b from-slate-900 to-slate-950 border border-slate-800 hover:border-emerald-500/40 rounded-3xl p-6 sm:p-8 shadow-2xl transition-all duration-300 space-y-6">
        
        <!-- Top Metadata Pill Row -->
        <div class="flex items-center justify-between text-xs">
          <div class="flex items-center space-x-2">
            <span class="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${getTopicBadgeClass(idea.topic)}">
              ${idea.topic || 'Mental Model'}
            </span>
            <span class="px-2.5 py-0.5 rounded-full text-[11px] font-mono font-bold bg-indigo-500/10 text-indigo-300 border border-indigo-500/30">
              Box ${boxNum} • Review
            </span>
          </div>
          <span class="text-slate-400 font-medium truncate max-w-[150px]">${idea.author || 'Author'}</span>
        </div>

        <!-- The Retrieval Challenge Question -->
        <div class="space-y-3 py-2">
          <span class="text-xs font-bold uppercase tracking-wider text-emerald-400 flex items-center space-x-1.5">
            <i data-lucide="help-circle" class="w-4 h-4"></i>
            <span>Active Recall Prompt</span>
          </span>
          <h3 class="text-xl sm:text-2xl font-extrabold text-white leading-tight">
            ${idea.title}
          </h3>
          <p class="text-sm sm:text-base text-slate-300 italic border-l-2 border-indigo-500/40 pl-3">
            "${idea.one_liner}"
          </p>
        </div>

        <!-- Active Retrieval Exercise Instructions -->
        <div class="p-4 rounded-2xl bg-indigo-950/30 border border-indigo-500/30 text-xs text-indigo-200/90 flex items-start space-x-3">
          <i data-lucide="sparkles" class="w-5 h-5 text-indigo-400 shrink-0 mt-0.5"></i>
          <div class="space-y-1">
            <span class="font-bold text-white block">Test Your Memory First</span>
            <p class="text-slate-300 leading-relaxed">
              Before revealing, mentally answer: What is the underlying mechanism? How would you explain this model to a peer?
            </p>
          </div>
        </div>

        <!-- Big Reveal Answer Button -->
        <button onclick="revealLeitnerAnswer()" class="w-full py-4 rounded-2xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold text-sm sm:text-base shadow-xl shadow-emerald-950/50 flex items-center justify-center space-x-2 transition transform hover:scale-[1.01] active:scale-[0.99] cursor-pointer">
          <i data-lucide="eye" class="w-5 h-5"></i>
          <span>Reveal Answer & Explanation</span>
          <span class="ml-2 px-2 py-0.5 rounded-md bg-white/20 text-xs font-mono hidden sm:inline">Space</span>
        </button>

      </div>
    `;
  } else {
    // BACK: Revealed Knowledge & Self-Grading Buttons
    const detailedHtml = (idea.detailed_explanation && idea.detailed_explanation.trim().length >= 80)
      ? renderMarkdownDetailed(idea.detailed_explanation)
      : `<p class="text-slate-300 leading-relaxed">${idea.summary}</p>`;

    container.innerHTML = `
      <div class="bg-gradient-to-b from-slate-900 to-slate-950 border border-emerald-500/40 rounded-3xl p-6 sm:p-8 shadow-2xl transition-all duration-300 space-y-6">
        
        <!-- Header -->
        <div class="flex items-center justify-between text-xs border-b border-slate-800 pb-3">
          <div class="flex items-center space-x-2">
            <span class="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${getTopicBadgeClass(idea.topic)}">
              ${idea.topic || 'Mental Model'}
            </span>
            <span class="px-2.5 py-0.5 rounded-full text-[11px] font-mono font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
              Box ${boxNum} Revealed
            </span>
          </div>
          <button onclick="playIdeaAudioById('${idea.id}')" class="p-1.5 rounded-xl text-slate-400 hover:text-sky-400 hover:bg-slate-800 transition cursor-pointer" title="Listen to narration">
            <i data-lucide="volume-2" class="w-4 h-4"></i>
          </button>
        </div>

        <!-- Title & Core Summary -->
        <div class="space-y-2">
          <h3 class="text-xl sm:text-2xl font-bold text-white">${idea.title}</h3>
          <p class="text-sm text-slate-300 leading-relaxed bg-slate-950/60 p-3.5 rounded-2xl border border-slate-800/80">
            ${idea.summary}
          </p>
        </div>

        <!-- In-Depth Theoretical Mechanics -->
        <div class="space-y-2">
          <span class="text-xs font-bold uppercase tracking-wider text-indigo-400 flex items-center space-x-1.5">
            <i data-lucide="book-open" class="w-3.5 h-3.5"></i>
            <span>Theoretical Mechanics & First Principles</span>
          </span>
          <div class="text-xs sm:text-sm text-slate-300 leading-relaxed space-y-2 bg-slate-950/40 p-4 rounded-2xl border border-indigo-950/40 max-h-56 overflow-y-auto">
            ${detailedHtml}
          </div>
        </div>

        <!-- Concrete Real-World Example -->
        ${idea.example ? `
          <div class="p-3.5 rounded-2xl bg-amber-950/20 border border-amber-500/30 text-xs sm:text-sm text-amber-200/90 flex items-start space-x-2.5">
            <i data-lucide="zap" class="w-4 h-4 text-amber-400 shrink-0 mt-0.5"></i>
            <div class="space-y-0.5">
              <span class="font-bold text-amber-300 block text-[11px] uppercase tracking-wider">Applied Example</span>
              <p class="text-slate-300 leading-relaxed">${idea.example}</p>
            </div>
          </div>
        ` : ''}

        <!-- Self-Grading Feedback Bar -->
        <div class="pt-2 border-t border-slate-800 space-y-3">
          <div class="flex items-center justify-between text-xs">
            <span class="font-semibold text-slate-300">How well did you recall this mental model?</span>
            <span class="text-[11px] text-slate-500 hidden sm:inline">Keys: [1] Hard • [2] Good • [3] Easy</span>
          </div>

          <div class="grid grid-cols-3 gap-2 sm:gap-3">
            <!-- HARD -->
            <button onclick="submitLeitnerGrade('hard')" class="p-3 sm:p-3.5 rounded-2xl bg-rose-500/15 hover:bg-rose-500/25 border border-rose-500/40 text-rose-300 font-semibold text-xs sm:text-sm flex flex-col items-center justify-center space-y-1 transition transform hover:scale-[1.02] active:scale-[0.98] cursor-pointer">
              <span class="font-bold flex items-center space-x-1">
                <span>❌ Hard</span>
                <span class="text-[10px] font-mono opacity-75 hidden sm:inline">(1)</span>
              </span>
              <span class="text-[10px] sm:text-[11px] text-rose-400 font-normal">Reset Box 1 [1d]</span>
            </button>

            <!-- GOOD -->
            <button onclick="submitLeitnerGrade('good')" class="p-3 sm:p-3.5 rounded-2xl bg-indigo-500/15 hover:bg-indigo-500/25 border border-indigo-500/40 text-indigo-300 font-semibold text-xs sm:text-sm flex flex-col items-center justify-center space-y-1 transition transform hover:scale-[1.02] active:scale-[0.98] cursor-pointer">
              <span class="font-bold flex items-center space-x-1">
                <span>👍 Good</span>
                <span class="text-[10px] font-mono opacity-75 hidden sm:inline">(2)</span>
              </span>
              <span class="text-[10px] sm:text-[11px] text-indigo-400 font-normal">Next Box [3-7d]</span>
            </button>

            <!-- EASY -->
            <button onclick="submitLeitnerGrade('easy')" class="p-3 sm:p-3.5 rounded-2xl bg-emerald-500/15 hover:bg-emerald-500/25 border border-emerald-500/40 text-emerald-300 font-semibold text-xs sm:text-sm flex flex-col items-center justify-center space-y-1 transition transform hover:scale-[1.02] active:scale-[0.98] cursor-pointer">
              <span class="font-bold flex items-center space-x-1">
                <span>⚡ Easy</span>
                <span class="text-[10px] font-mono opacity-75 hidden sm:inline">(3)</span>
              </span>
              <span class="text-[10px] sm:text-[11px] text-emerald-400 font-normal">+2 Boxes [14-30d]</span>
            </button>
          </div>
        </div>

      </div>
    `;
  }

  if (window.lucide) lucide.createIcons();
  updateLeitnerStatsUI();
}

function revealLeitnerAnswer() {
  window.state.isLeitnerRevealed = true;
  renderLeitnerCard();
}

async function submitLeitnerGrade(grade) {
  const dueList = window.state.leitnerIdeas || [];
  const currIdx = window.state.currentLeitnerIndex || 0;
  if (!dueList.length || currIdx >= dueList.length) return;

  const idea = dueList[currIdx];

  try {
    const res = await fetch(`/api/ideas/${idea.id}/leitner-review`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ grade })
    });
    if (res.ok) {
      const data = await res.json();
      idea.leitner_box = data.new_box;
      idea.next_review_date = data.next_review_date;
      
      // Update matching idea in global list
      const globalIdea = (window.state.ideas || []).find(i => String(i.id) === String(idea.id));
      if (globalIdea) {
        globalIdea.leitner_box = data.new_box;
        globalIdea.next_review_date = data.next_review_date;
      }
    }
  } catch (err) {
    console.warn("Failed to record Leitner review:", err);
  }

  // Increment session counter
  window.state.currentLeitnerIndex++;
  window.state.isLeitnerRevealed = false;

  // Gamification bump
  if (typeof recordCurrentIdeaRead === 'function') {
    recordCurrentIdeaRead();
  }

  renderLeitnerCard();
}

function restartLeitnerPractice() {
  window.state.leitnerIdeas = [...(window.state.ideas || [])];
  window.state.currentLeitnerIndex = 0;
  window.state.isLeitnerRevealed = false;
  renderLeitnerCard();
}

// Canonical window bindings
window.switchTab = switchTab;
window.setAIMode = setAIMode;
window.setQueryAndFetch = setQueryAndFetch;
window.runAutoFetchAndGenerate = runAutoFetchAndGenerate;
window.runAIExtraction = runAIExtraction;
window.saveAllExtractedCards = saveAllExtractedCards;
window.saveAsDedicatedBookStash = saveAsDedicatedBookStash;
window.fillSampleAI = fillSampleAI;
window.filterByTopic = filterByTopic;
window.debounceFeedSearch = debounceFeedSearch;
window.jumpToSwipeCard = jumpToSwipeCard;
window.playIdeaAudioById = playIdeaAudioById;
window.toggleLikeCurrentCard = toggleLikeCurrentCard;
window.toggleSaveCurrentCard = toggleSaveCurrentCard;
window.viewStashDetail = viewStashDetail;
window.closeStashDetail = closeStashDetail;
window.removeIdeaFromStash = removeIdeaFromStash;
window.openStashModal = openStashModal;
window.closeStashModal = closeStashModal;
window.saveIdeaToSpecificStash = saveIdeaToSpecificStash;
window.openCreateStashModal = openCreateStashModal;
window.closeCreateStashModal = closeCreateStashModal;
window.submitNewStash = submitNewStash;
window.toggleTheme = toggleTheme;
window.openDeepDiveModal = openDeepDiveModal;
window.closeDeepDiveModal = closeDeepDiveModal;
window.regenerateCurrentDeepDive = regenerateCurrentDeepDive;
window.copyCurrentDeepDive = copyCurrentDeepDive;
window.modalSaveToStash = modalSaveToStash;
window.modalShareCard = modalShareCard;
window.advanceCard = advanceCard;
window.recordCurrentIdeaRead = recordCurrentIdeaRead;
window.loadLeitnerDue = loadLeitnerDue;
window.renderLeitnerCard = renderLeitnerCard;
window.revealLeitnerAnswer = revealLeitnerAnswer;
window.submitLeitnerGrade = submitLeitnerGrade;
window.restartLeitnerPractice = restartLeitnerPractice;
window.setDiagramViewMode = setDiagramViewMode;

// =========================================================================
// PROGRESSIVE DISCLOSURE SLIDE CONTROLLER (3-SLIDE MICRO-PAGER)
// =========================================================================
function switchDeepDiveSlide(slideKey) {
  const secMechanism = document.getElementById("slide-sec-mechanism");
  const secExample = document.getElementById("slide-sec-example");
  const secBoundary = document.getElementById("slide-sec-boundary");

  const btnMechanism = document.getElementById("tab-btn-mechanism");
  const btnExample = document.getElementById("tab-btn-example");
  const btnBoundary = document.getElementById("tab-btn-boundary");
  const btnAll = document.getElementById("tab-btn-all");

  const allBtns = [btnMechanism, btnExample, btnBoundary, btnAll];
  allBtns.forEach(b => {
    if (b) {
      b.classList.remove("bg-indigo-600", "text-white", "shadow-sm");
      b.classList.add("text-slate-400");
    }
  });

  if (slideKey === 'all') {
    if (secMechanism) secMechanism.classList.remove("hidden");
    if (secExample) secExample.classList.remove("hidden");
    if (secBoundary) secBoundary.classList.remove("hidden");
    if (btnAll) {
      btnAll.classList.add("bg-indigo-600", "text-white", "shadow-sm");
      btnAll.classList.remove("text-slate-400");
    }
  } else if (slideKey === 'example') {
    if (secMechanism) secMechanism.classList.add("hidden");
    if (secExample) secExample.classList.remove("hidden");
    if (secBoundary) secBoundary.classList.add("hidden");
    if (btnExample) {
      btnExample.classList.add("bg-indigo-600", "text-white", "shadow-sm");
      btnExample.classList.remove("text-slate-400");
    }
  } else if (slideKey === 'boundary') {
    if (secMechanism) secMechanism.classList.add("hidden");
    if (secExample) secExample.classList.add("hidden");
    if (secBoundary) secBoundary.classList.remove("hidden");
    if (btnBoundary) {
      btnBoundary.classList.add("bg-indigo-600", "text-white", "shadow-sm");
      btnBoundary.classList.remove("text-slate-400");
    }
  } else {
    // Default: mechanism
    if (secMechanism) secMechanism.classList.remove("hidden");
    if (secExample) secExample.classList.add("hidden");
    if (secBoundary) secBoundary.classList.add("hidden");
    if (btnMechanism) {
      btnMechanism.classList.add("bg-indigo-600", "text-white", "shadow-sm");
      btnMechanism.classList.remove("text-slate-400");
    }
  }
}

// =========================================================================
// SECOND BRAIN EXPORTER (OBSIDIAN / NOTION MARKDOWN EXPORT)
// =========================================================================
async function exportCurrentToObsidian() {
  if (!currentDeepDiveIdea || !currentDeepDiveIdea.id) return;
  try {
    const res = await fetch(`/api/ideas/${currentDeepDiveIdea.id}/export-markdown`);
    if (!res.ok) throw new Error("Export failed");
    const data = await res.json();
    
    // Copy to clipboard
    await navigator.clipboard.writeText(data.markdown);
    
    // Provide visual feedback
    const toast = document.createElement("div");
    toast.className = "fixed bottom-8 right-8 z-50 px-4 py-3 rounded-2xl bg-purple-600 text-white font-bold text-xs shadow-2xl flex items-center space-x-2 animate-bounce";
    toast.innerHTML = `<i data-lucide="check" class="w-4 h-4"></i><span>Copied Obsidian / Notion Markdown!</span>`;
    document.body.appendChild(toast);
    if (typeof lucide !== 'undefined') lucide.createIcons();
    setTimeout(() => toast.remove(), 2500);
  } catch (err) {
    console.error("Markdown export error:", err);
    alert("Could not export markdown. Copied standard text instead.");
  }
}

// =========================================================================
// COGNITIVE BLINDSPOT DIAGNOSTIC CONTROLLER
// =========================================================================
let userQuizProfile = {
  blindspot: null,
  context: null
};

function openOnboardingQuiz() {
  const modal = document.getElementById("onboarding-quiz-modal");
  if (!modal) return;
  modal.classList.remove("hidden");
  document.getElementById("quiz-step-1").classList.remove("hidden");
  document.getElementById("quiz-step-2").classList.add("hidden");
  document.getElementById("quiz-step-result").classList.add("hidden");
  if (typeof lucide !== 'undefined') lucide.createIcons();
}

function closeOnboardingQuiz() {
  const modal = document.getElementById("onboarding-quiz-modal");
  if (modal) modal.classList.add("hidden");
}

function selectQuizBlindspot(type) {
  userQuizProfile.blindspot = type;
  document.getElementById("quiz-step-1").classList.add("hidden");
  document.getElementById("quiz-step-2").classList.remove("hidden");
  if (typeof lucide !== 'undefined') lucide.createIcons();
}

function selectQuizContext(ctx) {
  userQuizProfile.context = ctx;
  document.getElementById("quiz-step-2").classList.add("hidden");
  const resultStep = document.getElementById("quiz-step-result");
  resultStep.classList.remove("hidden");

  // Determine Archetype
  let title = "The First-Principles Strategist";
  let desc = "You thrive on deep logic but face decision friction when uncertainty clouds the horizon. Your tailored starter workout trains you to invert problems and isolate immutable constraints.";
  let cards = [
    { title: "First-Principles Thinking", topic: "Mental Models" },
    { title: "The Inversion Principle", topic: "Strategy" },
    { title: "Second-Order Thinking", topic: "Systems" }
  ];

  if (userQuizProfile.blindspot === "emotional_reactive") {
    title = "The Stoic Sovereign";
    desc = "You operate with intense passion and energy, but high-stress volatility can trigger first-order emotional reactions. Your starter workout focuses on radical emotional armor and asymmetric defense.";
    cards = [
      { title: "The Dichotomy of Control", topic: "Stoicism" },
      { title: "The Obstacle is the Way", topic: "Stoicism" },
      { title: "System 1 vs System 2 Thinking", topic: "Psychology" }
    ];
  } else if (userQuizProfile.blindspot === "execution_drag") {
    title = "The Kinetic Executor";
    desc = "You conceptualize brilliant plans, but daily friction drains execution velocity. Your starter workout wires rapid action habits and attention residue shields into your muscle memory.";
    cards = [
      { title: "The Two-Minute Rule", topic: "Productivity" },
      { title: "Identity-Based Habits", topic: "Habits" },
      { title: "Attention Residue", topic: "Focus" }
    ];
  } else if (userQuizProfile.blindspot === "sunk_cost") {
    title = "The Asymmetric Antifragile";
    desc = "You push hard into ambitious bets, but sometimes hold on to declining assets too long. Your starter workout trains strict alignment and skin in the game filters.";
    cards = [
      { title: "Skin in the Game", topic: "Governance" },
      { title: "Loss Aversion & Sunk Cost", topic: "Psychology" },
      { title: "The Circle of Competence", topic: "Investing" }
    ];
  }

  document.getElementById("quiz-archetype-title").textContent = title;
  document.getElementById("quiz-archetype-desc").textContent = desc;

  const cardsContainer = document.getElementById("quiz-recommended-cards");
  cardsContainer.innerHTML = cards.map(c => `
    <div class="p-2.5 rounded-xl bg-slate-900/90 border border-slate-700/60 flex items-center justify-between">
      <span class="font-bold text-white text-xs">${c.title}</span>
      <span class="text-[10px] uppercase font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">${c.topic}</span>
    </div>
  `).join("");

  if (typeof lucide !== 'undefined') lucide.createIcons();
}

function applyQuizWorkoutAndClose() {
  closeOnboardingQuiz();
  // Filter by daily workout
  filterByTopic('leitner-workout');
}

window.switchDeepDiveSlide = switchDeepDiveSlide;
window.exportCurrentToObsidian = exportCurrentToObsidian;
window.openOnboardingQuiz = openOnboardingQuiz;
window.closeOnboardingQuiz = closeOnboardingQuiz;
window.selectQuizBlindspot = selectQuizBlindspot;
window.selectQuizContext = selectQuizContext;
window.applyQuizWorkoutAndClose = applyQuizWorkoutAndClose;

// =========================================================================
// GOOGLE STITCH UI ENGINE EXTENSIONS & LIVE BINDINGS
// =========================================================================

function updateStitchHeroCard() {
  const ideas = window.state.ideas;
  if (!ideas || !ideas.length) return;
  const idea = ideas[window.state.currentIdeaIndex] || ideas[0];
  if (!idea) return;

  const topicBadge = document.getElementById("card-topic-badge");
  if (topicBadge) topicBadge.textContent = idea.topic.toUpperCase();

  const readTime = document.getElementById("card-read-time");
  if (readTime) readTime.textContent = `${idea.read_time_mins || 1} min read`;

  const titleEl = document.getElementById("card-title");
  if (titleEl) titleEl.textContent = idea.title;

  const authorEl = document.getElementById("card-author");
  if (authorEl) authorEl.textContent = idea.author;

  const initialsEl = document.getElementById("card-avatar-initials");
  if (initialsEl && idea.author) {
    const parts = idea.author.split(" ");
    initialsEl.textContent = parts.length > 1 ? (parts[0][0] + parts[1][0]).toUpperCase() : idea.author.slice(0, 2).toUpperCase();
  }

  const oneLinerEl = document.getElementById("card-one-liner");
  if (oneLinerEl) oneLinerEl.textContent = `"${idea.one_liner}"`;

  const leitnerText = document.getElementById("card-leitner-box-text");
  if (leitnerText) leitnerText.textContent = `Box ${idea.leitner_box || 1}`;

  const likeCount = document.getElementById("card-like-count");
  if (likeCount) likeCount.textContent = idea.likes || 0;

  const likeIcon = document.getElementById("card-like-icon");
  if (likeIcon) {
    likeIcon.textContent = idea.is_liked ? "favorite" : "favorite_border";
    likeIcon.className = idea.is_liked ? "material-symbols-outlined text-[18px] text-rose-500" : "material-symbols-outlined text-[18px]";
  }

  const saveBtn = document.getElementById("card-btn-save");
  if (saveBtn) {
    saveBtn.innerHTML = `<span class="material-symbols-outlined text-[18px] ${idea.is_saved ? 'text-primary' : ''}">${idea.is_saved ? 'bookmark' : 'bookmark_border'}</span>`;
  }

  // Render diagram in Stitch container
  const diagContainer = document.getElementById("card-diagram-container");
  if (diagContainer) {
    renderIdeaVisualDiagram(idea, "card-diagram-container");
  }
}

function triggerCurrentCardStressTest() {
  const ideas = window.state.ideas;
  if (!ideas || !ideas.length) return;
  const idea = ideas[window.state.currentIdeaIndex] || ideas[0];
  if (idea) openStressTestModal(idea.id);
}

async function toggleLikeCurrentCard() {
  const ideas = window.state.ideas;
  if (!ideas || !ideas.length) return;
  const idea = ideas[window.state.currentIdeaIndex];
  if (!idea) return;

  try {
    const res = await fetch(`/api/ideas/${idea.id}/like`, { method: "POST" });
    if (res.ok) {
      const updated = await res.json();
      idea.is_liked = updated.is_liked;
      idea.likes = updated.likes;
      updateStitchHeroCard();
    }
  } catch (err) {
    console.error("Like error:", err);
  }
}

async function toggleSaveCurrentCard() {
  const ideas = window.state.ideas;
  if (!ideas || !ideas.length) return;
  const idea = ideas[window.state.currentIdeaIndex];
  if (!idea) return;

  try {
    const res = await fetch(`/api/ideas/${idea.id}/save`, { method: "POST" });
    if (res.ok) {
      const updated = await res.json();
      idea.is_saved = updated.is_saved;
      idea.saved_count = updated.saved_count;
      updateStitchHeroCard();
    }
  } catch (err) {
    console.error("Save error:", err);
  }
}

function playCurrentCardAudio() {
  const ideas = window.state.ideas;
  if (!ideas || !ideas.length) return;
  const idea = ideas[window.state.currentIdeaIndex];
  if (!idea) return;
  
  if (typeof playAudioForIdea === 'function') {
    playAudioForIdea(idea.id);
  } else {
    // Web Speech API fallback
    const utter = new SpeechSynthesisUtterance(`${idea.title}. By ${idea.author}. ${idea.one_liner}. ${idea.summary}`);
    window.speechSynthesis.speak(utter);
  }
}

// Workout screen logic
let currentWorkoutIndex = 0;
let isWorkoutCardFlipped = false;

function renderWorkoutCard() {
  const ideas = window.state.ideas || [];
  if (!ideas.length) return;
  const idea = ideas[currentWorkoutIndex % ideas.length];
  if (!idea) return;

  const topicEl = document.getElementById("workout-card-topic");
  if (topicEl) topicEl.textContent = idea.topic.toUpperCase();

  const titleEl = document.getElementById("workout-card-title");
  if (titleEl) titleEl.textContent = idea.title;

  const bodyEl = document.getElementById("workout-card-body");
  if (bodyEl) {
    bodyEl.textContent = isWorkoutCardFlipped ? (idea.detailed_explanation || idea.summary) : `"${idea.one_liner}"`;
  }

  const statusEl = document.getElementById("workout-card-flip-status");
  if (statusEl) statusEl.textContent = isWorkoutCardFlipped ? "MODEL REVEALED" : "TAP TO REVEAL";
}

function flipWorkoutCard() {
  isWorkoutCardFlipped = !isWorkoutCardFlipped;
  renderWorkoutCard();
}

async function gradeWorkoutCard(grade) {
  const ideas = window.state.ideas || [];
  if (!ideas.length) return;
  const idea = ideas[currentWorkoutIndex % ideas.length];
  if (!idea) return;

  try {
    await fetch(`/api/ideas/${idea.id}/leitner-review`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ grade: grade })
    });
  } catch (e) {}

  currentWorkoutIndex++;
  isWorkoutCardFlipped = false;
  renderWorkoutCard();
  loadStats();
}

// Hook into updateSwipeCardDisplay
const originalUpdateSwipe = updateSwipeCardDisplay;
updateSwipeCardDisplay = function() {
  originalUpdateSwipe();
  updateStitchHeroCard();
  renderWorkoutCard();
};

// Stitch tab switcher
const origSwitchTab = switchTab;
switchTab = function(tabId) {
  origSwitchTab(tabId);
  
  // Also update stitch tab contents
  const swipeTab = document.getElementById("tab-swipe-content");
  const leitnerTab = document.getElementById("tab-leitner-content");
  const feedTab = document.getElementById("tab-feed-content");
  const stashesTab = document.getElementById("tab-stashes-content");
  const aiTab = document.getElementById("tab-ai-content");

  if (swipeTab) swipeTab.classList.toggle("hidden", tabId !== "swipe");
  if (leitnerTab) leitnerTab.classList.toggle("hidden", tabId !== "leitner");
  if (feedTab) feedTab.classList.toggle("hidden", tabId !== "feed");
  if (stashesTab) stashesTab.classList.toggle("hidden", tabId !== "stashes");
  if (aiTab) aiTab.classList.toggle("hidden", tabId !== "ai");

  // Stitch bottom nav active state
  ["swipe", "leitner", "feed", "stashes", "ai"].forEach(t => {
    const btn = document.getElementById(`stitch-nav-${t}`);
    if (btn) {
      if (t === tabId) {
        btn.className = "flex flex-col items-center justify-center bg-primary/15 text-primary rounded-full px-4 py-1.5 shadow-[0_0_12px_rgba(78,222,163,0.25)] transition";
      } else {
        btn.className = "flex flex-col items-center justify-center text-on-surface-variant hover:text-primary transition px-3 py-1.5";
      }
    }
  });

  if (tabId === "leitner") renderWorkoutCard();
};

window.triggerCurrentCardStressTest = triggerCurrentCardStressTest;
window.toggleLikeCurrentCard = toggleLikeCurrentCard;
window.toggleSaveCurrentCard = toggleSaveCurrentCard;
window.playCurrentCardAudio = playCurrentCardAudio;
window.flipWorkoutCard = flipWorkoutCard;
window.gradeWorkoutCard = gradeWorkoutCard;


// =========================================================================
// UNIVERSAL GLOBAL BOOK CACHE & COMMUNITY LIBRARY CONTROLLER
// =========================================================================

let globalBooksCache = [];
let bookSearchDebounce = null;

async function loadGlobalBooks() {
  try {
    const res = await fetch('/api/books');
    if (!res.ok) return;
    const books = await res.json();
    globalBooksCache = books;
    renderGlobalBooksShelf(books);

    const badge = document.getElementById("books-count-badge");
    if (badge) badge.textContent = `${books.length} Books Cached`;
  } catch (e) {
    console.error("Failed to load global books:", e);
  }
}

function renderGlobalBooksShelf(books) {
  const container = document.getElementById("books-shelf-container");
  if (!container) return;

  if (!books || !books.length) {
    container.innerHTML = `
      <div class="col-span-full p-6 rounded-2xl bg-surface-container-high/40 border border-outline-variant/30 text-center">
        <span class="material-symbols-outlined text-outline text-[32px] mb-1">menu_book</span>
        <p class="text-xs text-on-surface-variant">No books registered yet. Use the search bar to scan any book into the global cache!</p>
      </div>
    `;
    return;
  }

  container.innerHTML = books.map(book => {
    return `
      <div onclick="openBookDetailModal('${book.id}')" class="cursor-pointer tactile-glass p-4 rounded-2xl border border-outline-variant/30 hover:border-primary/50 transition-all duration-200 flex items-start gap-3.5 group shadow-lg">
        <div class="w-12 h-16 rounded-xl bg-primary/15 border border-primary/30 flex items-center justify-center text-primary flex-shrink-0 group-hover:scale-105 transition-transform shadow-inner">
          <span class="material-symbols-outlined text-[24px]">menu_book</span>
        </div>
        <div class="flex-1 min-w-0">
          <div class="flex items-center justify-between gap-1 mb-1">
            <span class="px-2 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-wider bg-surface-container-highest text-primary">
              ${book.topic || 'Mental Models'}
            </span>
            <span class="text-[10px] text-secondary font-bold flex items-center gap-0.5">
              <span class="material-symbols-outlined text-[12px]">flash_on</span>
              ${book.ideas_count || 0} models
            </span>
          </div>
          <h4 class="text-xs sm:text-sm font-headline font-bold text-white group-hover:text-primary transition-colors truncate">
            ${book.title}
          </h4>
          <p class="text-[11px] text-on-surface-variant truncate mt-0.5">
            By ${book.author} • <span class="text-on-surface-variant/70">${book.publisher || 'Original Publication'}</span>
          </p>
          <div class="mt-2 flex items-center gap-1 text-[10px] text-primary/80 font-semibold">
            <span>⚡ Instant Global Cache</span>
            <span class="material-symbols-outlined text-[13px]">arrow_forward</span>
          </div>
        </div>
      </div>
    `;
  }).join('');
}

function handleGlobalBookSearch(val) {
  const query = (val || "").trim();
  const clearBtn = document.getElementById("global-search-clear");
  const dropdown = document.getElementById("global-search-autocomplete");
  if (!dropdown) return;

  if (clearBtn) clearBtn.classList.toggle("hidden", !query);

  if (!query) {
    dropdown.classList.add("hidden");
    dropdown.innerHTML = "";
    return;
  }

  clearTimeout(bookSearchDebounce);
  bookSearchDebounce = setTimeout(async () => {
    try {
      const res = await fetch(`/api/books?search=${encodeURIComponent(query)}`);
      const books = await res.json();
      
      const localMatches = (window.state.ideas || []).filter(i => 
        i.title.toLowerCase().includes(query.toLowerCase()) || 
        i.author.toLowerCase().includes(query.toLowerCase()) || 
        i.source.toLowerCase().includes(query.toLowerCase())
      ).slice(0, 4);

      if (!books.length && !localMatches.length) {
        dropdown.innerHTML = `
          <div class="p-3 text-center">
            <p class="text-xs text-on-surface-variant">No cached books found for "${query}".</p>
            <button onclick="requestNewBookScan('${query.replace(/'/g, "\\'")}')" class="mt-2 px-3 py-1.5 rounded-full bg-primary/20 text-primary border border-primary/40 text-[11px] font-bold hover:bg-primary/30 transition">
              ✨ Scan & Add to Global Library
            </button>
          </div>
        `;
        dropdown.classList.remove("hidden");
        return;
      }

      let html = '';
      if (books.length) {
        html += `<div class="px-2 py-1 text-[10px] font-bold uppercase tracking-wider text-primary">Globally Cached Books</div>`;
        html += books.map(b => `
          <div onclick="openBookDetailModal('${b.id}'); clearGlobalSearch();" class="p-2.5 rounded-xl hover:bg-surface-container-high cursor-pointer transition flex items-center justify-between gap-2 border-b border-outline-variant/20 last:border-0">
            <div class="flex items-center gap-2.5 min-w-0">
              <span class="material-symbols-outlined text-primary text-[18px]">menu_book</span>
              <div class="truncate">
                <p class="text-xs font-bold text-white truncate">${b.title}</p>
                <p class="text-[10px] text-on-surface-variant truncate">${b.author} • ${b.publisher || 'Original Publication'}</p>
              </div>
            </div>
            <span class="px-2 py-0.5 rounded-full bg-primary/10 text-primary border border-primary/30 text-[9px] font-bold flex-shrink-0">
              ⚡ 0s Scan (${b.ideas_count})
            </span>
          </div>
        `).join('');
      }

      if (localMatches.length) {
        html += `<div class="px-2 pt-2 pb-1 text-[10px] font-bold uppercase tracking-wider text-secondary">Matching Mental Models</div>`;
        html += localMatches.map(m => `
          <div onclick="jumpToSwipeCard('${m.id}'); clearGlobalSearch();" class="p-2.5 rounded-xl hover:bg-surface-container-high cursor-pointer transition flex items-center justify-between gap-2 border-b border-outline-variant/20 last:border-0">
            <div class="flex items-center gap-2.5 min-w-0">
              <span class="material-symbols-outlined text-secondary text-[18px]">psychology</span>
              <div class="truncate">
                <p class="text-xs font-bold text-white truncate">${m.title}</p>
                <p class="text-[10px] text-on-surface-variant truncate">${m.author} • ${m.source}</p>
              </div>
            </div>
            <span class="text-[10px] text-primary font-bold">Study →</span>
          </div>
        `).join('');
      }

      dropdown.innerHTML = html;
      dropdown.classList.remove("hidden");
    } catch (e) {
      console.error("Search error:", e);
    }
  }, 180);
}

function clearGlobalSearch() {
  const input = document.getElementById("global-book-search-input");
  if (input) input.value = "";
  const clearBtn = document.getElementById("global-search-clear");
  if (clearBtn) clearBtn.classList.add("hidden");
  const dropdown = document.getElementById("global-search-autocomplete");
  if (dropdown) {
    dropdown.classList.add("hidden");
    dropdown.innerHTML = "";
  }
}

async function requestNewBookScan(bookTitle) {
  clearGlobalSearch();
  switchTab('ai');
  const textarea = document.getElementById("ai-input-text");
  if (textarea) {
    textarea.value = `Extract all core chapters, decision frameworks, and mental models from the book: ${bookTitle}`;
    runAiExtraction();
  }
}

async function openBookDetailModal(bookSlug) {
  const modal = document.getElementById("book-detail-modal");
  if (!modal) return;

  try {
    const res = await fetch(`/api/books/${bookSlug}`);
    if (!res.ok) return;
    const book = await res.json();

    document.getElementById("book-modal-title").textContent = book.title;
    document.getElementById("book-modal-author-pub").textContent = `By ${book.author} • Published by ${book.publisher || 'Original Publication'}`;
    document.getElementById("book-modal-topic").textContent = (book.topic || 'Mental Models').toUpperCase();
    document.getElementById("book-modal-ideas-count").innerHTML = `<span class="material-symbols-outlined text-[13px]">flash_on</span><span>${(book.ideas || []).length} Models</span>`;
    
    const cNotice = book.copyright_notice || `Transformative educational commentary & mental model summary of '${book.title}' by ${book.author}. All original copyrights remain with the author and publisher.`;
    document.getElementById("book-modal-copyright-notice").textContent = cNotice;

    const cardsList = document.getElementById("book-modal-cards-list");
    if (cardsList) {
      if (!book.ideas || !book.ideas.length) {
        cardsList.innerHTML = `<p class="text-xs text-on-surface-variant text-center py-6">No cards found for this book.</p>`;
      } else {
        cardsList.innerHTML = book.ideas.map((card, idx) => `
          <div class="p-4 rounded-2xl bg-surface-container-high/80 border border-outline-variant/30 space-y-2">
            <div class="flex items-center justify-between">
              <span class="text-[10px] font-bold uppercase text-primary tracking-wider">Model #${idx + 1}</span>
              <button onclick="openStressTestModal('${card.id}')" class="flex items-center gap-1 px-2.5 py-1 rounded-full bg-secondary/15 text-secondary border border-secondary/30 text-[10px] font-bold hover:bg-secondary/25 transition">
                <span class="material-symbols-outlined text-[13px]">bolt</span>
                <span>Stress-Test</span>
              </button>
            </div>
            <h4 class="text-base font-headline font-bold text-white">${card.title}</h4>
            <p class="text-xs text-primary italic font-semibold">"${card.one_liner}"</p>
            <p class="text-xs text-on-surface/90 leading-relaxed">${card.summary}</p>
            <div class="pt-1 flex items-center justify-between text-[11px] text-on-surface-variant/70 border-t border-outline-variant/20 mt-2">
              <span>${card.read_time_mins || 1} min read</span>
              <button onclick="jumpToSwipeCard('${card.id}'); closeBookDetailModal();" class="text-primary hover:underline font-bold">
                Study in Swipe Gym →
              </button>
            </div>
          </div>
        `).join('');
      }
    }

    modal.classList.remove("hidden");
  } catch (e) {
    console.error("Failed to load book details:", e);
  }
}

function closeBookDetailModal() {
  const modal = document.getElementById("book-detail-modal");
  if (modal) modal.classList.add("hidden");
}

// Hook loadGlobalBooks on init
document.addEventListener("DOMContentLoaded", () => {
  loadGlobalBooks();
});

// Update Stitch Hero Card with publisher attribution
const prevStitchUpdate = updateStitchHeroCard;
updateStitchHeroCard = function() {
  if (typeof prevStitchUpdate === 'function') prevStitchUpdate();
  const ideas = window.state.ideas;
  if (!ideas || !ideas.length) return;
  const idea = ideas[window.state.currentIdeaIndex] || ideas[0];
  if (!idea) return;

  const citeEl = document.getElementById("card-source-citation");
  if (citeEl) {
    citeEl.textContent = `• ${idea.source} (${idea.publisher || 'Original Publication'})`;
  }

  const attribEl = document.getElementById("card-attribution");
  if (attribEl) {
    attribEl.textContent = idea.copyright_notice || `Transformative educational commentary & mental model summary of '${idea.source}' by ${idea.author}. All original copyrights remain with the author and publisher under Fair Use.`;
  }

  const modalNotice = document.getElementById("modal-copyright-notice");
  if (modalNotice) {
    modalNotice.textContent = idea.copyright_notice || `Transformative educational commentary & mental model summary of '${idea.source}' by ${idea.author}. All original copyrights remain with the author and publisher under Fair Use.`;
  }
};

window.loadGlobalBooks = loadGlobalBooks;
window.handleGlobalBookSearch = handleGlobalBookSearch;
window.clearGlobalSearch = clearGlobalSearch;
window.requestNewBookScan = requestNewBookScan;
window.openBookDetailModal = openBookDetailModal;
window.closeBookDetailModal = closeBookDetailModal;


// =========================================================================
// UNIFIED ACTION CONTROLLERS & LIVE BUTTON HANDLERS
// =========================================================================

// 1. Progressive Disclosure 3-Slide Deep Dive System
function setDeepDiveSlide(slideNum) {
  [1, 2, 3].forEach(n => {
    const slide = document.getElementById(`modal-slide-${n}`);
    const pill = document.getElementById(`pill-slide-${n}`);
    if (slide) {
      if (n === slideNum) {
        slide.classList.remove("hidden");
      } else {
        slide.classList.add("hidden");
      }
    }
    if (pill) {
      if (n === slideNum) {
        pill.className = "flex-1 py-1.5 px-3 rounded-full text-[11px] font-bold text-primary bg-primary/20 border border-primary/50 transition text-center shadow-sm";
      } else {
        pill.className = "flex-1 py-1.5 px-3 rounded-full text-[11px] font-medium text-on-surface-variant bg-surface-container border border-outline-variant/30 transition text-center hover:text-white";
      }
    }
  });
}

function closeDeepDiveModal() {
  const modal = document.getElementById("deep-dive-modal");
  if (modal) {
    modal.classList.add("hidden");
    modal.classList.remove("flex");
  }
}

async function openDeepDiveModal(ideaId = null) {
  let idea = null;
  if (ideaId !== null && ideaId !== undefined) {
    idea = (window.state.ideas || []).find(i => String(i.id) === String(ideaId));
    if (!idea && lastExtractedIdeas && lastExtractedIdeas.length) {
      if (typeof ideaId === 'number' || (!isNaN(Number(ideaId)) && Number(ideaId) < lastExtractedIdeas.length)) {
        idea = lastExtractedIdeas[Number(ideaId)];
      } else {
        idea = lastExtractedIdeas.find(i => String(i.id) === String(ideaId));
      }
    }
    if (!idea) {
      try {
        const res = await fetch(`/api/ideas/${ideaId}`);
        if (res.ok) idea = await res.json();
      } catch (e) {
        console.warn("Could not fetch idea detail:", e);
      }
    }
  }

  if (!idea) {
    idea = (window.state.ideas || [])[window.state.currentIdeaIndex];
  }

  if (!idea) return;
  currentDeepDiveIdea = idea;

  const modal = document.getElementById("deep-dive-modal");
  if (!modal) return;
  modal.dataset.ideaId = idea.id || '';

  const topicEl = document.getElementById("modal-topic");
  if (topicEl) {
    topicEl.textContent = (idea.topic || "Mental Model").toUpperCase();
    topicEl.className = "px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-primary/15 text-primary border border-primary/30";
  }

  const authorSourceEl = document.getElementById("modal-author-source");
  if (authorSourceEl) {
    const pub = idea.publisher ? ` • ${idea.publisher}` : '';
    authorSourceEl.textContent = `${idea.author} • ${idea.source}${pub}`;
  }

  const titleEl = document.getElementById("modal-title");
  if (titleEl) titleEl.textContent = idea.title;

  const oneLinerEl = document.getElementById("modal-one-liner");
  if (oneLinerEl) oneLinerEl.textContent = `"${idea.one_liner}"`;

  // Slide 1: Mechanism & Detailed Explanation
  const detailedEl = document.getElementById("modal-detailed-explanation") || document.getElementById("modal-detailed");
  if (detailedEl) {
    if (idea.detailed_explanation && idea.detailed_explanation.trim().length > 0) {
      detailedEl.innerHTML = renderMarkdownDetailed(idea.detailed_explanation);
    } else {
      detailedEl.innerHTML = `<p class="leading-relaxed text-on-surface/90">${idea.summary}</p>`;
    }
  }

  // Diagram rendering into modal
  renderIdeaVisualDiagram(idea, 'modal-diagram-container');

  // Slide 2: Case Study
  const exampleEl = document.getElementById("modal-example");
  if (exampleEl) {
    exampleEl.textContent = idea.example || "Practitioners apply this mental model systematically to navigate uncertainty and avoid irreversible failure modes.";
  }

  // Slide 3: Action & Bounds
  const boundaryEl = document.getElementById("modal-boundary-text");
  if (boundaryEl) {
    boundaryEl.textContent = idea.boundary || "Avoid dogmatic application when foundational axioms or systemic constraints are altered by sudden environmental shifts.";
  }

  const actionEl = document.getElementById("modal-action-item") || document.getElementById("modal-action");
  if (actionEl) {
    actionEl.textContent = idea.action_item || "Apply this model to one difficult decision today.";
  }

  const cNoticeEl = document.getElementById("modal-copyright-notice");
  if (cNoticeEl) {
    cNoticeEl.textContent = idea.copyright_notice || `Transformative educational commentary & mental model summary of '${idea.source}' by ${idea.author}. All original copyrights remain with the author and publisher under Fair Use.`;
  }

  // Reset to Slide 1
  setDeepDiveSlide(1);

  modal.classList.remove("hidden");
  modal.classList.add("flex");
}

// 2. Socratic Dilemma Stress-Test Modal
function closeStressTestModal() {
  const modal = document.getElementById("stress-test-modal");
  if (modal) {
    modal.classList.add("hidden");
    modal.classList.remove("flex");
  }
}

async function openStressTestModal(ideaId = null) {
  let idea = null;
  if (ideaId) {
    idea = (window.state.ideas || []).find(i => String(i.id) === String(ideaId));
    if (!idea) {
      try {
        const res = await fetch(`/api/ideas/${ideaId}`);
        if (res.ok) idea = await res.json();
      } catch (e) {}
    }
  }
  if (!idea) {
    idea = (window.state.ideas || [])[window.state.currentIdeaIndex];
  }
  if (!idea) return;

  const modal = document.getElementById("stress-test-modal");
  if (!modal) return;

  const scenarioEl = document.getElementById("stress-scenario");
  const questionEl = document.getElementById("stress-question");
  const optionsEl = document.getElementById("stress-options");
  const feedbackBox = document.getElementById("stress-feedback-box");

  if (feedbackBox) feedbackBox.classList.add("hidden");
  if (scenarioEl) scenarioEl.textContent = `Synthesizing high-stakes dilemma for '${idea.title}'...`;
  if (questionEl) questionEl.textContent = "Which response correctly applies the model?";
  if (optionsEl) optionsEl.innerHTML = `<div class="py-4 text-center text-xs text-on-surface-variant animate-pulse">Generating scenario choices...</div>`;

  modal.classList.remove("hidden");
  modal.classList.add("flex");

  try {
    const res = await fetch(`/api/ai/stress-test/${encodeURIComponent(idea.id)}`);
    if (!res.ok) throw new Error("Stress test synthesis failed");
    const testData = await res.json();

    if (scenarioEl) scenarioEl.textContent = testData.dilemma || idea.summary;
    if (questionEl) questionEl.textContent = testData.question || "Which response correctly applies the model?";

    if (optionsEl && testData.options && testData.options.length) {
      optionsEl.innerHTML = testData.options.map((opt, idx) => {
        const escapedExp = (opt.explanation || '').replace(/'/g, "\\'").replace(/"/g, '&quot;');
        const escapedHeuristic = (testData.first_principles_heuristic || '').replace(/'/g, "\\'").replace(/"/g, '&quot;');
        return `
          <button 
            onclick="handleStressChoice(${idx}, ${opt.is_correct ? 'true' : 'false'}, '${escapedExp}', '${escapedHeuristic}')"
            class="stress-option-btn w-full text-left p-3.5 rounded-2xl bg-surface-container-high/80 hover:bg-surface-container-highest border border-outline-variant/40 hover:border-primary/50 text-xs text-white leading-relaxed transition flex items-start gap-2.5"
          >
            <span class="w-5 h-5 rounded-full bg-surface-container flex items-center justify-center text-[10px] font-bold text-primary flex-shrink-0 mt-0.5">
              ${String.fromCharCode(65 + idx)}
            </span>
            <span class="flex-1">${opt.text}</span>
          </button>
        `;
      }).join('');
    }
  } catch (err) {
    console.error("Stress test load error:", err);
    if (scenarioEl) scenarioEl.textContent = `Scenario: You face a strategic crossroad involving ${idea.title}.`;
    if (optionsEl) {
      optionsEl.innerHTML = `
        <button onclick="handleStressChoice(0, true, 'Accurate! Applying ${idea.title} directly identifies and eliminates systemic failure traps.', '${idea.one_liner}')" class="w-full text-left p-3.5 rounded-2xl bg-surface-container-high border border-outline-variant/40 text-xs text-white">
          A) Systematically identify and prevent failure vectors before committing capital.
        </button>
        <button onclick="handleStressChoice(1, false, 'Incorrect. This relies on superficial optimism rather than first principles.', '${idea.one_liner}')" class="w-full text-left p-3.5 rounded-2xl bg-surface-container-high border border-outline-variant/40 text-xs text-white mt-2">
          B) Maximize short-term leverage and assume positive momentum continues uninterrupted.
        </button>
      `;
    }
  }
}

function handleStressChoice(idx, isCorrect, explanation, heuristic) {
  const feedbackBox = document.getElementById("stress-feedback-box");
  const titleEl = document.getElementById("stress-feedback-title");
  const expEl = document.getElementById("stress-feedback-explanation");
  const heuristicEl = document.getElementById("stress-first-principles");

  if (!feedbackBox) return;

  const buttons = document.querySelectorAll(".stress-option-btn");
  buttons.forEach((btn, i) => {
    if (i === idx) {
      if (isCorrect) {
        btn.classList.add("border-primary", "bg-primary/10");
      } else {
        btn.classList.add("border-error", "bg-error/10");
      }
    }
  });

  if (isCorrect) {
    feedbackBox.className = "p-4 rounded-2xl border border-primary/40 bg-primary/10 leading-relaxed";
    if (titleEl) titleEl.innerHTML = `<span class="material-symbols-outlined text-primary text-[20px]">check_circle</span> <span class="text-primary font-bold">First-Principles Mastered (+10 XP)</span>`;
  } else {
    feedbackBox.className = "p-4 rounded-2xl border border-error/40 bg-error/10 leading-relaxed";
    if (titleEl) titleEl.innerHTML = `<span class="material-symbols-outlined text-error text-[20px]">cancel</span> <span class="text-error font-bold">Cognitive Trap Detected</span>`;
  }

  if (expEl) expEl.textContent = explanation;
  if (heuristicEl) {
    heuristicEl.textContent = heuristic ? `💡 Key Heuristic: ${heuristic}` : '';
  }

  feedbackBox.classList.remove("hidden");
}

// 3. Audio & Markdown Export Handlers
function toggleCardAudio() {
  playCurrentCardAudio();
}

function exportCurrentCardMarkdown() {
  const idea = currentDeepDiveIdea || (window.state.ideas || [])[window.state.currentIdeaIndex];
  if (!idea) return;

  const md = `---
title: "${idea.title}"
author: "${idea.author}"
source: "${idea.source}"
publisher: "${idea.publisher || 'Original Publication'}"
topic: "${idea.topic}"
tags: [${(idea.tags || []).map(t => `"${t}"`).join(', ')}]
type: mental-model
---

# ${idea.title}
> *"${idea.one_liner}"* — **${idea.author}** (*${idea.source}*)

## 1. Summary
${idea.summary}

## 2. First-Principles Mechanics & Detailed Treatise
${idea.detailed_explanation || idea.summary}

## 3. Real-World Case Study
${idea.example || 'Applied across strategic planning and system architecture.'}

## 4. Visual Causal Architecture
\`\`\`mermaid
${idea.visual_diagram || 'graph LR\n  A[Challenge] --> B[Model Application] --> C[Robust Outcome]'}
\`\`\`

## 5. Daily Action Item
- ${idea.action_item || 'Integrate this model into decision logs today.'}

---
*${idea.copyright_notice || ''}*
`;

  const blob = new Blob([md], { type: 'text/markdown;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${(idea.title || 'mental-model').toLowerCase().replace(/[^a-z0-9]+/g, '-')}.md`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

// 4. Deck Navigation Controls
function prevCard() {
  const ideas = window.state.ideas || [];
  if (!ideas.length) return;
  window.state.currentIdeaIndex = (window.state.currentIdeaIndex - 1 + ideas.length) % ideas.length;
  updateStitchHeroCard();
}

function nextCard() {
  const ideas = window.state.ideas || [];
  if (!ideas.length) return;
  window.state.currentIdeaIndex = (window.state.currentIdeaIndex + 1) % ideas.length;
  updateStitchHeroCard();
}

function jumpToSwipeCard(target) {
  if (typeof target === 'string') {
    const idx = (window.state.ideas || []).findIndex(i => String(i.id) === String(target));
    if (idx !== -1) {
      window.state.currentIdeaIndex = idx;
    }
  } else if (typeof target === 'number') {
    window.state.currentIdeaIndex = target;
  }
  updateStitchHeroCard();
  switchTab('swipe');
}

// 5. Topic Filter & Chip State
function filterByTopic(topic) {
  window.state.selectedTopic = topic;
  window.state.currentIdeaIndex = 0;
  
  document.querySelectorAll(".topic-chip, .topic-pill").forEach(chip => {
    const text = chip.textContent.trim().toLowerCase();
    const isMatch = (topic.toLowerCase() === 'all' && text.includes('all')) || 
                    (topic.toLowerCase() === 'leitner-workout' && text.includes('workout')) ||
                    text === topic.toLowerCase();
    if (isMatch) {
      chip.className = "topic-chip px-3.5 py-1.5 rounded-full bg-primary/20 text-primary border border-primary/50 text-xs font-bold whitespace-nowrap transition flex items-center gap-1 shadow-sm";
    } else {
      chip.className = "topic-chip px-3.5 py-1.5 rounded-full bg-surface-container-high/50 text-on-surface-variant hover:text-white border border-outline-variant/30 text-xs font-medium whitespace-nowrap transition flex items-center gap-1";
    }
  });

  loadIdeas();
}

// 6. Global Library Cards Feed Renderer
function renderFeedGrid() {
  const container = document.getElementById("feed-grid-container") || document.getElementById("feed-grid");
  if (!container) return;

  const ideas = window.state.ideas || [];
  const feedBadge = document.getElementById("feed-count-badge");
  if (feedBadge) feedBadge.textContent = `${ideas.length} Models`;

  if (!ideas.length) {
    container.innerHTML = `
      <div class="col-span-full py-12 text-center text-on-surface-variant">
        <span class="material-symbols-outlined text-4xl opacity-40 mb-2">inbox</span>
        <p class="text-sm font-semibold text-white">No mental model cards match this filter</p>
        <p class="text-xs text-on-surface-variant mt-1">Try selecting 'All Models' or enter a search query.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = ideas.map((idea, index) => {
    return `
      <div class="tactile-glass p-4 sm:p-5 rounded-2xl border border-outline-variant/30 hover:border-primary/50 transition-all duration-200 flex flex-col justify-between group shadow-lg">
        <div>
          <div class="flex items-center justify-between gap-1 mb-2">
            <span class="px-2.5 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-wider bg-primary/15 text-primary border border-primary/30">
              ${idea.topic}
            </span>
            <span class="text-[10px] text-on-surface-variant font-medium flex items-center gap-0.5">
              <span class="material-symbols-outlined text-[13px]">timer</span>
              ${idea.read_time_mins || 1} min
            </span>
          </div>

          <h4 class="text-sm sm:text-base font-headline font-bold text-white group-hover:text-primary transition-colors mb-1">
            ${idea.title}
          </h4>

          <p class="text-[11px] text-primary/90 font-medium italic mb-2 line-clamp-2">
            "${idea.one_liner}"
          </p>

          <p class="text-xs text-on-surface-variant leading-relaxed line-clamp-3 mb-3">
            ${idea.summary}
          </p>
        </div>

        <div class="pt-3 border-t border-outline-variant/20 flex items-center justify-between gap-2">
          <div class="text-[10px] text-on-surface-variant truncate max-w-[110px]">
            <span class="text-white font-semibold block truncate">${idea.author}</span>
            <span class="truncate block text-on-surface-variant/70">${idea.source}</span>
          </div>

          <div class="flex items-center gap-1.5 flex-shrink-0">
            <button onclick="openStressTestModal('${idea.id}')" class="p-1.5 rounded-xl bg-secondary/15 hover:bg-secondary/25 text-secondary border border-secondary/30 transition text-[11px] font-bold flex items-center gap-1" title="Socratic Dilemma Arena">
              <span class="material-symbols-outlined text-[14px]">bolt</span>
              <span class="hidden sm:inline">Stress-Test</span>
            </button>
            <button onclick="openDeepDiveModal('${idea.id}')" class="p-1.5 rounded-xl bg-primary/15 hover:bg-primary/25 text-primary border border-primary/30 transition text-[11px] font-bold flex items-center gap-1" title="Detailed First Principles Treatise">
              <span class="material-symbols-outlined text-[14px]">menu_book</span>
              <span>Deep Dive</span>
            </button>
            <button onclick="jumpToSwipeCard('${idea.id}')" class="p-1.5 rounded-xl bg-surface-container-high hover:bg-surface-container-highest text-on-surface transition text-[11px] font-bold flex items-center" title="Study in Gym">
              <span class="material-symbols-outlined text-[14px]">explore</span>
            </button>
          </div>
        </div>
      </div>
    `;
  }).join('');
}

// Global window registrations
window.setDeepDiveSlide = setDeepDiveSlide;
window.closeDeepDiveModal = closeDeepDiveModal;
window.openDeepDiveModal = openDeepDiveModal;
window.openStressTestModal = openStressTestModal;
window.handleStressChoice = handleStressChoice;
window.closeStressTestModal = closeStressTestModal;
window.toggleCardAudio = toggleCardAudio;
window.exportCurrentCardMarkdown = exportCurrentCardMarkdown;
window.nextCard = nextCard;
window.prevCard = prevCard;
window.jumpToSwipeCard = jumpToSwipeCard;
window.filterByTopic = filterByTopic;
window.renderFeedGrid = renderFeedGrid;
