from shared.libs.audit_chain import read_chain, verify_chain

chain = read_chain()

if not chain:
    print("Audit chain is empty.")
    raise SystemExit(0)

print("\nAudit Chain")
print("-" * 100)

for row in chain[-10:]:
    print(f"Index:        {row['index']}")
    print(f"Timestamp:    {row['timestamp']}")
    print(f"Event Type:   {row['event_type']}")
    print(f"Payload:      {row['event_payload']}")
    print(f"Prev Hash:    {row['previous_hash']}")
    print(f"Event Hash:   {row['event_hash']}")
    print("-" * 100)

print("\nVerification:")
print(verify_chain())
