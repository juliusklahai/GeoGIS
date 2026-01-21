// Initialize Map
const map = L.map('map', {
    zoomControl: false
}).setView([-1.94, 29.87], 9);

// Add Dark Map Tiles
const darkTiles = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    subdomains: 'abcd',
    maxZoom: 20
}).addTo(map);

L.control.zoom({ position: 'bottomright' }).addTo(map);

// Add mock change polygons
const mockLoss = L.circle([-1.94, 29.80], {
    color: '#da3633',
    fillColor: '#da3633',
    fillOpacity: 0.5,
    radius: 1000
}).addTo(map).bindPopup('Forest Loss: 45.6 ha');

const mockGain = L.circle([-1.80, 30.0], {
    color: '#238636',
    fillColor: '#238636',
    fillOpacity: 0.5,
    radius: 800
}).addTo(map).bindPopup('Forest Gain: 12.4 ha');

// Initialize Chart
const ctx = document.getElementById('changeChart').getContext('2d');
const changeChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        datasets: [{
            label: 'Forest Loss',
            data: [1200, 1500, 1800, 3000, 4500, 3800, 2500, 2000, 1500, 1200, 1000, 800],
            borderColor: '#da3633',
            backgroundColor: 'rgba(218, 54, 51, 0.2)',
            fill: true,
            tension: 0.4
        }, {
            label: 'Forest Gain',
            data: [400, 500, 600, 800, 700, 600, 500, 700, 900, 1100, 1200, 1300],
            borderColor: '#238636',
            backgroundColor: 'rgba(35, 134, 54, 0.2)',
            fill: true,
            tension: 0.4
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                grid: { color: '#30363d' },
                ticks: { color: '#8b949e' }
            },
            x: {
                grid: { display: false },
                ticks: { color: '#8b949e' }
            }
        }
    }
});

// Layer Toggles
document.getElementById('loss-toggle').addEventListener('change', (e) => {
    if (e.target.checked) map.addLayer(mockLoss);
    else map.removeLayer(mockLoss);
});

document.getElementById('gain-toggle').addEventListener('change', (e) => {
    if (e.target.checked) map.addLayer(mockGain);
    else map.removeLayer(mockGain);
});
