/* ─────────────────────────────────────────────────────────────────
   Pokédex  ·  app.js
───────────────────────────────────────────────────────────────── */

// ── Stat display names ──────────────────────────────────────────
const STAT_LABELS = {
  "hp":              "HP",
  "attack":          "Attack",
  "defense":         "Defense",
  "special-attack":  "Sp. Atk",
  "special-defense": "Sp. Def",
  "speed":           "Speed",
};

// Colour the bar based on the value
function statBarClass(val) {
  if (val >= 100) return "green";
  if (val >= 60)  return "amber";
  return "";          // red (default)
}

// ── Build a card from JSON data ─────────────────────────────────
function buildCard(data, containerEl) {
  const tmpl = document.getElementById("card-template");
  const card = tmpl.content.cloneNode(true);

  // Sprite + shiny toggle
  const sprite      = card.querySelector(".sprite");
  const shinyToggle = card.querySelector(".shiny-toggle");
  let   isShiny     = false;

  sprite.src = data.sprite_url;
  sprite.alt = data.name;

  shinyToggle.addEventListener("click", () => {
    isShiny = !isShiny;
    sprite.style.opacity = "0";
    setTimeout(() => {
      sprite.src = isShiny ? data.sprite_shiny_url : data.sprite_url;
      sprite.style.opacity = "1";
    }, 150);
    shinyToggle.classList.toggle("active", isShiny);
  });

  // Basic info
  card.querySelector(".pokemon-number").textContent = `#${String(data.id).padStart(4, "0")}`;
  card.querySelector(".pokemon-name").textContent   = data.name;
  card.querySelector(".pokemon-desc").textContent   = data.description || "";

  // Types
  const typesEl = card.querySelector(".type-badges");
  (data.types || []).forEach(t => {
    const span = document.createElement("span");
    span.className = `type-badge type-${t}`;
    span.textContent = t;
    typesEl.appendChild(span);
  });

  // Meta
  card.querySelector(".pokemon-height").textContent = `${data.height_m} m`;
  card.querySelector(".pokemon-weight").textContent = `${data.weight_kg} kg`;
  card.querySelector(".pokemon-xp").textContent     = data.base_experience ?? "—";

  // Abilities
  const abilitiesEl = card.querySelector(".ability-list");
  (data.abilities || []).forEach(a => {
    const chip = document.createElement("span");
    chip.className = "ability-chip";
    chip.textContent = a.replace(/-/g, " ");
    abilitiesEl.appendChild(chip);
  });

  // Stats
  const statsGrid = card.querySelector(".stats-grid");
  const stats = data.stats || {};
  Object.entries(stats).forEach(([key, val]) => {
    const row = document.createElement("div");
    row.className = "stat-row";
    row.innerHTML = `
      <span class="stat-name">${STAT_LABELS[key] || key}</span>
      <span class="stat-num">${val}</span>
      <div class="stat-bar-bg">
        <div class="stat-bar ${statBarClass(val)}" style="width:0" data-val="${val}"></div>
      </div>`;
    statsGrid.appendChild(row);
  });
  card.querySelector(".total-val").textContent = data.total_base_stats ?? "";

  // Evolution button
  const evoBtn   = card.querySelector(".evo-btn");
  const evoChain = card.querySelector(".evo-chain");
  let   evoLoaded = false;

  evoBtn.addEventListener("click", async () => {
    if (!evoLoaded) {
      evoBtn.textContent = "Loading…";
      evoBtn.disabled = true;
      try {
        const resp = await fetch(`/api/pokemon/evolution/${data.name}`);
        const json = await resp.json();
        if (json.error) throw new Error(json.error);
        renderEvoChain(json.chain, evoChain, containerEl);
        evoLoaded = true;
        evoBtn.textContent = "Hide Evolution Chain ↑";
      } catch {
        evoBtn.textContent = "Evolution data unavailable";
        return;
      }
      evoBtn.disabled = false;
    }
    const isHidden = evoChain.classList.toggle("hidden");
    evoBtn.textContent = isHidden ? "View Evolution Chain →" : "Hide Evolution Chain ↑";
  });

  containerEl.innerHTML = "";
  containerEl.appendChild(card);
  containerEl.classList.remove("hidden");

  // Animate stat bars after paint
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      containerEl.querySelectorAll(".stat-bar").forEach(bar => {
        const val = parseInt(bar.dataset.val, 10);
        bar.style.width = `${Math.min(val / 255 * 100, 100)}%`;
      });
    });
  });
}

// ── Render evolution chain ──────────────────────────────────────
function renderEvoChain(chain, evoChainEl, cardContainer) {
  evoChainEl.innerHTML = "";
  const row = document.createElement("div");
  row.className = "evo-stage-row";

  chain.forEach((stage, idx) => {
    if (idx > 0) {
      const arrow = document.createElement("span");
      arrow.className = "evo-arrow";
      arrow.textContent = "→";
      row.appendChild(arrow);
    }
    const stageDiv = document.createElement("div");
    stageDiv.className = "evo-stage";

    stage.forEach(member => {
      const a = document.createElement("div");
      a.className = "evo-member";
      a.title = member.name;
      a.innerHTML = `
        <img src="${member.sprite_url}" alt="${member.name}" loading="lazy" />
        <span>${member.name}</span>`;
      a.addEventListener("click", () => fetchAndShow(member.name, cardContainer));
      stageDiv.appendChild(a);
    });

    row.appendChild(stageDiv);
  });

  evoChainEl.appendChild(row);
}

// ── Fetch + show helper ─────────────────────────────────────────
async function fetchAndShow(nameOrId, resultEl, loaderEl, errorEl) {
  loaderEl  && loaderEl.classList.remove("hidden");
  resultEl  && resultEl.classList.add("hidden");
  errorEl   && errorEl.classList.add("hidden");

  try {
    const resp = await fetch(`/api/pokemon/search/${encodeURIComponent(nameOrId)}`);
    const data = await resp.json();

    if (data.error) throw new Error(data.error);

    loaderEl && loaderEl.classList.add("hidden");
    buildCard(data, resultEl);
  } catch (err) {
    loaderEl && loaderEl.classList.add("hidden");
    if (errorEl) {
      errorEl.textContent = `Pokémon not found: "${nameOrId}". Try a different name or number.`;
      errorEl.classList.remove("hidden");
    }
  }
}

// ── Search view ─────────────────────────────────────────────────
const searchInput  = document.getElementById("search-input");
const searchBtn    = document.getElementById("search-btn");
const resultArea   = document.getElementById("result-area");
const errorMsg     = document.getElementById("error-msg");
const loader       = document.getElementById("loader");

function doSearch() {
  const q = searchInput.value.trim();
  if (!q) return;
  fetchAndShow(q, resultArea, loader, errorMsg);
}

searchBtn.addEventListener("click", doSearch);
searchInput.addEventListener("keydown", e => { if (e.key === "Enter") doSearch(); });

document.querySelectorAll(".hint-chip").forEach(chip => {
  chip.addEventListener("click", () => {
    searchInput.value = chip.dataset.name;
    doSearch();
  });
});

// ── Random view ─────────────────────────────────────────────────
const randomBtn        = document.getElementById("random-btn");
const randomResultArea = document.getElementById("random-result-area");
const randomErrorMsg   = document.getElementById("random-error-msg");
const randomLoader     = document.getElementById("random-loader");

randomBtn.addEventListener("click", async () => {
  randomLoader.classList.remove("hidden");
  randomResultArea.classList.add("hidden");
  randomErrorMsg.classList.add("hidden");

  try {
    const resp = await fetch("/api/pokemon/random");
    const data = await resp.json();
    if (data.error) throw new Error(data.error);
    randomLoader.classList.add("hidden");
    buildCard(data, randomResultArea);
  } catch {
    randomLoader.classList.add("hidden");
    randomErrorMsg.textContent = "Couldn't retrieve a random Pokémon. Try again!";
    randomErrorMsg.classList.remove("hidden");
  }
});

// ── Nav ─────────────────────────────────────────────────────────
document.querySelectorAll(".nav-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".nav-btn").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".view").forEach(v => v.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById(`view-${btn.dataset.view}`).classList.add("active");
  });
});

// Helper used by evolution chain clicks (scoped to search view)
function fetchAndShow(nameOrId, containerEl) {
  const loaderEl = document.getElementById("loader");
  const errorEl  = document.getElementById("error-msg");

  loaderEl.classList.remove("hidden");
  containerEl.classList.add("hidden");
  errorEl.classList.add("hidden");

  fetch(`/api/pokemon/search/${encodeURIComponent(nameOrId)}`)
    .then(r => r.json())
    .then(data => {
      if (data.error) throw new Error(data.error);
      loaderEl.classList.add("hidden");
      buildCard(data, containerEl);
      containerEl.scrollIntoView({ behavior: "smooth", block: "start" });
    })
    .catch(() => {
      loaderEl.classList.add("hidden");
      errorEl.textContent = `Could not load "${nameOrId}".`;
      errorEl.classList.remove("hidden");
    });
}
