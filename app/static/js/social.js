/**
 * Microstash Social Learning & Shared Stashes Controller
 * Enables publishing decks to community, 1-click link sharing,
 * and cloning curated mental model stashes into personal libraries.
 */

window.currentStashScope = 'my';

function showToast(message, icon = 'check_circle') {
  let toast = document.getElementById('microstash-toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'microstash-toast';
    toast.className = 'fixed bottom-20 left-1/2 -translate-x-1/2 z-50 px-4 py-2.5 rounded-2xl bg-surface-container-highest border border-primary/40 text-white text-xs font-bold shadow-2xl flex items-center gap-2 transition-all duration-300 pointer-events-none opacity-0';
    document.body.appendChild(toast);
  }
  toast.innerHTML = `<span class="material-symbols-outlined text-[18px] text-primary">${icon}</span><span>${message}</span>`;
  toast.classList.remove('opacity-0', 'translate-y-2');
  toast.classList.add('opacity-100', 'translate-y-0');

  setTimeout(() => {
    toast.classList.remove('opacity-100', 'translate-y-0');
    toast.classList.add('opacity-0', 'translate-y-2');
  }, 3200);
}

// 1. Switch Scope (My Stashes vs Community Public Stashes)
async function switchStashScope(scope) {
  window.currentStashScope = scope;
  const btnMy = document.getElementById('btn-stash-scope-my');
  const btnPub = document.getElementById('btn-stash-scope-public');

  if (scope === 'my') {
    if (btnMy) btnMy.className = 'px-3.5 py-1.5 rounded-full text-xs font-headline font-bold bg-primary text-surface-container-lowest transition flex items-center gap-1.5 shadow-sm';
    if (btnPub) btnPub.className = 'px-3.5 py-1.5 rounded-full text-xs font-headline font-bold bg-surface-container-high text-on-surface-variant hover:text-white transition flex items-center gap-1.5';
    renderStashesGrid(window.state.stashes);
  } else {
    if (btnPub) btnPub.className = 'px-3.5 py-1.5 rounded-full text-xs font-headline font-bold bg-primary text-surface-container-lowest transition flex items-center gap-1.5 shadow-sm';
    if (btnMy) btnMy.className = 'px-3.5 py-1.5 rounded-full text-xs font-headline font-bold bg-surface-container-high text-on-surface-variant hover:text-white transition flex items-center gap-1.5';
    try {
      const res = await fetch('/api/stashes/public');
      if (res.ok) {
        const publicStashes = await res.json();
        renderStashesGrid(publicStashes, true);
      }
    } catch (err) {
      console.error('Failed to load public stashes:', err);
    }
  }
}

// 2. Render Stashes Grid
function renderStashesGrid(stashesList, isPublicView = false) {
  const container = document.getElementById('stashes-grid') || document.getElementById('stashes-grid-container');
  if (!container) return;

  const stashes = stashesList || window.state.stashes || [];
  if (!stashes.length) {
    container.innerHTML = `
      <div class="col-span-full py-12 text-center text-slate-500 border border-slate-200 rounded-3xl bg-white p-8">
        <span class="material-symbols-outlined text-4xl text-slate-400 mb-2">folder_open</span>
        <p class="text-xs font-bold text-slate-900">${isPublicView ? 'No community stashes found.' : 'You have no personal stashes yet.'}</p>
        <p class="text-[11px] text-slate-500 mt-1">${isPublicView ? 'Be the first to publish a curated stash!' : 'Create a stash or clone one from the Community tab.'}</p>
      </div>
    `;
    return;
  }

  container.innerHTML = stashes.map(stash => {
    const isPublic = stash.is_public;
    const shareSlug = stash.share_slug || stash.id;
    const clones = stash.clone_count || 0;

    return `
      <div onclick="viewStashDetail('${stash.id}')" class="cursor-pointer group bento-card bg-white hover:border-blue-400 border border-slate-200 rounded-2xl p-5 shadow-sm transition-all duration-200 hover:-translate-y-0.5 flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between mb-3">
            <div class="w-10 h-10 rounded-xl bg-blue-50 text-blue-700 border border-blue-200 flex items-center justify-center text-base font-bold">
              <span class="material-symbols-outlined text-[20px]">${stash.icon === 'book-open' ? 'menu_book' : (stash.icon || 'bookmark')}</span>
            </div>
            <div class="flex items-center gap-1.5">
              ${isPublic ? `
                <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-50 text-amber-700 border border-amber-200 flex items-center gap-1">
                  <span class="material-symbols-outlined text-[12px]">public</span>
                  <span>${clones} Clones</span>
                </span>
              ` : `
                <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-100 text-slate-600 border border-slate-200">
                  Private
                </span>
              `}
              <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-50 text-blue-700 border border-blue-200">
                ${stash.ideas_count} cards
              </span>
            </div>
          </div>

          <h3 class="text-base font-headline font-bold text-slate-900 group-hover:text-blue-600 transition line-clamp-1">
            ${stash.title}
          </h3>
          <p class="text-xs text-slate-500 line-clamp-2 leading-relaxed mt-1">
            ${stash.description || 'Curated microlearning mental model deck.'}
          </p>
        </div>

        <div class="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
          <button onclick="event.stopPropagation(); shareStashLink('${shareSlug}', '${stash.title.replace(/'/g, "\\'")}')" class="flex items-center gap-1 text-[11px] font-bold text-blue-600 hover:underline" title="Copy shareable link">
            <span class="material-symbols-outlined text-[14px]">share</span>
            <span>Share Link</span>
          </button>
          ${isPublicView ? `
            <button onclick="event.stopPropagation(); cloneStashToMyLibrary('${stash.id}')" class="px-2.5 py-1 rounded-xl bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 text-[11px] font-bold transition flex items-center gap-1">
              <span class="material-symbols-outlined text-[13px]">content_copy</span>
              <span>Clone Stash</span>
            </button>
          ` : `
            <span class="text-blue-600 font-bold flex items-center gap-0.5 text-[11px] group-hover:translate-x-1 transition-transform">
              <span>Open</span>
              <span class="material-symbols-outlined text-[14px]">arrow_forward</span>
            </span>
          `}
        </div>
      </div>
    `;
  }).join('');
}

// 3. Stash Detail View
async function viewStashDetail(stashId) {
  try {
    const res = await fetch(`/api/stashes/${stashId}`);
    if (!res.ok) throw new Error("Stash not found");
    const stash = await res.json();

    const grid = document.getElementById('stashes-grid');
    const detailView = document.getElementById('stash-detail-view');
    const detailContent = document.getElementById('stash-detail-content');
    const detailActions = document.getElementById('stash-detail-actions');

    if (grid) grid.classList.add('hidden');
    if (detailView) detailView.classList.remove('hidden');

    const shareSlug = stash.share_slug || stash.id;
    const isPublic = stash.is_public;

    // Actions in detail header
    if (detailActions) {
      detailActions.innerHTML = `
        <button onclick="shareStashLink('${shareSlug}', '${stash.title.replace(/'/g, "\\'")}')" class="px-3 py-1.5 rounded-full bg-surface-container-high hover:bg-surface-container-highest border border-primary/40 text-primary text-xs font-bold transition flex items-center gap-1">
          <span class="material-symbols-outlined text-[15px]">share</span>
          <span>Share</span>
        </button>
        <button onclick="toggleStashPublish('${stash.id}', ${!isPublic})" class="px-3 py-1.5 rounded-full ${isPublic ? 'bg-secondary/20 border-secondary/40 text-secondary' : 'bg-surface-container-high border-outline-variant/40 text-on-surface-variant'} border text-xs font-bold transition flex items-center gap-1">
          <span class="material-symbols-outlined text-[15px]">${isPublic ? 'public' : 'lock'}</span>
          <span>${isPublic ? 'Public' : 'Make Public'}</span>
        </button>
        <button onclick="cloneStashToMyLibrary('${stash.id}')" class="px-3 py-1.5 rounded-full bg-primary text-surface-container-lowest text-xs font-headline font-bold transition flex items-center gap-1 shadow-sm">
          <span class="material-symbols-outlined text-[15px]">library_add</span>
          <span>Clone to Library</span>
        </button>
      `;
    }

    if (detailContent) {
      detailContent.innerHTML = `
        <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3">
          <div class="flex items-center justify-between">
            <span class="px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider bg-blue-50 text-blue-700 border border-blue-200">
              Curated Mental Model Deck
            </span>
            <span class="text-xs text-slate-500 font-medium">
              Curated by <strong class="text-slate-900">@${stash.owner_username || 'community'}</strong> • ${stash.clone_count || 0} Clones
            </span>
          </div>
          <h2 class="text-2xl font-headline font-extrabold text-slate-900">${stash.title}</h2>
          <p class="text-xs text-slate-600 leading-relaxed">${stash.description || 'Complete microlearning mental model deck.'}</p>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          ${(stash.ideas || []).map(card => `
            <div class="bg-white border border-slate-200 shadow-2xs rounded-2xl p-5 flex flex-col justify-between space-y-3">
              <div>
                <div class="flex items-center justify-between mb-1.5">
                  <span class="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-blue-50 text-blue-700 border border-blue-200">
                    ${card.topic}
                  </span>
                  <span class="text-[11px] text-slate-500">${card.read_time_mins || 1} min read</span>
                </div>
                <h4 class="text-base font-headline font-bold text-slate-900 mt-1">${card.title}</h4>
                <p class="text-xs text-blue-600 font-medium italic mt-0.5">"${card.one_liner}"</p>
                <p class="text-xs text-slate-700 leading-relaxed mt-2">${card.summary}</p>
              </div>

              <div class="pt-2 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                <span class="font-medium truncate max-w-[150px]">• ${card.author}</span>
                <div class="flex items-center gap-2">
                  <button onclick="jumpToSwipeCard('${card.id}')" class="text-blue-600 hover:underline font-bold text-[11px]">
                    Study in Gym →
                  </button>
                </div>
              </div>
            </div>
          `).join('')}
        </div>
      `;
    }
  } catch (err) {
    console.error("Failed to view stash:", err);
  }
}

function closeStashDetail() {
  const grid = document.getElementById('stashes-grid');
  const detailView = document.getElementById('stash-detail-view');
  if (grid) grid.classList.remove('hidden');
  if (detailView) detailView.classList.add('hidden');
}

// 4. Social Sharing & Cloning Handlers
function shareStashLink(slugOrId, title) {
  const url = `${window.location.origin}/share/stash/${slugOrId}`;
  if (navigator.clipboard) {
    navigator.clipboard.writeText(url).then(() => {
      showToast(`Link to "${title}" copied to clipboard!`, 'share');
    }).catch(() => {
      prompt("Copy share link:", url);
    });
  } else {
    prompt("Copy share link:", url);
  }
}

async function toggleStashPublish(stashId, makePublic) {
  try {
    const res = await fetch(`/api/stashes/${stashId}/publish`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ is_public: makePublic })
    });
    if (res.ok) {
      showToast(makePublic ? 'Published to Community Library! 🌐' : 'Stash is now Private.');
      await viewStashDetail(stashId);
      if (typeof loadStashes === 'function') await loadStashes();
    }
  } catch (err) {
    console.error("Publish toggle error:", err);
  }
}

async function cloneStashToMyLibrary(stashId) {
  try {
    const res = await fetch(`/api/stashes/${stashId}/clone`, { method: 'POST' });
    if (res.ok) {
      const data = await res.json();
      showToast('🎉 Cloned to your personal library!', 'library_add');
      if (typeof loadStashes === 'function') await loadStashes();
      switchStashScope('my');
    }
  } catch (err) {
    console.error("Clone error:", err);
    showToast('Failed to clone stash.');
  }
}

// 5. Create New Stash Form Handlers
function openCreateStashModal() {
  const modal = document.getElementById('create-stash-modal');
  if (modal) {
    modal.classList.remove('hidden');
    modal.classList.add('flex');
  }
}

function closeCreateStashModal() {
  const modal = document.getElementById('create-stash-modal');
  if (modal) {
    modal.classList.add('hidden');
    modal.classList.remove('flex');
  }
}

async function handleCreateStashSubmit(e) {
  if (e) e.preventDefault();
  const title = document.getElementById('new-stash-title')?.value?.trim();
  const desc = document.getElementById('new-stash-desc')?.value?.trim();
  const isPublic = document.getElementById('new-stash-public')?.checked || false;

  if (!title) {
    alert("Please enter a title for your stash.");
    return;
  }

  try {
    const res = await fetch('/api/stashes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: title,
        description: desc || "Personal collection of microlearning mental models.",
        icon: "bookmark",
        color: "indigo",
        is_public: isPublic
      })
    });

    if (res.ok) {
      closeCreateStashModal();
      showToast(`Stash "${title}" created!`);
      if (typeof loadStashes === 'function') await loadStashes();
      switchStashScope('my');
    }
  } catch (err) {
    console.error("Create stash error:", err);
  }
}

// Expose globals for inline event attributes
window.switchStashScope = switchStashScope;
window.renderStashesGrid = renderStashesGrid;
window.viewStashDetail = viewStashDetail;
window.closeStashDetail = closeStashDetail;
window.shareStashLink = shareStashLink;
window.toggleStashPublish = toggleStashPublish;
window.cloneStashToMyLibrary = cloneStashToMyLibrary;
window.openCreateStashModal = openCreateStashModal;
window.closeCreateStashModal = closeCreateStashModal;
window.handleCreateStashSubmit = handleCreateStashSubmit;
window.showToast = showToast;
