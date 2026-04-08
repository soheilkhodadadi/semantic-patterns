# AI-Washing Long-Run Job Resilience Lessons V1

## Purpose

This note records a repeated operational lesson from the Track A refresh work:

Long-running extraction, classification, and patent jobs should not leave us in
the dark while they run.

## Observed problem

Several heavy jobs in this project have had one or more of these weaknesses:
- no reliable percentage progress while running
- no partial result files until the very end
- no easy way to inspect how much has already completed
- no clean resume point after interruption
- no distinction between:
  - work completed
  - work currently running
  - work still pending

This has happened enough times that it should now be treated as an engineering
lesson, not a one-off annoyance.

## Recommended default design for future long jobs

Every long-running pipeline job should, by default, support:

1. `progress file`
   - current status
   - total items
   - completed items
   - current batch or shard
   - last updated timestamp

2. `checkpointed outputs`
   - write partial batch outputs as the run progresses
   - avoid end-only output when possible

3. `resumability`
   - skip completed batches
   - restart from last clean checkpoint

4. `inspectable work units`
   - quarter
   - year
   - batch
   - chunk
   - whatever the natural unit is

5. `final reconciliation step`
   - combine batch outputs only after partial outputs are already safely written

## Practical implementation pattern

The preferred pattern for this repo is:
- split the run into natural chunks
- persist a progress JSON
- write per-chunk outputs
- reconcile into the final artifact at the end

That pattern is already much better than:
- one monolithic run
- one final output file
- no intermediate state

## Specific future targets

This should be the default posture for:
- patent extraction jobs
- sentence extraction jobs
- restartable classification jobs
- large WRDS refresh pulls
- any later event-study preparation runs

## Bottom line

For this repo, long-running data jobs should be designed as:
- observable
- checkpointed
- resumable

That should be treated as a standard engineering expectation going forward, not
as optional polish.
