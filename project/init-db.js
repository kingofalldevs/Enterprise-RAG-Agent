const Database = require('better-sqlite3');
const db = new Database('sqlite.db');

db.exec(`
CREATE TABLE IF NOT EXISTS Chat (
  id TEXT PRIMARY KEY NOT NULL,
  createdAt INTEGER NOT NULL,
  messages TEXT NOT NULL,
  author TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Chunk (
  id TEXT PRIMARY KEY NOT NULL,
  filePath TEXT NOT NULL,
  content TEXT NOT NULL,
  embedding TEXT NOT NULL
);
`);

console.log("Database initialized");
