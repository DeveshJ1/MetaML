import requests

URL = "http://localhost:8000/recommend"

payload = {
    "candidates": [
        {
            "bot_id": "baseline-bot",
            "strategy_type": "baseline_random",
            "risk_profile": "low",
            "market_regime": "VOLATILE",
            "trade_count": 3,
            "buy_count": 2,
            "sell_count": 1,
            "net_position": 2,
            "pnl": -0.5,
            "drawdown": 1.2,
            "fill_rate": 1.0,
            "avg_trade_size": 3,
            "avg_execution_price": 100.2,
            "price_volatility": 0.8
        },
        {
            "bot_id": "momentum-bot",
            "strategy_type": "momentum",
            "risk_profile": "medium",
            "market_regime": "TREND_UP",
            "trade_count": 5,
            "buy_count": 5,
            "sell_count": 0,
            "net_position": 15,
            "pnl": 2.5,
            "drawdown": 0.2,
            "fill_rate": 1.0,
            "avg_trade_size": 3,
            "avg_execution_price": 100.5,
            "price_volatility": 0.25
        },
        {
            "bot_id": "mean-reversion-bot",
            "strategy_type": "mean_reversion",
            "risk_profile": "medium",
            "market_regime": "MEAN_REVERT",
            "trade_count": 4,
            "buy_count": 2,
            "sell_count": 2,
            "net_position": 0,
            "pnl": 1.2,
            "drawdown": 0.3,
            "fill_rate": 1.0,
            "avg_trade_size": 3,
            "avg_execution_price": 100.0,
            "price_volatility": 0.15
        }
    ]
}

resp = requests.post(URL, json=payload)
print("Status:", resp.status_code)
print(resp.json())
