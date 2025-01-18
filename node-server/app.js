const db = require("better-sqlite3")("site_info_2025-01-08.db");
db.pragma("journal_mode = WAL");
const express = require("express");
const cors = require("cors");
const app = express();
const port = 3000;
app.use(cors());

app.listen(port);

app.get(
  "/get-question/:site/:difficulty",
  ({ params: { site, difficulty } }, res) => {
    const depth = difficulty === "easy" ? 0 : difficulty === "normal" ? 1 : 2;
    const {
      question,
      correct,
      wrong1,
      wrong2,
      wrong3,
      loaded_url,
      title,
      from_site_id,
    } = db
      .prepare(
        `
          SELECT 
          sites.site, sites.from_site_id, sites.id, sites.title, sites.loaded_url, questions.question, questions.correct, questions.wrong1, questions.wrong2, questions.wrong3 
          FROM questions 
          INNER JOIN sites 
          ON questions.site_id = sites.id 
          WHERE sites.depth =? 
          AND sites.site =? ORDER BY RANDOM() LIMIT 1`,
      )
      .get(depth, site);
    const shortestPath = [];
    for (let prevSiteId = from_site_id; prevSiteId; ) {
      const shortestPathSite = db
        .prepare(
          `
            SELECT sites.loaded_url, sites.from_site_id
            FROM sites
            WHERE id =?`,
        )
        .get(prevSiteId);
      prevSiteId = shortestPathSite.from_site_id;
      shortestPath.push(shortestPathSite.loaded_url);
    }
    res.send({
      question,
      responses: [correct, wrong1, wrong2, wrong3],
      loaded_url,
      title,
      site,
      from_site_id,
    });
  },
);
