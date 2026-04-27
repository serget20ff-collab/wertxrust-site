(function () {
    document.addEventListener('DOMContentLoaded', function () {
        const header = document.getElementById('topHeader');
        const glow = document.getElementById('cursorGlow');

        const dropdowns = document.querySelectorAll('[data-dropdown]');
        const topupOpenButtons = document.querySelectorAll('[data-open-topup]');
        const topupCloseButtons = document.querySelectorAll('[data-close-topup]');
        const topupBackdrop = document.querySelector('[data-modal-backdrop]');

        let lastScrollY = window.scrollY;
        let ticking = false;

        function updateHeader() {
            if (!header) {
                ticking = false;
                return;
            }

            const currentScrollY = window.scrollY;
            const scrollDiff = currentScrollY - lastScrollY;

            if (currentScrollY > 130 && scrollDiff > 4) {
                header.classList.add('is-hidden');
            }

            if (scrollDiff < -4 || currentScrollY <= 20) {
                header.classList.remove('is-hidden');
            }

            lastScrollY = currentScrollY;
            ticking = false;
        }

        window.addEventListener('scroll', function () {
            if (!ticking) {
                window.requestAnimationFrame(updateHeader);
                ticking = true;
            }
        }, { passive: true });

        window.addEventListener('mousemove', function (event) {
            if (glow) {
                glow.style.transform = `translate3d(${event.clientX}px, ${event.clientY}px, 0)`;
            }
        }, { passive: true });

        dropdowns.forEach(function (dropdown) {
            const button = dropdown.querySelector('[data-dropdown-button]');

            if (!button) return;

            button.addEventListener('click', function (event) {
                event.preventDefault();
                event.stopPropagation();

                dropdowns.forEach(function (item) {
                    if (item !== dropdown) {
                        item.classList.remove('is-open');
                    }
                });

                dropdown.classList.toggle('is-open');
            });
        });

        document.addEventListener('click', function () {
            dropdowns.forEach(function (dropdown) {
                dropdown.classList.remove('is-open');
            });
        });

        function openTopupModal() {
            if (!topupBackdrop) return;

            topupBackdrop.hidden = false;
            document.body.classList.add('modal-open');

            window.requestAnimationFrame(function () {
                topupBackdrop.classList.add('is-visible');
            });
        }

        function closeTopupModal() {
            if (!topupBackdrop || topupBackdrop.hidden) return;

            topupBackdrop.classList.remove('is-visible');
            document.body.classList.remove('modal-open');

            window.setTimeout(function () {
                topupBackdrop.hidden = true;
            }, 180);
        }

        topupOpenButtons.forEach(function (button) {
            button.addEventListener('click', function (event) {
                event.preventDefault();
                event.stopPropagation();
                openTopupModal();
            });
        });

        topupCloseButtons.forEach(function (button) {
            button.addEventListener('click', function (event) {
                event.preventDefault();
                closeTopupModal();
            });
        });

        if (topupBackdrop) {
            topupBackdrop.addEventListener('click', function (event) {
                if (event.target === topupBackdrop) {
                    closeTopupModal();
                }
            });
        }

        function closeProductModals() {
            document.querySelectorAll('.product-modal').forEach(function (modal) {
                modal.classList.remove('is-visible');

                window.setTimeout(function () {
                    modal.hidden = true;
                }, 160);
            });

            document.body.classList.remove('modal-open');
        }

        document.querySelectorAll('[data-product-open]').forEach(function (button) {
            button.addEventListener('click', function () {
                const productId = button.dataset.productId;
                const modal = document.querySelector(`[data-product-modal="${productId}"]`);

                if (!modal) return;

                modal.hidden = false;
                document.body.classList.add('modal-open');

                window.requestAnimationFrame(function () {
                    modal.classList.add('is-visible');
                });
            });
        });

        document.querySelectorAll('[data-product-close]').forEach(function (button) {
            button.addEventListener('click', function () {
                closeProductModals();
            });
        });

        document.querySelectorAll('.product-modal').forEach(function (modal) {
            modal.addEventListener('click', function (event) {
                if (event.target === modal) {
                    closeProductModals();
                }
            });
        });

        function updateModalPrice(modal) {
    const input = modal.querySelector('[data-qty-input]');
    const currentPrice = modal.querySelector('[data-total-price]');
    const oldPrice = modal.querySelector('[data-total-old-price]');

    if (!input || !currentPrice) return;

    let quantity = parseInt(input.value || '1', 10);

    if (Number.isNaN(quantity) || quantity < 1) {
        quantity = 1;
    }

    if (quantity > 99) {
        quantity = 99;
    }

    const basePrice = parseFloat(String(currentPrice.dataset.basePrice || '0').replace(',', '.'));
    const total = Math.round(basePrice * quantity);

    input.value = quantity;
    currentPrice.textContent = `${total} ₽`;

    if (oldPrice) {
        const baseOldPrice = parseFloat(String(oldPrice.dataset.baseOldPrice || '0').replace(',', '.'));
        const oldTotal = Math.round(baseOldPrice * quantity);

        oldPrice.textContent = `${oldTotal} ₽`;
    }
}

        document.querySelectorAll('[data-qty-minus]').forEach(function (button) {
            button.addEventListener('click', function () {
                const modal = button.closest('.product-modal');
                const input = modal.querySelector('[data-qty-input]');

                input.value = Math.max(1, parseInt(input.value || '1', 10) - 1);
                updateModalPrice(modal);
            });
        });

        document.querySelectorAll('[data-qty-plus]').forEach(function (button) {
            button.addEventListener('click', function () {
                const modal = button.closest('.product-modal');
                const input = modal.querySelector('[data-qty-input]');

                input.value = Math.min(99, parseInt(input.value || '1', 10) + 1);
                updateModalPrice(modal);
            });
        });

        document.querySelectorAll('[data-qty-input]').forEach(function (input) {
            input.addEventListener('input', function () {
                const modal = input.closest('.product-modal');
                updateModalPrice(modal);
            });
        });

        document.querySelectorAll('[data-copy]').forEach(function (button) {
            button.addEventListener('click', function () {
                const value = button.dataset.copy || '';

                if (!value) return;

                navigator.clipboard.writeText(value).then(function () {
                    const oldText = button.textContent;
                    button.textContent = 'Скопировано';

                    window.setTimeout(function () {
                        button.textContent = oldText;
                    }, 1200);
                });
            });
        });

        document.querySelectorAll('[data-connect]').forEach(function (button) {
            button.addEventListener('click', function () {
                const value = button.dataset.connect || '';

                if (!value) return;

                window.location.href = `steam://connect/${value}`;
            });
        });

        document.addEventListener('keydown', function (event) {
            if (event.key === 'Escape') {
                closeTopupModal();
                closeProductModals();

                dropdowns.forEach(function (dropdown) {
                    dropdown.classList.remove('is-open');
                });
            }
        });
    });
})();