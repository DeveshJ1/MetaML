from shared.libs.audit_chain import append_audit_event, verify_chain

event1 = append_audit_event(
    event_type="SERVICE_REGISTERED",
    event_payload={
        "service_id": "market-engine",
        "service_type": "market_infrastructure_node"
    }
)

print("Appended event:")
print(event1)

event2 = append_audit_event(
    event_type="BOT_SWITCH_DECISION",
    event_payload={
        "previous_active_bot": "baseline-bot",
        "recommended_bot": "momentum-bot",
        "decision": "SWITCH",
        "reason": "test audit event"
    }
)

print("\nAppended event:")
print(event2)

print("\nVerification:")
print(verify_chain())
