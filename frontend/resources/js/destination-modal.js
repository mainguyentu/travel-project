/**
 * Destination Detail Modal Handler
 * Manages modal open/close, API fetching, and content rendering
 */

function initDestinationModal() {
    const modalRoot = document.querySelector('[data-destination-modal]');
    if (!modalRoot) {
        return;
    }

    const dialog = modalRoot.querySelector('.destination-modal-dialog');
    const modalTitle = document.getElementById('destination-modal-title');
    const modalContent = modalRoot.querySelector('[data-destination-modal-content]');
    const closeButtons = modalRoot.querySelectorAll('[data-close-destination-modal]');
    const ratingModalRoot = document.querySelector('[data-rating-modal]');
    const ratingDialog = ratingModalRoot?.querySelector('.destination-modal-dialog') || null;
    const ratingTitle = document.getElementById('rating-modal-title');
    const ratingForm = ratingModalRoot?.querySelector('[data-rating-form]') || null;
    const ratingStars = ratingModalRoot?.querySelector('.star-rating') || null;
    const ratingCloseButtons = ratingModalRoot?.querySelectorAll('[data-close-rating-modal]') || [];
    const detailTriggers = document.querySelectorAll('[data-open-destination][data-destination-id]');
    const apiEndpoint = (modalRoot.dataset.apiEndpoint || '').replace(/\/$/, '');
    const ratingEndpoint = (modalRoot.dataset.ratingEndpoint || '').replace(/\/$/, '');
    const canRate = modalRoot.dataset.canRate === 'true';
    const loginUrl = modalRoot.dataset.loginUrl || '';

    if (!apiEndpoint || detailTriggers.length === 0) {
        return;
    }

    const priceLabels = {
        '1': 'Tiết kiệm',
        '2': 'Vừa phải',
        '3': 'Cao cấp',
        low: 'Giá rẻ',
        medium: 'Trung bình',
        high: 'Cao cấp',
        free: 'Miễn Phí',
    };

    let activeRequestToken = null;

    const renderLoading = () => {
        modalTitle.textContent = 'Đang tải chi tiết...';
        modalContent.innerHTML = '<p class="muted">Vui lòng chờ trong giây lát...</p>';
    };

    const renderError = (message) => {
        modalTitle.textContent = 'Không thể tải chi tiết';
        modalContent.innerHTML = `<p class="muted">${message}</p>`;
    };

    const toSafeText = (value, fallback = 'N/A') => {
        if (value === null || value === undefined || value === '') {
            return fallback;
        }
        return String(value)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    };

    const normalizePrice = (priceLevel) => {
        if (priceLevel === null || priceLevel === undefined) {
            return 'N/A';
        }
        const key = String(priceLevel).toLowerCase().trim();
        return priceLabels[key] || String(priceLevel);
    };

    const renderDestination = (destination) => {
        const name = toSafeText(destination.name, 'N/A');
        const category = toSafeText(destination.categories?.[0]?.name, 'Điểm đến');
        const address = toSafeText(destination.address, 'Chưa cập nhật');
        const description = toSafeText(destination.description, 'Chưa có mô tả cho địa điểm này.');
        const rating = Number(destination.rating_avg || 0).toFixed(1);
        const reviewCount = Number(destination.review_count || 0);
        const price = toSafeText(normalizePrice(destination.price_level));
        const image = destination.img_url ? toSafeText(destination.img_url, '') : '';
        const mapUrl = destination.url_map ? toSafeText(destination.url_map, '') : '';
        const safeLoginUrl = loginUrl ? toSafeText(loginUrl, '') : '';
        const ratingAction = ratingModalRoot && ratingForm && ratingEndpoint
            ? (canRate
                ? `<button type="button" class="btn-secondary" data-open-rating data-destination-id="${destination.id}" data-destination-name="${name}">Đánh giá</button>`
                : (safeLoginUrl ? `<a href="${safeLoginUrl}" class="btn-secondary">Đăng nhập để đánh giá</a>` : ''))
            : '';

        modalTitle.textContent = destination.name || 'Chi tiết điểm đến';

        modalContent.innerHTML = `
            <section class="destination-modal-hero">
                ${image ? `<img src="${image}" alt="${name}">` : '<div class="destination-modal-image-placeholder">No image</div>'}
                <div class="destination-modal-hero-overlay">
                    <span class="badge badge-soft">${category}</span>
                    <h3>${name}</h3>
                    <p>Đánh giá ${rating}/5 · ${reviewCount} reviews · ${price}</p>
                </div>
            </section>

            <section class="destination-modal-meta-grid meta-grid">
                <article class="public-card destination-modal-meta-card">
                    <strong>Danh mục</strong>
                    <p class="muted">${category}</p>
                </article>
                <article class="public-card destination-modal-meta-card">
                    <strong>Địa chỉ</strong>
                    <p class="muted">${address}</p>
                </article>
                <article class="public-card destination-modal-meta-card">
                    <strong>Mức giá</strong>
                    <p class="muted">${price}</p>
                </article>
            </section>
            <section class="detail-panel destination-modal-section">
                <h3>Thông tin tổng quan</h3>
                <p class="muted">${description}</p>
            </section>

            ${(mapUrl || ratingAction) ? `
                <div class="destination-modal-actions">
                    ${ratingAction}
                    ${mapUrl ? `
                        <a href="${mapUrl}" target="_blank" rel="noopener noreferrer" class="btn-primary">
                            🗺️ Xem bản đồ
                        </a>
                    ` : ''}
                </div>
            ` : ''}
        `;
    };

    const openRatingModal = (destinationId, destinationName) => {
        if (!ratingModalRoot || !ratingDialog || !ratingForm || !ratingEndpoint) {
            return;
        }

        ratingModalRoot.hidden = false;
        document.body.classList.add('modal-open');

        ratingForm.action = `${ratingEndpoint}/${destinationId}`;
        ratingForm.reset();

        if (ratingTitle) {
            ratingTitle.textContent = destinationName
                ? `Đánh giá ${destinationName}`
                : 'Đánh giá địa điểm';
        }

        ratingDialog.focus();
    };

    const closeRatingModal = () => {
        if (!ratingModalRoot) {
            return;
        }
        ratingModalRoot.hidden = true;
        if (modalRoot.hidden) {
            document.body.classList.remove('modal-open');
        }
    };

    const openModal = async (destinationId) => {
        const requestToken = Symbol('destination-request');
        activeRequestToken = requestToken;

        modalRoot.hidden = false;
        document.body.classList.add('modal-open');
        renderLoading();

        dialog.focus();

        try {
            const response = await fetch(`${apiEndpoint}/destinations/${destinationId}`, {
                headers: {
                    Accept: 'application/json',
                },
            });

            if (!response.ok) {
                throw new Error(`HTTP_${response.status}`);
            }

            const payload = await response.json();
            if (activeRequestToken !== requestToken) {
                return;
            }

            if (!payload?.data) {
                renderError('Dữ liệu chi tiết không hợp lệ. Vui lòng thử lại.');
                return;
            }

            renderDestination(payload.data);
        } catch (error) {
            if (activeRequestToken !== requestToken) {
                return;
            }
            renderError('Không tải được dữ liệu điểm đến. Vui lòng thử lại sau.');
            console.error('Destination detail error:', error);
        }
    };

    const closeModal = () => {
        modalRoot.hidden = true;
        document.body.classList.remove('modal-open');
        activeRequestToken = null;
    };

    closeButtons.forEach((element) => {
        element.addEventListener('click', closeModal);
    });

    detailTriggers.forEach((trigger) => {
        trigger.addEventListener('click', (event) => {
            event.preventDefault();
            const destinationId = trigger.dataset.destinationId;
            if (!destinationId) {
                return;
            }
            openModal(destinationId);
        });
    });

    if (ratingModalRoot) {
        ratingCloseButtons.forEach((element) => {
            element.addEventListener('click', closeRatingModal);
        });
    }

    if (ratingStars) {
        let isScrubbing = false;
        const starLabels = Array.from(ratingStars.querySelectorAll('label.star'));

        const getStarValue = (label) => {
            if (!label || !ratingForm) {
                return null;
            }
            const inputId = label.getAttribute('for');
            if (!inputId) {
                return null;
            }
            const input = ratingForm.querySelector(`#${CSS.escape(inputId)}`);
            return input ? Number(input.value) : null;
        };

        const syncSelectedStars = () => {
            if (!ratingForm) {
                return;
            }
            const checked = ratingForm.querySelector('input[name="rating_score"]:checked');
            const selectedValue = checked ? Number(checked.value) : 0;
            starLabels.forEach((label) => {
                const value = getStarValue(label);
                label.classList.toggle('is-selected', value !== null && value <= selectedValue);
            });
        };

        const previewStars = (value) => {
            starLabels.forEach((label) => {
                const starValue = getStarValue(label);
                label.classList.toggle('is-preview', value !== null && starValue !== null && starValue <= value);
            });
        };

        const clearPreview = () => {
            starLabels.forEach((label) => {
                label.classList.remove('is-preview');
            });
        };

        ratingStars.addEventListener('pointerdown', (event) => {
            if (event.pointerType === 'mouse' && event.button !== 0) {
                return;
            }
            isScrubbing = true;
            const label = event.target.closest('label.star');
            if (!label || !ratingForm) {
                return;
            }
            const inputId = label.getAttribute('for');
            if (!inputId) {
                return;
            }
            const input = ratingForm.querySelector(`#${CSS.escape(inputId)}`);
            if (input) {
                input.checked = true;
                syncSelectedStars();
            }
        });

        ratingStars.addEventListener('pointermove', (event) => {
            const label = event.target.closest('label.star');
            if (!label) {
                return;
            }
            const value = getStarValue(label);
            previewStars(value);
            if (event.pointerType !== 'mouse' && isScrubbing && ratingForm) {
                const inputId = label.getAttribute('for');
                const input = inputId ? ratingForm.querySelector(`#${CSS.escape(inputId)}`) : null;
                if (input) {
                    input.checked = true;
                    syncSelectedStars();
                }
            }
        });

        window.addEventListener('pointerup', () => {
            isScrubbing = false;
        });

        ratingStars.addEventListener('pointerleave', () => {
            isScrubbing = false;
            clearPreview();
        });

        ratingStars.addEventListener('click', (event) => {
            const label = event.target.closest('label.star');
            if (!label || !ratingForm) {
                return;
            }
            const inputId = label.getAttribute('for');
            if (!inputId) {
                return;
            }
            const input = ratingForm.querySelector(`#${CSS.escape(inputId)}`);
            if (input) {
                input.checked = true;
                syncSelectedStars();
            }
        });

        if (ratingForm) {
            ratingForm.addEventListener('change', (event) => {
                if (event.target?.name === 'rating_score') {
                    syncSelectedStars();
                }
            });
        }
    }

    modalContent.addEventListener('click', (event) => {
        const target = event.target.closest('[data-open-rating]');
        if (!target) {
            return;
        }
        event.preventDefault();
        const destinationId = target.dataset.destinationId;
        const destinationName = target.dataset.destinationName || '';
        if (!destinationId) {
            return;
        }
        if (!canRate) {
            if (loginUrl) {
                window.location.href = loginUrl;
            }
            return;
        }
        openRatingModal(destinationId, destinationName);
    });

    document.addEventListener('keydown', (event) => {
        if (event.key !== 'Escape') {
            return;
        }
        if (ratingModalRoot && !ratingModalRoot.hidden) {
            closeRatingModal();
            return;
        }
        if (!modalRoot.hidden) {
            closeModal();
        }
    });
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDestinationModal);
} else {
    initDestinationModal();
}
