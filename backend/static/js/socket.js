// Import the Socket.IO client library
const io = window.io

const socket = io()

socket.on("connect", () => {
  console.log("[v0] Connected to server")
})

socket.on("disconnect", () => {
  console.log("[v0] Disconnected from server")
})

socket.on("voter_arrived", (data) => {
  console.log("[v0] Voter arrived:", data)
  if (window.updateQueueDisplay) {
    window.updateQueueDisplay(data)
  }
})

socket.on("bilik_activate", (data) => {
  console.log("[v0] Booth activated:", data)
  if (window.activateVoting) {
    window.activateVoting(data.voter)
  }
})

socket.on("vote_update", (stats) => {
  console.log("[v0] Vote update:", stats)
  if (window.updateStats) {
    window.updateStats(stats)
  }
  if (window.updateChart) {
    window.updateChart(stats)
  }
})

socket.on("bilik_reset", (data) => {
  console.log("[v0] Booth reset:", data)
})
