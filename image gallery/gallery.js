const slides = [
  {
    title: "Night moves",
    category: "color",
    alt: "A vivid outdoor music festival lit up at night",
    src: "https://images.unsplash.com/photo-1531058020387-3be344556be6?auto=format&fit=crop&w=1400&q=85",
  },
  {
    title: "Somewhere, slowly",
    category: "places",
    alt: "A dreamlike pink and violet sky above a quiet landscape",
    src: "https://images.unsplash.com/photo-1519608487953-e999c86e7455?auto=format&fit=crop&w=1400&q=85",
  },
  {
    title: "Citrus season",
    category: "color",
    alt: "Bright oranges and citrus fruit in warm sunlight",
    src: "https://images.unsplash.com/photo-1547514701-42782101795e?auto=format&fit=crop&w=1400&q=85",
  },
  {
    title: "Main character energy",
    category: "people",
    alt: "A sunlit portrait with a confident, joyful expression",
    src: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=1400&q=85",
  },
  {
    title: "The long way home",
    category: "places",
    alt: "A peaceful mountain lake reflecting the landscape",
    src: "https://images.unsplash.com/photo-1470770841072-f978cf4d019e?auto=format&fit=crop&w=1400&q=85",
  },
  {
    title: "Flower power",
    category: "color",
    alt: "A joyful, saturated bunch of pink and orange flowers",
    src: "https://images.unsplash.com/photo-1490750967868-88aa4486c946?auto=format&fit=crop&w=1400&q=85",
  },
  {
    title: "Golden hour, always",
    category: "people",
    alt: "A warm portrait in the late afternoon sunshine",
    src: "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?auto=format&fit=crop&w=1400&q=85",
  },
  {
    title: "Out there, somewhere",
    category: "places",
    alt: "A winding path through an expansive sunlit landscape",
    src: "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1400&q=85",
  },
];

const featuredPhoto = document.querySelector("#featuredPhoto");
const featureTitle = document.querySelector("#featureTitle");
const featureIndex = document.querySelector("#featureIndex");
const lightbox = document.querySelector("#lightbox");
const lightboxPhoto = document.querySelector("#lightboxPhoto");
const lightboxTitle = document.querySelector("#lightboxTitle");
const lightboxCount = document.querySelector("#lightboxCount");
const photoCards = [...document.querySelectorAll(".photo-card")];
const autoplayButtons = [
  {
    button: document.querySelector("#autoplayButton"),
    label: document.querySelector("#autoplayLabel"),
  },
  {
    button: document.querySelector("#lightboxAutoplay"),
    label: document.querySelector("#lightboxAutoplay span"),
  },
];

let currentIndex = 0;
let autoplay = true;
let lastFocusedCard = null;

function showSlide(index) {
  currentIndex = (index + slides.length) % slides.length;
  const slide = slides[currentIndex];
  const count = `${String(currentIndex + 1).padStart(2, "0")} / ${String(slides.length).padStart(2, "0")}`;

  featuredPhoto.src = slide.src;
  featuredPhoto.alt = slide.alt;
  featureTitle.textContent = slide.title;
  featureIndex.textContent = count;

  lightboxPhoto.src = slide.src;
  lightboxPhoto.alt = slide.alt;
  lightboxTitle.textContent = slide.title;
  lightboxCount.textContent = count;

  photoCards.forEach((card, cardIndex) => {
    card.classList.toggle("is-current", cardIndex === currentIndex);
  });
}

function setAutoplay(isPlaying) {
  autoplay = isPlaying;
  autoplayButtons.forEach(({ button, label }) => {
    button.setAttribute("aria-pressed", String(autoplay));
    button.setAttribute("aria-label", autoplay ? "Pause autoplay" : "Start autoplay");
    button.querySelector(".play-icon").textContent = autoplay ? "Ⅱ" : "▶";
    label.textContent = autoplay
      ? button.id === "lightboxAutoplay" ? "PAUSE" : "AUTO: ON"
      : button.id === "lightboxAutoplay" ? "PLAY" : "AUTO: OFF";
  });
}

function openLightbox(index, card) {
  lastFocusedCard = card;
  showSlide(index);
  lightbox.showModal();
  document.querySelector("#closeLightbox").focus();
}

document.querySelector("#previousButton").addEventListener("click", () => showSlide(currentIndex - 1));
document.querySelector("#nextButton").addEventListener("click", () => showSlide(currentIndex + 1));
document.querySelector("#lightboxPrevious").addEventListener("click", () => showSlide(currentIndex - 1));
document.querySelector("#lightboxNext").addEventListener("click", () => showSlide(currentIndex + 1));
autoplayButtons.forEach(({ button }) => {
  button.addEventListener("click", () => setAutoplay(!autoplay));
});

photoCards.forEach((card) => {
  card.addEventListener("click", () => openLightbox(Number(card.dataset.index), card));
});

document.querySelectorAll(".filter-button").forEach((button) => {
  button.addEventListener("click", () => {
    const filter = button.dataset.filter;
    document.querySelectorAll(".filter-button").forEach((filterButton) => {
      const selected = filterButton === button;
      filterButton.classList.toggle("is-active", selected);
      filterButton.setAttribute("aria-pressed", String(selected));
    });
    photoCards.forEach((card) => {
      card.hidden = filter !== "all" && card.dataset.category !== filter;
    });
  });
});

document.querySelector("#closeLightbox").addEventListener("click", () => lightbox.close());
lightbox.addEventListener("click", (event) => {
  if (event.target === lightbox) {
    lightbox.close();
  }
});
lightbox.addEventListener("close", () => lastFocusedCard?.focus());

document.addEventListener("keydown", (event) => {
  if (!lightbox.open) {
    return;
  }
  if (event.key === "ArrowRight") {
    event.preventDefault();
    showSlide(currentIndex + 1);
  } else if (event.key === "ArrowLeft") {
    event.preventDefault();
    showSlide(currentIndex - 1);
  }
});

window.setInterval(() => {
  if (autoplay && document.visibilityState === "visible") {
    showSlide(currentIndex + 1);
  }
}, 4500);

showSlide(currentIndex);
