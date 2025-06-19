// Stock ticker configuration
const STOCKS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'BRK.B', 'TSLA', 'UNH', 'JNJ',
    'JPM', 'V', 'PG', 'MA', 'HD', 'MRK', 'ABBV', 'CVX', 'PFE', 'KO',
    'BAC', 'PEP', 'COST', 'TMO', 'DHR', 'CSCO', 'VZ', 'ADBE', 'CRM', 'MCD',
    'ACN', 'LLY', 'WMT', 'NEE', 'PM', 'DIS', 'NFLX', 'INTC', 'QCOM', 'TXN',
    'UNP', 'LIN', 'AVGO', 'HON', 'RTX', 'UPS', 'BMY', 'AMAT', 'SBUX', 'AMD'
];

const SYMBOL_TO_DOMAIN = {
    'AAPL': 'apple.com',
    'MSFT': 'microsoft.com',
    'GOOGL': 'google.com',
    'AMZN': 'amazon.com',
    'NVDA': 'nvidia.com',
    'META': 'meta.com',
    'BRK.B': 'berkshirehathaway.com',
    'TSLA': 'tesla.com',
    'UNH': 'unitedhealthgroup.com',
    'JNJ': 'jnj.com',
    'JPM': 'jpmorganchase.com',
    'V': 'visa.com',
    'PG': 'pg.com',
    'MA': 'mastercard.com',
    'HD': 'homedepot.com',
    'MRK': 'merck.com',
    'ABBV': 'abbvie.com',
    'CVX': 'chevron.com',
    'PFE': 'pfizer.com',
    'KO': 'coca-cola.com',
    'BAC': 'bankofamerica.com',
    'PEP': 'pepsico.com',
    'COST': 'costco.com',
    'TMO': 'thermofisher.com',
    'DHR': 'danaher.com',
    'CSCO': 'cisco.com',
    'VZ': 'verizon.com',
    'ADBE': 'adobe.com',
    'CRM': 'salesforce.com',
    'MCD': 'mcdonalds.com',
    'ACN': 'accenture.com',
    'LLY': 'lilly.com',
    'WMT': 'walmart.com',
    'NEE': 'nexteraenergy.com',
    'PM': 'pmi.com',
    'DIS': 'disney.com',
    'NFLX': 'netflix.com',
    'INTC': 'intel.com',
    'QCOM': 'qualcomm.com',
    'TXN': 'ti.com',
    'UNP': 'up.com',
    'LIN': 'linde.com',
    'AVGO': 'broadcom.com',
    'HON': 'honeywell.com',
    'RTX': 'rtx.com',
    'UPS': 'ups.com',
    'BMY': 'bms.com',
    'AMAT': 'amat.com',
    'SBUX': 'starbucks.com',
    'AMD': 'amd.com'
};

// Function to fetch stock data
async function fetchStockData(symbol) {
    try {
        const response = await fetch(`/api/stock/${symbol}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error(`Error fetching data for ${symbol}:`, error);
        return null;
    }
}

// Function to create ticker item DOM node
function createTickerItemNode(symbol, data) {
    const change = data.change;
    const changeClass = change >= 0 ? 'positive' : 'negative';
    const changeSymbol = change >= 0 ? '▲' : '▼';
    const domain = SYMBOL_TO_DOMAIN[symbol] || '';
    const logoUrl = domain ? `https://logo.clearbit.com/${domain}` : '';

    const tickerItem = document.createElement('div');
    tickerItem.className = 'ticker-item';
    tickerItem.innerHTML = `
        ${logoUrl ? `<img class="ticker-logo" src="${logoUrl}" alt="${symbol} logo" />` : ''}
        <span class="symbol">${symbol}</span>
        <span class="price">$${data.price.toFixed(2)}</span>
        <span class="change ${changeClass}">${changeSymbol} ${Math.abs(change).toFixed(2)}%</span>
    `;
    return tickerItem;
}

// Function to update ticker prices in-place
async function updateTickerPrices() {
    const tickerContainer = document.getElementById('stock-ticker');
    if (!tickerContainer) return;
    const items = tickerContainer.querySelectorAll('.ticker-item');
    // Only update the first half (original set)
    const half = items.length / 2;
    const stockDataPromises = STOCKS.map(symbol => fetchStockData(symbol));
    const stockDataResults = await Promise.allSettled(stockDataPromises);
    stockDataResults.forEach((result, index) => {
        if (result.status === 'fulfilled' && result.value) {
            const item = items[index];
            if (item) {
                const data = result.value;
                const change = data.change;
                const changeClass = change >= 0 ? 'positive' : 'negative';
                const changeSymbol = change >= 0 ? '▲' : '▼';
                item.querySelector('.price').textContent = `$${data.price.toFixed(2)}`;
                const changeSpan = item.querySelector('.change');
                changeSpan.className = `change ${changeClass}`;
                changeSpan.textContent = `${changeSymbol} ${Math.abs(change).toFixed(2)}%`;
                // Also update the duplicate item for seamless loop
                const dupItem = items[index + half];
                if (dupItem) {
                    dupItem.querySelector('.price').textContent = `$${data.price.toFixed(2)}`;
                    const dupChangeSpan = dupItem.querySelector('.change');
                    dupChangeSpan.className = `change ${changeClass}`;
                    dupChangeSpan.textContent = `${changeSymbol} ${Math.abs(change).toFixed(2)}%`;
                }
            }
        }
    });
}

// Function to initialize ticker DOM and animation
async function initializeTicker() {
    const tickerContainer = document.getElementById('stock-ticker');
    if (!tickerContainer) return;
    // Remove CSS animation
    tickerContainer.style.animation = 'none';
    tickerContainer.innerHTML = '';
    // Fetch initial data
    const stockDataPromises = STOCKS.map(symbol => fetchStockData(symbol));
    const stockDataResults = await Promise.allSettled(stockDataPromises);
    // Create ticker items
    const tickerItems = [];
    stockDataResults.forEach((result, index) => {
        if (result.status === 'fulfilled' && result.value) {
            const tickerItem = createTickerItemNode(STOCKS[index], result.value);
            tickerItems.push(tickerItem);
            tickerContainer.appendChild(tickerItem);
        }
    });
    // Duplicate for seamless loop
    tickerItems.forEach(item => {
        const clone = item.cloneNode(true);
        tickerContainer.appendChild(clone);
    });
    // Set width for smooth scroll
    const tickerWidth = Array.from(tickerContainer.children).reduce((acc, el) => acc + el.offsetWidth, 0);
    tickerContainer.style.width = tickerWidth + 'px';
    // Start JS animation
    startTickerAnimation(tickerContainer, tickerWidth / 2);
}

// JS-based seamless ticker animation
function startTickerAnimation(container, loopWidth) {
    let pos = 0;
    function step() {
        pos -= 1; // px per frame
        if (Math.abs(pos) >= loopWidth) {
            pos = 0;
        }
        container.style.transform = `translateX(${pos}px)`;
        requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
}

// Initialize ticker and set up price updates
document.addEventListener('DOMContentLoaded', () => {
    initializeTicker();
    setInterval(updateTickerPrices, 30000);
}); 