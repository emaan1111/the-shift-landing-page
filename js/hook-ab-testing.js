(function() {
    const STORAGE_KEY = 'the-shift-hook-variant';

    const variants = [
        {
            id: 'A',
            label: 'Original Hook',
            tagText: 'TRANSFORMATION CHALLENGE',
            heroHeadingHtml: 'You are <span>JUST ONE SHIFT</span> away',
            includeNameInHeading: true,
            personalizeHeading(name) {
                return `${name}, you are <span>JUST ONE SHIFT</span> away`;
            },
            highlightedMessageHtml: `From forcing your child to pray, read Qur'an, and learn Islam — to <span class="emphasis">them wanting it themselves</span> ... even if they don't seem to care`
        },
        {
            id: 'B',
            label: 'Original Hook',
            tagText: 'TRANSFORMATION CHALLENGE',
            heroHeadingHtml: 'You are <span>JUST ONE SHIFT</span> away',
            includeNameInHeading: false,
            highlightedMessageHtml: `From forcing your child to pray, read Qur'an, and learn Islam — to <span class="emphasis">them wanting it themselves</span> ... even if they don't seem to care`
        }
    ];

    function getSavedVariantId() {
        try {
            return window.localStorage.getItem(STORAGE_KEY);
        } catch (error) {
            return null;
        }
    }

    function saveVariantId(id) {
        try {
            window.localStorage.setItem(STORAGE_KEY, id);
        } catch (error) {
            // Ignore storage errors (e.g. Safari private mode)
        }
    }

    function pickVariant() {
        const savedId = getSavedVariantId();
        let variant = variants.find(item => item.id === savedId);

        if (!variant) {
            const randomIndex = Math.floor(Math.random() * variants.length);
            variant = variants[randomIndex];
            saveVariantId(variant.id);
        }

        return variant;
    }

    function applyVariant(variant) {
        const tagElement = document.querySelector('.hero .tag');
        const heroHeading = document.getElementById('hero-heading');
        const highlightedMessage = document.querySelector('.highlighted-message p');

        if (tagElement && variant.tagText) {
            tagElement.textContent = variant.tagText;
        }

        if (heroHeading && variant.heroHeadingHtml) {
            heroHeading.innerHTML = variant.heroHeadingHtml;
        }

        if (highlightedMessage && variant.highlightedMessageHtml) {
            highlightedMessage.innerHTML = variant.highlightedMessageHtml;
        }

        document.documentElement.setAttribute('data-hook-variant', variant.id);
        window.__HOOK_VARIANT__ = variant;
    }

    function notifyVariantApplied(variant) {
        try {
            const event = new CustomEvent('hookVariantApplied', { detail: { variant } });
            window.dispatchEvent(event);
        } catch (error) {
            // Ignore environments without CustomEvent support
        }
    }

    const selectedVariant = pickVariant();
    window.__HOOK_VARIANT__ = selectedVariant;

    document.addEventListener('DOMContentLoaded', function() {
        applyVariant(window.__HOOK_VARIANT__);
        notifyVariantApplied(window.__HOOK_VARIANT__);
    });
})();
