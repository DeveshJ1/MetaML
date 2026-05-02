import csv
import hashlib
import json
import os
from datetime import datetime, timezone

AUDIT_PATH = "data/audit/audit_chain.csv"

FIELDS = [
    "index",
    "timestamp",
    "event_type",
    "event_payload",
    "previous_hash",
    "event_hash"
]

def utc_now():
    return datetime.now(timezone.utc).isoformat()

def ensure_audit_file():
    os.makedirs(os.path.dirname(AUDIT_PATH), exist_ok=True)

    if not os.path.exists(AUDIT_PATH):
        with open(AUDIT_PATH, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()

def canonical_json(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))

def compute_hash(index, timestamp, event_type, event_payload, previous_hash):
    raw = canonical_json({
        "index": index,
        "timestamp": timestamp,
        "event_type": event_type,
        "event_payload": event_payload,
        "previous_hash": previous_hash
    })

    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def read_chain():
    ensure_audit_file()

    with open(AUDIT_PATH, "r", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)

def append_audit_event(event_type, event_payload):
    ensure_audit_file()

    chain = read_chain()

    if chain:
        previous_hash = chain[-1]["event_hash"]
        index = int(chain[-1]["index"]) + 1
    else:
        previous_hash = "GENESIS"
        index = 0

    timestamp = utc_now()
    payload_str = canonical_json(event_payload)

    event_hash = compute_hash(
        index=index,
        timestamp=timestamp,
        event_type=event_type,
        event_payload=event_payload,
        previous_hash=previous_hash
    )

    row = {
        "index": index,
        "timestamp": timestamp,
        "event_type": event_type,
        "event_payload": payload_str,
        "previous_hash": previous_hash,
        "event_hash": event_hash
    }

    with open(AUDIT_PATH, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writerow(row)

    return row

def verify_chain():
    chain = read_chain()

    if not chain:
        return {
            "valid": True,
            "message": "Audit chain is empty",
            "events_checked": 0
        }

    previous_hash = "GENESIS"

    for i, row in enumerate(chain):
        index = int(row["index"])
        timestamp = row["timestamp"]
        event_type = row["event_type"]
        event_payload = json.loads(row["event_payload"])
        stored_previous_hash = row["previous_hash"]
        stored_event_hash = row["event_hash"]

        if index != i:
            return {
                "valid": False,
                "message": f"Invalid index at row {i}",
                "events_checked": i
            }

        if stored_previous_hash != previous_hash:
            return {
                "valid": False,
                "message": f"Invalid previous_hash at row {i}",
                "events_checked": i
            }

        recomputed_hash = compute_hash(
            index=index,
            timestamp=timestamp,
            event_type=event_type,
            event_payload=event_payload,
            previous_hash=stored_previous_hash
        )

        if recomputed_hash != stored_event_hash:
            return {
                "valid": False,
                "message": f"Invalid event_hash at row {i}",
                "events_checked": i
            }

        previous_hash = stored_event_hash

    return {
        "valid": True,
        "message": "Audit chain verified successfully",
        "events_checked": len(chain)
    }
