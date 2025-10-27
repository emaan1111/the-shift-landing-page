// Analytics Charts Module
import { getFirestore, collection, query, getDocs, where } from "https://www.gstatic.com/firebasejs/10.7.0/firebase-firestore.js";

// Function to fetch and display registrations by country
export async function displayRegistrationsByCountry(db, containerId = 'registrations-by-country') {
    try {
        console.log('📊 Fetching registrations by country...');
        
        const registrationsRef = collection(db, 'registrations');
        const q = query(registrationsRef);
        const querySnapshot = await getDocs(q);
        
        // Count registrations by country
        const countryData = {};
        querySnapshot.forEach((doc) => {
            const data = doc.data();
            const country = data.country || 'Unknown';
            countryData[country] = (countryData[country] || 0) + 1;
        });
        
        // Sort by count descending
        const sortedCountries = Object.entries(countryData)
            .sort((a, b) => b[1] - a[1]);
        
        // Create chart HTML
        const container = document.getElementById(containerId);
        if (!container) {
            console.error('❌ Container not found:', containerId);
            return;
        }
        
        const maxCount = Math.max(...sortedCountries.map(([_, count]) => count));
        const total = sortedCountries.reduce((sum, [_, count]) => sum + count, 0);
        
        container.innerHTML = `
            <div class="chart-container">
                <h3>Registrations by Country</h3>
                <p class="chart-subtitle">Total: ${total} registrations</p>
                <div class="bar-chart">
                    ${sortedCountries.map(([country, count]) => {
                        const percentage = ((count / total) * 100).toFixed(1);
                        const barWidth = (count / maxCount) * 100;
                        return `
                            <div class="bar-item">
                                <div class="bar-label">
                                    <span class="country-name">${country}</span>
                                    <span class="country-count">${count} (${percentage}%)</span>
                                </div>
                                <div class="bar-background">
                                    <div class="bar-fill" style="width: ${barWidth}%"></div>
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        `;
        
        console.log('✅ Registrations by country chart displayed');
    } catch (error) {
        console.error('❌ Error displaying registrations by country:', error);
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = `
                <div class="chart-container">
                    <h3>Registrations by Country</h3>
                    <p style="color: red;">Error loading chart: ${error.message}</p>
                </div>
            `;
        }
    }
}

// Add CSS styles
const styles = `
.chart-container {
    background: white;
    border-radius: 8px;
    padding: 24px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    margin: 20px 0;
}

.chart-container h3 {
    margin: 0 0 8px 0;
    font-size: 20px;
    font-weight: 600;
    color: #1a1a1a;
}

.chart-subtitle {
    margin: 0 0 20px 0;
    color: #666;
    font-size: 14px;
}

.bar-chart {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.bar-item {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.bar-label {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 14px;
}

.country-name {
    font-weight: 500;
    color: #1a1a1a;
}

.country-count {
    color: #666;
    font-size: 13px;
}

.bar-background {
    height: 24px;
    background: #f0f0f0;
    border-radius: 4px;
    overflow: hidden;
}

.bar-fill {
    height: 100%;
    background: linear-gradient(90deg, #4CAF50, #45a049);
    transition: width 0.3s ease;
    animation: slideIn 0.5s ease;
}

@keyframes slideIn {
    from {
        width: 0;
    }
}
`;

// Inject styles
if (!document.getElementById('analytics-charts-styles')) {
    const styleElement = document.createElement('style');
    styleElement.id = 'analytics-charts-styles';
    styleElement.textContent = styles;
    document.head.appendChild(styleElement);
}
