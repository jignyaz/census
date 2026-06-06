/* ============================================
   CENSUS SURVEY — WIZARD LOGIC
   ============================================ */

// ===== Questions Data =====
const QUESTIONS = [
    { key: 'census_house_number', label: 'Census house number', type: 'number' },
    { key: 'floor_material', label: 'Main material of floor', type: 'radio',
      options: ['Soil/Mud','Tiles/Bricks','Stone-slab flooring','Stones','Cement','Mosaic / Vitrified tiles','Other materials'] },
    { key: 'wall_material', label: 'Main material of walls', type: 'radio',
      options: ['Soil/Mud','Tiles/Bricks','Stone-slab flooring','Stones','Cement','Mosaic / Vitrified tiles','Other materials'] },
    { key: 'ceiling_material', label: 'Main material of ceiling', type: 'radio',
      options: ['Polythene','Mud','Penkulu','Burnt Bricks','Stone','Asbestos Sheets','Concrete','Other materials'] },
    { key: 'building_usage', label: 'Building usage', type: 'radio',
      options: ['House','Rent','Shop','School','Hotel','Hospital','Devotional Place','Empty'] },
    { key: 'building_condition', label: 'Condition of building', type: 'radio',
      options: ['Livable','Non Livable','Broken'] },
    { key: 'num_people', label: 'Number of people in house', type: 'number' },
    { key: 'head_of_family', label: 'Name of head of family', type: 'text' },
    { key: 'gender', label: 'Gender', type: 'radio', options: ['Male','Female','N/A'] },
    { key: 'rooms', label: 'Rooms in house', type: 'number' },
    { key: 'married_pairs', label: 'Married pairs in house', type: 'number' },
    { key: 'water_source', label: 'Drinking water source', type: 'radio',
      options: ['Purified water','Well','Hand pump','Lake','River','Packaged water','Other sources'] },
    { key: 'water_location', label: 'Location of water sources', type: 'radio',
      options: ['In premises','Community','In range of 500m'] },
    { key: 'light_source', label: 'Light source', type: 'radio',
      options: ['Electricity','Kerosene','Solar power','Any oil','No sunlight','Any other'] },
    { key: 'sanitation', label: 'Sanitation facilities', type: 'radio',
      options: ['Usage only for family','Shared by community','Walkable distance'] },
    { key: 'restroom', label: 'Rest room', type: 'radio', options: ['Yes','No'] },
    { key: 'sewage', label: 'Sewage flow', type: 'radio', options: ['Septic tank','Rings','N/A'] },
    { key: 'bathing', label: 'In premises bathing facilities', type: 'radio',
      options: ['Bathroom','No roof','N/A'] },
    { key: 'cooking_gas', label: 'Cooking gas', type: 'radio', options: ['LPG/PNG','N/A'] },
    { key: 'cooking_fuel', label: 'Cooking fuel', type: 'radio',
      options: ['Wood','Grass (dry)','Cow dung cakes','Kerosene','Electricity','Solar cooker','Biogas'] },
    { key: 'radio_transmitter', label: 'Radio transmitter', type: 'radio',
      options: ['Radio','Smartphone','N/A'] },
    { key: 'tv', label: 'TV', type: 'radio',
      options: ['Doordarshan','DTH connection','Cable connection','Other','N/A'] },
    { key: 'internet', label: 'Internet connection', type: 'radio', options: ['Yes','No'] },
    { key: 'laptop_computer', label: 'Laptop / Computer', type: 'radio', options: ['Yes','No'] },
    { key: 'transportation', label: 'Transportation mode', type: 'radio',
      options: ['Cycle','Bike','Car','ATB','N/A'] },
    { key: 'primary_food', label: 'Primary consumed food', type: 'text' },
    { key: 'phone_number', label: 'Phone number', type: 'phone' },
];

const STORAGE_KEY = 'census_responses';
const ALL_KEYS = QUESTIONS.map(q => q.key);

// ===== State =====
let responses = loadResponses();
let currentSlide = 0;
const totalSlides = QUESTIONS.length + 1; // +1 for submit slide
const answers = {};

// ===== Init =====
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('prog-total').textContent = QUESTIONS.length;
    buildSlides();
    showSlide(0);
    renderResponses();
});

// ===== Build Slides =====
function buildSlides() {
    const container = document.getElementById('slides-container');

    QUESTIONS.forEach((q, i) => {
        const slide = document.createElement('div');
        slide.className = 'question-slide';
        slide.id = `slide-${i}`;

        let inputHTML = '';
        if (q.type === 'radio') {
            inputHTML = '<div class="radio-grid">' +
                q.options.map(opt => `
                    <label class="radio-pill">
                        <input type="radio" name="${q.key}" value="${opt}" onchange="onAnswer('${q.key}','${opt}',${i})">
                        <span class="radio-dot"></span>
                        <span class="radio-pill-label">${opt}</span>
                    </label>`).join('') + '</div>';
        } else {
            const phText = q.type === 'phone' ? '10-digit phone number' : 'Type your answer...';
            const inpType = q.type === 'phone' ? 'tel' : q.type;
            const maxLen = q.type === 'phone' ? ' maxlength="10"' : '';
            inputHTML = `<div class="wizard-input-wrap">
                <input type="${inpType}" class="wizard-input" id="input-${q.key}" placeholder="${phText}"${maxLen}
                    onkeydown="handleEnter(event, ${i})" oninput="onTypeAnswer('${q.key}',this.value,${i})">
            </div>`;
        }

        slide.innerHTML = `
            <div class="q-card" id="qcard-${i}">
                <div class="q-number">Question ${i + 1} of ${QUESTIONS.length}</div>
                <div class="q-label">${q.label} <span class="required">*</span></div>
                ${inputHTML}
                <div class="q-error" id="qerr-${i}">⚠ This field is required</div>
            </div>
            <div class="wizard-nav">
                <button class="nav-arrow" onclick="prevSlide()" ${i === 0 ? 'disabled' : ''} aria-label="Previous">
                    <svg viewBox="0 0 24 24" fill="currentColor"><path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z"/></svg>
                </button>
                <div class="nav-dots" id="dots-${i}"></div>
                <button class="nav-arrow" onclick="nextSlide(${i})" aria-label="Next">
                    <svg viewBox="0 0 24 24" fill="currentColor"><path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"/></svg>
                </button>
            </div>`;

        container.appendChild(slide);
    });

    // Submit slide
    const submitSlide = document.createElement('div');
    submitSlide.className = 'question-slide submit-slide';
    submitSlide.id = `slide-${QUESTIONS.length}`;
    submitSlide.innerHTML = `
        <div class="q-card">
            <div class="q-number">Almost done!</div>
            <div class="q-label" style="margin-bottom:12px">Ready to submit your response?</div>
            <p class="submit-summary">You have answered all ${QUESTIONS.length} questions. Click below to save your census data.</p>
            <button class="btn-submit-main" onclick="submitForm()">Submit Response</button>
        </div>
        <div class="wizard-nav">
            <button class="nav-arrow" onclick="prevSlide()" aria-label="Previous">
                <svg viewBox="0 0 24 24" fill="currentColor"><path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z"/></svg>
            </button>
            <div class="nav-dots" id="dots-${QUESTIONS.length}"></div>
            <button class="nav-arrow" disabled aria-label="Next">
                <svg viewBox="0 0 24 24" fill="currentColor"><path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"/></svg>
            </button>
        </div>`;
    container.appendChild(submitSlide);
}

// ===== Slide Navigation =====
function showSlide(idx) {
    document.querySelectorAll('.question-slide').forEach(s => {
        s.classList.remove('active');
        s.style.animation = '';
    });
    const slide = document.getElementById(`slide-${idx}`);
    slide.classList.add('active');
    slide.style.animation = 'none';
    slide.offsetHeight; // reflow
    slide.style.animation = 'slideIn 0.4s ease forwards';

    currentSlide = idx;
    updateProgress();
    renderDots();

    // Focus input if text type
    if (idx < QUESTIONS.length) {
        const q = QUESTIONS[idx];
        if (q.type !== 'radio') {
            setTimeout(() => {
                const inp = document.getElementById(`input-${q.key}`);
                if (inp) inp.focus();
            }, 400);
        }
    }
}

function nextSlide(fromIdx) {
    // Validate current
    if (fromIdx < QUESTIONS.length) {
        const q = QUESTIONS[fromIdx];
        const card = document.getElementById(`qcard-${fromIdx}`);
        const errEl = document.getElementById(`qerr-${fromIdx}`);

        let val = answers[q.key] || '';
        if (val === '') {
            card.classList.add('error-state');
            errEl.textContent = '⚠ This field is required';
            return;
        }
        if (q.type === 'phone' && !/^[0-9]{10}$/.test(val)) {
            card.classList.add('error-state');
            errEl.textContent = '⚠ Phone number must be exactly 10 digits';
            return;
        }
        card.classList.remove('error-state');
    }

    if (currentSlide < totalSlides - 1) {
        showSlide(currentSlide + 1);
    }
}

function prevSlide() {
    if (currentSlide > 0) showSlide(currentSlide - 1);
}

function handleEnter(e, idx) {
    if (e.key === 'Enter') { e.preventDefault(); nextSlide(idx); }
}

// ===== Answer Handlers =====
function onAnswer(key, value, idx) {
    answers[key] = value;
    document.getElementById(`qcard-${idx}`).classList.remove('error-state');
    // Auto-advance after radio selection
    setTimeout(() => nextSlide(idx), 350);
}

function onTypeAnswer(key, value, idx) {
    answers[key] = value.trim();
    document.getElementById(`qcard-${idx}`).classList.remove('error-state');
}

// ===== Progress =====
function updateProgress() {
    const num = Math.min(currentSlide + 1, QUESTIONS.length);
    document.getElementById('prog-current').textContent = num;
    const pct = ((currentSlide) / QUESTIONS.length) * 100;
    document.getElementById('progress-fill').style.width = Math.min(pct, 100) + '%';
}

function renderDots() {
    const dotsEl = document.getElementById(`dots-${currentSlide}`);
    if (!dotsEl) return;

    // Show a window of dots around current
    const maxDots = 9;
    let start = Math.max(0, currentSlide - Math.floor(maxDots / 2));
    let end = Math.min(totalSlides, start + maxDots);
    if (end - start < maxDots) start = Math.max(0, end - maxDots);

    let html = '';
    for (let i = start; i < end; i++) {
        let cls = 'nav-dot';
        if (i === currentSlide) cls += ' current';
        else if (i < currentSlide) cls += ' filled';
        html += `<div class="${cls}"></div>`;
    }
    dotsEl.innerHTML = html;
}

// ===== Submit =====
function submitForm() {
    // Final validation of all questions
    for (let i = 0; i < QUESTIONS.length; i++) {
        const q = QUESTIONS[i];
        if (!answers[q.key] || answers[q.key] === '') {
            showSlide(i);
            const card = document.getElementById(`qcard-${i}`);
            card.classList.add('error-state');
            return;
        }
        if (q.type === 'phone' && !/^[0-9]{10}$/.test(answers[q.key])) {
            showSlide(i);
            const card = document.getElementById(`qcard-${i}`);
            const errEl = document.getElementById(`qerr-${i}`);
            card.classList.add('error-state');
            errEl.textContent = '⚠ Phone number must be exactly 10 digits';
            return;
        }
    }

    const data = { ...answers };
    data.timestamp = new Date().toLocaleString();
    data.id = Date.now().toString();
    responses.push(data);
    saveResponses();

    // Show success
    document.getElementById('slides-container').style.display = 'none';
    document.getElementById('success-view').classList.add('active');
    document.querySelector('.wizard-progress').style.display = 'none';
    showToast('Response recorded successfully!');
}

function resetWizard() {
    // Clear answers
    Object.keys(answers).forEach(k => delete answers[k]);
    currentSlide = 0;

    // Reset all inputs
    document.querySelectorAll('.wizard-input').forEach(i => i.value = '');
    document.querySelectorAll('input[type="radio"]').forEach(r => r.checked = false);
    document.querySelectorAll('.q-card').forEach(c => c.classList.remove('error-state'));

    // Show slides
    document.getElementById('slides-container').style.display = 'block';
    document.getElementById('success-view').classList.remove('active');
    document.querySelector('.wizard-progress').style.display = 'flex';

    showSlide(0);
}

// ===== Tab Switching =====
function switchTab(tab) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.getElementById(`section-${tab}`).classList.add('active');
    document.getElementById('tab-questions').classList.toggle('active', tab === 'questions');
    document.getElementById('tab-responses').classList.toggle('active', tab === 'responses');
    if (tab === 'responses') renderResponses();
}

// ===== Storage =====
function loadResponses() {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY)) || []; }
    catch { return []; }
}
function saveResponses() { localStorage.setItem(STORAGE_KEY, JSON.stringify(responses)); }

// ===== Render Responses =====
function renderResponses() {
    renderSummaryStats();
    renderTable();
    document.getElementById('response-count').textContent = `${responses.length} response${responses.length !== 1 ? 's' : ''}`;
}

function renderSummaryStats() {
    const grid = document.getElementById('stats-grid');
    grid.innerHTML = '';
    if (responses.length === 0) return;

    const colors = ['#7c3aed','#06b6d4','#10b981','#f59e0b','#ef4444','#ec4899','#8b5cf6','#14b8a6'];
    QUESTIONS.filter(q => q.type === 'radio').forEach(q => {
        const counts = {};
        responses.forEach(r => { const v = r[q.key] || 'N/A'; counts[v] = (counts[v] || 0) + 1; });
        const total = responses.length;
        const bars = Object.entries(counts).sort((a, b) => b[1] - a[1]).map(([label, count], i) => {
            const pct = ((count / total) * 100).toFixed(1);
            return `<div class="stat-bar-row">
                <span class="stat-bar-label">${label}</span>
                <div class="stat-bar-track"><div class="stat-bar-fill" style="width:${pct}%;background:${colors[i % colors.length]}"></div></div>
                <span class="stat-bar-value">${count} (${pct}%)</span>
            </div>`;
        }).join('');
        grid.innerHTML += `<div class="stat-card"><div class="stat-card-title">${q.label}</div><div class="stat-bars">${bars}</div></div>`;
    });
}

function renderTable(filter = '') {
    const tbody = document.getElementById('resp-tbody');
    const thead = document.getElementById('resp-thead');
    const wrapper = document.getElementById('table-wrapper');
    const empty = document.getElementById('empty-state');

    const headers = ['#', 'Timestamp', ...QUESTIONS.map(q => q.label), 'Actions'];
    thead.innerHTML = '<tr>' + headers.map(h => `<th>${h}</th>`).join('') + '</tr>';

    const filtered = filter
        ? responses.filter(r => Object.values(r).some(v => String(v).toLowerCase().includes(filter.toLowerCase())))
        : responses;

    if (filtered.length === 0) {
        wrapper.style.display = 'none';
        empty.style.display = 'flex';
        return;
    }
    wrapper.style.display = 'block';
    empty.style.display = 'none';

    tbody.innerHTML = filtered.map((r, idx) =>
        `<tr><td>${idx + 1}</td><td>${r.timestamp || '-'}</td>` +
        ALL_KEYS.map(k => `<td>${r[k] || '-'}</td>`).join('') +
        `<td><button class="tbtn tbtn-view" onclick="viewDetail('${r.id}')">View</button><button class="tbtn tbtn-del" onclick="deleteResponse('${r.id}')">Delete</button></td></tr>`
    ).join('');
}

function filterResponses() { renderTable(document.getElementById('search-input').value); }

// ===== Modal =====
function viewDetail(id) {
    const r = responses.find(x => x.id === id);
    if (!r) return;
    document.getElementById('modal-body').innerHTML =
        `<div class="detail-row"><div class="detail-label">Submitted At</div><div class="detail-value">${r.timestamp}</div></div>` +
        QUESTIONS.map(q => `<div class="detail-row"><div class="detail-label">${q.label}</div><div class="detail-value">${r[q.key] || '-'}</div></div>`).join('');
    document.getElementById('detail-modal').classList.add('active');
}
function closeModal() { document.getElementById('detail-modal').classList.remove('active'); }
document.addEventListener('click', e => { if (e.target.id === 'detail-modal') closeModal(); });
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal(); });

// ===== Delete =====
function deleteResponse(id) {
    if (!confirm('Delete this response?')) return;
    responses = responses.filter(r => r.id !== id);
    saveResponses(); renderResponses(); showToast('Response deleted');
}
function deleteAllResponses() {
    if (!responses.length) return;
    if (!confirm(`Delete all ${responses.length} responses?`)) return;
    responses = []; saveResponses(); renderResponses(); showToast('All responses deleted');
}

// ===== CSV =====
function exportCSV() {
    if (!responses.length) { showToast('No responses to export'); return; }
    const headers = ['#', 'Timestamp', ...QUESTIONS.map(q => q.label)];
    const rows = responses.map((r, i) => [i + 1, r.timestamp, ...QUESTIONS.map(q => r[q.key] || '')]);
    let csv = headers.join(',') + '\n';
    rows.forEach(row => { csv += row.map(v => `"${String(v).replace(/"/g, '""')}"`).join(',') + '\n'; });
    const blob = new Blob([csv], { type: 'text/csv' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `census_${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    showToast('CSV exported!');
}

// ===== Toast =====
function showToast(msg) {
    const t = document.getElementById('toast');
    document.getElementById('toast-message').textContent = msg;
    t.classList.add('show');
    setTimeout(() => t.classList.remove('show'), 3000);
}

// =============================================
// FAKE RECORD DETECTION ENGINE
// =============================================
let flaggedIds = [];

function detectFakes() {
    if (!responses.length) { showToast('No responses to analyze'); return; }

    const issues = []; // { id, houseNum, reasons: [] }

    // Build phone number frequency map for duplicate detection
    const phoneMap = {};
    responses.forEach(r => {
        const ph = r.phone_number || '';
        if (ph && ph !== 'N/A') {
            if (!phoneMap[ph]) phoneMap[ph] = [];
            phoneMap[ph].push(r.id);
        }
    });

    // Build house number frequency map
    const houseMap = {};
    responses.forEach(r => {
        const h = r.census_house_number || '';
        if (h) {
            if (!houseMap[h]) houseMap[h] = [];
            houseMap[h].push(r.id);
        }
    });

    responses.forEach(r => {
        const reasons = [];
        const ppl = parseInt(r.num_people) || 0;
        const rooms = parseInt(r.rooms) || 0;
        const pairs = parseInt(r.married_pairs) || 0;
        const usage = r.building_usage || '';
        const cond = r.building_condition || '';
        const name = r.head_of_family || '';
        const phone = r.phone_number || '';
        const gender = r.gender || '';

        // === Rule 1: Empty building but people listed ===
        if (usage === 'Empty' && ppl > 0) {
            reasons.push(`Building is "Empty" but ${ppl} people listed`);
        }

        // === Rule 2: People but no head of family ===
        if (ppl > 0 && (name === '' || name === 'N/A' || name === '-') && usage !== 'Empty') {
            reasons.push('Has residents but no head of family name');
        }

        // === Rule 3: Married pairs exceed possible ===
        if (pairs > 0 && pairs * 2 > ppl) {
            reasons.push(`${pairs} married pairs impossible with only ${ppl} people`);
        }

        // === Rule 4: Broken building with too many people ===
        if (cond === 'Broken' && ppl > 5) {
            reasons.push(`Broken building with ${ppl} people — suspicious`);
        }

        // === Rule 5: 0 rooms but people living ===
        if (rooms === 0 && ppl > 0 && usage !== 'Empty') {
            reasons.push('0 rooms but residents listed');
        }

        // === Rule 6: Invalid phone number ===
        if (phone && phone !== 'N/A') {
            if (!/^[6-9][0-9]{9}$/.test(phone)) {
                reasons.push(`Invalid phone: "${phone}" — must be 10 digits starting with 6-9`);
            }
        }

        // === Rule 7: Duplicate phone numbers ===
        if (phone && phone !== 'N/A' && phoneMap[phone] && phoneMap[phone].length > 1) {
            reasons.push(`Duplicate phone number ${phone} (found ${phoneMap[phone].length} times)`);
        }

        // === Rule 8: Duplicate house numbers ===
        if (r.census_house_number && houseMap[r.census_house_number] && houseMap[r.census_house_number].length > 1) {
            reasons.push(`Duplicate house number ${r.census_house_number} (found ${houseMap[r.census_house_number].length} times)`);
        }

        // === Rule 9: Fake-looking names ===
        if (name && name !== 'N/A' && name !== '-') {
            if (/[0-9]/.test(name)) reasons.push(`Name contains numbers: "${name}"`);
            if (/[!@#$%^&*(){}[\]<>]/.test(name)) reasons.push(`Name has special characters: "${name}"`);
            if (name.length < 3) reasons.push(`Name too short: "${name}"`);
            if (name.length > 50) reasons.push(`Name suspiciously long: "${name}"`);
            if (/^(.)\1{3,}/.test(name)) reasons.push(`Name has repeated characters: "${name}"`);
        }

        // === Rule 10: No internet but has laptop ===
        if (r.internet === 'No' && r.laptop_computer === 'Yes' && usage === 'House') {
            reasons.push('Has laptop but no internet — verify');
        }

        // === Rule 11: LPG gas but using cow dung / wood only ===
        if (r.cooking_gas === 'LPG/PNG' && ['Cow dung cakes', 'Wood', 'Grass (dry)'].includes(r.cooking_fuel)) {
            reasons.push(`Has LPG/PNG but uses ${r.cooking_fuel} — contradictory`);
        }

        // === Rule 12: Unrealistic people count ===
        if (ppl > 20) {
            reasons.push(`${ppl} people in one house — unusually high`);
        }

        if (reasons.length > 0) {
            issues.push({
                id: r.id,
                houseNum: r.census_house_number,
                name: name,
                reasons: reasons,
                severity: reasons.length >= 3 ? 'high' : reasons.length >= 2 ? 'medium' : 'low'
            });
        }
    });

    // Update UI
    flaggedIds = issues.map(i => i.id);
    const panel = document.getElementById('fake-panel');
    const list = document.getElementById('fake-list');
    const count = document.getElementById('fake-count');

    if (issues.length === 0) {
        panel.style.display = 'none';
        showToast('No suspicious records found! All data looks clean.');
        return;
    }

    // Sort by severity
    const sevOrder = { high: 0, medium: 1, low: 2 };
    issues.sort((a, b) => sevOrder[a.severity] - sevOrder[b.severity]);

    count.textContent = issues.length;
    list.innerHTML = issues.map(item => `
        <div class="fake-item fake-${item.severity}">
            <div class="fake-item-header">
                <div class="fake-item-info">
                    <span class="fake-severity sev-${item.severity}">${item.severity.toUpperCase()}</span>
                    <strong>House #${item.houseNum}</strong>
                    <span class="fake-name">${item.name}</span>
                </div>
                <div class="fake-item-actions">
                    <button class="tbtn tbtn-view" onclick="viewDetail('${item.id}')">View</button>
                    <button class="tbtn tbtn-del" onclick="deleteResponse('${item.id}');detectFakes();">Delete</button>
                </div>
            </div>
            <ul class="fake-reasons">
                ${item.reasons.map(r => `<li>${r}</li>`).join('')}
            </ul>
        </div>
    `).join('');

    panel.style.display = 'block';
    panel.scrollIntoView({ behavior: 'smooth', block: 'start' });
    showToast(`Found ${issues.length} suspicious records!`);
}

function deleteFakes() {
    if (!flaggedIds.length) return;
    if (!confirm(`Delete all ${flaggedIds.length} flagged records? This cannot be undone.`)) return;
    responses = responses.filter(r => !flaggedIds.includes(r.id));
    flaggedIds = [];
    saveResponses();
    renderResponses();
    document.getElementById('fake-panel').style.display = 'none';
    showToast('All flagged records deleted!');
}

function closeFakePanel() {
    document.getElementById('fake-panel').style.display = 'none';
    flaggedIds = [];
}
