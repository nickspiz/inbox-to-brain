---
type: decision
project: example-app
date: 2026-10-01
tags: [decision, project/example-app]
---

# Retry failed payment webhooks with backoff

## Context
The payment provider sends each webhook once. When our worker was restarting, events were lost and orders stayed unpaid until someone noticed.

## Decision
The webhook handler now stores every event first, then processes it from a queue. Failures retry after 1, 5 and 30 minutes, then go to a dead-letter table we check each morning.

## Consequences
No more lost events. We now need to watch the dead-letter table, and handlers have to be safe to run twice.
