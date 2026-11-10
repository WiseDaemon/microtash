/**
 * Microstash Neural Audio Narration Controller
 * Seamless Gemini 2.5 Neural TTS + Web Speech API Fallback
 */

let isAudioPlaying = false;
let currentIdeaSpeaking = null;
let currentPlaybackSpeed = 1.0;
let isAudioLoading = false;

function formatAudioTime(seconds) {
  if (!seconds || isNaN(seconds) || seconds < 0) return "0:00";
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
}

function playCurrentCardAudio() {
  if (!window.state || !window.state.ideas.length) return;
  const idea = window.state.ideas[window.state.currentIdeaIndex];
  if (!idea) return;

  if (isAudioPlaying && currentIdeaSpeaking === idea.id) {
    toggleAudioPlayPause();
    return;
  }

  startAudioForIdea(idea);
}

function playModalAudio() {
  const modal = document.getElementById("deep-dive-modal");
  const ideaId = modal ? modal.dataset.ideaId : null;
  let idea = null;

  if (ideaId) {
    idea = (window.state.ideas || []).find(i => String(i.id) === String(ideaId));
  }
  if (!idea && window.state.ideas.length) {
    idea = window.state.ideas[window.state.currentIdeaIndex];
  }

  if (idea) {
    startAudioForIdea(idea);
  }
}

function startAudioForIdea(idea) {
  if (!idea) return;

  stopAllAudio();
  currentIdeaSpeaking = idea.id;
  isAudioLoading = true;

  const bar = document.getElementById("audio-player-bar");
  const titleEl = document.getElementById("audio-title");
  const subEl = document.getElementById("audio-sub");
  const statusPill = document.getElementById("audio-status-pill");
  const timeCurrent = document.getElementById("audio-time-current");
  const timeDuration = document.getElementById("audio-time-duration");
  const progressBar = document.getElementById("audio-progress-bar");

  if (bar) bar.classList.remove("hidden");
  if (titleEl) titleEl.textContent = idea.title;
  if (subEl) subEl.textContent = `${idea.author} — ${idea.source}`;
  if (statusPill) {
    statusPill.classList.remove("hidden");
    statusPill.textContent = "Loading...";
    statusPill.className = "text-[9px] px-1.5 py-0.5 rounded-full bg-amber-500/20 text-amber-300 font-semibold border border-amber-500/30";
  }

  if (timeCurrent) timeCurrent.textContent = "0:00";
  if (timeDuration) timeDuration.textContent = "0:00";
  if (progressBar) progressBar.style.width = "0%";

  updatePlayIcons(false);

  const audioEl = document.getElementById("global-audio-element");
  if (!audioEl) {
    speakWithWebSpeech(idea);
    return;
  }

  // Set audio source to backend Gemini Neural Voice WAV endpoint
  const audioUrl = `/api/audio/${idea.id}?t=${Date.now()}`;
  audioEl.src = audioUrl;
  audioEl.playbackRate = currentPlaybackSpeed;

  audioEl.onloadedmetadata = () => {
    isAudioLoading = false;
    if (timeDuration) timeDuration.textContent = formatAudioTime(audioEl.duration);
    if (statusPill) {
      statusPill.textContent = "Neural Voice";
      statusPill.className = "text-[9px] px-1.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 font-semibold border border-emerald-500/30";
    }
  };

  audioEl.ontimeupdate = () => {
    if (timeCurrent) timeCurrent.textContent = formatAudioTime(audioEl.currentTime);
    if (timeDuration && audioEl.duration) timeDuration.textContent = formatAudioTime(audioEl.duration);
    if (progressBar && audioEl.duration) {
      const pct = (audioEl.currentTime / audioEl.duration) * 100;
      progressBar.style.width = `${pct}%`;
    }
  };

  audioEl.onended = () => {
    isAudioPlaying = false;
    isAudioLoading = false;
    updatePlayIcons(false);
    if (statusPill) statusPill.classList.add("hidden");
  };

  audioEl.onerror = (e) => {
    console.warn("[Audio] Backend stream error, switching to Neural Web Speech fallback:", e);
    isAudioLoading = false;
    speakWithWebSpeech(idea);
  };

  // Trigger play
  audioEl.play().then(() => {
    isAudioPlaying = true;
    isAudioLoading = false;
    updatePlayIcons(true);
    if (statusPill) {
      statusPill.textContent = "Neural Voice";
      statusPill.className = "text-[9px] px-1.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 font-semibold border border-emerald-500/30";
    }
  }).catch((err) => {
    console.warn("[Audio] Autoplay / backend stream deferred, using Web Speech fallback:", err);
    speakWithWebSpeech(idea);
  });
}

function seekAudioFromClick(event) {
  const container = document.getElementById("audio-progress-container");
  const audioEl = document.getElementById("global-audio-element");
  if (!container || !audioEl || !audioEl.duration) return;

  const rect = container.getBoundingClientRect();
  const clickX = event.clientX - rect.left;
  const width = rect.width;
  const pct = Math.max(0, Math.min(1, clickX / width));

  audioEl.currentTime = pct * audioEl.duration;
}

function speakWithWebSpeech(idea) {
  if (!('speechSynthesis' in window)) {
    alert("Audio speech synthesis is not supported on this browser.");
    return;
  }

  window.speechSynthesis.cancel();

  const statusPill = document.getElementById("audio-status-pill");
  if (statusPill) {
    statusPill.classList.remove("hidden");
    statusPill.textContent = "Web Speech";
    statusPill.className = "text-[9px] px-1.5 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 font-semibold border border-indigo-500/30";
  }

  // Use a slight timeout after cancel() to avoid Chrome Web Speech cancellation bug
  setTimeout(() => {
    const textToSpeak = `${idea.title}. ${idea.one_liner}. ${idea.summary}. Practical takeaway: ${idea.action_item || ''}. By ${idea.author}.`;
    const utterance = new SpeechSynthesisUtterance(textToSpeak);
    utterance.rate = currentPlaybackSpeed;
    utterance.pitch = 1.0;

    const voices = window.speechSynthesis.getVoices();
    if (voices && voices.length > 0) {
      const preferred = voices.find(v => v.lang.startsWith("en") && (v.name.includes("Natural") || v.name.includes("Google") || v.name.includes("Neural")));
      if (preferred) utterance.voice = preferred;
    }

    utterance.onstart = () => {
      isAudioPlaying = true;
      isAudioLoading = false;
      updatePlayIcons(true);
    };

    utterance.onend = () => {
      isAudioPlaying = false;
      updatePlayIcons(false);
      if (statusPill) statusPill.classList.add("hidden");
    };

    utterance.onerror = () => {
      isAudioPlaying = false;
      isAudioLoading = false;
      updatePlayIcons(false);
      if (statusPill) statusPill.classList.add("hidden");
    };

    window.speechSynthesis.speak(utterance);
  }, 60);
}

function toggleAudioPlayPause() {
  const audioEl = document.getElementById("global-audio-element");

  if (window.speechSynthesis && window.speechSynthesis.speaking) {
    if (window.speechSynthesis.paused) {
      window.speechSynthesis.resume();
      isAudioPlaying = true;
    } else {
      window.speechSynthesis.pause();
      isAudioPlaying = false;
    }
    updatePlayIcons(isAudioPlaying);
    return;
  }

  if (audioEl && audioEl.src) {
    if (audioEl.paused) {
      audioEl.play().then(() => {
        isAudioPlaying = true;
        updatePlayIcons(true);
      }).catch(e => console.warn(e));
    } else {
      audioEl.pause();
      isAudioPlaying = false;
      updatePlayIcons(false);
    }
  }
}

function togglePlaybackSpeed() {
  const speeds = [1.0, 1.25, 1.5, 2.0];
  const nextIdx = (speeds.indexOf(currentPlaybackSpeed) + 1) % speeds.length;
  currentPlaybackSpeed = speeds[nextIdx];

  const audioEl = document.getElementById("global-audio-element");
  if (audioEl) audioEl.playbackRate = currentPlaybackSpeed;

  const btn = document.getElementById("btn-audio-speed");
  if (btn) btn.textContent = `${currentPlaybackSpeed}x`;
}

function updatePlayIcons(playing) {
  // Update floating bar play/pause button icon safely
  const wrapper = document.getElementById("audio-play-icon-wrapper");
  if (wrapper) {
    wrapper.innerHTML = `<i id="audio-play-icon" data-lucide="${playing ? 'pause' : 'play'}" class="w-4 h-4"></i>`;
  }

  // Update animated audio equalizer waves
  const waves = document.getElementById("audio-waves");
  if (waves) {
    waves.classList.toggle("hidden", !playing);
  }

  // Update swipe controls audio button
  const mainBtn = document.getElementById("btn-audio-listen");
  if (mainBtn) {
    mainBtn.classList.toggle("text-sky-400", playing);
    mainBtn.classList.toggle("border-sky-500/50", playing);
    mainBtn.classList.toggle("bg-sky-500/10", playing);
  }

  // Update modal listen button
  const modalAudioBtn = document.getElementById("modal-btn-audio");
  if (modalAudioBtn) {
    modalAudioBtn.innerHTML = playing ? 
      `<i data-lucide="pause" class="w-3.5 h-3.5"></i><span>Pause Narration</span>` :
      `<i data-lucide="volume-2" class="w-3.5 h-3.5"></i><span>Listen</span>`;
  }

  if (window.lucide) lucide.createIcons();
}

function stopAllAudio() {
  const audioEl = document.getElementById("global-audio-element");
  if (audioEl) {
    audioEl.pause();
    audioEl.currentTime = 0;
  }
  if (window.speechSynthesis) {
    window.speechSynthesis.cancel();
  }
  isAudioPlaying = false;
  isAudioLoading = false;
  updatePlayIcons(false);
}

function closeAudioPlayer() {
  stopAllAudio();
  const bar = document.getElementById("audio-player-bar");
  if (bar) bar.classList.add("hidden");
}

// Window bindings
window.playCurrentCardAudio = playCurrentCardAudio;
window.playModalAudio = playModalAudio;
window.startAudioForIdea = startAudioForIdea;
window.toggleAudioPlayPause = toggleAudioPlayPause;
window.togglePlaybackSpeed = togglePlaybackSpeed;
window.seekAudioFromClick = seekAudioFromClick;
window.closeAudioPlayer = closeAudioPlayer;
