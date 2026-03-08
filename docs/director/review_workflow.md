# Review Workflow

Director adds a formal review boundary at the end of each iteration and an explicit kickoff boundary at the start of the next one.

Stakeholder alignment is part of the review boundary, not a separate side process. Reviews must report which stakeholder requirements are satisfied, still open, or deferred before the next iteration is authorized.

## Review Scopes
- `IterationReview`: mandatory at the end of every iteration
- `PhaseReview`: optional, but recommended after blocked, deferred, or materially redesigned phases

## Iteration Review Flow
1. Generate the review draft:
   - `python -m semantic_ai_washing.director.cli review --iteration <N>`
2. Inspect review outputs in `director/reviews/`:
   - `iteration_<N>_review.json`
   - `iteration_<N>_review.md`
   - `iteration_<N>_patch_proposal.yaml`
   - `iteration_<N>_branch_plan.md`
   - `iteration_<N>_starter_prompt.md`
   - stakeholder alignment summary, unmet stakeholder requirements, deferred stakeholder requirements, and publication-readiness blockers
3. Approve or defer the review:
   - `python -m semantic_ai_washing.director.cli approve-review --review-file director/reviews/iteration_<N>_review.json --decision approve --accept-patch all`
4. Optionally apply accepted roadmap changes:
   - `python -m semantic_ai_washing.director.cli apply-review-patch --approval-file director/reviews/iteration_<N>_approval.json`

## Approval Rules
- Review approval is manual and explicit.
- Approval authorizes:
  - branch closeout
  - next-iteration kickoff
- Deferral keeps the review evidence but does not authorize the next iteration.
- Approval should confirm that all stakeholder requirements due in the current iteration are either satisfied or intentionally deferred with rationale.

## Patch Application
- Review generation is proposal-only.
- Roadmap mutation happens only through `apply-review-patch`.
- Patch application:
  - updates `director/model/roadmap_model.yaml`
  - regenerates `docs/director/roadmap_master.md`
  - re-ingests roadmap snapshots when the canonical protocol and iteration log are present
  - preserves stakeholder-expectation traceability through explicit accepted or deferred review changes

## Kickoff Flow
1. Create or switch to the iteration integration branch.
2. Run:
   - `python -m semantic_ai_washing.director.cli kickoff --iteration <N>`
3. Director validates:
   - branch naming against policy
   - previous iteration approval
   - merge-base against `main`
   - tracked worktree cleanliness
4. Kickoff writes:
   - `director/reviews/iteration_<N>_kickoff.json`

## Starter Prompt
- Every approved iteration review generates a starter prompt Markdown artifact.
- Default policy is to start a new Codex chat at approved iteration boundaries.
- Same-chat continuation remains allowed if context continuity matters more than separation.
- The starter prompt should be treated as a boundary handoff, not as a replacement for current repo state:
  - if kickoff already passed, continue to the next substantive phase
  - if kickoff has not passed, run kickoff first

## Iteration 2 Parallel Execution Note
- Iteration 2 is intentionally split into parallel tracks:
  - tranche-1 human verification of `labeling_batch_v1`
  - expanded sentence-pool buildout and later tranche preparation
- Reviews should explicitly report whether both tracks are advancing truthfully.
- Assistive prelabels are allowed as operational aids, but review must continue to treat human-verified labels as the only canonical labeling source.
