// ClickFunnels 2.0 Integration
// Sends contact data to ClickFunnels when user registers

async function sendToClickFunnels(contactData) {
    try {
        const { apiKey, workspaceId } = CLICKFUNNELS_CONFIG;
        
        // ClickFunnels 2.0 API endpoint for creating contacts
        const url = `https://api.myclickfunnels.com/api/v2/workspaces/${workspaceId}/contacts`;
        
        // Prepare contact payload
        const payload = {
            contact: {
                email: contactData.email,
                first_name: contactData.firstName || '',
                last_name: contactData.lastName || '',
                phone_number: contactData.phone || '',
                // Custom fields
                fields: {
                    source: contactData.source || window.location.href,
                    utm_source: contactData.utm_source || '',
                    utm_medium: contactData.utm_medium || '',
                    utm_campaign: contactData.utm_campaign || '',
                    country: contactData.country || '',
                    city: contactData.city || '',
                    referrer: contactData.referrer || ''
                }
            }
        };
        
        // Send to ClickFunnels
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
            console.log('✅ Contact sent to ClickFunnels:', result);
            return { success: true, data: result };
        } else {
            const error = await response.json();
            console.error('❌ ClickFunnels API Error:', error);
            return { success: false, error: error };
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
    const firstName = urlParams.get('first_name') || 
                     urlParams.get('firstname') || 
                     urlParams.get('name') || '';
    const lastName = urlParams.get('last_name') || 
                    urlParams.get('lastname') || '';
    
    // Get email
    const email = urlParams.get('email') || '';
    
    // Get phone if provided
    const phone = urlParams.get('phone') || '';
    
    // Get UTM parameters
    const utm_source = urlParams.get('utm_source') || '';
    const utm_medium = urlParams.get('utm_medium') || '';
    const utm_campaign = urlParams.get('utm_campaign') || '';
    const utm_content = urlParams.get('utm_content') || '';
    
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

// Main function to handle registration
async function handleRegistration() {
    // Get contact data from URL
    let contactData = getContactData();
    
    // Check if we have at least an email
    if (!contactData.email || contactData.email.trim() === '') {
        console.log('No email found in URL parameters. Skipping ClickFunnels sync.');
        return;
    }
    
    // Add geolocation
    contactData = await addGeolocation(contactData);
    
    // Send to ClickFunnels
    const result = await sendToClickFunnels(contactData);
    
    if (result.success) {
        console.log('✅ Successfully registered contact in ClickFunnels');
        
        // Optional: Show success message to user
        // You can add a subtle notification here if needed
    } else {
        console.log('⚠️ Could not register contact in ClickFunnels');
    }
}

// Auto-register when page loads if email is present
window.addEventListener('load', () => {
    // Wait a bit to ensure other scripts are loaded
    setTimeout(() => {
        if (typeof CLICKFUNNELS_CONFIG !== 'undefined') {
            handleRegistration();
        } else {
            console.error('ClickFunnels config not loaded');
        }
    }, 500);
});

// Also expose function globally for manual triggering
window.registerInClickFunnels = handleRegistration;
