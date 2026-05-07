from alphavantage.client import AlphaVantageClient

client = AlphaVantageClient(verbose=False)

spot = client.get_gold_silver_spot("GOLD")
print(spot["price"], spot["timestamp"])

history = client.get_gold_silver_history("GOLD", "daily")
print(history.head())
print(history.columns.tolist())