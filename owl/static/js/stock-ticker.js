// Stock ticker configuration
const STOCKS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'BRK.B', 'TSLA', 'UNH', 'JNJ',
    'JPM', 'V', 'PG', 'MA', 'HD', 'MRK', 'ABBV', 'CVX', 'PFE', 'KO',
    'BAC', 'PEP', 'COST', 'TMO', 'DHR', 'CSCO', 'VZ', 'ADBE', 'CRM', 'MCD',
    'ACN', 'LLY', 'WMT', 'NEE', 'PM', 'DIS', 'NFLX', 'INTC', 'QCOM', 'TXN',
    'UNP', 'LIN', 'AVGO', 'HON', 'RTX', 'UPS', 'BMY', 'AMAT', 'SBUX', 'AMD'
];

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

// Function to create ticker item
function createTickerItem(symbol, data) {
    const change = data.change;
    const changeClass = change >= 0 ? 'positive' : 'negative';
    const changeSymbol = change >= 0 ? '▲' : '▼';
    
    const tickerItem = document.createElement('div');
    tickerItem.className = 'ticker-item';
    tickerItem.innerHTML = `
        <span class="symbol">${symbol}</span>
        <span class="price">$${data.price.toFixed(2)}</span>
        <span class="change ${changeClass}">${changeSymbol} ${Math.abs(change).toFixed(2)}%</span>
    `;
    return tickerItem;
}

// Function to update ticker
async function updateTicker() {
    const tickerContainer = document.getElementById('stock-ticker');
    if (!tickerContainer) return;

    // Clear existing content
    tickerContainer.innerHTML = '';

    // Fetch data for all stocks in parallel
    const stockDataPromises = STOCKS.map(symbol => fetchStockData(symbol));
    const stockDataResults = await Promise.allSettled(stockDataPromises);

    // Process results and create ticker items
    stockDataResults.forEach((result, index) => {
        if (result.status === 'fulfilled' && result.value) {
            const tickerItem = createTickerItem(STOCKS[index], result.value);
            tickerContainer.appendChild(tickerItem);
        }
    });

    // Clone the ticker items to create a seamless loop
    const items = tickerContainer.innerHTML;
    tickerContainer.innerHTML = items + items;
}

// Initialize ticker
document.addEventListener('DOMContentLoaded', () => {
    updateTicker();
    // Update every 30 seconds
    setInterval(updateTicker, 30000);
}); 