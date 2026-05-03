import json
import os
import hashlib
import pandas as pd
from azure.cosmos import CosmosClient

COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT")
COSMOS_KEY = os.getenv("COSMOS_KEY")
DATABASE_NAME = os.getenv("COSMOS_DATABASE", "metaml")

if not COSMOS_ENDPOINT or not COSMOS_KEY:
    raise RuntimeError("COSMOS_ENDPOINT and COSMOS_KEY environment variables are required.")

client = CosmosClient(COSMOS_ENDPOINT, credential=COSMOS_KEY)
database = client.get_database_client(DATABASE_NAME)

def stable_id(prefix, payload):
    raw = json.dumps(payload, sort_keys=True, default=str)
    return f"{prefix}-{hashlib.sha256(raw.encode()).hexdigest()[:24]}"

def clean_value(value):
    if pd.isna(value):
        return None
    return value

def clean_record(record):
    return {k: clean_value(v) for k, v in record.items()}

def upsert_taxonomy():
    container = database.get_container_client("bot_taxonomy")

    with open("shared/schemas/bot_taxonomy.json", "r") as f:
        taxonomy = json.load(f)

    count = 0
    for bot_id, metadata in taxonomy.items():
        item = {
            "id": bot_id,
            "entity_type": "bot_taxonomy",
            "bot_id": bot_id,
            **metadata
        }
        container.upsert_item(item)
        count += 1

    print(f"Upserted {count} taxonomy documents.")

def upsert_csv(csv_path, container_name, entity_type, id_prefix):
    if not os.path.exists(csv_path):
        print(f"Skipping missing file: {csv_path}")
        return

    df = pd.read_csv(csv_path)
    container = database.get_container_client(container_name)

    count = 0
    for _, row in df.iterrows():
        payload = clean_record(row.to_dict())
        item = {
            "id": stable_id(id_prefix, payload),
            "entity_type": entity_type,
            **payload
        }
        container.upsert_item(item)
        count += 1

    print(f"Upserted {count} documents into {container_name}.")

def main():
    upsert_taxonomy()

    upsert_csv(
        csv_path="data/logs/bot_fingerprints.csv",
        container_name="bot_fingerprints",
        entity_type="bot_fingerprint",
        id_prefix="fingerprint"
    )

    upsert_csv(
        csv_path="data/logs/orchestrator_decisions.csv",
        container_name="orchestrator_decisions",
        entity_type="orchestrator_decision",
        id_prefix="decision"
    )

    print("Done exporting MetaML data to Azure Cosmos DB.")

if __name__ == "__main__":
    main()
