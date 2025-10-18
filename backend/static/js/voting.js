// Voting booth page script
let currentVoter = null
let selectedCandidate = null
let candidates = []
const socket = window.socket // Declare the socket variable

document.addEventListener("DOMContentLoaded", () => {
  loadCandidates()
  registerAsReadyBooth()
  addLightningEffects()
  setupVotingListeners()
})

function setupVotingListeners() {
  if (socket) {
    socket.on("start_voting", (data) => {
      console.log("[v0] Received start_voting event:", data)
      // Show voting screen when panitia starts voting
      const standbyScreen = document.getElementById("standbyScreen")
      if (standbyScreen) {
        standbyScreen.style.display = "none"
      }
      const votingScreen = document.getElementById("votingScreen")
      if (votingScreen) {
        votingScreen.style.display = "block"
      }
    })
  }
}

function registerAsReadyBooth() {
  socket.emit("bilik_ready", {
    client_id: "booth_" + Math.random().toString(36).substr(2, 9),
  })
}

function loadCandidates() {
  fetch("/api/candidates")
    .then((res) => res.json())
    .then((data) => {
      candidates = data
      renderCandidates()
    })
    .catch((err) => console.error("Error loading candidates:", err))
}

function renderCandidates() {
  const grid = document.getElementById("candidatesGrid")
  grid.innerHTML = candidates
    .map(
      (candidate) => `
        <div class="candidate-card" onclick="selectCandidate(${candidate.id}, '${candidate.name}')" data-candidate-id="${candidate.id}">
            <div class="candidate-photo">
                ${candidate.photo ? `<img src="${candidate.photo}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 8px;">` : "👤"}
            </div>
            <div class="candidate-name">${candidate.name}</div>
            <div class="candidate-desc">${candidate.description || ""}</div>
            <canvas class="lightning-canvas" width="250" height="250" style="position: absolute; top: 0; left: 0; border-radius: 10px; pointer-events: none;"></canvas>
        </div>
    `,
    )
    .join("")

  addLightningEffects()
}

function addLightningEffects() {
  const cards = document.querySelectorAll(".candidate-card")
  cards.forEach((card) => {
    card.addEventListener("mouseenter", () => {
      createLightningSparks(card)
    })
  })
}

function createLightningSparks(card) {
  const canvas = card.querySelector(".lightning-canvas")
  if (!canvas) return

  const ctx = canvas.getContext("2d")
  ctx.clearRect(0, 0, canvas.width, canvas.height)

  // Draw random lightning sparks
  for (let i = 0; i < 3; i++) {
    const x = Math.random() * canvas.width
    const y = Math.random() * canvas.height
    drawLightningSpark(ctx, x, y)
  }

  // Clear after animation
  setTimeout(() => {
    ctx.clearRect(0, 0, canvas.width, canvas.height)
  }, 200)
}

function drawLightningSpark(ctx, x, y) {
  ctx.strokeStyle = "#d4d94a"
  ctx.lineWidth = 2
  ctx.globalAlpha = 0.8

  ctx.beginPath()
  ctx.moveTo(x, y)

  for (let i = 0; i < 5; i++) {
    const offsetX = (Math.random() - 0.5) * 20
    const offsetY = (Math.random() - 0.5) * 20
    ctx.lineTo(x + offsetX, y + offsetY)
  }

  ctx.stroke()
  ctx.globalAlpha = 1
}

window.activateVoting = (voter) => {
  currentVoter = voter
  document.getElementById("standbyScreen").style.display = "none"
  document.getElementById("votingScreen").style.display = "block"
  document.getElementById("voterName").textContent = voter.name
  socket.emit("bilik_ack", { voter_nim: voter.nim })
}

function selectCandidate(candidateId, candidateName) {
  selectedCandidate = { id: candidateId, name: candidateName }
  document.getElementById("selectedCandidateName").textContent = candidateName
  document.getElementById("confirmModal").classList.add("active")
}

window.cancelVote = () => {
  document.getElementById("confirmModal").classList.remove("active")
  selectedCandidate = null
}

window.confirmVote = async () => {
  if (!currentVoter || !selectedCandidate) return

  document.getElementById("confirmModal").classList.remove("active")
  document.getElementById("votingScreen").style.display = "none"
  document.getElementById("loadingScreen").style.display = "flex"

  try {
    const response = await fetch("/api/vote", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        nim: currentVoter.nim,
        candidate_id: selectedCandidate.id,
      }),
    })

    if (response.ok) {
      setTimeout(() => {
        window.location.href = "/thankyou"
      }, 1000)
    } else {
      alert("Terjadi kesalahan saat merekam suara")
      document.getElementById("loadingScreen").style.display = "none"
      document.getElementById("votingScreen").style.display = "block"
    }
  } catch (err) {
    console.error("Error voting:", err)
    alert("Terjadi kesalahan")
    document.getElementById("loadingScreen").style.display = "none"
    document.getElementById("votingScreen").style.display = "block"
  }
}
