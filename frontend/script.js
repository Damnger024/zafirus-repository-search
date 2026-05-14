// script.js

// =========================
// CONFIG
// =========================

const API_URL = "http://127.0.0.1:8000/search"

// =========================
// VIEW SYSTEM
// =========================

function showView(viewId, button = null) {

  document
    .querySelectorAll(".view")
    .forEach(view => {
      view.classList.remove("active-view")
    })

  document
    .getElementById(viewId)
    .classList.add("active-view")

  document
    .querySelectorAll(".nav-button")
    .forEach(btn => {
      btn.classList.remove("active")
    })

  if (button) {
    button.classList.add("active")
  }
}

// =========================
// RESULTS VIEW MODE
// =========================

let currentResultsView = "cards"

function setResultsView(mode) {

  currentResultsView = mode

  const results =
    document.getElementById("results")

  const cardsToggle =
    document.getElementById("cardsToggle")

  const listToggle =
    document.getElementById("listToggle")

  cardsToggle.classList.remove("active-toggle")
  listToggle.classList.remove("active-toggle")

  if (mode === "cards") {

    results.classList.remove("list-view")
    results.classList.add("results-grid")

    cardsToggle.classList.add("active-toggle")

  } else {

    results.classList.remove("results-grid")
    results.classList.add("list-view")

    listToggle.classList.add("active-toggle")
  }
}

// =========================
// WEIGHTS UI
// (solo visual)
// =========================

const defaultWeights = {
  activity: 35,
  relevance: 25,
  documentation: 20,
  stars: 20
}

const sliderMap = [
  {
    id: "activityWeight",
    value: "activityValue"
  },
  {
    id: "relevanceWeight",
    value: "relevanceValue"
  },
  {
    id: "documentationWeight",
    value: "documentationValue"
  },
  {
    id: "starsWeight",
    value: "starsValue"
  }
]

function updateWeightLabels() {

  let total = 0

  sliderMap.forEach(item => {

    const slider =
      document.getElementById(item.id)

    const value =
      Number(slider.value)

    total += value

    document.getElementById(
      item.value
    ).textContent = `${value}%`
  })

  const totalElement =
    document.getElementById("weightsTotal")

  totalElement.textContent =
    `${total}%`

  totalElement.style.color =
    total === 100
      ? "#6366f1"
      : "#ff6262"
}

sliderMap.forEach(item => {

  const slider =
    document.getElementById(item.id)

  slider.addEventListener("input", e => {

    let total = 0

    sliderMap.forEach(s => {
      total += Number(
        document.getElementById(s.id).value
      )
    })

    if (total > 100) {

      e.target.value =
        Number(e.target.value) -
        (total - 100)
    }

    updateWeightLabels()
  })
})

function resetWeights() {

  document.getElementById(
    "activityWeight"
  ).value = defaultWeights.activity

  document.getElementById(
    "relevanceWeight"
  ).value = defaultWeights.relevance

  document.getElementById(
    "documentationWeight"
  ).value = defaultWeights.documentation

  document.getElementById(
    "starsWeight"
  ).value = defaultWeights.stars

  updateWeightLabels()
}

updateWeightLabels()

// =========================
// SEARCH
// =========================

async function searchRepositories() {

  const query = document
    .getElementById("query")
    .value
    .trim()

  const languages = document
    .getElementById("languages")
    .value
    .split(",")
    .map(lang => lang.trim())
    .filter(Boolean)

  if (!query) {

    alert("Ingresá una búsqueda.")
    return
  }

  showView(
    "resultsView",
    document.querySelectorAll(".nav-button")[1]
  )

  const loadingSection =
    document.getElementById("loadingSection")

  const resultsDiv =
    document.getElementById("results")

  loadingSection.classList.remove("hidden")

  resultsDiv.innerHTML = ""

  try {

    const response = await fetch(
      API_URL,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          query,
          languages
        })
      }
    )

    if (!response.ok) {
      throw new Error("Backend error")
    }

    const data =
      await response.json()

    console.log(data)

    loadingSection.classList.add("hidden")

    if (
      !data.repositories ||
      data.repositories.length === 0
    ) {

      resultsDiv.innerHTML = `
        <div class="glass-card compact-card">
          <h2>No se encontraron resultados</h2>

          <p style="
            margin-top:14px;
            color:#8b8b93;
            line-height:1.6;
          ">
            Probá ampliar la búsqueda.
          </p>
        </div>
      `

      return
    }

    renderResults(data.repositories)

  } catch (error) {

    console.error(error)

    loadingSection.classList.add("hidden")

    resultsDiv.innerHTML = `
      <div class="glass-card compact-card">
        <h2>Error de conexión</h2>

        <p style="
          margin-top:14px;
          color:#8b8b93;
          line-height:1.6;
        ">
          No se pudo conectar con el backend.
        </p>
      </div>
    `
  }
}

// =========================
// SCORE COLORS
// =========================

function getConfidenceLabel(confidence) {

  switch (confidence) {

    case "high":
      return "Alta precisión"

    case "medium":
      return "Precisión media"

    default:
      return "Baja precisión"
  }
}

function getScoreClass(score) {

  if (score >= 80) {
    return "score-high"
  }

  if (score >= 50) {
    return "score-medium"
  }

  return "score-low"
}

// =========================
// RENDER RESULTS
// =========================

function renderResults(repositories) {

  const resultsContainer =
    document.getElementById("results")

  resultsContainer.innerHTML = ""

  repositories.forEach(repo => {

    const card =
      document.createElement("div")

    card.className =
      "result-card"

    card.innerHTML = `
      <div class="result-top">

        <div>

          <div class="result-name">
            #${repo.rank || 0}
            ${repo.full_name}
          </div>

          <div class="result-language">
            ${repo.language || "Unknown"}
          </div>

        </div>

        <div class="score-pill ${getScoreClass(repo.score)}">
          ${repo.score || 0}
        </div>

      </div>

      <div class="result-description">
        ${repo.description || "Sin descripción"}
      </div>

      <div class="result-meta">
      <span>
      ⭐ ${repo.stars?.toLocaleString() || 0}
      </span>

      <span>
      ${getConfidenceLabel(repo.confidence)}
      </span>

      <span>
      ${repo.last_update?.slice(0, 10) || "Unknown"}
      </span>
      </div>

      <div class="score-breakdown">
      <div class="breakdown-item">
        <span>Actividad</span>
        <strong>
        ${repo.score_breakdown?.activity || 0}/30
        </strong>
      </div>

      <div class="breakdown-item">
        <span>Relevancia</span>
        <strong>
        ${repo.score_breakdown?.relevance || 0}/35
        </strong>
      </div>

      <div class="breakdown-item">
        <span>Documentación</span>
        <strong>
        ${repo.score_breakdown?.documentation || 0}/20
        </strong>
      </div>

      <div class="breakdown-item">
        <span>Popularidad</span>
        <strong>
        ${repo.score_breakdown?.stars || 0}/25
        </strong>
      </div>

      ${
        repo.score_breakdown?.penalties
        ? `
        <div class="breakdown-item penalty">
          <span>Penalizaciones</span>
          <strong>
          ${repo.score_breakdown.penalties}
          </strong>
        </div>
        `
        : ""
      }
      </div>

      <div class="tags-row">

        ${
          [
            ...(repo.reasons || []),
            ...(repo.topics || []).slice(0, 4)
          ]
            .slice(0, 6)
            .map(tag => `
              <div class="tag-pill">
                ${tag}
              </div>
            `)
            .join("")
        }

      </div>

      <div class="result-actions">

        <a
          href="${repo.url}"
          target="_blank"
          class="result-button"
        >
          Ver repositorio
        </a>

        ${
          repo.homepage
            ? `
              <a
                href="${repo.homepage}"
                target="_blank"
                class="secondary-button live-demo-button"
              >
                Live Demo
              </a>
            `
            : ""
        }

      </div>
    `

    resultsContainer.appendChild(card)
  })
}