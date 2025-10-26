// Firebase-based Analytics Tracker
// Replaces GitHub-based tracking with Firestore database

// Initialize Firebase
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.0/firebase-app.js";
import { getFirestore, collection, addDoc, serverTimestamp } from "https://www.gstatic.com/firebasejs/10.7.0/firebase-firestore.js";

// Import Firebase config - make sure to create this file with your credentials
// See firebase-config.js.template for the structure
let firebaseConfig;
try {
    // Dynamically load the config
    const configResponse = await fetch('/firebase-config.js');
    const configText = await configResponse.text();
    eval(configResponse);
} catch (error) {
    console.error('❌ Could not load Firebase config. Please create js/firebase-config.js with your Firebase credentials.');
    console.error('See FIREBASE_SETUP.md for instructions.');
}

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

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
            return {
                ipAddress: geoData.ip || 'Unknown',
                city: geoData.city || 'Unknown',
                region: geoData.region || 'Unknown',
                timezone: geoData.timezone || 'Unknown',
                country: geoData.country_name || 'Unknown',
                countryCode: geoData.country_code || 'XX'
            };
        } else if (geoResponse.status === 429) {
            console.log('⚠️ Geolocation API rate limited (429)');
            return null;
        }
    } catch (error) {
        console.log('⚠️ Could not fetch geolocation:', error);
        return null;
    }
}

// Track page visit
async function trackPageVisit() {
    // Skip if on analytics page or if Firebase not initialized
    if (window.location.pathname.includes('analytics') || !db) {
        console.log('⏭️ Tracking skipped - on analytics page or Firebase not ready');
        return;
    }
    
    console.log('🔍 Starting page visit tracking...');
    
    const data = {
        page: window.location.pathname,
        timestamp: serverTimestamp(),
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
            console.log('✅ Using country from form:', urlCountry);
        } else {
            data.country = geoData.country;
            data.countryCode = geoData.countryCode;
            console.log('✅ Using country from geolocation:', geoData.country);
        }
    } else if (urlCountry) {
        data.country = urlCountry;
        console.log('✅ Using country from form (geolocation failed):', urlCountry);
    }

    // Save to Firestore
    try {
        const docRef = await addDoc(collection(db, 'analytics'), data);
        console.log('✅ Page visit tracked! Document ID:', docRef.id);
    } catch (error) {
        console.error('❌ Error tracking page visit:', error);
    }
}

// Track page exit
async function trackPageExit() {
    if (!db) return;
    
    const duration = Math.round((Date.now() - pageEntryTime) / 1000);
    
    const data = {
        page: window.location.pathname,
        timestamp: serverTimestamp(),
        event: 'page_exit',
        sessionId: sessionId,
        visitorId: visitorId,
        duration: duration
    };

    if (window.__HOOK_VARIANT__ && window.__HOOK_VARIANT__.id) {
        data.hookVariant = window.__HOOK_VARIANT__.id;
    }

    try {
        await addDoc(collection(db, 'analytics'), data);
        console.log('✅ Page exit tracked! Duration:', duration, 'seconds');
    } catch (error) {
        console.log('⚠️ Exit tracking error:', error);
    }
}

// Track button clicks
async function trackButtonClick(buttonName) {
    if (!db) return;
    
    const data = {
        page: window.location.pathname,
        timestamp: serverTimestamp(),
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
        await addDoc(collection(db, 'analytics'), data);
        console.log('✅ Button click tracked:', buttonName);
    } catch (error) {
        console.error('❌ Error tracking button click:', error);
    }
}

// Track registrations
async function trackRegistration(formData) {
    if (!db) return;
    
    const data = {
        timestamp: serverTimestamp(),
        event: 'registration',
        visitorId: visitorId,
        sessionId: sessionId,
        ...formData
    };

    if (window.__HOOK_VARIANT__ && window.__HOOK_VARIANT__.id) {
        data.hookVariant = window.__HOOK_VARIANT__.id;
    }

    try {
        const docRef = await addDoc(collection(db, 'registrations'), data);
        console.log('✅ Registration tracked! Document ID:', docRef.id);
        return docRef.id;
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
        if (buttonText.includes('Register') || 
            buttonText.includes('Join') || 
            buttonText.includes('Get') ||
            buttonText.includes('Yes') ||
            buttonText.includes('Add to Calendar')) {
            trackButtonClick(buttonText);
        }
    }
});

// Export functions for use in HTML
window.trackButtonClick = trackButtonClick;
window.trackRegistration = trackRegistration;
window.trackPageVisit = trackPageVisit;
