import './bootstrap';

document.addEventListener('DOMContentLoaded', () => {
	const mobileToggle = document.querySelector('[data-mobile-toggle]');
	const mobileNav = document.querySelector('[data-mobile-nav]');
	const userMenu = document.querySelector('[data-user-menu]');
	const userMenuToggle = document.querySelector('[data-user-menu-toggle]');
	const userMenuList = document.querySelector('[data-user-menu-list]');

	if (mobileToggle && mobileNav) {
		mobileToggle.addEventListener('click', () => {
			mobileNav.classList.toggle('is-open');
		});
	}

	if (userMenu && userMenuToggle && userMenuList) {
		userMenuToggle.addEventListener('click', (event) => {
			event.stopPropagation();
			userMenuList.classList.toggle('is-open');
		});

		document.addEventListener('click', (event) => {
			if (!userMenu.contains(event.target)) {
				userMenuList.classList.remove('is-open');
			}
		});
	}
});
