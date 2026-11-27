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
    textRow(content, 'Địa chỉ', d.address);
    textRow(content, 'Mô tả', d.description);
    textRow(content, 'Mức giá', d.price_level);
    textRow(content, 'Rating', String(d.rating_avg ?? 0));
    textRow(content, 'Lượt xem', String(d.view_count ?? 0));
    if (d.insight && d.insight.summary) {
        textRow(content, 'Insight', d.insight.summary);
    }
    if (d.metrics && (d.metrics.favorite_count || d.metrics.rating_count)) {
        textRow(content, 'Yêu thích', String(d.metrics.favorite_count ?? 0));
    }
}
