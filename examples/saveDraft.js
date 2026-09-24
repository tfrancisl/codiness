const fs = require("fs");
const path = require("path");

function saveDraft(dir, id, text) {
  fs.mkdirSync(dir, { recursive: true });
  const file = path.join(dir, `${id}.md`);
  fs.writeFileSync(file, text, "utf8");
  console.log(`saved draft ${id}`);
  return file;
}

module.exports = { saveDraft };
