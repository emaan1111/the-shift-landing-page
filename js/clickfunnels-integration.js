// ClickFunnels 2.0 Integration
// Sends contact data to ClickFunnels when user registers

const DEFAULT_REGISTER_TAG_IDS = [367566]; // List-ShiftRegistered-Nov25
const DEFAULT_VISITOR_TAG_IDS = [367576]; // List-ShiftVisitiedNov24

function getParamValue(params, keys) {
    for (const key of keys) {
        const value = params.get(key);
        if (value && value.trim() !== '') {
            return value;
        }
    }
    return '';
}

function getRegisterTagIds() {
    if (typeof CLICKFUNNELS_CONFIG !== 'undefined' && Array.isArray(CLICKFUNNELS_CONFIG.tagIds) && CLICKFUNNELS_CONFIG.tagIds.length > 0) {
        return CLICKFUNNELS_CONFIG.tagIds;
    }
    return DEFAULT_REGISTER_TAG_IDS;
}

function getVisitorTagIds() {
    if (typeof CLICKFUNNELS_CONFIG !== 'undefined' && Array.isArray(CLICKFUNNELS_CONFIG.visitorTagIds) && CLICKFUNNELS_CONFIG.visitorTagIds.length > 0) {
        return CLICKFUNNELS_CONFIG.visitorTagIds;
    }
    return DEFAULT_VISITOR_TAG_IDS;
}

async function sendToClickFunnels(contactData, options = {}) {
    if (typeof CLICKFUNNELS_CONFIG === 'undefined') {
        throw new Error('ClickFunnels config not loaded');
    }

    const { apiKey, workspaceId, tagIds } = CLICKFUNNELS_CONFIG;
    const finalTagIds = Array.isArray(options.tagIds) && options.tagIds.length > 0
        ? options.tagIds
        : (contactData.tagIds && contactData.tagIds.length > 0
            ? contactData.tagIds
            : (tagIds && tagIds.length > 0 ? tagIds : getRegisterTagIds()));

    const normalizedPayload = {
        email: contactData.email,
        firstName: contactData.firstName || '',
        lastName: contactData.lastName || '',
        phone: contactData.phone || '',
        tagIds: finalTagIds,
        source: contactData.source || window.location.href,
        utm_source: contactData.utm_source || '',
        utm_medium: contactData.utm_medium || '',
        utm_campaign: contactData.utm_campaign || '',
        utm_content: contactData.utm_content || '',
        country: contactData.country || '',
        city: contactData.city || '',
        referrer: contactData.referrer || ''
    };

    if (contactData.registration_date) {
        normalizedPayload.registration_date = contactData.registration_date;
    }

    const canUseBackend = typeof window !== 'undefined'
        && window.location
        && (window.location.protocol === 'http:' || window.location.protocol === 'https:');

    if (canUseBackend) {
        try {
            const backendUrl = `${window.location.origin}/api/clickfunnels/contact`;
            const response = await fetch(backendUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(normalizedPayload)
            });

            let result;
            try {
                result = await response.json();
            } catch (parseError) {
                result = { success: false, error: 'Invalid JSON response from backend' };
            }

            if (response.ok && result && result.success) {
                console.log('✅ Contact sent to ClickFunnels via backend:', result);
                return result;
            }

            console.warn('Backend ClickFunnels proxy failed:', response.status, result);
        } catch (backendError) {
            console.warn('Backend ClickFunnels proxy error:', backendError);
        }
    }

    // Fallback to direct ClickFunnels API call
    try {
        const url = `https://api.myclickfunnels.com/api/v2/workspaces/${workspaceId}/contacts/upsert`;
        const payload = {
            contact: {
                email_address: contactData.email,
                first_name: contactData.firstName || '',
                last_name: contactData.lastName || '',
                phone_number: contactData.phone || '',
                tag_ids: finalTagIds,
                fields: {
                    source: contactData.source || window.location.href,
                    utm_source: contactData.utm_source || '',
                    utm_medium: contactData.utm_medium || '',
                    utm_campaign: contactData.utm_campaign || '',
                    utm_content: contactData.utm_content || '',
                    country: contactData.country || '',
                    city: contactData.city || '',
                    referrer: contactData.referrer || ''
                }
            }
        };

        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${apiKey}`,
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            const result = await response.json();
            console.log('✅ Contact sent to ClickFunnels directly:', result);
            return { success: true, data: result };
        } else {
            const error = await response.json().catch(() => ({ message: 'Unknown error' }));
            console.error('❌ ClickFunnels API Error:', error);
            return { success: false, error };
        }
    } catch (error) {
        console.error('❌ Error sending to ClickFunnels:', error);
        return { success: false, error: error.message };
    }
}

// Function to extract contact data from URL parameters and page context
function getContactData() {
    const urlParams = new URLSearchParams(window.location.search);
    
    // Get name parts
    const firstName = getParamValue(urlParams, ['first_name', 'firstname', 'firstName', 'name', 'FirstName', 'FIRSTNAME']);
    const lastName = getParamValue(urlParams, ['last_name', 'lastname', 'lastName', 'LastName', 'LASTNAME']);
    
    // Get email
    const email = getParamValue(urlParams, ['email', 'Email', 'EMAIL', 'e', 'email_address', 'EmailAddress', 'EMAIL_ADDRESS']);
    
    // Get phone if provided
    const phone = getParamValue(urlParams, ['phone', 'Phone', 'PHONE', 'phone_number', 'PhoneNumber']);
    
    // Get UTM parameters
    const utm_source = getParamValue(urlParams, ['utm_source', 'UTM_SOURCE', 'utmSource']);
    const utm_medium = getParamValue(urlParams, ['utm_medium', 'UTM_MEDIUM', 'utmMedium']);
    const utm_campaign = getParamValue(urlParams, ['utm_campaign', 'UTM_CAMPAIGN', 'utmCampaign']);
    const utm_content = getParamValue(urlParams, ['utm_content', 'UTM_CONTENT', 'utmContent']);
    
    // Get referrer
    const referrer = document.referrer || '';
    
    return {
        email,
        firstName,
        lastName,
        phone,
        utm_source,
        utm_medium,
        utm_campaign,
        utm_content,
        referrer,
        source: window.location.href,
        // Geolocation will be added after API call
        country: '',
        city: ''
    };
}

// Function to add geolocation data
async function addGeolocation(contactData) {
    try {
        const response = await fetch('https://ipapi.co/json/');
        const data = await response.json();
        
        contactData.country = data.country_name || '';
        contactData.city = data.city || '';
        
    } catch (error) {
        console.log('Could not get geolocation:', error);
    }
    
    return contactData;
}

function buildNextUrl(contactData) {
    const params = new URLSearchParams();
    if (contactData.email) {
        params.set('email', contactData.email);
    }
    if (contactData.firstName) {
        params.set('name', contactData.firstName);
    }
    return params.toString().length > 0 ? `upsell.html?${params.toString()}` : 'upsell.html';
}

async function handleRegistration(options = {}) {
    let contactData = options.contactData ? { ...options.contactData } : getContactData();

    if (!contactData.email || contactData.email.trim() === '') {
        console.log('No email found for registration. Skipping ClickFunnels sync.');
        return { success: false, reason: 'missing_email' };
    }

    if (options.includeGeo !== false) {
        contactData = await addGeolocation(contactData);
    }

    if (!contactData.registration_date) {
        contactData.registration_date = new Date().toISOString();
    }

    const tagIds = Array.isArray(options.tagIds) && options.tagIds.length > 0
        ? options.tagIds
        : getRegisterTagIds();

    const result = await sendToClickFunnels(
        { ...contactData, tagIds },
        { tagIds }
    );

    if (result.success) {
        console.log('✅ Successfully registered contact in ClickFunnels');
    } else {
        console.log('⚠️ Could not register contact in ClickFunnels');
    }

    return result;
}

async function tagVisitIfNeeded(contactData) {
    if (!contactData.email) {
        return;
    }

    try {
        const visitorTags = getVisitorTagIds();
        const result = await sendToClickFunnels(
            { ...contactData, tagIds: visitorTags },
            { tagIds: visitorTags }
        );

        if (result.success) {
            console.log('✅ Visitor tag applied in ClickFunnels');
        } else {
            console.warn('Visitor tagging failed:', result.error);
        }
    } catch (error) {
        console.warn('Visitor tagging error:', error);
    }
}

function setupCtaAutoRegistration(contactData) {
    const selectors = [
        'a.cta-main',
        'a.cta-header',
        'a.cta-grand',
        'a.cta-final',
        'a[data-register-cta]',
        'button[data-register-cta]'
    ];

    const ctaElements = Array.from(document.querySelectorAll(selectors.join(', ')));

    if (!ctaElements.length || !contactData.email) {
        return;
    }

    const nextUrl = buildNextUrl(contactData);
    const combinedTagIds = Array.from(new Set([...getVisitorTagIds(), ...getRegisterTagIds()]));
    let inFlight = false;

    const handleCtaClick = async (event) => {
        if (event) {
            event.preventDefault();
        }

        if (inFlight) {
            if (nextUrl) {
                window.location.href = nextUrl;
            }
            return;
        }

        inFlight = true;
        try {
            let enrichedData = await addGeolocation({ ...contactData });
            enrichedData.tagIds = combinedTagIds;
            enrichedData.registration_date = new Date().toISOString();

            const result = await sendToClickFunnels(
                enrichedData,
                { tagIds: combinedTagIds }
            );

            if (result.success) {
                if (nextUrl) {
                    window.location.href = nextUrl;
                }
                return;
            }

            console.warn('CTA registration failed:', result.error);
            if (nextUrl) {
                window.location.href = nextUrl;
                return;
            }

            inFlight = false;
            const targetHref = event?.currentTarget?.getAttribute('href');
            if (targetHref) {
                window.location.href = targetHref;
            }
        } catch (error) {
            console.error('CTA auto registration error:', error);
            if (nextUrl) {
                window.location.href = nextUrl;
                return;
            }

            inFlight = false;
            const targetHref = event?.currentTarget?.getAttribute('href');
            if (targetHref) {
                window.location.href = targetHref;
            }
        }
    };

    ctaElements.forEach((cta) => {
        cta.addEventListener('click', handleCtaClick);
    });
}

// Initialise auto-tagging and CTA handling when config is loaded
window.addEventListener('load', () => {
    setTimeout(() => {
        if (typeof CLICKFUNNELS_CONFIG === 'undefined') {
            console.error('ClickFunnels config not loaded');
            return;
        }

        const contactData = getContactData();
        if (!contactData.email) {
            return;
        }

        tagVisitIfNeeded(contactData);
        setupCtaAutoRegistration(contactData);
    }, 500);
});

// Also expose function globally for manual triggering
window.registerInClickFunnels = handleRegistration;
