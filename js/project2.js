// === LANG TOGGLE ===
let currentLang = 'en';

function setLang(lang) {
    currentLang = lang;

    // Update all elements with data-en / data-id
    document.querySelectorAll('[data-en], [data-id]').forEach(el => {
        const text = el.getAttribute(`data-${lang}`);
        if (!text) return;
        // Preserve inner HTML for elements that use <em> etc.
        if (text.includes('<')) {
        el.innerHTML = text;
        } else {
        el.textContent = text;
        }
    });

    // Update placeholders that use data-placeholder-en / data-placeholder-id
    document.querySelectorAll('[data-placeholder-en], [data-placeholder-id]').forEach(el => {
        const ph = el.getAttribute(`data-placeholder-${lang}`);
        if (ph) el.placeholder = ph;
    });

    // Update active state on all toggle buttons
    ['btn-id', 'btn-en', 'btn-id-m', 'btn-en-m'].forEach(id => {
        const btn = document.getElementById(id);
        if (!btn) return;
        const btnLang = id.includes('-en') ? 'en' : 'id';
        btn.classList.toggle('active', btnLang === lang);
    });
};

// === NAVBAR SCROLL EFFECT ===
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
    if (window.scrollY > 20) {
        navbar.classList.add('bg-white/95', 'backdrop-blur', 'shadow-sm');
    } else {
        navbar.classList.remove('bg-white/95', 'backdrop-blur', 'shadow-sm');
    }
});

// === SCROLL PROGRES BAR ===
const progressBar = document.getElementById('progress-bar');
window.addEventListener('scroll', () => {
    const totalHeight = document.body.scrollHeight - window.innerHeight;
    const progress = (window.scrollY / totalHeight) * 100;
    if (progressBar) progressBar.style.width = progress + '%';
});

// === BACK TO TOP ===
const btt = document.getElementById('backToTop');
window.addEventListener('scroll', () => {
    btt.classList.toggle('show', window.scrollY > 400);
});

// === CHART ===
Chart.defaults.font.family = "'DM Sans', sans-serif";

// === RFM SEGMENT DONUT CHART ===
new Chart(document.getElementById('rfmDonut'), {
    type: 'doughnut',
    data: {
        labels: ['Champions', 'Loyal Customers', 'Potential Loyalists',
                'Recent Customers', 'At Risk', "Can't Lose Them", 'Lost Customers'],
        datasets: [{
        data: [187, 214, 156, 123, 98, 72, 150],
        backgroundColor: ['#4ade80','#22c55e','#86efac','#fbbf24','#f87171','#fb923c','#ef4444'],
        borderColor: '#1a1f2e', borderWidth: 3
        }]
    },
    options: {
        responsive: true, maintainAspectRatio: false,
        plugins: {
        legend: {
            position: 'right',
            labels: { color: '#9ca3af', font: { size: 8 }, boxWidth: 9, padding: 6 }
        }
        }
    }
});

// === RFM MONETARY BAR (AVG PER SEGMENT) ===
new Chart(document.getElementById('rfmMonetary'), {
    type: 'bar',
    data: {
        labels: ['Champions', 'Loyal', 'Potential', 'Recent', 'At Risk', "Can't Lose", 'Lost'],
        datasets: [{
        label: 'Avg Monetary (Rp M)',
        data: [18.4, 11.2, 7.8, 4.3, 5.9, 14.1, 2.1],
        backgroundColor: ['#4ade80','#22c55e','#86efac','#fbbf24','#f87171','#fb923c','#ef4444'],
        borderRadius: 5
        }]
    },
    options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
        x: { ticks: { color: '#9ca3af', font: { size: 7.5 }, maxRotation: 30 }, grid: { color: '#2d3748' } },
        y: { ticks: { color: '#9ca3af', font: { size: 8 }, callback: v => 'Rp' + v + 'M' }, grid: { color: '#2d3748' } }
        }
    }
});

// === MONTHLY REVENUE TREND ===
new Chart(document.getElementById('revenueChart'), {
    type: 'line',
    data: {
        labels: ['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Agu','Sep','Okt','Nov','Des',
                'Jan','Feb','Mar','Apr','Mei','Jun','Jul','Agu','Sep','Okt','Nov','Des'],
        datasets: [{
        label: 'Revenue (Rp M)',
        data: [31.2, 28.6, 42.1, 38.9, 35.4, 51.8, 44.2, 38.7, 40.1, 37.8, 52.3, 61.4,
                39.5, 34.1, 48.7, 43.2, 40.8, 57.4, 49.1, 43.5, 45.8, 42.4, 58.9, 68.2],
        borderColor: '#4ade80', backgroundColor: 'rgba(74,222,128,.1)',
        borderWidth: 2.5, fill: true, tension: 0.4,
        pointBackgroundColor: '#4ade80', pointRadius: 2.5, pointHoverRadius: 5
        }]
    },
    options: {
        responsive: true, maintainAspectRatio: false,
        plugins: {
        legend: { display: false },
        annotation: {}
        },
        scales: {
        x: { ticks: { color: '#9ca3af', font: { size: 7.5 }, maxRotation: 0 }, grid: { color: '#2d3748' } },
        y: { ticks: { color: '#9ca3af', font: { size: 8 }, callback: v => v + 'M' }, grid: { color: '#2d3748' } }
        }
    }
});

// === COHORT HEATMAP (CANVAS-RENDERED) ===
(function renderCohortHeatmap() {
    const canvas = document.getElementById('cohortCanvas');
    const ctx    = canvas.getContext('2d');

    // 8 cohorts × 8 periods — retention rates (%)
    const cohorts = ['Jan 23','Feb 23','Mar 23','Apr 23','Mei 23','Jun 23','Jul 23','Agu 23'];
    const periods = ['M+0','M+1','M+2','M+3','M+4','M+5','M+6','M+7'];
    const data = [
        [100, 38, 22, 17, 14, 12, 10,  9],
        [100, 35, 21, 16, 13, 11,  9,  8],
        [100, 41, 25, 18, 15, 13, 11, 10],
        [100, 33, 19, 14, 11,  9,  8,  7],
        [100, 44, 27, 20, 16, 14, 12, 10],
        [100, 37, 23, 17, 14, 12, 10,  8],
        [100, 39, 24, 18, 14, 12,  null, null],
        [100, 36, 22, 16, 13, null, null, null],
    ];

    function hexToRgb(h) {
        const r = parseInt(h.slice(1,3),16), g = parseInt(h.slice(3,5),16), b = parseInt(h.slice(5,7),16);
        return [r,g,b];
    }
    function lerpColor(pct) {
        // 0% → dark, 100% → #4ade80 green
        const lo = hexToRgb('#1e3a2f'), hi = hexToRgb('#4ade80');
        const r = Math.round(lo[0] + (hi[0]-lo[0]) * pct/100);
        const g = Math.round(lo[1] + (hi[1]-lo[1]) * pct/100);
        const b = Math.round(lo[2] + (hi[2]-lo[2]) * pct/100);
        return `rgb(${r},${g},${b})`;
    }

    const cw = canvas.offsetWidth, ch = canvas.offsetHeight;
    canvas.width  = cw * window.devicePixelRatio;
    canvas.height = ch * window.devicePixelRatio;
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);

    const marginL = 54, marginT = 28, marginR = 8, marginB = 22;
    const cols = periods.length, rows = cohorts.length;
    const cellW = (cw - marginL - marginR) / cols;
    const cellH = (ch - marginT - marginB) / rows;

    ctx.font = '8px DM Sans, sans-serif';

    // Column headers
    ctx.fillStyle = '#6b7280';
    ctx.textAlign = 'center';
    periods.forEach((p, ci) => {
        ctx.fillText(p, marginL + ci * cellW + cellW/2, marginT - 8);
    });

    // Row labels + cells
    cohorts.forEach((cohort, ri) => {
        ctx.fillStyle = '#9ca3af';
        ctx.textAlign = 'right';
        ctx.fillText(cohort, marginL - 6, marginT + ri * cellH + cellH/2 + 3);

        periods.forEach((_, ci) => {
        const val = data[ri][ci];
        const x = marginL + ci * cellW;
        const y = marginT + ri * cellH;

        if (val === null) {
            ctx.fillStyle = '#252d3d';
            ctx.fillRect(x+1, y+1, cellW-2, cellH-2);
            return;
        }

        ctx.fillStyle = lerpColor(ci === 0 ? 100 : val * 2);
        ctx.fillRect(x+1, y+1, cellW-2, cellH-2);

        ctx.fillStyle = val > 50 ? '#14532d' : '#ffffff';
        ctx.textAlign = 'center';
        ctx.font = 'bold 7.5px DM Sans, sans-serif';
        ctx.fillText(val + '%', x + cellW/2, y + cellH/2 + 3);
        ctx.font = '8px DM Sans, sans-serif';
        });
    });
})();


// === INIT ===
setLang('en');