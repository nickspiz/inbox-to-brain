---
type: insight
project: example-app
date: 2026-10-02
tags: [insight, project/example-app]
---

# Simulator clock does not follow the Mac clock

## What happened
A token-expiry test passed on the Mac and failed in the simulator. The simulator had kept the time from when it was last booted, about two hours behind.

## Why it matters
Anything time-based looks like a bug in the code when it is only the device clock.

## Pattern to reuse
Check the device clock first when a time-based test behaves differently on the device.
