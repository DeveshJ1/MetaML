#!/bin/bash

set -e

echo "=== MetaML Cloud Data Export ==="

echo ""
echo "1) Uploading telemetry/logs to AWS S3..."
AWS_REGION=${AWS_REGION:-us-east-1}
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

S3_BUCKET=${S3_BUCKET:-metaml-telemetry-$AWS_ACCOUNT_ID}
ATHENA_RESULTS_BUCKET=${ATHENA_RESULTS_BUCKET:-metaml-athena-results-$AWS_ACCOUNT_ID}

aws s3 mb s3://$S3_BUCKET --region $AWS_REGION 2>/dev/null || true
aws s3 mb s3://$ATHENA_RESULTS_BUCKET --region $AWS_REGION 2>/dev/null || true

aws s3 cp data/logs/trades.csv s3://$S3_BUCKET/trades/trades.csv
aws s3 cp data/logs/bot_fingerprints.csv s3://$S3_BUCKET/fingerprints/bot_fingerprints.csv
aws s3 cp data/logs/orchestrator_decisions.csv s3://$S3_BUCKET/decisions/orchestrator_decisions.csv

echo "AWS S3 upload complete."
echo "Telemetry bucket: s3://$S3_BUCKET"

echo ""
echo "2) Exporting logs to GCP BigQuery..."
GCP_PROJECT_ID=${GCP_PROJECT_ID:-cchw2-487819}
GCP_PROJECT_ID=$GCP_PROJECT_ID PYTHONPATH=. python scripts/cloud_exports/export_to_bigquery.py

echo ""
echo "3) Exporting metadata/fingerprints/decisions to Azure Cosmos DB..."
if [ -z "$COSMOS_ENDPOINT" ] || [ -z "$COSMOS_KEY" ]; then
  echo "ERROR: COSMOS_ENDPOINT and COSMOS_KEY must be set."
  echo "Example:"
  echo "COSMOS_ENDPOINT=<endpoint> COSMOS_KEY=<key> ./scripts/export_all_cloud_data.sh"
  exit 1
fi

COSMOS_ENDPOINT=$COSMOS_ENDPOINT COSMOS_KEY=$COSMOS_KEY PYTHONPATH=. python scripts/cloud_exports/export_to_cosmos.py

echo ""
echo "All cloud data exports completed successfully."
