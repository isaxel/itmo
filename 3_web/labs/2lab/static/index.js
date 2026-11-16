'use strict';


const API_URL = '/fcgi-bin/2lab.jar';

const X_MIN = -5;
const X_MAX = 3;
const Y_MIN = -5;
const Y_MAX = 3;
const R_VALUES = [1, 1.5, 2, 2.5, 3];

const NUMBER_RE = /^-?\d{1,12}([.,]\d{1,14})?$/;

const NUMBER_FMT = new Intl.NumberFormat('en-US', { maximumFractionDigits: 14, useGrouping: false });


const form = document.getElementById('pointForm');
const xInput = document.getElementById('xInput');
const yInput = document.getElementById('yInput');
const rRadios = document.querySelectorAll('input[name="r"]');
const xError = document.getElementById('xError');
const yError = document.getElementById('yError');
const serverError = document.getElementById('serverError');
const serverNow = document.getElementById('serverNow');
const submitBtn = document.getElementById('submitBtn');
const clearBtn = document.getElementById('clearBtn');
const resultsBody = document.getElementById('resultsBody');
const emptyMsg = document.getElementById('emptyMsg');
const canvas = document.getElementById('graph');
const ctx = canvas.getContext('2d');

let results = [];
let busy = false;


function parseNumber(str) {
    const s = str.trim();
    if (!NUMBER_RE.test(s)) {
        return NaN;
    }
    return Number(s.replace(',', '.'));
}

function validateCoord(input, name, min, max) {
    const raw = input.value.trim();
    if (raw === '') {
        return { ok: false, message: `Введите ${name}` };
    }
    const v = parseNumber(raw);
    if (Number.isNaN(v)) {
        return { ok: false, message: `${name} должен быть числом (не больше 14 знаков после запятой)` };
    }
    if (!(v > min && v < max)) {
        return { ok: false, message: `${name} должен быть в интервале (${min} … ${max})` };
    }
    return { ok: true, value: v, raw: raw.replace(',', '.') };
}

function validateX() {
    return validateCoord(xInput, 'X', X_MIN, X_MAX);
}

function validateY() {
    return validateCoord(yInput, 'Y', Y_MIN, Y_MAX);
}

function validateR() {
    const checked = document.querySelector('input[name="r"]:checked');
    if (!checked) {
        return { ok: false, message: 'Выберите R' };
    }
    const r = Number(checked.value);
    if (!R_VALUES.includes(r)) {
        return { ok: false, message: 'Недопустимое значение R' };
    }
    return { ok: true, value: r, raw: checked.value };
}

function showFieldState(input, errorEl, check, showEmptyError) {
    const isEmpty = input && input.value.trim() === '';
    if (check.ok || (isEmpty && !showEmptyError)) {
        errorEl.textContent = '';
        if (input) input.classList.remove('formInputInvalid');
    } else {
        errorEl.textContent = check.message;
        if (input) input.classList.add('formInputInvalid');
    }
}

function updateFormState(showEmptyErrors = false) {
    const x = validateX();
    const y = validateY();
    const r = validateR();

    showFieldState(xInput, xError, x, showEmptyErrors);
    showFieldState(yInput, yError, y, showEmptyErrors);

    submitBtn.disabled = busy || !(x.ok && y.ok && r.ok);
    drawGraph();
    return { x, y, r };
}

function filterInput(event) {
    const input = event.target;
    const cleaned = input.value.replace(/[^0-9.,-]/g, '');
    if (cleaned !== input.value) {
        input.value = cleaned;
    }
    updateFormState();
}



async function callServer(params) {
    let response;
    try {
        response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8' },
            body: new URLSearchParams(params).toString(),
            cache: 'no-store'
        });
    } catch (e) {
        throw new Error('Сервер недоступен');
    }

    let data;
    try {
        data = await response.json();
    } catch (e) {
        throw new Error(`Некорректный ответ сервера (HTTP ${response.status})`);
    }

    if (typeof data.serverTime === 'number') {
        serverNow.textContent = formatDate(data.serverTime);
    }
    if (!data.ok) {
        throw new Error(data.reason || `Ошибка сервера (HTTP ${response.status})`);
    }
    return data;
}

function acceptResults(list) {
    results = (Array.isArray(list) ? list : [])
        .map(item => ({
            x: Number(item.x),
            y: Number(item.y),
            r: Number(item.r),
            hit: item.hit === true,
            time: Number(item.time),
            executionTime: Number(item.executionTime)
        }))
        .filter(item => [item.x, item.y, item.r, item.time].every(Number.isFinite));
    renderTable();
    drawGraph();
}

async function withBusy(action) {
    busy = true;
    submitBtn.disabled = true;
    clearBtn.disabled = true;
    serverError.textContent = '';
    try {
        await action();
    } catch (e) {
        serverError.textContent = e.message;
    } finally {
        busy = false;
        clearBtn.disabled = false;
        updateFormState();
    }
}



function formatDate(timestamp) {
    return new Date(timestamp).toLocaleString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        timeZoneName: 'short'
    });
}

function createCell(text, className) {
    const td = document.createElement('td');
    td.textContent = text;
    if (className) td.className = className;
    return td;
}

function renderTable() {
    resultsBody.innerHTML = '';

    for (let i = results.length - 1; i >= 0; i--) {
        const item = results[i];
        const tr = document.createElement('tr');
        tr.append(
            createCell(NUMBER_FMT.format(item.x)),
            createCell(NUMBER_FMT.format(item.y)),
            createCell(NUMBER_FMT.format(item.r)),
            createCell(item.hit ? 'Попадание' : 'Промах',
                item.hit ? 'resultHit' : 'resultMiss'),
            createCell(formatDate(item.time)),
            createCell(String(item.executionTime))
        );
        resultsBody.append(tr);
    }

    emptyMsg.classList.toggle('hidden', results.length > 0);
}



const SIZE = canvas.width;
const CENTER = SIZE / 2;
const R_PX_MAX = 150;
const EDGE = 20;
let R_PX = R_PX_MAX;

const HIT_COLOR = '#a8ff3e';
const MISS_COLOR = '#ff3b3b';

function getDisplayR() {
    const rCheck = validateR();
    if (rCheck.ok) return rCheck.value;
    if (results.length > 0) return results[results.length - 1].r;
    return null;
}

function updateScale(r) {
    let maxK = 1.15;
    if (r !== null) {
        for (const item of results) {
            if (item.r !== r) continue;
            maxK = Math.max(maxK, Math.abs(item.x) / r, Math.abs(item.y) / r);
        }
    }
    R_PX = Math.min(R_PX_MAX, (CENTER - EDGE) / maxK);
}

function drawGraph() {
    const displayR = getDisplayR();
    updateScale(displayR);

    ctx.clearRect(0, 0, SIZE, SIZE);
    ctx.fillStyle = '#101d13';
    ctx.fillRect(0, 0, SIZE, SIZE);

    ctx.fillStyle = '#2fb57a';

    // 1 четв: прямоугольник 0 <= x <= R, 0 <= y <= R/2
    ctx.fillRect(CENTER, CENTER - R_PX / 2, R_PX, R_PX / 2);

    ctx.beginPath();
    // 2 четв: треугольник (0,0), (-R/2,0), (0,R/2)
    ctx.moveTo(CENTER, CENTER);
    ctx.lineTo(CENTER - R_PX / 2, CENTER);
    ctx.lineTo(CENTER, CENTER - R_PX / 2);
    ctx.closePath();

    // 3 четв: четверть круга радиуса R/2
    ctx.moveTo(CENTER, CENTER);
    ctx.arc(CENTER, CENTER, R_PX / 2, Math.PI / 2, Math.PI, false);
    ctx.closePath();
    ctx.fill();

    ctx.strokeStyle = '#d5dde6';
    ctx.fillStyle = '#d5dde6';
    ctx.lineWidth = 1;

    ctx.beginPath();
    ctx.moveTo(10, CENTER);
    ctx.lineTo(SIZE - 10, CENTER);
    ctx.moveTo(CENTER, SIZE - 10);
    ctx.lineTo(CENTER, 10);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(SIZE - 10, CENTER);
    ctx.lineTo(SIZE - 20, CENTER - 5);
    ctx.lineTo(SIZE - 20, CENTER + 5);
    ctx.closePath();
    ctx.moveTo(CENTER, 10);
    ctx.lineTo(CENTER - 5, 20);
    ctx.lineTo(CENTER + 5, 20);
    ctx.closePath();
    ctx.fill();

    ctx.font = '14px Arial';
    ctx.fillText('x', SIZE - 18, CENTER - 10);
    ctx.fillText('y', CENTER + 10, 20);

    const marks = [
        { k: -1, label: '-R' },
        { k: -0.5, label: '-R/2' },
        { k: 0.5, label: 'R/2' },
        { k: 1, label: 'R' }
    ];

    ctx.font = '13px Arial';
    for (const { k, label } of marks) {
        if (R_PX < 60 && Math.abs(k) === 0.5) continue;

        const px = CENTER + k * R_PX;
        const py = CENTER - k * R_PX;

        ctx.beginPath();
        ctx.moveTo(px, CENTER - 4);
        ctx.lineTo(px, CENTER + 4);
        ctx.moveTo(CENTER - 4, py);
        ctx.lineTo(CENTER + 4, py);
        ctx.stroke();

        ctx.textAlign = 'center';
        ctx.fillText(label, px, CENTER - 10);
        ctx.textAlign = 'left';
        ctx.fillText(label, CENTER + 8, py + 4);
    }
    ctx.textAlign = 'left';

    drawPoints(displayR);
}

function drawPoints(r) {
    if (r === null) return;

    for (const item of results) {
        if (item.r !== r) continue;
        const px = CENTER + (item.x / r) * R_PX;
        const py = CENTER - (item.y / r) * R_PX;

        const color = item.hit ? HIT_COLOR : MISS_COLOR;
        ctx.beginPath();
        ctx.arc(px, py, 4, 0, Math.PI * 2);
        ctx.fillStyle = color;
        ctx.fill();
        ctx.lineWidth = 2;
        ctx.strokeStyle = color;
        ctx.stroke();
        ctx.lineWidth = 1;
    }
}



xInput.addEventListener('input', filterInput);
yInput.addEventListener('input', filterInput);

rRadios.forEach(radio => {
    radio.addEventListener('change', () => updateFormState());
});

form.addEventListener('submit', (event) => {
    event.preventDefault();

    const { x, y, r } = updateFormState(true);
    if (busy || !(x.ok && y.ok && r.ok)) {
        return;
    }

    withBusy(async () => {
        const data = await callServer({ action: 'check', x: x.raw, y: y.raw, r: r.raw });
        acceptResults(data.results);
    });
});

clearBtn.addEventListener('click', () => {
    withBusy(async () => {
        const data = await callServer({ action: 'clear' });
        acceptResults(data.results);
    });
});


renderTable();
drawGraph();
withBusy(async () => {
    const data = await callServer({ action: 'list' });
    acceptResults(data.results);
});
