/**
 * Экспорт колоды в сторонние форматы.
 *
 *   node scripts/export.mjs
 *
 * Кладёт в export/:
 *   anki.tsv        импорт в Anki (Вопрос / Ответ / Теги), ответ размечен <br> и <li>
 *   quizlet.txt     вставка в Quizlet: термин TAB определение, карточки через пустую строку
 *   cards.csv       таблица для Excel, Google Sheets, любой обработки
 *   cards.md        конспект-шпаргалка по разделам с оглавлением
 *   print.html      версия для печати и сохранения в PDF (Ctrl+P)
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const cards = JSON.parse(fs.readFileSync(path.join(root, "data", "cards.json"), "utf8"));
const out = path.join(root, "export");
fs.mkdirSync(out, { recursive: true });
const w = (name, text) => fs.writeFileSync(path.join(out, name), text);

const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const tag = (topic) => topic.replace(/\s+/g, "_").replace(/[^\wА-Яа-яЁё_-]/g, "");
const oneLine = (s) => String(s).replace(/[\t\r\n]+/g, " ").trim();

/* --- Anki: три поля, разделитель — табуляция, HTML внутри поля --- */
w(
  "anki.tsv",
  "#separator:tab\n#html:true\n#tags column:3\n" +
    cards
      .map((c) => {
        const [lead, ...rest] = c.answer;
        const body =
          esc(lead) + (rest.length ? "<ul><li>" + rest.map(esc).join("</li><li>") + "</li></ul>" : "");
        return [oneLine("№" + c.id + ". " + c.question), body.replace(/\t/g, " "), "архитектура " + tag(c.topic)].join("\t");
      })
      .join("\n") + "\n"
);

/* --- Quizlet: термин TAB определение, между карточками пустая строка --- */
w(
  "quizlet.txt",
  cards.map((c) => oneLine(c.question) + "\t" + c.answer.map(oneLine).join(" • ")).join("\n\n") + "\n"
);

/* --- CSV (RFC 4180) --- */
const q = (s) => '"' + String(s).replace(/"/g, '""') + '"';
w(
  "cards.csv",
  "﻿id,topic,question,answer\n" +
    cards.map((c) => [c.id, q(c.topic), q(c.question), q(c.answer.join("\n"))].join(",")).join("\n") + "\n"
);

/* --- Markdown: шпаргалка по разделам --- */
const byTopic = new Map();
for (const c of cards) {
  if (!byTopic.has(c.topic)) byTopic.set(c.topic, []);
  byTopic.get(c.topic).push(c);
}
let md = "# Архитектура компьютера — ответы на экзаменационные вопросы\n\n";
md += `Всего вопросов: ${cards.length}. Разделов: ${byTopic.size}.\n\n## Оглавление\n\n`;
for (const [topic, list] of byTopic) {
  md += `- [${topic}](#${topic.toLowerCase().replace(/[^\wА-Яа-яЁё]+/g, "-")}) — ${list.length}\n`;
}
md += "\n";
for (const [topic, list] of byTopic) {
  md += `\n## ${topic}\n`;
  for (const c of list) {
    md += `\n### ${c.id}. ${c.question}\n\n`;
    md += c.answer.map((line, i) => (i === 0 ? line : "- " + line)).join("\n") + "\n";
  }
}
w("cards.md", md);

/* --- HTML для печати и PDF --- */
let ph = `<!doctype html><html lang="ru"><head><meta charset="utf-8">
<title>Архитектура компьютера — ${cards.length} вопросов</title>
<style>
 body{font:11pt/1.45 Georgia,serif;color:#111;max-width:190mm;margin:0 auto;padding:14mm 10mm}
 h1{font:600 20pt/1.2 system-ui,sans-serif;margin:0 0 4mm}
 h2{font:600 13pt/1.2 system-ui,sans-serif;margin:9mm 0 3mm;padding-bottom:1mm;border-bottom:1px solid #999;
    break-after:avoid}
 .card{break-inside:avoid;margin:0 0 5mm}
 .q{font:600 11.5pt/1.3 system-ui,sans-serif;margin:0 0 1.5mm}
 .q span{color:#666;font-weight:400}
 ul{margin:0;padding-left:5mm} li{margin:0 0 1mm}
 p.lead{margin:0 0 1.5mm}
 @page{margin:14mm}
</style></head><body>
<h1>Архитектура компьютера — ответы на ${cards.length} вопросов</h1>`;
for (const [topic, list] of byTopic) {
  ph += `<h2>${esc(topic)}</h2>`;
  for (const c of list) {
    const [lead, ...rest] = c.answer;
    ph += `<div class="card"><p class="q"><span>${c.id}.</span> ${esc(c.question)}</p><p class="lead">${esc(lead)}</p>`;
    if (rest.length) ph += "<ul><li>" + rest.map(esc).join("</li><li>") + "</li></ul>";
    ph += "</div>";
  }
}
ph += "</body></html>\n";
w("print.html", ph);

console.log("export/: anki.tsv, quizlet.txt, cards.csv, cards.md, print.html");
