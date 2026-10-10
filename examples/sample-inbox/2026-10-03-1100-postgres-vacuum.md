---
type: knowledge
tags: [knowledge, databases]
---

# Autovacuum falls behind on the events table

The events table takes about two million inserts a day. With default autovacuum settings the table bloated to three times its real size within a month. Lowering autovacuum_vacuum_scale_factor to 0.02 for that table alone fixed it, and other tables do not need the change. Check pg_stat_user_tables for n_dead_tup before assuming an index problem.
