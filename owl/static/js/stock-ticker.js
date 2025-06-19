/**
 * Author(s):
 *    Antonio Rosado
 *    Kashan Khan
 *    Imad Khan
 *    Alexander Schifferle
 *    Mike Kheang
 * Assignment:
 *    Senior Project (Summer 2025) – “stock-ticker.js”
 * Last Update:
 *    Revised June 19, 2025
 * Purpose:
 *    Manage the stock ticker on the front-end: define which symbols to track,
 *    fetch their latest data from the back-end API, and render a continuously
 *    scrolling ticker loop.
 */

/* ---------- Stock Ticker Configuration ---------- */
const STOCKS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'BRK.B', 'TSLA', 'UNH', 'JNJ',
    'JPM', 'V', 'PG', 'MA', 'HD', 'MRK', 'ABBV', 'CVX', 'PFE', 'KO',
    'BAC', 'PEP', 'COST', 'TMO', 'DHR', 'CSCO', 'VZ', 'ADBE', 'CRM', 'MCD',
    'ACN', 'LLY', 'WMT', 'NEE', 'PM', 'DIS', 'NFLX', 'INTC', 'QCOM', 'TXN',
    'UNP', 'LIN', 'AVGO', 'HON', 'RTX', 'UPS', 'BMY', 'AMAT', 'SBUX', 'AMD'
]; 
// List of ticker symbols to display in the scrolling ticker

/**
 * Fetches the latest price and change percentage for a given symbol.
 * @param {string} symbol - Stock ticker symbol (e.g., 'AAPL').
 * @returns {Promise<Object|null>} - An object with `price` and `change` or null on error.
 */
async function fetchStockData(symbol) {
    try {
        const response = await fetch(`/api/stock/${symbol}`);
        if (!response.ok) {
            // If the API returns an error status, throw to be caught below
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error(`Error fetching data for ${symbol}:`, error);
        return null;
    }
}

/**
 * Creates a DOM element representing a single ticker item.
 * @param {string} symbol - Stock symbol.
 * @param {Object} data - Data object containing `price` (Number) and `change` (Number).
 * @returns {HTMLElement} - A <div> element styled as a ticker item.
 */
function createTickerItem(symbol, data) {
    const change = data.change;
    const changeClass = change >= 0 ? 'positive' : 'negative';
    const changeSymbol = change >= 0 ? '▲' : '▼';
    
    const tickerItem = document.createElement('div');
    tickerItem.className = 'ticker-item';
    tickerItem.innerHTML = `
        <span class="symbol">${symbol}</span>
        <span class="price">$${data.price.toFixed(2)}</span>
        <span class="change ${changeClass}">
            ${changeSymbol} ${Math.abs(change).toFixed(2)}%
        </span>
    `;
    return tickerItem;
}

/**
 * Fetches data for all configured stocks, renders them into the ticker container,
 * and duplicates the items to enable a seamless scrolling loop.
 */
async function updateTicker() {
    const tickerContainer = document.getElementById('stock-ticker');
    if (!tickerContainer) return;  // Bail out if ticker container is not present

    // Clear any existing ticker items before re-rendering
    tickerContainer.innerHTML = '';

    // Kick off all fetches in parallel
    const stockDataPromises = STOCKS.map(symbol => fetchStockData(symbol));
    const stockDataResults = await Promise.allSettled(stockDataPromises);

    // For each fulfilled fetch, append a ticker item
    stockDataResults.forEach((result, index) => {
        if (result.status === 'fulfilled' && result.value) {
            const tickerItem = createTickerItem(STOCKS[index], result.value);
            tickerContainer.appendChild(tickerItem);
        }
    });

    // Duplicate the inner HTML so that items loop seamlessly
    const itemsHTML = tickerContainer.innerHTML;
    tickerContainer.innerHTML = itemsHTML + itemsHTML;
}

// Initialize the ticker on DOM ready and set it to refresh every 30 seconds
document.addEventListener('DOMContentLoaded', () => {
    updateTicker();
    setInterval(updateTicker, 30_000);  // 30,000 ms = 30 seconds
});
