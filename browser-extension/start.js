import { domains } from "./domains.js";

function enableDisableButton(url) {
  const { origin } = new URL(url);
  if (domains.hasOwnProperty(origin)) {
    for (const difficulty of ["easy", "normal", "hard"]) {
      document.getElementById(difficulty).classList.remove("disableClick");
    }
  } else {
    for (const difficulty of ["easy", "normal", "hard"]) {
      document.getElementById(difficulty).classList.add("disableClick");
    }
  }
}

// Checks that the user is on the correct site and disable or enables the buttons accordingly
chrome.tabs
  .query({ active: true, lastFocusedWindow: true })
  .then(([{ url }]) => enableDisableButton(url));

//enable buttons when user is on correct sites

chrome.tabs.onActivated.addListener(() => {
  chrome.tabs
    .query({ active: true, lastFocusedWindow: true })
    .then(([{ url }]) => enableDisableButton(url));
});

chrome.tabs.onUpdated.addListener(() => {
  chrome.tabs
    .query({ active: true, lastFocusedWindow: true })
    .then(([{ url }]) => enableDisableButton(url));
});
