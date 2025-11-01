  // Dark Mode Toggle
  const modeToggle = document.getElementById("modeToggle");
  if (modeToggle) {
    modeToggle.addEventListener("click", () => {
      document.body.classList.toggle("dark");
      if (document.body.classList.contains("dark")) {
        document.body.style.background = "#121212";
        document.body.style.color = "#fff";
        modeToggle.textContent = "☀️";
      } else {
        document.body.style.background = "#f9f9f9";
        document.body.style.color = "#333";
        modeToggle.textContent = "🌙";
      }
    });
  }

  // Scroll Animation Trigger (optional fade-in animations)
  const fadeEls = document.querySelectorAll(".fade-in");
  window.addEventListener("scroll", () => {
    fadeEls.forEach(el => {
      const rect = el.getBoundingClientRect();
      if (rect.top < window.innerHeight - 100) el.classList.add("visible");
    });
  });
