/**
 * Social Quote Graphic Card Exporter (HTML5 Canvas)
 */
let currentShareStyle = 'gradient';
let activeShareIdea = null;

function openShareStudioModal(customIdea = null) {
  activeShareIdea = customIdea || (window.state && window.state.ideas ? window.state.ideas[window.state.currentIdeaIndex] : null);
  const modal = document.getElementById("share-modal");
  if (!modal) return;
  modal.classList.remove("hidden");
  renderShareCard(currentShareStyle);
}

function closeShareModal() {
  const modal = document.getElementById("share-modal");
  if (modal) modal.classList.add("hidden");
}

function renderShareCard(style = 'gradient') {
  currentShareStyle = style;
  const canvas = document.getElementById("share-canvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  const idea = activeShareIdea || (window.state && window.state.ideas ? window.state.ideas[window.state.currentIdeaIndex] : null);
  if (!idea) return;

  const width = canvas.width;
  const height = canvas.height;

  // Background
  if (style === 'gradient') {
    const grad = ctx.createLinearGradient(0, 0, width, height);
    grad.addColorStop(0, '#1e1b4b'); // deep indigo
    grad.addColorStop(0.5, '#311042'); // rich violet
    grad.addColorStop(1, '#0f172a'); // slate dark
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, width, height);
  } else if (style === 'minimal-dark') {
    ctx.fillStyle = '#090d16';
    ctx.fillRect(0, 0, width, height);
  } else {
    // Warm paper
    ctx.fillStyle = '#f8f5ee';
    ctx.fillRect(0, 0, width, height);
  }

  // Border Accent Line
  ctx.strokeStyle = style === 'paper' ? '#e2d9c8' : 'rgba(255, 255, 255, 0.1)';
  ctx.lineWidth = 16;
  ctx.strokeRect(16, 16, width - 32, height - 32);

  // Microstash Branding Tag
  ctx.font = 'bold 16px Inter, sans-serif';
  ctx.fillStyle = style === 'paper' ? '#4f46e5' : '#818cf8';
  ctx.fillText('MICROSTASH  •  BITE-SIZED WISDOM', 50, 70);

  // Topic Badge
  ctx.font = '600 13px Inter, sans-serif';
  ctx.fillStyle = style === 'paper' ? '#64748b' : '#94a3b8';
  ctx.fillText(idea.topic.toUpperCase(), 50, 95);

  // Quote or One-liner Text (Wrapped)
  const mainQuote = idea.quote ? `“${idea.quote.replace(/^["“”]|["“”]$/g, '')}”` : `“${idea.one_liner}”`;
  ctx.font = 'italic 26px "Playfair Display", Georgia, serif';
  ctx.fillStyle = style === 'paper' ? '#1e293b' : '#ffffff';
  
  wrapText(ctx, mainQuote, 50, 160, width - 100, 38);

  // Concept Title
  ctx.font = 'bold 20px Inter, sans-serif';
  ctx.fillStyle = style === 'paper' ? '#0f172a' : '#f8fafc';
  ctx.fillText(`Concept: ${idea.title}`, 50, height - 140);

  // Author & Source
  ctx.font = '500 16px Inter, sans-serif';
  ctx.fillStyle = style === 'paper' ? '#475569' : '#cbd5e1';
  ctx.fillText(`— ${idea.author}, ${idea.source}`, 50, height - 110);

  // Anti-Doomscroll Watermark & Scan Badge
  ctx.font = '13px Inter, sans-serif';
  ctx.fillStyle = style === 'paper' ? '#94a3b8' : '#64748b';
  ctx.fillText('microstash.ai  •  Replace doomscrolling with microlearning', 50, height - 60);

  // Draw High-Contrast Scan Badge / Micro-Matrix in Bottom Right
  drawScanBadge(ctx, width - 110, height - 110, 60, style);
}

function drawScanBadge(ctx, x, y, size, style) {
  // Border & background pill
  ctx.fillStyle = style === 'paper' ? '#ffffff' : '#020617';
  ctx.strokeStyle = style === 'paper' ? '#cbd5e1' : 'rgba(99, 102, 241, 0.4)';
  ctx.lineWidth = 1.5;
  ctx.beginPath();
  ctx.roundRect(x - 10, y - 10, size + 20, size + 32, 10);
  ctx.fill();
  ctx.stroke();

  // Simulated clean QR matrix pattern
  ctx.fillStyle = style === 'paper' ? '#0f172a' : '#818cf8';
  const dotSize = size / 7;
  // Corner markers
  ctx.fillRect(x, y, dotSize * 2.5, dotSize * 2.5);
  ctx.fillRect(x + size - dotSize * 2.5, y, dotSize * 2.5, dotSize * 2.5);
  ctx.fillRect(x, y + size - dotSize * 2.5, dotSize * 2.5, dotSize * 2.5);
  // Interior accent dots
  ctx.fillRect(x + dotSize * 3, y + dotSize * 1.5, dotSize, dotSize);
  ctx.fillRect(x + dotSize * 4.5, y + dotSize * 3, dotSize, dotSize);
  ctx.fillRect(x + dotSize * 1.5, y + dotSize * 4, dotSize, dotSize);
  ctx.fillRect(x + dotSize * 3, y + dotSize * 5, dotSize * 1.5, dotSize);

  // Micro label under QR
  ctx.font = 'bold 8px Inter, sans-serif';
  ctx.fillStyle = style === 'paper' ? '#64748b' : '#94a3b8';
  ctx.textAlign = 'center';
  ctx.fillText('SCAN CARD', x + size / 2, y + size + 14);
  ctx.textAlign = 'left';
}

function wrapText(ctx, text, x, y, maxWidth, lineHeight) {
  const words = text.split(' ');
  let line = '';
  let curY = y;

  for (let n = 0; n < words.length; n++) {
    const testLine = line + words[n] + ' ';
    const metrics = ctx.measureText(testLine);
    const testWidth = metrics.width;
    if (testWidth > maxWidth && n > 0) {
      ctx.fillText(line, x, curY);
      line = words[n] + ' ';
      curY += lineHeight;
      if (curY > 400) {
        ctx.fillText(line + '...', x, curY);
        return;
      }
    } else {
      line = testLine;
    }
  }
  ctx.fillText(line, x, curY);
}

function downloadShareCard() {
  const canvas = document.getElementById("share-canvas");
  if (!canvas) return;
  const link = document.createElement("a");
  link.download = `microstash-${Date.now()}.png`;
  link.href = canvas.toDataURL("image/png");
  link.click();
}

function copyQuoteText() {
  const idea = activeShareIdea || (window.state && window.state.ideas ? window.state.ideas[window.state.currentIdeaIndex] : null);
  if (!idea) return;
  const text = `"${idea.quote || idea.one_liner}"\n\n— ${idea.author} (${idea.source})\nVia Microstash • Replace Doomscrolling with Microlearning`;
  navigator.clipboard.writeText(text).then(() => {
    alert("Quote copied to clipboard!");
  });
}

async function shareNativeSocial() {
  const idea = activeShareIdea || (window.state && window.state.ideas ? window.state.ideas[window.state.currentIdeaIndex] : null);
  if (!idea) return;
  const canvas = document.getElementById("share-canvas");

  const shareData = {
    title: `${idea.title} — Microstash`,
    text: `💡 "${idea.quote || idea.one_liner}" — ${idea.author}\n\nReplaced 10 minutes of doomscrolling with microlearning on Microstash. #MentalModels #Microlearning`,
    url: window.location.origin
  };

  if (navigator.share) {
    try {
      if (canvas && canvas.toBlob) {
        canvas.toBlob(async (blob) => {
          const file = new File([blob], `microstash-${idea.id || 'quote'}.png`, { type: 'image/png' });
          if (navigator.canShare && navigator.canShare({ files: [file] })) {
            await navigator.share({ ...shareData, files: [file] });
          } else {
            await navigator.share(shareData);
          }
        });
      } else {
        await navigator.share(shareData);
      }
    } catch (err) {
      if (err.name !== 'AbortError') {
        console.warn("Share failed, falling back to copy:", err);
        copyQuoteText();
      }
    }
  } else {
    copyQuoteText();
  }
}
