const db = require("better-sqlite3")("site_info_2025-01-08.db");
db.pragma("journal_mode = WAL");
const express = require("express");
const app = require("cors");
const port = 3000;
app.use(cors());

app.listen(port);

app.get(
//routes


)