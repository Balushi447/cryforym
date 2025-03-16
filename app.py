from flask import Flask, jsonify, request
from flask_cors import CORS  # Import CORS
import requests
import pandas as pd
import numpy as np

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# CoinGecko API endpoint
COINGECKO_URL = "https://api.coingecko.com/api/v3"

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

if __name__ == '__main__':
    app.run(debug=True)
