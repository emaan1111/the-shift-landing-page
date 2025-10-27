// Database-based Analytics Tracker
// Replaces GitHub-based tracking with direct database storage via API

// Generate or retrieve persistent visitor ID
let visitorId = localStorage.getItem('visitorId');
if (!visitorId) {
    visitorId = 'visitor_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    localStorage.setItem('visitorId', visitorId);
    console.log('🆕 New visitor ID created:', visitorId);
} else {
    console.log('✅ Existing visitor ID found:', visitorId);
}

// Generate unique session ID for this page view
let sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
console.log('🔔 Session ID for this page view:', sessionId);

let pageEntryTime = Date.now();

// Helper function to get URL parameters
function getURLParameter(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}

// Get geolocation data
async function getGeolocationData() {
    try {
        console.log('🌍 Fetching geolocation data...');
        const geoResponse = await fetch('/api/geolocation');
        
        if (geoResponse.ok) {
            const geoData = await geoResponse.json();
            console.log('✅ Geolocation data:', geoData);
            return {
                ipAddress: geoData.ip || 'Unknown',
                city: geoData.city || 'Unknown',
                region: geoData.region || 'Unknown',
                country: geoData.country_name || 'Unknown',
                timezone: geoData.timezone || 'Unknown'
            };
        } else {
            console.log('⚠️ Geolocation API returned status:', geoResponse.status);
            return null;
        }
    } catch (error) {
        console.log('⚠️ Could not fetch geolocation:', error);
        return null;
    }
}

// Track page visit
async function trackPageVisit() {
    // Skip if on analytics page
    if (window.location.pathname.includes('analytics')) {
        console.log('⏭️ Tracking skipped - on analytics page');
        return;
    }
    
    console.log('🔍 Starting page visit tracking...');
    
    const data = {
        page: window.location.pathname,
        timestamp: new Date().toISOString(),
        event: 'page_visit',
        visitorId: visitorId,
        sessionId: sessionId,
        referrer: document.referrer || 'Direct',
        userAgent: navigator.userAgent,
        screenWidth: window.screen.width,
        screenHeight: window.screen.height,
        language: navigator.language
    };

    // Add hook variant if present
    if (window.__HOOK_VARIANT__ && window.__HOOK_VARIANT__.id) {
        data.hookVariant = window.__HOOK_VARIANT__.id;
    }

    // Get URL parameters
    const email = getURLParameter('email');
    const name = getURLParameter('name');
    const firstName = getURLParameter('first_name') || getURLParameter('firstname');
    const lastName = getURLParameter('last_name') || getURLParameter('lastname');
    const urlCountry = getURLParameter('country');
    const utmSource = getURLParameter('utm_source');
    const utmMedium = getURLParameter('utm_medium');
    const utmCampaign = getURLParameter('utm_campaign');
    const utmContent = getURLParameter('utm_content');
    const referredBy = getURLParameter('ref'); // Referral ID
    
    if (email) data.email = email;
    if (name) {
        data.name = name;
    } else if (firstName || lastName) {
        data.name = [firstName, lastName].filter(Boolean).join(' ');
    }
    if (utmSource) data.utmSource = utmSource;
    if (utmMedium) data.utmMedium = utmMedium;
    if (utmCampaign) data.utmCampaign = utmCampaign;
    if (utmContent) data.utmContent = utmContent;
    if (referredBy) data.referredBy = parseInt(referredBy, 10); // Convert to integer

    // Get geolocation
    const geoData = await getGeolocationData();
    if (geoData) {
        data.ipAddress = geoData.ipAddress;
        data.city = geoData.city;
        data.region = geoData.region;
        data.timezone = geoData.timezone;
        
        // Prefer URL country parameter, fall back to geolocation
        if (urlCountry) {
            data.country = urlCountry;
        } else {
            data.country = geoData.country;
        }
    } else if (urlCountry) {
        data.country = urlCountry;
    }

    // Save to database via API
    try {
        const response = await fetch('/api/analytics/track', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log('✅ Page visit tracked! ID:', result.id);
        } else {
            console.error('❌ Error tracking page visit:', response.status);
        }
    } catch (error) {
        console.error('❌ Error tracking page visit:', error);
    }
}

// Track page exit
async function trackPageExit() {
    const duration = Math.round((Date.now() - pageEntryTime) / 1000);
    
    const data = {
        page: window.location.pathname,
        timestamp: new Date().toISOString(),
        event: 'page_exit',
        sessionId: sessionId,
        visitorId: visitorId,
        duration: duration
    };

    if (window.__HOOK_VARIANT__ && window.__HOOK_VARIANT__.id) {
        data.hookVariant = window.__HOOK_VARIANT__.id;
    }

    try {
        // Use sendBeacon for reliable exit tracking (doesn't block page unload)
        const blob = new Blob([JSON.stringify(data)], { type: 'application/json' });
        navigator.sendBeacon('/api/analytics/track', blob);
        console.log('✅ Page exit tracked! Duration:', duration, 'seconds');
    } catch (error) {
        console.log('⚠️ Exit tracking error:', error);
    }
}

// Track button clicks
async function trackButtonClick(buttonName) {
    const data = {
        page: window.location.pathname,
        timestamp: new Date().toISOString(),
        event: 'button_click',
        buttonName: buttonName,
        visitorId: visitorId,
        sessionId: sessionId,
        referrer: document.referrer || 'Direct'
    };

    if (window.__HOOK_VARIANT__ && window.__HOOK_VARIANT__.id) {
        data.hookVariant = window.__HOOK_VARIANT__.id;
    }

    try {
        const response = await fetch('/api/analytics/track', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            console.log('✅ Button click tracked:', buttonName);
        } else {
            console.error('❌ Error tracking button click:', response.status);
        }
    } catch (error) {
        console.error('❌ Error tracking button click:', error);
    }
}

// Track registrations
async function trackRegistration(formData) {
    const data = {
        timestamp: new Date().toISOString(),
        visitorId: visitorId,
        sessionId: sessionId,
        ...formData
    };

    if (window.__HOOK_VARIANT__ && window.__HOOK_VARIANT__.id) {
        data.hookVariant = window.__HOOK_VARIANT__.id;
    }

    try {
        const response = await fetch('/api/analytics/registration', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log('✅ Registration tracked! ID:', result.id);
            return result.id;
        } else {
            console.error('❌ Error tracking registration:', response.status);
            return null;
        }
    } catch (error) {
        console.error('❌ Error tracking registration:', error);
        return null;
    }
}

// Initialize tracking when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', trackPageVisit);
} else {
    trackPageVisit();
}

// Track page exit
window.addEventListener('beforeunload', trackPageExit);
window.addEventListener('pagehide', trackPageExit);

// Track visibility changes
let visibilityChangeTime = Date.now();
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        visibilityChangeTime = Date.now();
    } else {
        const awayTime = Date.now() - visibilityChangeTime;
        if (awayTime > 1000) {
            pageEntryTime += awayTime;
        }
    }
});

// Track CTA button clicks
document.addEventListener('click', function(e) {
    const target = e.target.closest('a, button');
    if (target) {
        const buttonText = target.textContent.trim();
        const href = target.getAttribute('href') || '';
        
        // Track if button text matches these keywords OR if it's a social share link
        if (buttonText.includes('Register') || 
            buttonText.includes('Join') || 
            buttonText.includes('Get') ||
            buttonText.includes('Yes') ||
            buttonText.includes('Add to Calendar') ||
            buttonText.includes('Share') ||
            href.includes('whatsapp') ||
            href.includes('facebook') ||
            href.includes('twitter') ||
            href.includes('mailto:') ||
            target.classList.contains('btn-whatsapp') ||
            target.classList.contains('btn-calendar') ||
            target.classList.contains('btn-community') ||
            target.classList.contains('btn-vip')) {
            
            // Create a more descriptive button name
            let trackingName = buttonText;
            if (href.includes('whatsapp')) trackingName = 'WhatsApp Share';
            if (href.includes('facebook')) trackingName = 'Facebook Share';
            if (href.includes('twitter')) trackingName = 'Twitter Share';
            if (href.includes('mailto:')) trackingName = 'Email Share';
            if (target.classList.contains('btn-vip')) trackingName = 'VIP Upgrade Button';
            if (target.classList.contains('btn-community')) trackingName = 'Join Community Button';
            
            trackButtonClick(trackingName);
        }
    }
});

// Export functions for use in HTML
window.trackButtonClick = trackButtonClick;
window.trackRegistration = trackRegistration;
window.trackPageVisit = trackPageVisit;
