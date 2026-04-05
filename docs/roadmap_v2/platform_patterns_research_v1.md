# Platform Patterns Research V1

## Purpose

This note distills public architecture patterns from established data and ML platform tooling that are relevant to a multi-program disclosure-intelligence lab.

It is intentionally public-safe.
It uses only public documentation and abstracts patterns rather than copying any private system design.

## Sources reviewed

Official documentation used for this note:
- Dagster overview and asset-based orchestration docs: <https://docs.dagster.io/>
- MLflow tracking and model registry docs: <https://mlflow.org/docs/latest/ml/tracking/> and <https://mlflow.org/docs/latest/ml/model-registry>
- Kubeflow profiles and namespaces docs: <https://www.kubeflow.org/docs/components/central-dash/profiles/>
- lakeFS branching and branch protection docs: <https://docs.lakefs.io/latest/quickstart/branch/> and <https://docs.lakefs.io/v1.76/howto/protect-branches/>
- Prefect deployment and work pool docs: <https://docs.prefect.io/v3/concepts/deployments>
- DVC user guide: <https://doc.dvc.org/user-guide>

## Core patterns that transfer well

### 1. Assets and evidence should be first-class objects

Dagster emphasizes asset lineage, observability, asset checks, and data contracts rather than treating pipelines only as opaque jobs.

Transferable implication:
- our lab should treat evidence objects, benchmark tables, model artifacts, and reports as first-class tracked assets
- this is stronger than a script-centric view of the repo

### 2. Runs, experiments, and models need explicit registries

MLflow organizes work around runs, experiments, models, and a central model registry with versions, aliases, tags, lineage, and metadata.

Transferable implication:
- the lab should have explicit registries for runs, experiments, evaluation bundles, and scoring versions
- we should be able to say which scoring artifact is the current `champion`, which is experimental, and which outputs were built from which version

### 3. Multi-project work requires explicit isolation

Kubeflow uses profiles and namespaces to isolate users and resources and to manage contributors and permissions.

Transferable implication:
- the lab should have explicit project workspaces, privacy classes, and contributor boundaries
- even in a monorepo, projects should feel like isolated workspaces with shared core services rather than one large undifferentiated folder tree

### 4. Data and evidence changes need branch-like isolation and protected merge paths

lakeFS emphasizes efficient branching for data, protected branches, and pre-merge hooks to validate changes before they reach important branches.

Transferable implication:
- we should treat authoritative data and artifact lanes like protected branches conceptually
- changes should happen in bounded working areas and then be promoted into canonical lanes only after validation
- this pattern is highly relevant for benchmarks, labels, panel builds, and delivery artifacts

### 5. Orchestration should be deployment-aware, not just script-aware

Prefect emphasizes deployments, work pools, versioned deployment metadata, schedules, event triggers, and infrastructure templates across teams.

Transferable implication:
- the lab should separate pipeline logic from execution profiles
- the same workflow may need to run under different project or environment profiles without editing the code path itself
- this is relevant even if we do not adopt Prefect directly

### 6. Reproducibility should build on Git-like workflows, not replace them

DVC emphasizes human-readable metadata, Git-compatible workflows, experiment management, and data versioning without requiring a full always-on platform.

Transferable implication:
- the lab should preserve a Git-native operating model where possible
- we do not need to jump immediately to heavyweight platform services to get reproducibility, branching, and experiment history

## Patterns we should borrow

The strongest public patterns for us are:
- asset and lineage thinking
- explicit experiment / version / registry thinking
- workspace and access isolation
- branch / promotion / protection rules for data and outputs
- deployment profiles and execution templates
- Git-compatible reproducibility

## Patterns we should not over-copy yet

We should avoid copying heavyweight patterns before they are needed:
- full enterprise microservice decomposition
- complex Kubernetes-first infrastructure
- real-time event streaming for every workflow
- large-scale platform tooling whose complexity exceeds the current team and workload

The correct move is to borrow the boundary logic and governance discipline first.

## Implications for our lab

The lab should eventually have:
- one control plane for project registry, privacy class, run metadata, and acceptance gates
- one shared evidence core for manifests, canonical text units, labels, benchmarks, and evaluation outputs
- project adapters for AI-washing, ERI, AllocationLab, and future programs
- one shared delivery surface for reports, tables, figures, memos, and proof artifacts
- a promotion path for moving work from project-specific experimentation into authoritative shared lanes

## Suggested architectural stance

Near-term stance:
- monorepo lab with explicit boundaries and project adapters

Not-yet stance:
- separate platform repo
- multi-service deployment platform
- large-scale orchestration stack

This is the best tradeoff between ambition and control.

## Bottom line

The strongest lesson from public platform examples is not that we need more infrastructure.
The strongest lesson is that multi-program work becomes manageable when evidence, runs, versions, workspaces, and promotions are explicit.

That is the design pressure the current repo should respond to first.
