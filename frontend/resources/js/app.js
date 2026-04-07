import "./bootstrap";
import "./destination-modal";

document.addEventListener("DOMContentLoaded", () => {
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

        button.addEventListener("click", () => {
            const isHidden = target.hasAttribute("hidden");
            if (isHidden) {
                target.removeAttribute("hidden");
                button.textContent = button.textContent.replace("Mo", "Dong");
            } else {
                target.setAttribute("hidden", "");
                button.textContent = button.textContent.replace("Dong", "Mo");
            }
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
});
