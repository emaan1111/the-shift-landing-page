// GitHub-based Visitor Tracker
// Configuration is loaded from analytics-config.js
// If ANALYTICS_CONFIG is not defined, uses default placeholder values

const GITHUB_CONFIG = typeof ANALYTICS_CONFIG !== 'undefined' ? ANALYTICS_CONFIG : {
    owner: 'emaan1111',
    repo: 'the-shift-landing-page',
    token: 'YOUR_GITHUB_TOKEN',
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
            console.log('GitHub tracking error:', await putResponse.text());
        }
    } catch (error) {
        console.log('Tracking error:', error);
    }
}

// Track page visit
function trackPageVisit() {
    // Skip if on analytics page or if no token configured
    if (window.location.pathname.includes('analytics') || GITHUB_CONFIG.token === 'YOUR_GITHUB_TOKEN') {
        return;
    }
    
    const data = {
        page: window.location.pathname,
        timestamp: new Date().toISOString(),
        event: 'page_visit',
        referrer: document.referrer || 'Direct',
        userAgent: navigator.userAgent,
        screenWidth: window.screen.width,
        screenHeight: window.screen.height,
        language: navigator.language
    };

    saveToGitHub(data);
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
