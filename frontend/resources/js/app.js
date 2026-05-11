import "./bootstrap";
import "./destination-modal";

document.addEventListener("DOMContentLoaded", () => {
    const setToggleLabel = (button, isOpen) => {
        if (!button) {
            return;
        }

        const openLabel =
            button.getAttribute("data-label-open") || "Mở form";
        const closeLabel =
            button.getAttribute("data-label-close") || "Đóng form";
        button.textContent = isOpen ? closeLabel : openLabel;
    };

    const slugify = (value) => {
        if (!value) {
            return "";
        }

        return value
            .toString()
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .replace(/[đĐ]/g, (m) => (m === "đ" ? "d" : "D"))
            .toLowerCase()
            .replace(/[^a-z0-9\s-]/g, "")
            .trim()
            .replace(/\s+/g, "-")
            .replace(/-+/g, "-");
    };

    const slugPairs = document.querySelectorAll("[data-slug-target]");
    slugPairs.forEach((sourceInput) => {
        const targetSelector = sourceInput.getAttribute("data-slug-target");
        if (!targetSelector) {
            return;
        }

        const targetInput = document.querySelector(targetSelector);
        if (!targetInput) {
            return;
        }

        const lock = { value: false };

        targetInput.addEventListener("input", () => {
            if (targetInput.value !== "") {
                lock.value = true;
            }
        });

        sourceInput.addEventListener("input", () => {
            if (lock.value) {
                return;
            }

            targetInput.value = slugify(sourceInput.value);
        });
    });

    const toggleButtons = document.querySelectorAll("[data-toggle-target]");
    toggleButtons.forEach((button) => {
        const targetSelector = button.getAttribute("data-toggle-target");
        if (!targetSelector) {
            return;
        }

        const target = document.querySelector(targetSelector);
        if (!target) {
            return;
        }

        setToggleLabel(button, !target.hasAttribute("hidden"));

        button.addEventListener("click", () => {
            const shouldOpen = target.hasAttribute("hidden");
            if (shouldOpen) {
                target.removeAttribute("hidden");
            } else {
                target.setAttribute("hidden", "");
            }

            setToggleLabel(button, shouldOpen);
        });
    });

    const quickOpenLinks = document.querySelectorAll("[data-open-target]");
    quickOpenLinks.forEach((link) => {
        const openTargetSelector = link.getAttribute("data-open-target");
        if (!openTargetSelector) {
            return;
        }

        const openTarget = document.querySelector(openTargetSelector);
        if (!openTarget) {
            return;
        }

        const toggleButton = document.querySelector(
            `[data-toggle-target=\"${openTargetSelector}\"]`,
        );

        link.addEventListener("click", (event) => {
            if (openTarget.hasAttribute("hidden")) {
                openTarget.removeAttribute("hidden");
                setToggleLabel(toggleButton, true);
            }

            const href = link.getAttribute("href");
            if (!href || !href.startsWith("#")) {
                return;
            }

            const scrollTarget = document.querySelector(href);
            if (!scrollTarget) {
                return;
            }

            event.preventDefault();
            scrollTarget.scrollIntoView({ behavior: "smooth", block: "start" });
        });
    });

    const mobileToggle = document.querySelector("[data-mobile-toggle]");
    const mobileNav = document.querySelector("[data-mobile-nav]");
    const userMenu = document.querySelector("[data-user-menu]");
    const userMenuToggle = document.querySelector("[data-user-menu-toggle]");
    const userMenuList = document.querySelector("[data-user-menu-list]");

    const setMobileNav = (isOpen) => {
        if (!mobileToggle || !mobileNav) {
            return;
        }

        mobileToggle.setAttribute("aria-expanded", String(isOpen));
        mobileNav.hidden = !isOpen;
        mobileNav.classList.toggle("is-open", isOpen);
    };

    const setUserMenu = (isOpen) => {
        if (!userMenuToggle || !userMenuList) {
            return;
        }

        userMenuToggle.setAttribute("aria-expanded", String(isOpen));
        userMenuList.classList.toggle("is-open", isOpen);
    };

    if (mobileToggle && mobileNav) {
        setMobileNav(false);

        mobileToggle.addEventListener("click", (event) => {
            event.stopPropagation();
            const nextState = mobileNav.hidden;
            setMobileNav(nextState);
        });
    }

    if (userMenu && userMenuToggle && userMenuList) {
        setUserMenu(false);

        userMenuToggle.addEventListener("click", (event) => {
            event.stopPropagation();
            const nextState = !userMenuList.classList.contains("is-open");
            setUserMenu(nextState);
        });
    }

    document.addEventListener("click", (event) => {
        if (
            userMenu &&
            userMenuList.classList.contains("is-open") &&
            !userMenu.contains(event.target)
        ) {
            setUserMenu(false);
        }

        if (mobileToggle && mobileNav.classList.contains("is-open")) {
            const clickedInsideMobileMenu =
                mobileNav.contains(event.target) ||
                mobileToggle.contains(event.target);
            if (!clickedInsideMobileMenu) {
                setMobileNav(false);
            }
        }
    });

    document.addEventListener("keydown", (event) => {
        if (event.key !== "Escape") {
            return;
        }

        if (userMenuList && userMenuList.classList.contains("is-open")) {
            setUserMenu(false);
            userMenuToggle?.focus();
        }

        if (mobileNav && mobileNav.classList.contains("is-open")) {
            setMobileNav(false);
            mobileToggle?.focus();
        }
    });

    const csrfToken =
        document.querySelector('meta[name="csrf-token"]')?.getAttribute("content") || "";
    const favoriteSyncEvent = "favorite:changed";

    const setFavoriteUi = (form, isFavorite) => {
        if (!form) {
            return;
        }

        form.dataset.favorited = isFavorite ? "true" : "false";
        const button = form.querySelector("[data-favorite]");
        const text = form.querySelector(".favorite-text");
        if (button) {
            button.setAttribute(
                "aria-label",
                isFavorite ? "Xoá khỏi danh sách yêu thích" : "Thêm vào danh sách yêu thích",
            );
        }
        if (text) {
            text.textContent = isFavorite
                ? "Đã yêu thích · Nhấn để bỏ"
                : "Thêm vào danh sách yêu thích !";
        }
    };

    const syncFavoriteForms = (destinationId, isFavorite) => {
        if (!destinationId) {
            return;
        }
        document
            .querySelectorAll(
                `[data-favorite-form][data-destination-id="${CSS.escape(String(destinationId))}"]`,
            )
            .forEach((form) => setFavoriteUi(form, isFavorite));
    };

    const toggleFavorite = async (form) => {
        const currentlyFavorite = form.dataset.favorited === "true";
        const addUrl = form.dataset.favoriteAddUrl;
        const removeUrl = form.dataset.favoriteRemoveUrl;
        const button = form.querySelector("[data-favorite]");
        const endpoint = currentlyFavorite ? removeUrl : addUrl;

        if (!endpoint || !button) {
            return;
        }

        const payload = new FormData();
        payload.append("_token", csrfToken);
        if (currentlyFavorite) {
            payload.append("_method", "DELETE");
        }

        button.disabled = true;
        try {
            const response = await fetch(endpoint, {
                method: "POST",
                headers: {
                    Accept: "application/json",
                    "X-Requested-With": "XMLHttpRequest",
                },
                body: payload,
                credentials: "same-origin",
                redirect: "follow",
            });

            const contentType = response.headers.get("content-type") || "";
            if (response.redirected && !contentType.includes("application/json")) {
                window.location.href = response.url;
                return;
            }

            const result = contentType.includes("application/json")
                ? await response.json()
                : null;

            if (!response.ok || !result || result.success === false) {
                throw new Error(result?.error || "Không thể cập nhật yêu thích.");
            }

            const destinationId = form.dataset.destinationId;
            const nextFavorite = !currentlyFavorite;
            setFavoriteUi(form, nextFavorite);
            syncFavoriteForms(destinationId, nextFavorite);
            document.dispatchEvent(
                new CustomEvent(favoriteSyncEvent, {
                    detail: { destinationId, isFavorite: nextFavorite },
                }),
            );
        } catch (_) {
            return;
        } finally {
            button.disabled = false;
        }
    };

    document.querySelectorAll("[data-favorite-form]").forEach((form) => {
        setFavoriteUi(form, form.dataset.favorited === "true");
        form.addEventListener("submit", (event) => {
            event.preventDefault();
            toggleFavorite(form);
        });
    });
});
