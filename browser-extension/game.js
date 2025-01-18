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

let correctAnsSelected = false;
let onCorrectPage = false;

const { question, responses, title, loaded_url } = await getQnAndAns();
document
  .getElementById("titleFoundAt")
  .append(`The answer can be found at: ${title}`);

function pathTurnsGreen(url) {
  if (url.replace("www.", "") === loaded_url.replace("www.", "")) {
    onCorrectPage = true;
    document.getElementById("currentLocation").style = "color: green";
    checkWin();
  }
}

// Shows the path taken by the user to get to the correct link to answer the qn
const webpages = [];
chrome.tabs.onUpdated.addListener((tabId, info, { url, title }) => {
  if (webpages.length > 0 && url === webpages[webpages.length - 1].url) {
    webpages.pop();
  }
  pathTurnsGreen(url);
  webpages.push({ title, url });
  document.getElementById("linksClicked").innerHTML =
    `You have visited: ${webpages.map(({ title }) => title).join(" --> ")}`;
  document.getElementById("currentLocation").innerHTML =
    `You are currently at: ${title}`;
});

chrome.tabs.onActivated.addListener((tabId, info, { url, title }) => {
  document.getElementById("currentLocation").innerHTML =
    `You are currently at: ${title}`;
  pathTurnsGreen(url);
});
chrome.tabs
  .query({ active: true, lastFocusedWindow: true })
  .then(([{ url, title }]) => {
    document.getElementById("currentLocation").innerHTML =
      `You are currently at: ${title}`;
    pathTurnsGreen(url);
  });

let timeLeft = 120;
function checkWin() {
  if (correctAnsSelected && onCorrectPage) {
    clearInterval(intervalId);
    document
      .getElementById("winTimeTaken")
      .append(`You took ${120 - timeLeft} seconds to find the correct answer!`);
    document.getElementById("winDialogDisplay").style = "display: block";
    document.querySelector("dialog").showModal();
  }
}

// timer function
const timerElement = document.getElementById("timer");
timerElement.innerHTML = timeLeft;

const intervalId = setInterval(() => {
  timeLeft = parseInt(timerElement.innerText);
  if (timeLeft <= 0) {
    clearInterval(intervalId);
    document
      .getElementById("ansFoundAt")
      .append(`The answer could have been found at page ${loaded_url}`);
    document.getElementById("ansFoundAt").style = "display: block";
    document.getElementById("timesUpDialog").style = "display: block";
    document.querySelector("dialog").showModal();
  } else {
    timerElement.innerText = timeLeft - 1;
    const blinkId = setInterval(() => {
      const timeLeft = parseInt(timerElement.innerText);
      if (timeLeft <= 0) {
        clearInterval(blinkId);
      }
      if (timeLeft <= 10) {
        timerElement.style.borderColor = "red";
        setTimeout(() => (timerElement.style.borderColor = "black"), 500);
      }
    }, 1000);
  }
  const blinkId = setInterval(() => {
    const timeLeft = parseInt(timerElement.innerText);
    if (timeLeft <= 0) {
      clearInterval(blinkId);
    }
    if (timeLeft <= 10) {
      timerElement.style.borderColor = "red";
      setTimeout(() => (timerElement.style.borderColor = "black"), 500);
    }
  }, 1000);
}, 1000);

const questionElement = document.getElementById("question");
questionElement.innerHTML = question;
const correct = responses[0];
responses.sort(() => Math.random() - 0.5);
const buttons = responses.map((response, index) => {
  const button = document.createElement("button");
  button.id = `response${index}`;
  button.className = "ansButtons";
  button.innerText = response;
  button.addEventListener("click", () => {
    const timeLeft = parseInt(timerElement.innerText);
    if (button.innerText === correct) {
      correctAnsSelected = true;
      button.classList.add("correct");
      checkWin();
    } else if (button.innerText !== correct && attemptsLeft > 1) {
      button.classList.add("wrong");
      button.classList.add("disableAns");
      attemptsLeft--;
      numOfTriesElement.innerHTML = `Numbers of attempts left: ${attemptsLeft}`;
    } else if (timeLeft === 0) {
      document
        .getElementById("ansFoundAt")
        .append(`The answer could have been found at page ${loaded_url}`);
      document.getElementById("ansFoundAt").style = "display: block";
    } else {
      attemptsLeft--;
      numOfTriesElement.innerHTML = `No attempts left!`;
      clearInterval(intervalId);
      button.classList.add("wrong");
      button.classList.add("disableAns");

      document.getElementById("loseDialogDisplay").style = "display: block";
      document
        .getElementById("ansFoundAt")
        .append(`The answer can be found at page ${loaded_url}`);
      document.getElementById("ansFoundAt").style = "display: block";
      document.querySelector("dialog").showModal();
    }
  });

  return button;
});
questionElement.after(...buttons);
