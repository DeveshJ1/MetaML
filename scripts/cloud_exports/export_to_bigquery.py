import os
from google.cloud import bigquery

PROJECT_ID = os.getenv("GCP_PROJECT_ID", "cchw2-487819")
DATASET_ID = os.getenv("BQ_DATASET", "metaml_analytics")

EXPORTS = [
    {
        "csv_path": "data/logs/bot_fingerprints.csv",
        "table_id": "bot_fingerprints"
    },
    {
        "csv_path": "data/logs/orchestrator_decisions.csv",
        "table_id": "orchestrator_decisions"
    },
    {
        "csv_path": "data/logs/trades.csv",
        "table_id": "trades"
    }
]

def load_csv(client, csv_path, table_name):
    if not os.path.exists(csv_path):
        print(f"Skipping missing file: {csv_path}")
        return

    full_table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=True,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
    )

    with open(csv_path, "rb") as source_file:
        job = client.load_table_from_file(
            source_file,
            full_table_id,
            job_config=job_config
        )

    job.result()

    table = client.get_table(full_table_id)
    print(f"Loaded {table.num_rows} rows into {full_table_id}")

def main():
    client = bigquery.Client(project=PROJECT_ID)

    for export in EXPORTS:
        load_csv(client, export["csv_path"], export["table_id"])

    print("Done exporting MetaML data to BigQuery.")

if __name__ == "__main__":
    main()
