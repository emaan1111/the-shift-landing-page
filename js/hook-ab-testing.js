(function() {
    const STORAGE_KEY = 'the-shift-hook-variant';

    const variants = [
        {
            id: 'A',
            label: 'Variant A - Don\'t Seem to Care',
            tagText: 'FOR MUSLIM MOTHERS',
            heroHeadingHtml: 'them wanting it themselves',
            includeNameInHeading: false,
            highlightedMessageHtml: `Discover how mothers like you shifted from pushing their children to <span class="emphasis">pray, read Qur'an, and learn Islam </span>— to <span class="emphasis">them wanting it themselves</span> … even if they just want to play games or watch YouTube`,
            ctaText: '[NAME], you are <span class="emphasis">JUST One Shift Away</span>'

        },
        {
            id: 'B',
            label: 'Variant B - Games/YouTube',
            tagText: 'FOR MUSLIM MOTHERS',
            heroHeadingHtml: 'them wanting it themselves',
            includeNameInHeading: false,
            highlightedMessageHtml: `Discover how mothers like you shifted from pushing their children to <span class="emphasis">pray, read Qur'an, and learn Islam </span>— to <span class="emphasis">them wanting it themselves</span> … even if they just want to play games or watch YouTube`,
            ctaText: '<span class="emphasis">You are JUST One Shift Away</span>'
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

    function applyVariant(variant, name = null) {
        const tagElement = document.querySelector('.hero .tag');
        const mainFocusTexts = document.querySelectorAll('.main-focus-text');
        const heroHeading = document.querySelector('#hero-heading');
        const miniHeading = document.querySelector('.mini-heading');

        if (tagElement && variant.tagText) {
            tagElement.textContent = variant.tagText;
        }

        // Update hero heading
        if (heroHeading && variant.heroHeadingHtml) {
            heroHeading.innerHTML = variant.heroHeadingHtml;
        }

        // Update the ending text (the last main-focus-text element)
        if (mainFocusTexts.length > 0) {
            const endingText = mainFocusTexts[mainFocusTexts.length - 1];
            if (variant.highlightedMessageHtml.includes('don\'t seem to care')) {
                endingText.textContent = '… even if they don\'t seem to care';
            } else if (variant.highlightedMessageHtml.includes('play games')) {
                endingText.textContent = '… even if they just want to play games or watch YouTube';
            }
        }

        // Update mini-heading with full CTA text
        if (miniHeading && variant.ctaText) {
            miniHeading.innerHTML = variant.ctaText;
        }

        // Personalize ctaText with name if available
        let personalizedCtaText = variant.ctaText;
        if (personalizedCtaText && name) {
            personalizedCtaText = personalizedCtaText.replace('[NAME],', name + ',');
        } else if (personalizedCtaText) {
            // Remove [NAME], if name is not provided
            personalizedCtaText = personalizedCtaText.replace('[NAME], ', '');
        }

        // Store personalized variant info
        const variantCopy = { ...variant, ctaText: personalizedCtaText };
        
        document.documentElement.setAttribute('data-hook-variant', variant.id);
        window.__HOOK_VARIANT__ = variantCopy;
        
        // Dispatch event with personalized CTA text available
        console.log('Applied Variant:', variant.id, 'Personalized CTA:', personalizedCtaText);
    }

    function notifyVariantApplied(variant) {
        try {
            const event = new CustomEvent('hookVariantApplied', { detail: { variant } });
            window.dispatchEvent(event);
        } catch (error) {
            // Ignore environments without CustomEvent support
        }
    }

    function getNameFromUrl() {
        const params = new URLSearchParams(window.location.search);
        return params.get('name');
    }

    function getVariantFromUrl() {
        const params = new URLSearchParams(window.location.search);
        return params.get('variant');
    }

    const selectedVariant = (() => {
        const urlVariant = getVariantFromUrl();
        if (urlVariant) {
            const variant = variants.find(item => item.id === urlVariant.toUpperCase());
            if (variant) {
                return variant;
            }
        }
        return pickVariant();
    })();
    window.__HOOK_VARIANT__ = selectedVariant;

    // Get name immediately from URL
    let visitorName = getNameFromUrl();

    document.addEventListener('DOMContentLoaded', function() {
        // If name not in URL, try to get from form input
        if (!visitorName) {
            const nameInput = document.getElementById('reg-name');
            visitorName = nameInput ? nameInput.value : null;
        }
        console.log('Hook Script - Variant:', window.__HOOK_VARIANT__.id, 'Name:', visitorName);
        applyVariant(window.__HOOK_VARIANT__, visitorName);
        notifyVariantApplied(window.__HOOK_VARIANT__);
    });
})();
