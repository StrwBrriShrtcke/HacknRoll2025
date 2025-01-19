# Introduction
<!--toc:start-->
- [Introduction](#Introduction)
- [Directory](#Directory)
- [Usage](#Usage)
- [How it works](#how-it-works)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Scope](#scope)
- [Data Analysis](#data-analysis)
- [Appendix](#appendix)
<!--toc:end-->


# Directory
browser-extension
llm
node-server
data-analysis

# Usage
1. Clone the directory `git clone https://github.com/StrwBrriShrtcke/HacknRoll2025.git`
2. cd into browser-extension and node-server, then install the neccessary packages with `npm install`
3. cd into node-server and run the server `node app.js`

# How it works
- Use a browser extension 
- Ask the user a trivia MCQ question whose answer can be retrieved from a website. (Potentially requiring the user to click some links)
- Present results:
  - Time taken 📈
  - The correct answer ✅
  - Where the information is (which webpage and where in the page) 📄
- Difficulty mode:
  - Easy: info can be found in up to 1 click (0 link clicks)
  - Medium: info can be found in up to 3 clicks (1 link clicks)
  - Hard: info can be found in up to 5 clicks (2 link clicks)

# Tech stack
- Browser extension frontend
  - [chrome browser extension]()
- Backend server (to handle app logic and link frontend and database)
  - [node](https://nodejs.org/en)
  - [expressjs](https://expressjs.com/)
- Database (to store needed info)
  - [SQLite](https://www.sqlite.org/)
- LLM content generation
  - LLM: [Ollama](https://ollama.com/blog/structured-outputs)
- Web crawler/scraping
  - [crawlee](https://crawlee.dev/) 

# Architecture
- frontend extension measures and sends data to the backend.
- backend handles the logic and make relevant queries to the database if needed.
- database contains webpages of a website domain, and a relevant MCQ question with answers of that webpage, also where in the webpage that info is.
- web crawler will crawl through a domain to store relevant info of each webpage (link, clicks away from homepage, html content).
- llm will use the data collected by the webcrawler to generate mcq trivia (question, answers, where the info is).
- the relevant info will be stored in a database to be queried by the backend server.

# Scope
To keep the scope realistic, we make these concessions:
- the evaluation only starts at the homepage of a website (i.e. nus.edu.sg, www.sim.edu.sg, www.ntu.edu.sg, sutd.edu.sg ).
- we only choose a few websites (some sch websites) for this project.
- content is pregenerated beforehand (not generated on the fly).
- measure only up to 2 links deep (otherwise too much data and pointless to click so far away).

# Data Analysis
To showcase some of the reasons behind this project, we have conducted exploratory data analysis on the database created after web-scraping. These visualisations are included in the browser extension.
- data analysis was done in a jupyter notebook
- matplotlib used to generate data visualisations\
- analysis focused on the following:
  1. Comparisons between universities
  2. Key correlations and patterns

# Appendix
