from shared.libs.service_registry import register_service

AWS_REGISTRY_URL = "https://w3mstcke3t.us-east-1.awsapprunner.com"
GCP_INFERENCE_URL = "https://metaml-inference-api-vhsoiocxlq-uc.a.run.app"
AZURE_DASHBOARD_URL = "https://metaml-dashboard.delightfulmoss-82c77b7a.eastus.azurecontainerapps.io"

services = [
    {
        "service_id": "aws-registry-api",
        "service_type": "decentralized_registry_node",
        "endpoint": AWS_REGISTRY_URL,
        "cloud": "aws",
        "metadata": {
            "paas": "AWS App Runner",
            "health": f"{AWS_REGISTRY_URL}/health"
        }
    },
    {
        "service_id": "gcp-inference-api",
        "service_type": "ml_inference_node",
        "endpoint": GCP_INFERENCE_URL,
        "cloud": "gcp",
        "metadata": {
            "paas": "Cloud Run",
            "health": f"{GCP_INFERENCE_URL}/health"
        }
    },
    {
        "service_id": "azure-dashboard",
        "service_type": "human_in_loop_node",
        "endpoint": AZURE_DASHBOARD_URL,
        "cloud": "azure",
        "metadata": {
            "paas": "Azure Container Apps"
        }
    }
]

for svc in services:
    registered = register_service(**svc)
    print(f"Registered cloud service: {registered['service_id']} -> {registered['endpoint']}")
