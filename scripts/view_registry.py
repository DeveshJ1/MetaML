from shared.libs.service_registry import list_services

registry = list_services()

if not registry:
    print("Registry is empty.")
    raise SystemExit(0)

print("\nRegistered MetaML Services")
print("-" * 100)

for service_id, svc in registry.items():
    print(f"ID:        {service_id}")
    print(f"Type:      {svc['service_type']}")
    print(f"Endpoint:  {svc['endpoint']}")
    print(f"Cloud:     {svc['cloud']}")
    print(f"Status:    {svc['status']}")
    print(f"Heartbeat: {svc['last_heartbeat']}")
    print(f"Metadata:  {svc['metadata']}")
    print("-" * 100)
