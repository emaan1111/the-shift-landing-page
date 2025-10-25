// GitHub-based Visitor Tracker
// Configuration is loaded from analytics-config.js
// If ANALYTICS_CONFIG is not defined, uses default placeholder values

const GITHUB_CONFIG = typeof ANALYTICS_CONFIG !== 'undefined' ? ANALYTICS_CONFIG : {
    owner: 'emaan1111',
    repo: 'the-shift-landing-page',
    token: '', // Configure in analytics-config.js (see README for setup)
    branch: 'main'
};

// Generate a unique filename for each day
function getDataFilename() {
    const date = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
    return `analytics/visits-${date}.json`;
}

// Save data to GitHub
async function saveToGitHub(data) {
    const filename = getDataFilename();
    const url = `https://api.github.com/repos/${GITHUB_CONFIG.owner}/${GITHUB_CONFIG.repo}/contents/${filename}`;
    
    try {
        // First, try to get existing file
        let existingData = [];
        let sha = null;
        
        try {
            const getResponse = await fetch(url, {
                headers: {
                    'Authorization': `token ${GITHUB_CONFIG.token}`,
                    'Accept': 'application/vnd.github.v3+json'
                }
            });
            
            if (getResponse.ok) {
                const fileData = await getResponse.json();
                sha = fileData.sha;
                const content = atob(fileData.content);
                existingData = JSON.parse(content);
            }
        } catch (e) {
            // File doesn't exist yet, that's okay
        }
        
        // Add new data
        existingData.push(data);
        
        // Save back to GitHub
        const content = btoa(JSON.stringify(existingData, null, 2));
        const message = sha ? 'Update analytics data' : 'Create analytics data';
        
        const putResponse = await fetch(url, {
            method: 'PUT',
            headers: {
                'Authorization': `token ${GITHUB_CONFIG.token}`,
                'Accept': 'application/vnd.github.v3+json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                content: content,
                sha: sha,
                branch: GITHUB_CONFIG.branch
            })
        });
        
        if (!putResponse.ok) {
            const errorText = await putResponse.text();
            console.error('❌ GitHub tracking error:', putResponse.status, errorText);
        } else {
            console.log('✅ Data successfully saved to GitHub!');
        }
    } catch (error) {
        console.error('❌ Tracking error:', error);
    }
}

// Track page visit
let pageEntryTime = Date.now();

// Generate or retrieve persistent visitor ID (stored in localStorage)
let visitorId = localStorage.getItem('visitorId');
if (!visitorId) {
    visitorId = 'visitor_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    localStorage.setItem('visitorId', visitorId);
    console.log('🆕 New visitor ID created:', visitorId);
} else {
    console.log('✅ Existing visitor ID found:', visitorId);
}

// Generate a unique session ID for this page view
let sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
console.log('🆔 Session ID for this page view:', sessionId);

// Helper function to get URL parameters
function getURLParameter(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}

async function trackPageVisit() {
    // Skip if on analytics page or if no token configured
    if (window.location.pathname.includes('analytics') || !GITHUB_CONFIG.token || GITHUB_CONFIG.token === 'YOUR_GITHUB_TOKEN') {
        console.log('Tracking skipped - on analytics page or no token configured');
        return;
    }
    
    console.log('🔍 Starting page visit tracking...');
    pageEntryTime = Date.now();
    
    const data = {
        page: window.location.pathname,
        timestamp: new Date().toISOString(),
        event: 'page_visit',
        visitorId: visitorId,  // Persistent visitor ID
        sessionId: sessionId,   // Unique per page view
        referrer: document.referrer || 'Direct',
        userAgent: navigator.userAgent,
        screenWidth: window.screen.width,
        screenHeight: window.screen.height,
        language: navigator.language
    };

    if (window.__HOOK_VARIANT__ && window.__HOOK_VARIANT__.id) {
        data.hookVariant = window.__HOOK_VARIANT__.id;
    }

    // Capture email and name from URL parameters if present
    const email = getURLParameter('email');
    const name = getURLParameter('name');
    const country = getURLParameter('country');
    const firstName = getURLParameter('first_name') || getURLParameter('firstname');
    const lastName = getURLParameter('last_name') || getURLParameter('lastname');
    
    if (email) {
        data.email = email;
    }
    
    if (name) {
        data.name = name;
    } else if (firstName || lastName) {
        // Construct name from first/last name if provided separately
        data.name = [firstName, lastName].filter(Boolean).join(' ');
    }
    
    // Capture country from URL parameter (passed from registration form)
    const urlCountry = getURLParameter('country');
    
    // Capture any other UTM parameters or custom parameters
    const utmSource = getURLParameter('utm_source');
    const utmMedium = getURLParameter('utm_medium');
    const utmCampaign = getURLParameter('utm_campaign');
    const utmContent = getURLParameter('utm_content');
    
    if (utmSource) data.utmSource = utmSource;
    if (utmMedium) data.utmMedium = utmMedium;
    if (utmCampaign) data.utmCampaign = utmCampaign;
    if (utmContent) data.utmContent = utmContent;

    // Get geolocation data from free API via Flask proxy
    // Priority: URL country (from form) > Geolocation country
    try {
        console.log('🌍 Fetching geolocation data...');
        const geoResponse = await fetch('/api/geolocation');
        
        if (geoResponse.ok) {
            const geoData = await geoResponse.json();
            data.ipAddress = geoData.ip || 'Unknown';
            data.city = geoData.city || 'Unknown';
            data.region = geoData.region || 'Unknown';
            data.timezone = geoData.timezone || 'Unknown';
            
            // Use URL country (from form) if available, otherwise use geolocation
            if (urlCountry) {
                data.country = urlCountry;
                console.log('✅ Using country from form:', urlCountry);
            } else {
                data.country = geoData.country_name || 'Unknown';
                data.countryCode = geoData.country_code || 'XX';
                console.log('✅ Using country from geolocation:', data.country);
            }
            
            console.log('✅ Geolocation data:', { city: data.city, country: data.country, ip: data.ipAddress });
        } else if (geoResponse.status === 429) {
            console.log('⚠️ Geolocation API rate limit reached (429). Using form country if available.');
            // Use form country if available
            if (urlCountry) {
                data.country = urlCountry;
                console.log('✅ Using country from form due to rate limit:', urlCountry);
            } else {
                console.log('⚠️ No country data available (rate limited and no form country)');
            }
        } else {
            console.log('⚠️ Geolocation API returned status:', geoResponse.status);
            // Use form country as fallback
            if (urlCountry) {
                data.country = urlCountry;
                console.log('✅ Using country from form as fallback:', urlCountry);
            }
        }
    } catch (error) {
        console.log('⚠️ Could not fetch geolocation:', error);
        // Use form country as fallback
        if (urlCountry) {
            data.country = urlCountry;
            console.log('✅ Using country from form (geolocation failed):', urlCountry);
        }
    }

    console.log('📤 Saving tracking data to GitHub...', data);
    await saveToGitHub(data);
    console.log('✅ Tracking complete!');
}

// Track page exit/duration
async function trackPageExit() {
    if (!GITHUB_CONFIG.token || GITHUB_CONFIG.token === 'YOUR_GITHUB_TOKEN') {
        return;
    }
    
    const duration = Math.round((Date.now() - pageEntryTime) / 1000); // seconds
    
    const data = {
        page: window.location.pathname,
        timestamp: new Date().toISOString(),
        event: 'page_exit',
        sessionId: sessionId,
        duration: duration
    };
    
    // Use sendBeacon for reliable exit tracking
    const url = `https://api.github.com/repos/${GITHUB_CONFIG.owner}/${GITHUB_CONFIG.repo}/contents/${getDataFilename()}`;
    
    try {
        // For page exit, we'll use a simpler approach - just send the data
        await saveToGitHub(data);
    } catch (error) {
        console.log('Exit tracking error:', error);
    }
}

// Track button clicks
function trackButtonClick(buttonName) {
    // Skip if no token configured
    if (GITHUB_CONFIG.token === 'YOUR_GITHUB_TOKEN') {
        return;
    }
    
    const data = {
        page: window.location.pathname,
        timestamp: new Date().toISOString(),
        event: 'button_click',
        buttonName: buttonName,
        referrer: document.referrer || 'Direct'
    };

    saveToGitHub(data);
}

// Track page visit on load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', trackPageVisit);
} else {
    trackPageVisit();
}

// Track page exit/duration
window.addEventListener('beforeunload', trackPageExit);
window.addEventListener('pagehide', trackPageExit);

// Also track visibility change (when user switches tabs)
let visibilityChangeTime = Date.now();
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        visibilityChangeTime = Date.now();
    } else {
        // User came back, update entry time
        const awayTime = Date.now() - visibilityChangeTime;
        if (awayTime > 1000) { // If away more than 1 second, adjust entry time
            pageEntryTime += awayTime;
        }
    }
});

// Track all CTA button clicks
document.addEventListener('click', function(e) {
    const target = e.target.closest('a, button');
    if (target) {
        const buttonText = target.textContent.trim();
        if (buttonText.includes('Register') || 
            buttonText.includes('Join') || 
            buttonText.includes('Get') ||
            buttonText.includes('Yes') ||
            buttonText.includes('Add to Calendar')) {
            trackButtonClick(buttonText);
        }
    }
});
