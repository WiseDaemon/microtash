/**
 * Touch, Mouse, and Keyboard Swipe Deck Engine
 */
let isDragging = false;
let startX = 0;
let startY = 0;
let currentX = 0;
let currentY = 0;

function initSwipeEngine() {
  const card = document.getElementById("swipe-card");
  if (!card) return;

  // Touch Events
  card.addEventListener("touchstart", (e) => {
    isDragging = true;
    startX = e.touches[0].clientX;
    startY = e.touches[0].clientY;
    card.style.transition = "none";
  }, { passive: true });

  window.addEventListener("touchmove", (e) => {
    if (!isDragging) return;
    currentX = e.touches[0].clientX - startX;
    currentY = e.touches[0].clientY - startY;

    // Apply translation & tilt rotation
    const rotate = currentX * 0.08;
    card.style.transform = `translate(${currentX}px, ${currentY * 0.4}px) rotate(${rotate}deg)`;
  }, { passive: true });

  window.addEventListener("touchend", () => {
    if (!isDragging) return;
    isDragging = false;
    evaluateSwipe(currentX);
  });

  // Mouse Drag Events
  card.addEventListener("mousedown", (e) => {
    // Ignore clicks on buttons
    if (e.target.closest("button")) return;
    isDragging = true;
    startX = e.clientX;
    startY = e.clientY;
    card.style.transition = "none";
  });

  window.addEventListener("mousemove", (e) => {
    if (!isDragging) return;
    currentX = e.clientX - startX;
    currentY = e.clientY - startY;
    const rotate = currentX * 0.08;
    card.style.transform = `translate(${currentX}px, ${currentY * 0.4}px) rotate(${rotate}deg)`;
  });

  window.addEventListener("mouseup", () => {
    if (!isDragging) return;
    isDragging = false;
    evaluateSwipe(currentX);
  });

  // Keyboard Navigation
  window.addEventListener("keydown", (e) => {
    // Only trigger if no input/textarea is focused
    if (["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement.tagName)) return;

    if (e.code === "Space" || e.key === "ArrowRight") {
      e.preventDefault();
      handleSwipe("left"); // Next
    } else if (e.key === "ArrowLeft") {
      e.preventDefault();
      handleSwipe("right"); // Save/Previous
    } else if (e.key.toLowerCase() === "s") {
      toggleSaveCurrentCard();
    } else if (e.key.toLowerCase() === "l") {
      toggleLikeCurrentCard();
    } else if (e.key.toLowerCase() === "a") {
      playCurrentCardAudio();
    } else if (e.key.toLowerCase() === "f") {
      flipCard();
    }
  });
}

function evaluateSwipe(distanceX) {
  const card = document.getElementById("swipe-card");
  if (!card) return;

  const threshold = 110;
  if (distanceX < -threshold) {
    // Swiped Left -> Skip / Next Idea
    handleSwipe("left");
  } else if (distanceX > threshold) {
    // Swiped Right -> Save to Stash & Next
    handleSwipe("right");
  } else {
    // Snap back
    card.style.transition = "transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275)";
    card.style.transform = "";
  }
  currentX = 0;
  currentY = 0;
}

function handleSwipe(direction) {
  const card = document.getElementById("swipe-card");
  if (!card) return;

  // Unflip if flipped
  card.classList.remove("flipped");

  if (direction === "left") {
    card.classList.add("swipe-left");
  } else {
    card.classList.add("swipe-right");
    // Auto-save on right swipe
    if (window.state && window.state.currentIdeaIndex < window.state.ideas.length) {
      const currentIdea = window.state.ideas[window.state.currentIdeaIndex];
      if (currentIdea && !currentIdea.is_saved) {
        toggleSaveCurrentCard(true);
      }
    }
  }

  // Record that user read this idea (gamification!)
  if (window.recordCurrentIdeaRead) {
    window.recordCurrentIdeaRead();
  }

  setTimeout(() => {
    card.classList.remove("swipe-left", "swipe-right");
    card.style.transform = "";
    card.style.transition = "none";

    // Advance to next card
    if (window.advanceCard) {
      window.advanceCard();
    }
  }, 320);
}

function flipCard() {
  const card = document.getElementById("swipe-card");
  if (card) {
    card.classList.toggle("flipped");
  }
}
