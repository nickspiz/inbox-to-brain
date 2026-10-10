---
type: insight
project: billing-v2
tags: [insight]
---

# Invoice rounding

We round each line item before summing, and the tax authority wants the sum rounded once at the end. The totals differ by a cent on about one invoice in fifty, which is enough for an audit to flag. The fix is to keep full precision until the final total.
