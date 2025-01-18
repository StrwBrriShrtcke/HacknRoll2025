import { domains } from "./domains.js";
const params = new URLSearchParams(window.location.search);

// Get question and answer from backend
async function getQnAndAns() {
  const [{ url }] = await chrome.tabs.query({
    active: true,
    lastFocusedWindow: true,
  });
  const { origin } = new URL(url);
  const res = await fetch(
    `http://localhost:3000/get-question/${domains[origin]}/${params.get("difficulty")}`,
  );
  return await res.json();
}

let attemptsLeft = 2;
const numOfTriesElement = document.getElementById("numberOfTries");
document.getElementById("numberOfTries").innerHTML =
  `Numbers of attempts left: ${attemptsLeft}`;
