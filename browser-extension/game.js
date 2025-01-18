import { domains } from "./domains.js";

// Get question and answer from backend
async function getQnAndAns() {
  const [{ url }] = await chrome.tabs.query({
    active: true,
    lastFocusedWindow: true,
  });
  const { origin } = new URL(url);
  const res = {
    question: "What colour is the sky?",
    correct: "blue",
    wrong1: "purple",
    wrong2: "pink",
    wrong3: "yellow  ",
  };

  return res;
}

let attemptsLeft = 2;
const numOfTriesElement = document.getElementById("numberOfTries");
document.getElementById("numberOfTries").innerHTML =
  `Numbers of attempts left: ${attemptsLeft}`;
