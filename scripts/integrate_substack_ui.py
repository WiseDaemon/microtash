"""
Substack Frontend Integration Script
Injects Substack Notes, Substack Reader, Restacks, Subscriptions, and Discussions
into index.html and app.js.
"""
import re

def update_index_html():
    path = "c:/LLM/deepstash_microlearning/app/templates/index.html"
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Top bar: add Substack Notes button next to Blindspot Quiz
    target_top = """          <!-- Blindspot Quiz Pill -->
          <button onclick="openOnboardingQuiz()" class="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-surface-container-high/80 border border-primary/40 text-xs font-bold text-primary hover:bg-primary/20 transition shadow-sm">
            <span class="material-symbols-outlined text-[16px]">target</span>
            <span>Blindspot Quiz</span>
          </button>"""
    
    replacement_top = """          <!-- Substack Notes Header Pill -->
          <button onclick="switchTab('notes')" class="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-[#ff6719]/15 border border-[#ff6719]/40 text-xs font-bold text-[#ff6719] hover:bg-[#ff6719]/25 transition shadow-sm relative">
            <span class="material-symbols-outlined text-[16px]">edit_note</span>
            <span>Notes</span>
            <span class="w-1.5 h-1.5 rounded-full bg-[#ff6719] animate-pulse"></span>
          </button>

          <!-- Blindspot Quiz Pill -->
          <button onclick="openOnboardingQuiz()" class="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-surface-container-high/80 border border-primary/40 text-xs font-bold text-primary hover:bg-primary/20 transition shadow-sm">
            <span class="material-symbols-outlined text-[16px]">target</span>
            <span>Blindspot Quiz</span>
          </button>"""
    if target_top in html:
        html = html.replace(target_top, replacement_top, 1)
        print("[OK] Top bar updated with Substack Notes pill.")

    # 2. Add tab-notes-content section before bottom nav
    target_nav = """    <!-- ===================================================================== -->
    <!-- 6. STITCH BOTTOM NAVIGATION BAR                                      -->
    <!-- ===================================================================== -->"""

    notes_section = """    <!-- ===================================================================== -->
    <!-- TAB 6: SUBSTACK NOTES & INTELLECTUAL STREAM                              -->
    <!-- ===================================================================== -->
    <section id="tab-notes-content" class="hidden flex-1 px-4 sm:px-5 pt-3 pb-8 space-y-4">
      <!-- Substack Header & Publications -->
      <div class="p-4 rounded-3xl bg-gradient-to-r from-surface-container via-surface-container-high to-surface-container border border-outline-variant/30 space-y-3">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2.5">
            <div class="w-9 h-9 rounded-full bg-[#ff6719]/20 border border-[#ff6719]/40 flex items-center justify-center text-[#ff6719] shadow-inner font-bold text-xs">
              <span class="material-symbols-outlined text-[20px]">edit_note</span>
            </div>
            <div>
              <div class="flex items-center gap-1.5">
                <h3 class="text-sm font-headline font-bold text-white tracking-wide">SUBSTACK NOTES</h3>
                <span class="px-2 py-0.5 rounded-full text-[9px] font-bold bg-[#ff6719] text-white">STREAM</span>
              </div>
              <p class="text-[10px] text-on-surface-variant font-medium">Atomic insights, mental model restacks & thinker dispatches</p>
            </div>
          </div>
          <button onclick="loadSubstackNotes()" class="w-7 h-7 rounded-full bg-surface-container-highest border border-outline-variant/40 flex items-center justify-center text-on-surface-variant hover:text-white transition" title="Refresh Notes">
            <span class="material-symbols-outlined text-[15px]">refresh</span>
          </button>
        </div>

        <!-- Featured Publications Carousel -->
        <div>
          <span class="text-[10px] uppercase font-bold text-on-surface-variant tracking-wider">Top Thinkers & Publications</span>
          <div id="substack-pubs-carousel" class="flex items-center gap-2.5 overflow-x-auto custom-scrollbar pt-2 pb-1 select-none">
            <!-- Publications loaded dynamically -->
          </div>
        </div>
      </div>

      <!-- Note Composer Card -->
      <div class="p-3.5 rounded-2xl bg-surface-container-low border border-outline-variant/30 space-y-2.5">
        <div class="flex items-start gap-2.5">
          <div class="w-8 h-8 rounded-full bg-primary/20 border border-primary/40 flex items-center justify-center text-primary font-bold text-xs shrink-0 mt-0.5">
            <span class="material-symbols-outlined text-[16px]">person</span>
          </div>
          <textarea id="note-compose-content" rows="2" placeholder="What's on your mind? Share an atomic insight, quote or mental model reflection..." class="w-full bg-surface-container/60 border border-outline-variant/40 rounded-xl p-2.5 text-xs text-white placeholder-on-surface-variant/60 focus:outline-none focus:border-[#ff6719] resize-none leading-relaxed custom-scrollbar"></textarea>
        </div>
        <div class="flex items-center justify-between pt-1 border-t border-outline-variant/20">
          <div class="flex items-center gap-2 text-on-surface-variant text-[11px]">
            <button onclick="switchTab('swipe')" class="hover:text-primary transition flex items-center gap-1">
              <span class="material-symbols-outlined text-[14px]">psychology</span>
              <span>Quote a Model</span>
            </button>
          </div>
          <button onclick="handleCreateSubstackNote()" class="px-4 py-1.5 rounded-xl bg-[#ff6719] hover:bg-[#e55913] text-white text-xs font-headline font-bold shadow-md transition flex items-center gap-1.5">
            <span>Post Note</span>
            <span class="material-symbols-outlined text-[14px]">send</span>
          </button>
        </div>
      </div>

      <!-- Stream of Notes -->
      <div id="substack-notes-list" class="space-y-3">
        <!-- Notes loaded dynamically -->
      </div>
    </section>

"""
    if target_nav in html:
        html = html.replace(target_nav, notes_section + target_nav, 1)
        print("[OK] tab-notes-content inserted.")

    # 3. Bottom nav: add Notes button
    target_bottom_nav = """      <!-- Nav 1: Feed (Active) -->
      <button onclick="switchTab('swipe')" id="stitch-nav-swipe" class="flex flex-col items-center justify-center bg-primary/15 text-primary rounded-full px-4 py-1.5 shadow-[0_0_12px_rgba(56,189,248,0.25)] transition">
        <span class="material-symbols-outlined text-[20px]" style="font-variation-settings: 'FILL' 1;">explore</span>
        <span class="text-[10px] font-headline font-bold">Gym Feed</span>
      </button>

      <!-- Nav 2: Bookshelf / Library -->"""

    replacement_bottom_nav = """      <!-- Nav 1: Feed (Active) -->
      <button onclick="switchTab('swipe')" id="stitch-nav-swipe" class="flex flex-col items-center justify-center bg-primary/15 text-primary rounded-full px-3 py-1 shadow-[0_0_12px_rgba(56,189,248,0.25)] transition">
        <span class="material-symbols-outlined text-[19px]" style="font-variation-settings: 'FILL' 1;">explore</span>
        <span class="text-[9px] font-headline font-bold">Gym Feed</span>
      </button>

      <!-- Nav 2: Substack Notes -->
      <button onclick="switchTab('notes')" id="stitch-nav-notes" class="flex flex-col items-center justify-center text-on-surface-variant hover:text-[#ff6719] transition px-2.5 py-1 relative">
        <span class="material-symbols-outlined text-[19px]">edit_note</span>
        <span class="text-[9px] font-headline font-medium">Notes</span>
        <span class="absolute top-1 right-2 w-1.5 h-1.5 rounded-full bg-[#ff6719] animate-pulse"></span>
      </button>

      <!-- Nav 3: Bookshelf / Library -->"""

    if target_bottom_nav in html:
        html = html.replace(target_bottom_nav, replacement_bottom_nav, 1)
        print("[OK] Bottom navigation bar updated with Notes button.")

    # 4. Deep Dive Modal Pills: Add 5th Substack Reader pill
    target_pills = """        <button onclick="setDeepDiveSlide(4)" id="pill-slide-4" class="flex-1 min-w-[75px] py-1.5 px-2.5 rounded-full text-[11px] font-medium text-secondary bg-surface-container border border-secondary/30 transition text-center hover:text-white flex items-center justify-center gap-1">
          <span class="material-symbols-outlined text-[13px]">menu_book</span>
          <span>Full Treatise</span>
        </button>
      </div>"""

    replacement_pills = """        <button onclick="setDeepDiveSlide(4)" id="pill-slide-4" class="flex-1 min-w-[70px] py-1.5 px-2 rounded-full text-[11px] font-medium text-secondary bg-surface-container border border-secondary/30 transition text-center hover:text-white flex items-center justify-center gap-1">
          <span class="material-symbols-outlined text-[13px]">menu_book</span>
          <span>Full Treatise</span>
        </button>
        <button onclick="setDeepDiveSlide(5)" id="pill-slide-5" class="flex-1 min-w-[75px] py-1.5 px-2 rounded-full text-[11px] font-bold text-[#ff6719] bg-[#ff6719]/15 border border-[#ff6719]/40 transition text-center hover:bg-[#ff6719]/25 flex items-center justify-center gap-1 shadow-sm">
          <span class="material-symbols-outlined text-[13px]">article</span>
          <span>Substack Reader</span>
        </button>
      </div>"""

    if target_pills in html:
        html = html.replace(target_pills, replacement_pills, 1)
        print("[OK] Deep Dive modal updated with Substack Reader 5th pill.")

    # 5. Deep Dive Modal Header: Add Restack button
    target_modal_header_btns = """          <button onclick="exportDeepDiveCheatSheet()" class="w-8 h-8 rounded-full bg-surface-container border border-outline-variant/40 flex items-center justify-center text-on-surface-variant hover:text-primary transition" title="Export Cheat Sheet">
            <span class="material-symbols-outlined text-[16px]">download</span>
          </button>
          <button onclick="closeDeepDiveModal()" class="w-8 h-8 rounded-full bg-surface-container border border-outline-variant/40 flex items-center justify-center text-on-surface-variant hover:text-white transition">"""

    replacement_modal_header_btns = """          <button onclick="openRestackModal(currentDeepDiveIdea ? currentDeepDiveIdea.id : null)" class="px-2.5 py-1 rounded-full bg-[#ff6719]/15 hover:bg-[#ff6719] text-[#ff6719] hover:text-white border border-[#ff6719]/30 text-[11px] font-bold transition flex items-center gap-1" title="Restack to Substack Notes">
            <span class="material-symbols-outlined text-[15px]">repeat</span>
            <span>Restack</span>
          </button>
          <button onclick="exportDeepDiveCheatSheet()" class="w-8 h-8 rounded-full bg-surface-container border border-outline-variant/40 flex items-center justify-center text-on-surface-variant hover:text-primary transition" title="Export Cheat Sheet">
            <span class="material-symbols-outlined text-[16px]">download</span>
          </button>
          <button onclick="closeDeepDiveModal()" class="w-8 h-8 rounded-full bg-surface-container border border-outline-variant/40 flex items-center justify-center text-on-surface-variant hover:text-white transition">"""

    if target_modal_header_btns in html:
        html = html.replace(target_modal_header_btns, replacement_modal_header_btns, 1)
        print("[OK] Deep Dive modal header updated with Restack button.")

    # 6. Deep Dive Modal: Add Slide 5 (Substack Reader Mode) + Discussions section
    slide_5_content = """
        <!-- SLIDE 5: SUBSTACK READER & PUBLICATION MODE -->
        <div id="modal-slide-5" class="hidden space-y-6">
          <!-- Substack Publication Masthead -->
          <div class="p-5 rounded-3xl bg-surface-container-lowest border border-outline-variant/30 space-y-3.5">
            <div class="flex items-center justify-between border-b border-outline-variant/20 pb-3">
              <div>
                <span class="text-[10px] font-headline font-extrabold uppercase tracking-widest text-[#ff6719]">THE MENTAL MODEL REVIEW</span>
                <h3 id="reader-title" class="text-xl sm:text-2xl font-serif font-bold text-white mt-1"></h3>
              </div>
              <button id="reader-subscribe-btn" onclick="handleReaderSubscribe()" class="px-4 py-1.5 rounded-full text-xs font-headline font-bold text-white bg-[#ff6719] hover:bg-[#e55913] shadow-md transition flex items-center gap-1.5 shrink-0">
                <span class="material-symbols-outlined text-[14px]">notifications_active</span>
                <span>Subscribe</span>
              </button>
            </div>

            <!-- Author byline & Read Time -->
            <div class="flex items-center justify-between text-xs text-on-surface-variant">
              <div class="flex items-center gap-2">
                <div class="w-7 h-7 rounded-full bg-[#ff6719]/20 text-[#ff6719] flex items-center justify-center font-bold text-xs">
                  <span class="material-symbols-outlined text-[15px]">person</span>
                </div>
                <div>
                  <span id="reader-author" class="font-bold text-slate-200"></span>
                  <span class="text-on-surface-variant/60">• <span id="reader-source"></span></span>
                </div>
              </div>
              <span id="reader-time" class="font-mono text-[11px] text-secondary">3 min read</span>
            </div>

            <!-- Substack Audio Voiceover Player Bar -->
            <div class="p-3 rounded-2xl bg-surface-container/70 border border-outline-variant/30 flex items-center justify-between gap-3">
              <div class="flex items-center gap-2.5">
                <button onclick="toggleSpeechAudio()" class="w-8 h-8 rounded-full bg-[#ff6719] text-white flex items-center justify-center shadow-md hover:scale-105 transition">
                  <span class="material-symbols-outlined text-[18px]">play_arrow</span>
                </button>
                <div>
                  <span class="text-xs font-bold text-white block">Listen to Essay</span>
                  <span class="text-[10px] text-on-surface-variant">Substack Voiceover Edition</span>
                </div>
              </div>
              <div class="flex items-center gap-1 text-[11px] font-mono text-[#ff6719] bg-[#ff6719]/10 px-2 py-0.5 rounded-full">
                <span>1.0x</span>
              </div>
            </div>
          </div>

          <!-- Editorial Serif Body -->
          <div class="p-6 rounded-3xl bg-surface-container-lowest/90 border border-outline-variant/30 space-y-4 font-serif text-[14px] sm:text-[15px] leading-relaxed text-slate-100">
            <!-- Pull Quote in Substack Styling -->
            <div class="border-l-4 border-[#ff6719] bg-surface-container-low/70 p-4 rounded-r-2xl my-3">
              <p id="reader-pullquote" class="text-sm sm:text-base font-serif italic text-slate-200 leading-snug"></p>
            </div>

            <div id="reader-detailed" class="space-y-3 font-sans text-xs sm:text-sm"></div>

            <!-- Real-World Case Study -->
            <div class="pt-4 border-t border-outline-variant/20">
              <h4 class="font-headline font-bold text-xs text-[#ff6719] uppercase tracking-wider mb-2 font-sans flex items-center gap-1.5">
                <span class="material-symbols-outlined text-[16px]">history_edu</span>
                <span>Case Analysis</span>
              </h4>
              <div id="reader-example" class="font-sans text-xs sm:text-sm space-y-2 text-slate-300"></div>
            </div>

            <!-- Boundaries & Execution -->
            <div class="p-3.5 rounded-2xl bg-surface-container/60 border border-outline-variant/30 space-y-1.5 font-sans">
              <span class="text-[11px] font-bold text-error uppercase tracking-wider flex items-center gap-1">
                <span class="material-symbols-outlined text-[14px]">dangerous</span>
                <span>Falsification Boundary</span>
              </span>
              <p id="reader-boundary" class="text-xs text-slate-300"></p>
            </div>
          </div>

          <!-- Threaded Community Discussion Section -->
          <div class="p-5 rounded-3xl bg-surface-container-lowest border border-outline-variant/30 space-y-4">
            <div class="flex items-center justify-between border-b border-outline-variant/20 pb-2.5">
              <div class="flex items-center gap-2">
                <span class="material-symbols-outlined text-[18px] text-[#ff6719]">chat</span>
                <h4 class="text-sm font-headline font-bold text-white">Discussion (<span id="modal-discussion-count">0</span>)</h4>
              </div>
              <span class="text-[10px] text-on-surface-variant font-medium">Substack Community</span>
            </div>

            <!-- Comment Input -->
            <div class="space-y-2">
              <textarea id="modal-new-comment-input" rows="2" placeholder="Write a response or share how you apply this mental model..." class="w-full bg-surface-container/60 border border-outline-variant/40 rounded-xl p-2.5 text-xs text-white placeholder-on-surface-variant/60 focus:outline-none focus:border-[#ff6719] resize-none leading-relaxed custom-scrollbar"></textarea>
              <div class="flex justify-end">
                <button onclick="handlePostComment()" class="px-4 py-1.5 rounded-xl bg-[#ff6719] hover:bg-[#e55913] text-white text-xs font-headline font-bold shadow-md transition flex items-center gap-1">
                  <span>Comment</span>
                  <span class="material-symbols-outlined text-[14px]">send</span>
                </button>
              </div>
            </div>

            <!-- Comments List -->
            <div id="modal-comments-list" class="space-y-2.5 pt-1">
              <!-- Loaded dynamically -->
            </div>
          </div>
        </div>
"""

    target_slide_4_end = """        <!-- SLIDE 4: FULL UNIFIED MASTERCLASS TREATISE -->"""
    if target_slide_4_end in html:
        # Also inject comments container inside Slide 4 before the copyright notice
        slide_4_comments = """
          <!-- Discussion in Full Treatise -->
          <div class="p-4 rounded-2xl bg-surface-container-lowest/80 border border-outline-variant/30 space-y-3">
            <h4 class="text-xs font-bold text-[#ff6719] uppercase tracking-wider flex items-center gap-1.5">
              <span class="material-symbols-outlined text-[16px]">forum</span>
              <span>Community Discussion & Applications</span>
            </h4>
            <div class="space-y-2">
              <button onclick="setDeepDiveSlide(5)" class="text-xs font-bold text-[#ff6719] hover:underline flex items-center gap-1">
                <span>View all discussions & join the conversation in Substack Reader</span>
                <span class="material-symbols-outlined text-[14px]">arrow_forward</span>
              </button>
            </div>
          </div>
"""
        target_copyright = """        <!-- Author, Publisher & Transformative Copyright Credit Footer -->"""
        html = html.replace(target_copyright, slide_4_comments + "\n" + slide_5_content + "\n" + target_copyright, 1)
        print("[OK] Slide 5 (Substack Reader Mode) & Discussions injected into Deep Dive modal.")

    # 7. Add Quote Restack Modal
    restack_modal = """
  <!-- ========================================================================= -->
  <!-- MODAL: SUBSTACK QUOTE RESTACK                                             -->
  <!-- ========================================================================= -->
  <div id="restack-modal" class="hidden fixed inset-0 z-50 bg-black/85 backdrop-blur-md flex items-center justify-center p-4">
    <div class="bg-surface border border-[#ff6719]/40 rounded-3xl max-w-lg w-full shadow-2xl flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-200">
      <div class="p-4 bg-surface-container-high border-b border-outline-variant/30 flex items-center justify-between">
        <div class="flex items-center gap-2">
          <span class="material-symbols-outlined text-[20px] text-[#ff6719]">repeat</span>
          <h3 class="text-sm font-headline font-bold text-white">Restack with your thought</h3>
        </div>
        <button onclick="closeRestackModal()" class="w-7 h-7 rounded-full bg-surface-container border border-outline-variant/40 flex items-center justify-center text-on-surface-variant hover:text-white transition">
          <span class="material-symbols-outlined text-[16px]">close</span>
        </button>
      </div>

      <div class="p-5 space-y-4">
        <!-- Quoted Preview -->
        <div class="p-3.5 rounded-2xl bg-surface-container-low border-l-4 border-[#ff6719] border-outline-variant/30 space-y-1">
          <div class="flex items-center justify-between">
            <span id="restack-preview-title" class="text-xs font-bold text-white">The Inversion Principle</span>
            <span id="restack-preview-author" class="text-[10px] text-on-surface-variant font-mono">Charlie Munger</span>
          </div>
          <p id="restack-preview-quote" class="text-xs text-slate-300 italic font-serif leading-snug">"Invert, always invert..."</p>
        </div>

        <div>
          <label class="block text-[11px] font-bold text-on-surface-variant uppercase tracking-wider mb-1.5">Add Your Reflection (Optional)</label>
          <textarea id="restack-comment-input" rows="3" placeholder="Why does this mental model matter? How did you apply it in your life or company?" class="w-full bg-surface-container-low border border-outline-variant/40 rounded-xl p-3 text-xs text-white placeholder-on-surface-variant/60 focus:outline-none focus:border-[#ff6719] resize-none leading-relaxed custom-scrollbar"></textarea>
        </div>

        <div class="flex items-center justify-end gap-2 pt-2">
          <button onclick="closeRestackModal()" class="px-4 py-2 rounded-xl text-xs font-bold text-on-surface-variant hover:text-white transition">
            Cancel
          </button>
          <button onclick="submitRestack()" class="px-5 py-2 rounded-xl bg-[#ff6719] hover:bg-[#e55913] text-white text-xs font-headline font-bold shadow-lg transition flex items-center gap-1.5">
            <span class="material-symbols-outlined text-[16px]">repeat</span>
            <span>Restack Note</span>
          </button>
        </div>
      </div>
    </div>
  </div>
"""
    target_body_end = """  <!-- Core JavaScript Controllers -->"""
    if target_body_end in html:
        html = html.replace(target_body_end, restack_modal + "\n" + target_body_end, 1)
        print("[OK] restack-modal injected.")

    # 8. Script tag for substack.js
    target_scripts = """  <script src="/static/js/social.js?v=1.0"></script>"""
    replacement_scripts = """  <script src="/static/js/social.js?v=1.0"></script>
  <script src="/static/js/substack.js?v=1.0"></script>"""
    if target_scripts in html:
        html = html.replace(target_scripts, replacement_scripts, 1)
        print("[OK] substack.js script tag injected.")

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print("[SUCCESS] index.html updated successfully!")

def update_app_js():
    path = "c:/LLM/deepstash_microlearning/app/static/js/app.js"
    with open(path, "r", encoding="utf-8") as f:
        js = f.read()

    # 1. Update switchTab in app.js to handle 'notes'
    old_switch = """  const swipeTab = document.getElementById("tab-swipe-content");
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

  if (tabId === "leitner") renderWorkoutCard();"""

    new_switch = """  const swipeTab = document.getElementById("tab-swipe-content");
  const notesTab = document.getElementById("tab-notes-content");
  const leitnerTab = document.getElementById("tab-leitner-content");
  const feedTab = document.getElementById("tab-feed-content");
  const stashesTab = document.getElementById("tab-stashes-content");
  const aiTab = document.getElementById("tab-ai-content");

  if (swipeTab) swipeTab.classList.toggle("hidden", tabId !== "swipe");
  if (notesTab) notesTab.classList.toggle("hidden", tabId !== "notes");
  if (leitnerTab) leitnerTab.classList.toggle("hidden", tabId !== "leitner");
  if (feedTab) feedTab.classList.toggle("hidden", tabId !== "feed");
  if (stashesTab) stashesTab.classList.toggle("hidden", tabId !== "stashes");
  if (aiTab) aiTab.classList.toggle("hidden", tabId !== "ai");

  // Stitch bottom nav active state
  ["swipe", "notes", "leitner", "feed", "stashes", "ai"].forEach(t => {
    const btn = document.getElementById(`stitch-nav-${t}`);
    if (btn) {
      if (t === tabId) {
        btn.className = "flex flex-col items-center justify-center bg-primary/15 text-primary rounded-full px-3 py-1 shadow-[0_0_12px_rgba(78,222,163,0.25)] transition";
      } else {
        btn.className = "flex flex-col items-center justify-center text-on-surface-variant hover:text-primary transition px-2.5 py-1";
      }
    }
  });

  if (tabId === "leitner") renderWorkoutCard();
  if (tabId === "notes") {
    if (window.loadSubstackNotes) window.loadSubstackNotes();
    if (window.loadPublicationsCarousel) window.loadPublicationsCarousel();
  }"""

    if old_switch in js:
        js = js.replace(old_switch, new_switch, 1)
        print("[OK] app.js switchTab updated.")

    # 2. Update setDeepDiveSlide to handle [1, 2, 3, 4, 5]
    old_slides = """function setDeepDiveSlide(slideNum) {
  [1, 2, 3, 4].forEach(n => {
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
        pill.className = "flex-1 min-w-[75px] py-1.5 px-2.5 rounded-full text-[11px] font-bold text-primary bg-primary/20 border border-primary/50 transition text-center shadow-sm flex items-center justify-center gap-1";
      } else {
        pill.className = "flex-1 min-w-[75px] py-1.5 px-2.5 rounded-full text-[11px] font-medium text-on-surface-variant bg-surface-container border border-outline-variant/30 transition text-center hover:text-white flex items-center justify-center gap-1";
      }
    }
  });
}"""

    new_slides = """function setDeepDiveSlide(slideNum) {
  [1, 2, 3, 4, 5].forEach(n => {
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
        if (n === 5) {
          pill.className = "flex-1 min-w-[75px] py-1.5 px-2 rounded-full text-[11px] font-bold text-white bg-[#ff6719] border border-[#ff6719] transition text-center shadow-md flex items-center justify-center gap-1";
        } else {
          pill.className = "flex-1 min-w-[70px] py-1.5 px-2 rounded-full text-[11px] font-bold text-primary bg-primary/20 border border-primary/50 transition text-center shadow-sm flex items-center justify-center gap-1";
        }
      } else {
        if (n === 5) {
          pill.className = "flex-1 min-w-[75px] py-1.5 px-2 rounded-full text-[11px] font-bold text-[#ff6719] bg-[#ff6719]/15 border border-[#ff6719]/40 transition text-center hover:bg-[#ff6719]/25 flex items-center justify-center gap-1";
        } else {
          pill.className = "flex-1 min-w-[70px] py-1.5 px-2 rounded-full text-[11px] font-medium text-on-surface-variant bg-surface-container border border-outline-variant/30 transition text-center hover:text-white flex items-center justify-center gap-1";
        }
      }
    }
  });
}"""

    if old_slides in js:
        js = js.replace(old_slides, new_slides, 1)
        print("[OK] app.js setDeepDiveSlide updated to 5 slides.")

    # 3. In openDeepDiveModal: populate Slide 5 (Substack Reader Mode) & discussions
    old_modal_tail = """  const fullActEl = document.getElementById("modal-full-action");
  if (fullActEl) {
    fullActEl.innerHTML = renderMarkdownDetailed(idea.action_item || "Apply this model to one difficult decision today.");
  }

  const cNoticeEl = document.getElementById("modal-copyright-notice");
  if (cNoticeEl) {
    cNoticeEl.textContent = idea.copyright_notice || `Transformative educational commentary & mental model summary of '${idea.source}' by ${idea.author}. All original copyrights remain with the author and publisher under Fair Use.`;
  }

  // Reset to Slide 1
  setDeepDiveSlide(1);"""

    new_modal_tail = """  const fullActEl = document.getElementById("modal-full-action");
  if (fullActEl) {
    fullActEl.innerHTML = renderMarkdownDetailed(idea.action_item || "Apply this model to one difficult decision today.");
  }

  // Slide 5: Substack Reader & Publication Mode Population
  const readerTitleEl = document.getElementById("reader-title");
  if (readerTitleEl) readerTitleEl.textContent = idea.title;

  const readerAuthorEl = document.getElementById("reader-author");
  if (readerAuthorEl) readerAuthorEl.textContent = idea.author;

  const readerSourceEl = document.getElementById("reader-source");
  if (readerSourceEl) readerSourceEl.textContent = idea.source;

  const readerTimeEl = document.getElementById("reader-time");
  if (readerTimeEl) readerTimeEl.textContent = `${idea.read_time_mins || 3} min read`;

  const readerPullquoteEl = document.getElementById("reader-pullquote");
  if (readerPullquoteEl) readerPullquoteEl.textContent = `“${(idea.quote || idea.one_liner).replace(/^[“"]|[”"]$/g, '')}”`;

  const readerDetailedEl = document.getElementById("reader-detailed");
  if (readerDetailedEl) readerDetailedEl.innerHTML = renderMarkdownDetailed(idea.detailed_explanation || idea.summary);

  const readerExampleEl = document.getElementById("reader-example");
  if (readerExampleEl) readerExampleEl.innerHTML = renderMarkdownDetailed(idea.example || "Empirical case analysis.");

  const readerBoundaryEl = document.getElementById("reader-boundary");
  if (readerBoundaryEl) readerBoundaryEl.textContent = idea.boundary || "Apply with critical discernment.";

  // Load Substack Community Discussions for this Idea
  if (window.loadIdeaComments) {
    window.loadIdeaComments(idea.id);
  }

  const cNoticeEl = document.getElementById("modal-copyright-notice");
  if (cNoticeEl) {
    cNoticeEl.textContent = idea.copyright_notice || `Transformative educational commentary & mental model summary of '${idea.source}' by ${idea.author}. All original copyrights remain with the author and publisher under Fair Use.`;
  }

  // Reset to Slide 1
  setDeepDiveSlide(1);"""

    if old_modal_tail in js:
        js = js.replace(old_modal_tail, new_modal_tail, 1)
        print("[OK] app.js openDeepDiveModal updated with Substack Reader population.")

    with open(path, "w", encoding="utf-8") as f:
        f.write(js)
    print("[SUCCESS] app.js updated successfully!")

if __name__ == "__main__":
    update_index_html()
    update_app_js()
