/**
 * Substack Ecosystem Controller for Microstash
 * Powers Substack Notes stream, Quote Restacks, Substack Reader mode,
 * Author/Publication Subscriptions, and Threaded Community Discussions.
 */

window.currentRestackIdeaId = null;
window.currentSubstackFilter = 'all';

// --- Format Time Ago ---
function formatSubstackTimeAgo(isoString) {
  if (!isoString) return "just now";
  const date = new Date(isoString);
  const now = new Date();
  const diffSecs = Math.max(1, Math.floor((now - date) / 1000));
  if (diffSecs < 60) return `${diffSecs}s ago`;
  const diffMins = Math.floor(diffSecs / 60);
  if (diffMins < 60) return `${diffMins}m ago`;
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays}d ago`;
}

// =========================================================================
// 1. SUBSTACK NOTES STREAM
// =========================================================================

async function loadSubstackNotes() {
  const container = document.getElementById("substack-notes-list");
  if (!container) return;

  try {
    const res = await fetch("/api/substack/notes");
    if (!res.ok) return;
    const notes = await res.json();
    renderSubstackNotes(notes);
  } catch (err) {
    console.error("Failed to load Substack notes:", err);
  }
}

function renderSubstackNotes(notes) {
  const container = document.getElementById("substack-notes-list");
  if (!container) return;

  if (!notes || notes.length === 0) {
    container.innerHTML = `
      <div class="p-8 text-center bg-surface-container-low rounded-2xl border border-outline-variant/30 text-on-surface-variant">
        <span class="material-symbols-outlined text-4xl text-[#ff6719] mb-2">edit_note</span>
        <h4 class="font-headline font-bold text-white text-sm">No Notes Yet</h4>
        <p class="text-xs text-on-surface-variant/80 mt-1">Be the first to share an insight or restack a mental model!</p>
      </div>
    `;
    return;
  }

  container.innerHTML = notes.map(note => {
    const avatar = note.author_avatar || `https://api.dicebear.com/7.x/initials/svg?seed=${encodeURIComponent(note.author_name)}`;
    const timeAgo = formatSubstackTimeAgo(note.created_at);
    const isLiked = !!note.is_liked;

    let quoteBlock = "";
    if (note.referenced_idea_id) {
      quoteBlock = `
        <div class="mt-3 p-3.5 rounded-xl bg-surface-container-highest/80 border-l-4 border-[#ff6719] border-outline-variant/30 transition hover:border-[#ff6719] cursor-pointer" onclick="openDeepDiveModal('${note.referenced_idea_id}')">
          <div class="flex items-center gap-1.5 text-[10px] uppercase font-bold text-[#ff6719] tracking-wider mb-1">
            <span class="material-symbols-outlined text-[13px]">psychology</span>
            <span>${note.referenced_idea_title || "Mental Model"}</span>
            <span class="text-on-surface-variant/50">• ${note.referenced_idea_author || "Curated"}</span>
          </div>
          <p class="text-xs text-slate-200 italic font-serif leading-snug">
            "${note.referenced_idea_quote || ''}"
          </p>
        </div>
      `;
    }

    let restackBadge = "";
    if (note.restack_comment) {
      restackBadge = `
        <div class="flex items-center gap-1.5 text-[11px] text-[#ff6719] font-medium mb-1.5">
          <span class="material-symbols-outlined text-[14px]">repeat</span>
          <span>Restacked with thought</span>
        </div>
      `;
    }

    return `
      <div class="p-4 rounded-2xl bg-surface-container-low border border-outline-variant/30 hover:border-outline-variant/60 transition shadow-sm space-y-2.5" id="note-card-${note.id}">
        ${restackBadge}
        <!-- Author Header -->
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2.5">
            <img src="${avatar}" alt="${note.author_name}" class="w-9 h-9 rounded-full object-cover border border-outline-variant/40 shadow-sm" />
            <div>
              <div class="flex items-center gap-1.5">
                <span class="font-headline font-bold text-xs text-white">${note.author_name}</span>
                <span class="text-[11px] text-on-surface-variant font-mono">@${note.author_handle}</span>
              </div>
              <span class="text-[10px] text-on-surface-variant/60">${timeAgo}</span>
            </div>
          </div>

          <!-- Substack Publication Follow Pill -->
          <button onclick="handleNoteAuthorSubscribe('${note.author_name}')" class="px-2.5 py-1 rounded-full text-[10px] font-bold text-[#ff6719] bg-[#ff6719]/10 hover:bg-[#ff6719]/20 border border-[#ff6719]/30 transition flex items-center gap-1">
            <span class="material-symbols-outlined text-[12px]">add</span>
            <span>Follow</span>
          </button>
        </div>

        <!-- Note Text Content -->
        <p class="text-xs sm:text-sm text-slate-100 leading-relaxed font-sans pt-1">
          ${note.restack_comment || note.content}
        </p>

        <!-- Quoted Idea Card if Restack -->
        ${quoteBlock}

        <!-- Actions Footer -->
        <div class="flex items-center justify-between pt-2 border-t border-outline-variant/20 text-on-surface-variant text-xs">
          <button onclick="handleLikeSubstackNote('${note.id}')" class="flex items-center gap-1.5 hover:text-rose-400 transition ${isLiked ? 'text-rose-500 font-bold' : ''}" id="note-like-btn-${note.id}">
            <span class="material-symbols-outlined text-[16px]" style="${isLiked ? 'font-variation-settings: \'FILL\' 1;' : ''}">favorite</span>
            <span id="note-likes-count-${note.id}">${note.likes_count}</span>
          </button>

          <button onclick="openRestackFromNote('${note.id}', '${escapeAttr(note.author_name)}', '${escapeAttr(note.content)}')" class="flex items-center gap-1.5 hover:text-[#ff6719] transition">
            <span class="material-symbols-outlined text-[16px]">repeat</span>
            <span>${note.restacks_count || 0}</span>
          </button>

          <button onclick="handleShareSubstackNote('${note.id}', '${escapeAttr(note.content)}')" class="flex items-center gap-1.5 hover:text-primary transition">
            <span class="material-symbols-outlined text-[16px]">share</span>
            <span>Share</span>
          </button>
        </div>
      </div>
    `;
  }).join('');
}

function escapeAttr(str) {
  if (!str) return "";
  return String(str).replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

async function handleCreateSubstackNote() {
  const inputEl = document.getElementById("note-compose-content");
  if (!inputEl) return;
  const content = inputEl.value.trim();
  if (!content) {
    if (window.showToast) window.showToast("Please enter a note before posting", "edit_note");
    return;
  }

  // Get current user display name if signed in
  const currentUser = window.currentAuthUser ? window.currentAuthUser.full_name || window.currentAuthUser.username : "Curated Learner";
  const currentHandle = window.currentAuthUser ? window.currentAuthUser.username : "learner";

  try {
    const res = await fetch("/api/substack/notes", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        content: content,
        author_name: currentUser,
        author_handle: currentHandle
      })
    });

    if (res.ok) {
      inputEl.value = "";
      if (window.showToast) window.showToast("Note published to Substack stream!", "check_circle");
      loadSubstackNotes();
    }
  } catch (err) {
    console.error("Failed to post note:", err);
  }
}

async function handleLikeSubstackNote(noteId) {
  const countEl = document.getElementById(`note-likes-count-${noteId}`);
  const btnEl = document.getElementById(`note-like-btn-${noteId}`);
  if (!btnEl) return;

  try {
    const res = await fetch(`/api/substack/notes/${noteId}/like`, { method: "POST" });
    if (res.ok) {
      const updated = await res.json();
      if (countEl) countEl.textContent = updated.likes_count;
      if (updated.is_liked) {
        btnEl.classList.add("text-rose-500", "font-bold");
        btnEl.querySelector(".material-symbols-outlined").style.fontVariationSettings = "'FILL' 1";
      } else {
        btnEl.classList.remove("text-rose-500", "font-bold");
        btnEl.querySelector(".material-symbols-outlined").style.fontVariationSettings = "";
      }
    }
  } catch (err) {
    console.error("Failed to toggle note like:", err);
  }
}

function handleShareSubstackNote(noteId, text) {
  const shareText = `"${text.substring(0, 140)}..." — Read more on Microstash Substack Notes`;
  if (navigator.share) {
    navigator.share({
      title: "Microstash Substack Note",
      text: shareText,
      url: window.location.href
    }).catch(() => {});
  } else {
    navigator.clipboard.writeText(`${shareText}\n${window.location.href}`);
    if (window.showToast) window.showToast("Note copied to clipboard!", "content_copy");
  }
}

// =========================================================================
// 2. QUOTE RESTACK SYSTEM
// =========================================================================

function openRestackModal(ideaId = null) {
  let idea = null;
  if (ideaId) {
    idea = (window.state.ideas || []).find(i => String(i.id) === String(ideaId));
  }
  if (!idea) {
    idea = (window.state.ideas || [])[window.state.currentIdeaIndex];
  }
  if (!idea) return;

  window.currentRestackIdeaId = idea.id;

  const modal = document.getElementById("restack-modal");
  if (!modal) return;

  const titleEl = document.getElementById("restack-preview-title");
  const authorEl = document.getElementById("restack-preview-author");
  const quoteEl = document.getElementById("restack-preview-quote");
  const inputEl = document.getElementById("restack-comment-input");

  if (titleEl) titleEl.textContent = idea.title;
  if (authorEl) authorEl.textContent = `${idea.author} • ${idea.source}`;
  if (quoteEl) quoteEl.textContent = `"${idea.quote || idea.one_liner}"`;
  if (inputEl) inputEl.value = "";

  modal.classList.remove("hidden");
  modal.classList.add("flex");
}

function closeRestackModal() {
  const modal = document.getElementById("restack-modal");
  if (modal) {
    modal.classList.add("hidden");
    modal.classList.remove("flex");
  }
}

async function submitRestack() {
  if (!window.currentRestackIdeaId) return;
  const inputEl = document.getElementById("restack-comment-input");
  const comment = inputEl ? inputEl.value.trim() : "";

  const currentUser = window.currentAuthUser ? window.currentAuthUser.full_name || window.currentAuthUser.username : "Curated Thinker";
  const currentHandle = window.currentAuthUser ? window.currentAuthUser.username : "thinker";

  try {
    const res = await fetch(`/api/substack/ideas/${window.currentRestackIdeaId}/restack`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        comment: comment,
        author_name: currentUser,
        author_handle: currentHandle
      })
    });

    if (res.ok) {
      closeRestackModal();
      if (window.showToast) window.showToast("Restacked to Substack Notes!", "repeat");
      // Switch to notes tab or refresh stream
      loadSubstackNotes();
    }
  } catch (err) {
    console.error("Failed to restack idea:", err);
  }
}

function openRestackFromNote(noteId, author, content) {
  // Direct quote restack from an existing note
  const inputEl = document.getElementById("note-compose-content");
  if (inputEl) {
    inputEl.value = `Restacking @${author}: "${content.substring(0, 100)}..." `;
    inputEl.focus();
    switchTab('notes');
    if (window.showToast) window.showToast("Quote loaded into Note composer", "edit_note");
  }
}

// =========================================================================
// 3. SUBSTACK DISCUSSIONS (Threaded Comments)
// =========================================================================

async function loadIdeaComments(ideaId) {
  const container = document.getElementById("modal-comments-list");
  if (!container) return;

  try {
    const res = await fetch(`/api/substack/ideas/${ideaId}/comments`);
    if (!res.ok) return;
    const comments = await res.json();
    renderIdeaComments(comments, ideaId);
  } catch (err) {
    console.error("Failed to load comments:", err);
  }
}

function renderIdeaComments(comments, ideaId) {
  const container = document.getElementById("modal-comments-list");
  const countBadge = document.getElementById("modal-discussion-count");
  if (!container) return;

  if (countBadge) countBadge.textContent = comments ? comments.length : 0;

  if (!comments || comments.length === 0) {
    container.innerHTML = `
      <div class="p-4 text-center text-xs text-on-surface-variant/70 italic bg-surface-container-highest/30 rounded-xl">
        No comments yet. Start the intellectual discussion below!
      </div>
    `;
    return;
  }

  container.innerHTML = comments.map(c => {
    const avatar = c.user_avatar || `https://api.dicebear.com/7.x/initials/svg?seed=${encodeURIComponent(c.user_name)}`;
    const timeAgo = formatSubstackTimeAgo(c.created_at);

    return `
      <div class="p-3.5 rounded-xl bg-surface-container-lowest border border-outline-variant/30 space-y-1.5">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <img src="${avatar}" alt="${c.user_name}" class="w-6 h-6 rounded-full object-cover" />
            <span class="font-headline font-bold text-xs text-white">${c.user_name}</span>
            <span class="text-[10px] text-on-surface-variant/60">${timeAgo}</span>
          </div>
          <button class="flex items-center gap-1 text-[11px] text-on-surface-variant hover:text-rose-400 transition">
            <span class="material-symbols-outlined text-[13px]">favorite</span>
            <span>${c.likes_count || 0}</span>
          </button>
        </div>
        <p class="text-xs text-slate-200 leading-relaxed pl-8">
          ${c.comment_text}
        </p>
      </div>
    `;
  }).join('');
}

async function handlePostComment(ideaId = null) {
  const targetId = ideaId || (window.currentDeepDiveIdea ? window.currentDeepDiveIdea.id : null);
  if (!targetId) return;

  const inputEl = document.getElementById("modal-new-comment-input");
  if (!inputEl) return;
  const commentText = inputEl.value.trim();
  if (!commentText) return;

  const currentUser = window.currentAuthUser ? window.currentAuthUser.full_name || window.currentAuthUser.username : "Curated Reader";

  try {
    const res = await fetch(`/api/substack/ideas/${targetId}/comments`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        comment_text: commentText,
        user_name: currentUser
      })
    });

    if (res.ok) {
      inputEl.value = "";
      if (window.showToast) window.showToast("Comment added to discussion!", "chat_bubble");
      loadIdeaComments(targetId);
    }
  } catch (err) {
    console.error("Failed to post comment:", err);
  }
}

// =========================================================================
// 4. SUBSTACK SUBSCRIPTIONS & PUBLICATIONS
// =========================================================================

async function handleNoteAuthorSubscribe(authorName) {
  try {
    const res = await fetch("/api/substack/subscribe", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        target_name: authorName,
        target_type: "author"
      })
    });

    if (res.ok) {
      const data = await res.json();
      const msg = data.subscribed ? `Subscribed to ${authorName}!` : `Unsubscribed from ${authorName}`;
      if (window.showToast) window.showToast(msg, "verified");
      updateSubscribeButtons(authorName, data.subscribed);
    }
  } catch (err) {
    console.error("Failed to subscribe:", err);
  }
}

async function handleReaderSubscribe() {
  if (!window.currentDeepDiveIdea) return;
  const authorName = window.currentDeepDiveIdea.author || "The Mental Model Review";
  handleNoteAuthorSubscribe(authorName);
}

function updateSubscribeButtons(authorName, isSubscribed) {
  const readerSubBtn = document.getElementById("reader-subscribe-btn");
  if (readerSubBtn) {
    if (isSubscribed) {
      readerSubBtn.className = "px-3.5 py-1.5 rounded-full text-xs font-headline font-bold text-slate-300 bg-surface-container border border-outline-variant/40 transition flex items-center gap-1.5";
      readerSubBtn.innerHTML = `<span class="material-symbols-outlined text-[14px] text-secondary">check</span><span>Subscribed</span>`;
    } else {
      readerSubBtn.className = "px-3.5 py-1.5 rounded-full text-xs font-headline font-bold text-white bg-[#ff6719] hover:bg-[#e55913] shadow-md transition flex items-center gap-1.5";
      readerSubBtn.innerHTML = `<span class="material-symbols-outlined text-[14px]">notifications_active</span><span>Subscribe</span>`;
    }
  }
}

async function loadPublicationsCarousel() {
  const container = document.getElementById("substack-pubs-carousel");
  if (!container) return;

  try {
    const res = await fetch("/api/substack/publications");
    if (!res.ok) return;
    const pubs = await res.json();
    container.innerHTML = pubs.map(p => `
      <div class="min-w-[190px] p-3 rounded-2xl bg-surface-container border border-outline-variant/30 flex flex-col justify-between shrink-0 shadow-sm">
        <div>
          <div class="flex items-center gap-2 mb-1.5">
            <div class="w-7 h-7 rounded-full bg-[#ff6719]/15 text-[#ff6719] flex items-center justify-center font-bold text-xs">
              <span class="material-symbols-outlined text-[16px]">${p.avatar || 'psychology'}</span>
            </div>
            <div>
              <h5 class="text-xs font-headline font-bold text-white leading-tight truncate max-w-[110px]">${p.name}</h5>
              <span class="text-[10px] text-on-surface-variant font-mono">${p.subscribers} readers</span>
            </div>
          </div>
          <p class="text-[11px] text-on-surface-variant/80 line-clamp-2 leading-snug">${p.description}</p>
        </div>
        <button onclick="handleNoteAuthorSubscribe('${escapeAttr(p.name)}')" class="w-full mt-2.5 py-1 rounded-xl bg-[#ff6719]/10 hover:bg-[#ff6719] text-[#ff6719] hover:text-white border border-[#ff6719]/30 transition text-[10px] font-bold tracking-wide flex items-center justify-center gap-1">
          <span class="material-symbols-outlined text-[12px]">add</span>
          <span>Subscribe</span>
        </button>
      </div>
    `).join('');
  } catch (err) {
    console.error("Failed to load publications:", err);
  }
}

// Global exports
window.loadSubstackNotes = loadSubstackNotes;
window.handleCreateSubstackNote = handleCreateSubstackNote;
window.handleLikeSubstackNote = handleLikeSubstackNote;
window.handleShareSubstackNote = handleShareSubstackNote;
window.openRestackModal = openRestackModal;
window.closeRestackModal = closeRestackModal;
window.submitRestack = submitRestack;
window.openRestackFromNote = openRestackFromNote;
window.loadIdeaComments = loadIdeaComments;
window.handlePostComment = handlePostComment;
window.handleNoteAuthorSubscribe = handleNoteAuthorSubscribe;
window.handleReaderSubscribe = handleReaderSubscribe;
window.loadPublicationsCarousel = loadPublicationsCarousel;
