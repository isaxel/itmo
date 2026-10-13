'use strict';


const X_MIN = -5;
const X_MAX = 3;
const R_MIN = 1;
const R_MAX = 4;
const Y_VALUES = [-3, -2, -1, 0, 1, 2, 3, 4, 5];

const STORAGE_KEY = 'lab1-results';

// минус, 8 зн посл точки
const NUMBER_RE = /^-?\d{1,12}([.,]\d{1,8})?$/;


const form = document.getElementById('pointForm');
const xInput = document.getElementById('xInput');
const rInput = document.getElementById('rInput');
const yRadios = document.querySelectorAll('input[name="y"]');
const xError = document.getElementById('xError');
const rError = document.getElementById('rError');
const submitBtn = document.getElementById('submitBtn');
const clearBtn = document.getElementById('clearBtn');
const resultsBody = document.getElementById('resultsBody');
const emptyMsg = document.getElementById('emptyMsg');
const canvas = document.getElementById('graph');
const ctx = canvas.getContext('2d');

let results = loadResults();


function parseNumber(str) {
    const s = str.trim();
    if (!NUMBER_RE.test(s)) {
        return NaN;
    }
    return Number(s.replace(',', '.'));
}

function validateX() {
    const raw = xInput.value.trim();
    if (raw === '') {
        return { ok: false, message: 'Введите X' };
    }
    const x = parseNumber(raw);
    if (Number.isNaN(x)) {
        return { ok: false, message: 'X должен быть числом' };
    }
    if (!(x >= X_MIN && x <= X_MAX)) {
        return { ok: false, message: `X должен быть от ${X_MIN} до ${X_MAX}` };
    }
    return { ok: true, value: x };
}

function validateY() {
    const checked = document.querySelector('input[name="y"]:checked');
    if (!checked) {
        return { ok: false, message: 'Выберите Y' };
    }
    const y = Number(checked.value);
    if (!Y_VALUES.includes(y)) {
        return { ok: false, message: 'Недопустимое значение Y' };
    }
    return { ok: true, value: y };
}

function validateR() {
    const raw = rInput.value.trim();
    if (raw === '') {
        return { ok: false, message: 'Введите R' };
    }
    const r = parseNumber(raw);
    if (Number.isNaN(r)) {
        return { ok: false, message: 'R должен быть числом' };
    }
    if (!(r >= R_MIN && r <= R_MAX)) {
        return { ok: false, message: `R должен быть от ${R_MIN} до ${R_MAX}` };
    }
    return { ok: true, value: r };
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
    showFieldState(rInput, rError, r, showEmptyErrors);

    submitBtn.disabled = !(x.ok && y.ok && r.ok);
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


function checkHit(x, y, r) {
    if (x >= 0 && y >= 0) {
        return x * x + y * y <= r * r;
    }
    if (x <= 0 && y >= 0) {
        return y <= x / 2 + r / 2;
    }
    if (x <= 0 && y <= 0) {
        return x >= -r && y >= -r / 2;
    }
    return false;
}


function loadResults() {
    try {
        const data = JSON.parse(localStorage.getItem(STORAGE_KEY));
        if (!Array.isArray(data)) return [];
        return data.filter(item =>
            item &&
            typeof item.x === 'number' &&
            typeof item.y === 'number' &&
            typeof item.r === 'number' &&
            typeof item.hit === 'boolean' &&
            typeof item.time === 'number'
        );
    } catch (e) {
        return [];
    }
}

function saveResults() {
    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(results));
    } catch (e) {
        console.error('Не удалось сохранить результаты', e);
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
            createCell(String(item.x)),
            createCell(String(item.y)),
            createCell(String(item.r)),
            createCell(item.hit ? 'Попадание' : 'Промах',
                item.hit ? 'resultHit' : 'resultMiss'),
            createCell(formatDate(item.time))
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
    ctx.beginPath();

    // 1четв
    ctx.moveTo(CENTER, CENTER);
    ctx.arc(CENTER, CENTER, R_PX, -Math.PI / 2, 0, false);
    ctx.closePath();

    // 2четв
    ctx.moveTo(CENTER, CENTER);
    ctx.lineTo(CENTER - R_PX, CENTER);
    ctx.lineTo(CENTER, CENTER - R_PX / 2);
    ctx.closePath();

    ctx.fill();

    // 3четв
    ctx.fillRect(CENTER - R_PX, CENTER, R_PX, R_PX / 2);

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
rInput.addEventListener('input', filterInput);

yRadios.forEach(radio => {
    radio.addEventListener('change', () => updateFormState());
});

form.addEventListener('submit', (event) => {
    event.preventDefault();

    const { x, y, r } = updateFormState(true);
    if (!(x.ok && y.ok && r.ok)) {
        return;
    }

    results.push({
        x: x.value,
        y: y.value,
        r: r.value,
        hit: checkHit(x.value, y.value, r.value),
        time: Date.now()
    });

    saveResults();
    renderTable();
    drawGraph();
});

clearBtn.addEventListener('click', () => {
    results = [];
    saveResults();
    renderTable();
    drawGraph();
});

window.addEventListener('focus', renderTable);


renderTable();
drawGraph();
