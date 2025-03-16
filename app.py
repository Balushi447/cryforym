from flask import Flask, jsonify, request
from flask_cors import CORS  # Import CORS
import requests
import pandas as pd

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# CoinGecko API endpoint
COINGECKO_URL = "https://api.coingecko.com/api/v3"

# CryptoPanic API endpoint and key
CRYPTOPANIC_URL = "https://cryptopanic.com/api/v1/posts/"
CRYPTOPANIC_API_KEY = "YOUR_CRYPTOPANIC_API_KEY"  # Replace with your API key

def get_historical_data(coin_id, days=30):
    """Fetch historical price data for a cryptocurrency."""
    url = f"{COINGECKO_URL}/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": days
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def calculate_rsi(prices, period=14):
    """Calculate Relative Strength Index (RSI)."""
    delta = pd.Series(prices).diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.dropna().tolist()

@app.route('/api/data', methods=['GET'])
def get_data():
    coin_id = request.args.get('coin', 'dogecoin')  # Default to Dogecoin
    days = int(request.args.get('days', 30))        # Default to 30 days

    # Fetch historical data
    data = get_historical_data(coin_id, days)
    if not data:
        return jsonify({"error": "Failed to fetch data"}), 500

    prices = [x[1] for x in data['prices']]
    timestamps = [x[0] for x in data['prices']]

    # Calculate RSI
    rsi = calculate_rsi(prices)

    # Generate recommendation
    latest_rsi = rsi[-1]
    if latest_rsi < 30:
        recommendation = "Buy"
    elif latest_rsi > 70:
        recommendation = "Sell"
    else:
        recommendation = "Hold"

    return jsonify({
        "prices": prices,
        "timestamps": timestamps,
        "rsi": rsi,
        "recommendation": recommendation
    })

# New function for future insights
def calculate_future_insights(prices, rsi):
    """Calculate future investment insights based on historical data."""
    insights = ""
    last_price = prices[-1]
    last_rsi = rsi[-1]

    # RSI-based insights
    if last_rsi < 30:
        insights += "The RSI indicates that the asset is oversold. This could be a good opportunity to buy for potential future gains. "
    elif last_rsi > 70:
        insights += "The RSI indicates that the asset is overbought. Consider taking profits or waiting for a pullback before investing. "
    else:
        insights += "The RSI is in a neutral zone. Monitor the market for potential entry or exit points. "

    # Price trend analysis
    price_change = ((prices[-1] - prices[0]) / prices[0]) * 100
    if price_change > 0:
        insights += f"The price has increased by {price_change:.2f}% over the selected period."
    else:
        insights += f"The price has decreased by {abs(price_change):.2f}% over the selected period."

    return insights

# New endpoint for future insights
@app.route('/api/future-insights', methods=['GET'])
def get_future_insights():
    coin_id = request.args.get('coin', 'dogecoin')  # Default to Dogecoin
    days = int(request.args.get('days', 30))        # Default to 30 days

    # Fetch historical data
    data = get_historical_data(coin_id, days)
    if not data:
        return jsonify({"error": "Failed to fetch data"}), 500

    prices = [x[1] for x in data['prices']]

    # Calculate RSI
    rsi = calculate_rsi(prices)

    # Calculate future insights
    insights = calculate_future_insights(prices, rsi)

    return jsonify({
        "insights": insights
    })

# New function to fetch cryptocurrency news
def get_crypto_news(coin_id):
    """Fetch cryptocurrency news from CryptoPanic."""
    params = {
        "auth_token": CRYPTOPANIC_API_KEY,
        "currencies": coin_id.upper(),  # CryptoPanic uses uppercase symbols (e.g., DOGE, XRP)
        "public": "true"
    }
    response = requests.get(CRYPTOPANIC_URL, params=params)
    if response.status_code == 200:
        return response.json().get('results', [])
    else:
        return None

# New endpoint for cryptocurrency news
@app.route('/api/news', methods=['GET'])
def get_news():
    coin_id = request.args.get('coin', 'DOGE')  # Default to Dogecoin
    news = get_crypto_news(coin_id)
    if not news:
        return jsonify({"error": "Failed to fetch news"}), 500

    # Format news data
    formatted_news = []
    for item in news:
        formatted_news.append({
            "title": item.get('title'),
            "url": item.get('url'),
            "published_at": item.get('published_at')
        })

    return jsonify({
        "news": formatted_news
    })

if __name__ == '__main__':
    app.run(debug=True)
