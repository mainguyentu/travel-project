// Destination detail modal — safe rendering (no innerHTML with API data).
document.addEventListener('click', async (event) => {
    const btn = event.target.closest('[data-detail]');
    if (!btn) {
        return;
    }
    const id = btn.getAttribute('data-detail');
    const modal = document.getElementById('destination-modal');
    const content = document.getElementById('modal-content');
    if (!modal || !content) {
        return;
    }
    content.textContent = 'Đang tải…';
    modal.hidden = false;
    try {
        const base = (window.API_BASE || '').replace(/\/$/, '');
        const res = await fetch(`${base}/destinations/${encodeURIComponent(id)}`);
        const body = await res.json();
        renderDetail(content, body.data || {});
    } catch (err) {
        content.textContent = 'Không tải được chi tiết.';
    }
});

document.addEventListener('click', (event) => {
    if (event.target.id === 'modal-close' || event.target.id === 'destination-modal') {
        const modal = document.getElementById('destination-modal');
        if (modal) {
            modal.hidden = true;
        }
    }
});

// ESC đóng popup chi tiết (không cần bấm Đóng).
document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
        const modal = document.getElementById('destination-modal');
        if (modal && !modal.hidden) {
            modal.hidden = true;
        }
    }
});

function textRow(parent, label, value) {
    const p = document.createElement('p');
    const strong = document.createElement('strong');
    strong.textContent = label + ': ';
    p.appendChild(strong);
    p.appendChild(document.createTextNode(value ?? '—'));
    parent.appendChild(p);
}

function renderDetail(content, d) {
    content.replaceChildren();
    const hero = document.getElementById('modal-hero');
    const img = document.getElementById('modal-img');
    if (hero && img) {
        if (d.img_url) {
            img.src = d.img_url;
            img.alt = d.name || '';
            hero.hidden = false;
        } else {
            hero.hidden = true;
        }
    }
    const h = document.createElement('h2');
    h.textContent = d.name || '';
    content.appendChild(h);
    // Khối điểm tổng hợp ★ + nguồn (thay form chấm điểm cá nhân).
    const box = document.createElement('div');
    box.className = 'rating-summary';
    const extCount = Number(d.external_rating_count || 0);
    const ins = d.insight || {};
    const avg = extCount > 0 ? Number(d.external_rating_avg || 0) : Number(ins.rating_avg ?? d.rating_avg ?? 0);
    const cnt = extCount > 0 ? extCount : Number(ins.rating_count ?? (d.metrics && d.metrics.rating_count) ?? 0);
    let src = 'đánh giá trên trang';
    if (extCount > 0) {
        const raw = d.external_source || 'manual';
        src = raw === 'google_maps' ? 'Google Maps' : String(raw).replace(/_/g, ' ');
    }
    const strong = document.createElement('strong');
    strong.textContent = `★ ${avg.toFixed(1)} (${cnt.toLocaleString('vi-VN')} đánh giá · ${src})`;
    box.appendChild(strong);
    if (!extCount && ins.status && ins.status !== 'ok') {
        const note = document.createElement('div');
        note.textContent = 'Ít dữ liệu — tham khảo thêm trước khi đi.';
        box.appendChild(note);
    }
    content.appendChild(box);
    textRow(content, 'Địa chỉ', d.address);
    textRow(content, 'Mô tả', d.description);
    textRow(content, 'Mức giá', d.price_level);
    textRow(content, 'Lượt xem', String(d.view_count ?? 0));
    if (d.insight && d.insight.summary) {
        textRow(content, 'Insight', d.insight.summary);
    }
    if (d.metrics && d.metrics.favorite_count) {
        textRow(content, 'Yêu thích', String(d.metrics.favorite_count ?? 0));
    }
}
