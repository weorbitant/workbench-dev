#!/usr/bin/env python3
"""
Analyze DLQ messages exported from a message broker.

Usage:
    python3 analyze_messages.py <messages_file.json>

The input file should be a JSON array of messages, as returned by the
RabbitMQ Management API's /api/queues/{vhost}/{queue}/get endpoint.

Output:
    - Total message count
    - Unique routing keys
    - Death reason distribution
    - Payload pattern analysis
    - Time range
    - Entity ID extraction (if present)
"""

import json
import sys
from collections import Counter
from datetime import datetime


def extract_entity_ids(payload_str):
    """Try to extract common entity ID patterns from the message payload."""
    ids = set()
    try:
        payload = json.loads(payload_str)
        # Common ID field names
        for key in ("id", "entityId", "entity_id", "userId", "user_id",
                     "orderId", "order_id", "documentId", "document_id",
                     "recordId", "record_id", "uuid"):
            if key in payload:
                ids.add(f"{key}={payload[key]}")
            # Check nested objects
            if isinstance(payload, dict):
                for nested_key, nested_val in payload.items():
                    if isinstance(nested_val, dict) and key in nested_val:
                        ids.add(f"{nested_key}.{key}={nested_val[key]}")
    except (json.JSONDecodeError, TypeError):
        pass
    return ids


def analyze(messages):
    """Analyze a list of messages and print a summary report."""
    total = len(messages)
    routing_keys = Counter()
    death_reasons = Counter()
    death_queues = Counter()
    entity_ids = Counter()
    timestamps = []
    payload_errors = []

    for msg in messages:
        # Routing key
        rk = msg.get("routing_key", "unknown")
        routing_keys[rk] += 1

        # Death headers
        headers = msg.get("properties", {}).get("headers", {})
        reason = headers.get("x-first-death-reason", "unknown")
        death_reasons[reason] += 1

        queue = headers.get("x-first-death-queue", "unknown")
        death_queues[queue] += 1

        # Timestamps
        ts = msg.get("properties", {}).get("timestamp")
        if ts:
            try:
                timestamps.append(datetime.fromtimestamp(ts))
            except (ValueError, OSError):
                pass

        # Payload analysis
        payload = msg.get("payload", "")
        try:
            json.loads(payload)
        except (json.JSONDecodeError, TypeError):
            payload_errors.append(rk)

        # Entity IDs
        ids = extract_entity_ids(payload)
        for eid in ids:
            entity_ids[eid] += 1

    # Report
    print(f"\n{'='*60}")
    print(f"DLQ Message Analysis Report")
    print(f"{'='*60}")
    print(f"\nTotal messages: {total}")

    if timestamps:
        timestamps.sort()
        print(f"Time range: {timestamps[0]} — {timestamps[-1]}")
        duration = timestamps[-1] - timestamps[0]
        print(f"Duration: {duration}")

    print(f"\n--- Death Reasons ---")
    for reason, count in death_reasons.most_common():
        pct = count / total * 100
        print(f"  {reason}: {count} ({pct:.1f}%)")

    print(f"\n--- Source Queues ---")
    for queue, count in death_queues.most_common():
        print(f"  {queue}: {count}")

    print(f"\n--- Routing Keys ---")
    for rk, count in routing_keys.most_common(10):
        print(f"  {rk}: {count}")

    if payload_errors:
        print(f"\n--- Malformed Payloads ---")
        print(f"  {len(payload_errors)} messages with invalid JSON")
        malformed_rks = Counter(payload_errors)
        for rk, count in malformed_rks.most_common(5):
            print(f"    routing_key={rk}: {count}")

    if entity_ids:
        print(f"\n--- Entity IDs (top 10) ---")
        for eid, count in entity_ids.most_common(10):
            print(f"  {eid}: {count} messages")

    # Classification
    print(f"\n--- Suggested Classification ---")
    if len(payload_errors) > total * 0.5:
        print("  -> MALFORMED PAYLOAD: Majority of messages have invalid JSON")
        print("     Producer serialization bug suspected")
    elif len(death_reasons) == 1 and "rejected" in death_reasons:
        if len(entity_ids) <= 3 and entity_ids:
            print("  -> ENTITY-SPECIFIC: Failures concentrated on few entities")
            print("     Check if entities exist and are in valid state")
        else:
            print("  -> CONSUMER REJECTION: All messages rejected by consumer")
            print("     Check consumer logs for error details")
    elif "expired" in death_reasons and death_reasons["expired"] > total * 0.5:
        print("  -> TTL EXPIRY: Messages expired before consumption")
        print("     Consumer may be down or not subscribed")
    else:
        print("  -> MIXED FAILURES: Multiple failure modes detected")
        print("     Investigate each category separately")

    print(f"\n{'='*60}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 analyze_messages.py <messages_file.json>")
        sys.exit(1)

    filepath = sys.argv[1]
    try:
        with open(filepath) as f:
            messages = json.load(f)
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Invalid JSON in file: {filepath}")
        sys.exit(1)

    if not isinstance(messages, list):
        print("Expected a JSON array of messages")
        sys.exit(1)

    analyze(messages)


if __name__ == "__main__":
    main()
