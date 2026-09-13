/**
 * Сборка сайта из src/ и data/cards.json.
 *
 *   node scripts/build.mjs
 *
 * Результат — папка dist/:
 *   index.html   единый самодостаточный файл (CSS + JS + все карточки внутри),
 *                открывается двойным кликом с диска, работает без сервера и без сети;
 *   sw.js, manifest.webmanifest, icon.svg, cards.json — для установки как PWA при хостинге.
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const p = (...s) => path.join(root, ...s);
const read = (...s) => fs.readFileSync(p(...s), "utf8");

const cards = JSON.parse(read("data", "cards.json"));
if (!Array.isArray(cards) || !cards.length) throw new Error("data/cards.json пуст");

const html = read("src", "index.html");
const css = read("src", "styles.css");
const app = read("src", "app.js");

// Данные для рантайма: короткие ключи, как ожидает app.js
const runtime = cards.map((c) => ({ t: c.topic, q: c.question, a: c.answer }));
const dataScript = "window.CARDS=" + JSON.stringify(runtime) + ";";

let out = html
  .replace(/\s*<link rel="stylesheet" href="\.\/styles\.css">/, "\n<style>\n" + css + "\n</style>")
  .replace(
    /\s*<script src="\.\/app\.js"><\/script>/,
    "\n<script>\n" + dataScript + "\n</script>\n<script>\n" + app + "\n</script>"
  );

const dist = p("dist");
fs.rmSync(dist, { recursive: true, force: true });
fs.mkdirSync(dist, { recursive: true });
fs.writeFileSync(path.join(dist, "index.html"), out);
for (const f of ["sw.js", "manifest.webmanifest", "icon.svg"]) {
  fs.copyFileSync(p("src", f), path.join(dist, f));
}
fs.copyFileSync(p("data", "cards.json"), path.join(dist, "cards.json"));

const kb = (fs.statSync(path.join(dist, "index.html")).size / 1024).toFixed(0);
console.log(`dist/index.html — ${cards.length} карточек, ${kb} КБ, автономный файл`);
console.log("dist/ также содержит sw.js, manifest.webmanifest, icon.svg, cards.json");
