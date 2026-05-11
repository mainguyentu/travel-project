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
    const ratingEndpoint = (modalRoot.dataset.ratingEndpoint || '').replace(/\/$/, '');
    const favoritesAddEndpoint = (modalRoot.dataset.favoritesAddEndpoint || '').replace(/\/$/, '');
    const canRate = modalRoot.dataset.canRate === 'true';
    const canFavorite = modalRoot.dataset.canFavorite === 'true';
    const loginUrl = modalRoot.dataset.loginUrl || '';
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
    const favoriteSyncEvent = 'favorite:changed';

    const destinationDatasetNode = modalRoot.querySelector('[data-destination-dataset]');
    const destinationList = (() => {
        if (!destinationDatasetNode) {
            return [];
        }
        try {
            const parsed = JSON.parse(destinationDatasetNode.textContent || '[]');
            return Array.isArray(parsed) ? parsed : [];
        } catch (_) {
            return [];
        }
    })();
    const destinationMap = new Map(
        destinationList
            .filter((destination) => destination && destination.id !== undefined && destination.id !== null)
            .map((destination) => [String(destination.id), destination])
    );

    if (detailTriggers.length === 0) {
        return;
    }

    const priceLabels = {
        '1': 'Tiết kiệm',
        '2': 'Vừa phải',
        '3': 'Cao cấp',
        low: 'Giá rẻ',
        medium: 'Trung bình',
        high: 'Cao cấp',
        free: 'Miễn phí',
    };

    const buildFavoriteUrls = (destinationId) => {
        const fallback = `/favorites/${destinationId}`;
        if (!favoritesAddEndpoint) {
            return {
                addUrl: fallback,
                removeUrl: fallback,
            };
        }

        return {
            addUrl: `${favoritesAddEndpoint}/${destinationId}`,
            removeUrl: `${favoritesAddEndpoint}/${destinationId}`,
        };
    };

    const renderLoading = () => {
        modalTitle.textContent = 'Đang tải chi tiết...';
        modalContent.innerHTML = `
            <div class="destination-modal-loading" role="status" aria-live="polite">
                <span class="destination-modal-spinner" aria-hidden="true"></span>
                <p class="muted">Đang tải thông tin điểm đến. Vui lòng chờ trong giây lát...</p>
            </div>
        `;
    };

    const renderError = (message) => {
        modalTitle.textContent = 'Không thể tải chi tiết';
        modalContent.innerHTML = `
            <section class="detail-panel destination-modal-error" role="alert">
                <h3>Đã xảy ra lỗi</h3>
                <p class="muted">${toSafeText(message, 'Không tải được dữ liệu điểm đến.')}</p>
                <p class="muted">Vui lòng đóng popup và thử lại sau vài giây.</p>
            </section>
        `;
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

    const getPrimaryImage = (destination) => {
        if (destination?.img_url) {
            return destination.img_url;
        }
        if (Array.isArray(destination?.img_urls) && destination.img_urls.length > 0) {
            return destination.img_urls[0];
        }
        return '';
    };

    const getOpenHours = (destination) => {
        return destination?.open_hours?.raw_text || destination?.open_hour || 'Đang cập nhật';
    };

    // Returns true if currently open, false if currently closed, null if unknown
    const isOpen = (destination) => {
        const openHours = destination?.open_hours?.raw_text || destination?.open_hour || null;
        if (!openHours) {
            return null;
        }

        const parseTimeToMinutes = (timeStr) => {
            const match = String(timeStr || '').trim().match(/^(\d{1,2}):(\d{2})$/);
            if (!match) {
                return null;
            }

            const hour = Number(match[1]);
            const minute = Number(match[2]);
            if (Number.isNaN(hour) || Number.isNaN(minute) || hour < 0 || hour > 23 || minute < 0 || minute > 59) {
                return null;
            }

            return hour * 60 + minute;
        };

        const [openText, closeText] = String(openHours).split(/\s*đến\s*/i);
        if (!openText || !closeText) {
            return null;
        }

        const openMinutes = parseTimeToMinutes(openText);
        const closeMinutes = parseTimeToMinutes(closeText);
        if (openMinutes === null || closeMinutes === null) {
            return null;
        }

        const now = new Date();
        const nowMinutes = now.getHours() * 60 + now.getMinutes();

        if (closeMinutes <= openMinutes) {
            return nowMinutes >= openMinutes || nowMinutes <= closeMinutes;
        }

        return nowMinutes >= openMinutes && nowMinutes <= closeMinutes;
    };


    const getPriceText = (destination) => {
        const level = destination?.price?.level ?? destination?.price_level;
        const priceLevel = (level !== null && level !== undefined && String(level).trim() !== '')
            ? normalizePrice(level)
            : 'N/A';
        const priceRawText = destination?.price?.raw_text ?? destination?.price_raw_text;
        const price = (priceRawText !== null && priceRawText !== undefined && String(priceRawText).trim() !== '')
            ? String(priceRawText)
            : 'N/A';

        return {
            price_level: priceLevel,
            price,
        };
    };

    const toSafeList = (items) => {
        if (!Array.isArray(items) || items.length === 0) {
            return '';
        }
        return items
            .map((item) => `<li>${toSafeText(item, '')}</li>`)
            .join('');
    };

    const renderDestination = (destination) => {
        const name = toSafeText(destination.name, 'N/A');
        const categoryNames = Array.isArray(destination.categories)
            ? destination.categories.map((item) => item?.name).filter(Boolean)
            : [];
        const categoryBadge = toSafeText(categoryNames[0], 'Điểm đến');
        const category = toSafeText(categoryNames.join(', '), 'Điểm đến');
        const address = toSafeText(destination.address, 'Đang cập nhật');
        const description = toSafeText(destination.description, 'Chưa có mô tả cho địa điểm này.');
        const rating = Number(destination.rating_avg || 0).toFixed(1);
        const metrics = destination.metrics || null;
        const openHours = toSafeText(getOpenHours(destination), 'Đang cập nhật');
        const open_hour_close = toSafeText(destination.open_hour_close, '');
        const openStatus = isOpen(destination);
        const openStatusText = openStatus === true ? 'Đang mở cửa' : (openStatus === false ? 'Đang đóng cửa' : 'Đang cập nhật');
        const openStatusClass = openStatus === true ? 'is-open' : (openStatus === false ? 'is-closed' : 'is-unknown');
        const favoriteCount = Number(metrics?.favorite_count ?? 0);
        const totalViews = Number(metrics?.view_count ?? destination.view_count ?? 0);
        const insight = destination.insight || null;
        const insightData = insight?.final_data || null;
        const insightSummary = toSafeText(
            insightData?.summary,
            'Hiện chưa có nhận định tổng quan cho địa điểm này.'
        );
        const highlightsList = toSafeList(insightData?.highlights);
        const risksList = toSafeList(insightData?.risks);
        const recommendation = toSafeText(insightData?.recommendation, '');
        const {
            price_level: priceLevel,
            price: priceRaw,
        } = getPriceText(destination);
        const price_raw_text = priceRaw !== 'N/A' ? toSafeText(priceRaw) : '';
        const image = toSafeText(getPrimaryImage(destination), '');
        const mapUrl = destination.url_map ? toSafeText(destination.url_map, '') : '';
        const safeLoginUrl = loginUrl ? toSafeText(loginUrl, '') : '';
        const ratingAction = ratingModalRoot && ratingForm && ratingEndpoint
            ? (canRate
                ? `<button type="button" class="btn-secondary" data-open-rating data-destination-id="${destination.id}" data-destination-name="${name}">Đánh giá</button>`
                : (safeLoginUrl ? `<a href="${safeLoginUrl}" class="btn-secondary">Đăng nhập để đánh giá</a>` : ''))
            : '';
        const isFavorite = destination?.is_favorite === true;
        const favoriteIndicatorLabel = isFavorite
            ? 'Đã yêu thích · Nhấn để bỏ'
            : 'Thêm vào danh sách yêu thích !';

        modalTitle.textContent = destination.name || 'Chi tiết điểm đến';

        modalContent.innerHTML = `
            <section class="destination-modal-hero">
                ${image ? `<img src="${image}" alt="${name}">` : '<div class="destination-modal-image-placeholder">No image</div>'}
                <div class="destination-modal-hero-overlay" aria-hidden="true"></div>
                <div
                    class="destination-modal-favorite-wrap"
                    data-favorite-form
                    data-favorited="${isFavorite ? 'true' : 'false'}"
                >
                    <button
                        type="button"
                        class="favorite-btn"
                        data-favorite
                        data-modal-favorite-indicator
                        data-destination-id="${destination.id}"
                        aria-label="${isFavorite ? 'Xoá khỏi danh sách yêu thích' : 'Thêm vào danh sách yêu thích'}"
                        title="${favoriteIndicatorLabel}"
                    >
                        <span class="favorite-icon">♥</span>
                        <span class="favorite-text">${favoriteIndicatorLabel}</span>
                    </button>
                </div>
                <div class="destination-modal-hero-content">
                    <span class="destination-pill">${categoryBadge}</span>
                    <h3>${name}</h3>
                    <p class="destination-modal-hero-address">${address}</p>
                    <div class="destination-modal-status-row">
                        <span class="destination-modal-status ${openStatusClass}">${openStatusText}</span>
                        <span class="destination-modal-hours">${openHours}${open_hour_close ? ` - ${open_hour_close}` : ''}</span>
                    </div>
                </div>
            </section>

            <section class="destination-modal-meta-grid" aria-label="Th?ng tin nhanh">
                <article class="public-card destination-modal-meta-card">
                    <strong>Mức giá</strong>
                    ${price_raw_text
                        ?`<p class="muted">${price_raw_text}</p>`
                        :`<p class="muted">Hiện chưa có thông tin giá</p>`
                     }
                </article>
                <article class="public-card destination-modal-meta-card">
                    <strong>Đánh giá</strong>
                    <p class="muted">${rating}</p>
                </article>
                <article class="public-card destination-modal-meta-card">
                    <strong>Lượt yêu thích</strong>
                    <p class="muted" data-modal-favorite-count>${favoriteCount}</p>
                </article>
                <article class="public-card destination-modal-meta-card">
                    <strong>Lượt xem</strong>
                    <p class="muted">${totalViews}</p>
                </article>
            </section>

            <div class="destination-modal-body-grid">
                <section class="detail-panel destination-modal-section">
                    <h3>Thông tin tổng quan</h3>
                    <p class="muted">${description}</p>
                </section>

                <section class="detail-panel destination-modal-section">
                    <h3>Nhận định</h3>
                    <div class="destination-modal-insight-block">
                        <strong>Đánh giá tổng hợp</strong>
                        <p class="muted">${insightSummary}</p>
                        <p class="muted">${recommendation}</p>
                    </div>
                    <div class="destination-modal-insight-block">
                        <div class="destination-modal-insight-split">
                            <div class="destination-modal-insight-col">
                                <strong>Điểm nổi bật</strong>
                                ${highlightsList
                                    ? `<ul class="muted">${highlightsList}</ul>`
                                    : '<p class="muted">Hiện chưa có điểm nổi bật.</p>'}
                            </div>
                            <div class="destination-modal-insight-col">
                                <strong>Điểm cần lưu ý</strong>
                                ${risksList
                                    ? `<ul class="muted">${risksList}</ul>`
                                    : '<p class="muted">Hiện chưa có điểm cần lưu ý.</p>'}
                            </div>
                        </div>
                    </div>
                </section>
            </div>

            ${(mapUrl || ratingAction) ? `
                <div class="destination-modal-actions">
                    ${ratingAction}
                    ${mapUrl ? `
                        <a href="${mapUrl}" target="_blank" rel="noopener noreferrer" class="btn-primary">
                            Xem bản đồ
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

    const openModal = (destinationId) => {
        modalRoot.hidden = false;
        document.body.classList.add('modal-open');
        renderLoading();

        dialog.focus();

        const destination = destinationMap.get(String(destinationId));
        if (!destination) {
            renderError('Không tìm thấy dữ liệu chi tiết cho điểm đến này.');
            return;
        }

        renderDestination(destination);
    };

    const closeModal = () => {
        modalRoot.hidden = true;
        document.body.classList.remove('modal-open');
    };

    const syncModalFavoriteUi = (destinationId, isFavorite) => {
        if (!destinationId) {
            return;
        }

        const favoriteIndicator = modalContent.querySelector(
            `[data-modal-favorite-indicator][data-destination-id="${CSS.escape(String(destinationId))}"]`
        );
        if (!favoriteIndicator) {
            return;
        }

        const previousState = favoriteIndicator.dataset.favorited === 'true';
        favoriteIndicator.dataset.favorited = isFavorite ? 'true' : 'false';

        const favoriteWrap = favoriteIndicator.closest('[data-favorite-form]');
        if (favoriteWrap) {
            favoriteWrap.dataset.favorited = isFavorite ? 'true' : 'false';
        }
        favoriteIndicator.setAttribute(
            'aria-label',
            isFavorite ? 'Xoá khỏi danh sách yêu thích' : 'Thêm vào danh sách yêu thích'
        );
        favoriteIndicator.setAttribute(
            'title',
            isFavorite ? 'Đã yêu thích · Nhấn để bỏ' : 'Thêm vào danh sách yêu thích !'
        );

        const favoriteText = favoriteIndicator.querySelector('.favorite-text');
        if (favoriteText) {
            favoriteText.textContent = isFavorite
                ? 'Đã yêu thích · Nhấn để bỏ'
                : 'Thêm vào danh sách yêu thích !';
        }

        const favoriteCountNode = modalContent.querySelector('[data-modal-favorite-count]');
        if (favoriteCountNode && previousState !== isFavorite) {
            const currentCount = Number(favoriteCountNode.textContent || 0);
            const nextCount = isFavorite
                ? currentCount + 1
                : Math.max(0, currentCount - 1);
            favoriteCountNode.textContent = String(nextCount);
        }
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
        const favoriteToggle = event.target.closest('[data-modal-favorite-indicator]');
        if (favoriteToggle) {
            event.preventDefault();
            if (!canFavorite) {
                if (loginUrl) {
                    window.location.href = loginUrl;
                }
                return;
            }

            const destinationId = favoriteToggle.dataset.destinationId;
            if (!destinationId) {
                return;
            }

            const currentlyFavorite = favoriteToggle.dataset.favorited === 'true';
            const { addUrl, removeUrl } = buildFavoriteUrls(destinationId);
            const payload = new FormData();
            payload.append('_token', csrfToken);
            if (currentlyFavorite) {
                payload.append('_method', 'DELETE');
            }

            favoriteToggle.disabled = true;
            fetch(currentlyFavorite ? removeUrl : addUrl, {
                method: 'POST',
                headers: {
                    Accept: 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: payload,
                credentials: 'same-origin',
                redirect: 'follow',
            })
                .then(async (response) => {
                    const contentType = response.headers.get('content-type') || '';
                    if (response.redirected && !contentType.includes('application/json')) {
                        window.location.href = response.url;
                        return null;
                    }

                    const result = contentType.includes('application/json')
                        ? await response.json()
                        : null;
                    if (!response.ok || !result || result.success === false) {
                        throw new Error(result?.error || 'Không thể cập nhật yêu thích.');
                    }
                    return result;
                })
                .then((result) => {
                    if (!result) {
                        return;
                    }
                    const nextFavorite = !currentlyFavorite;
                    syncModalFavoriteUi(destinationId, nextFavorite);
                    document.dispatchEvent(
                        new CustomEvent(favoriteSyncEvent, {
                            detail: { destinationId, isFavorite: nextFavorite },
                        })
                    );
                })
                .catch(() => undefined)
                .finally(() => {
                    favoriteToggle.disabled = false;
                });

            return;
        }

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

    document.addEventListener(favoriteSyncEvent, (event) => {
        const destinationId = event?.detail?.destinationId;
        const isFavorite = event?.detail?.isFavorite === true;
        syncModalFavoriteUi(destinationId, isFavorite);
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

