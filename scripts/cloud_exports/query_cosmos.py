import os
from azure.cosmos import CosmosClient

COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT")
COSMOS_KEY = os.getenv("COSMOS_KEY")
DATABASE_NAME = os.getenv("COSMOS_DATABASE", "metaml")

client = CosmosClient(COSMOS_ENDPOINT, credential=COSMOS_KEY)
database = client.get_database_client(DATABASE_NAME)

def query_container(container_name, query):
    container = database.get_container_client(container_name)
    rows = list(container.query_items(
        query=query,
        enable_cross_partition_query=True
    ))

    print(f"\n{container_name}: {len(rows)} result(s)")
    for row in rows[:10]:
        print(row)

def main():
    query_container(
        "bot_taxonomy",
        "SELECT * FROM c"
    )

    query_container(
        "bot_fingerprints",
        "SELECT TOP 5 c.bot_id, c.strategy_type, c.market_regime, c.pnl, c.drawdown FROM c"
    )

    query_container(
        "orchestrator_decisions",
        "SELECT TOP 5 c.timestamp, c.recommended_bot, c.decision, c.reason FROM c"
    )

if __name__ == "__main__":
    main()
