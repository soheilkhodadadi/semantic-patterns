# Script Deprecation Posture Refresh V1

## Purpose

Record the practical outcome of Queue V23 after the script inventory generator,
the inventory snapshot, and the rendered registry were all refreshed.

## What changed

These six historical data utilities are no longer advertised as current
canonical front-door entrypoints in the generated script registry:
- `semantic_ai_washing.data.clean_compustat`
- `semantic_ai_washing.data.clean_crsp`
- `semantic_ai_washing.data.clean_sec`
- `semantic_ai_washing.data.download_compustat`
- `semantic_ai_washing.data.download_crsp`
- `semantic_ai_washing.data.download_sec`

They now appear as transitional script-deprecation surfaces instead.

## Why this matters

Queue V22 already proved that these utilities were not retire-ready.
Queue V23 adds the missing operational clarity:
- they still exist
- they still have direct references
- but they are no longer framed as current canonical workflow front doors

That is a healthier late-stage posture for the lab:
- active workflows stay visible
- historical utilities remain traceable
- future cleanup work is easier to scope honestly

## What did not happen

- no code was deleted
- no shim was removed
- no quarantine lane was created
- no canonical active workflow authority changed

## Recommended next posture

- treat the six utilities as script-deprecation candidates
- do not promote them into new migration queues
- only consider retire/quarantine work after a later bounded queue updates
  registry and inventory consumers that still rely on them

## Bottom line

Queue V23 did not reduce code volume, but it did reduce ambiguity.

That is the right result for this stage.
