# Fresh Authority Comparison V5

## Scope

Choose the next downstream `director` authority from the active queue:

- `semantic_director.config`
- `semantic_director.readiness`

## Result

Chosen authority:

- `semantic_director.config`

## Why `config` Won

- smaller and safer than `readiness`
- directly serves the CLI and review surfaces
- improves package honesty by making the configuration/package boundary explicit
- is a cleaner precursor to `readiness`, which still depends on package and root
  control-plane state together

## Why `readiness` Waits One Round

- it is higher leverage, but also more coupled
- it depends on `TaskGraph`, `sensors`, and the state snapshot flow
- it is better taken after `config` is already canonical

## Decision

Take `semantic_director.config` now, then proceed directly to
`semantic_director.readiness` if the `config` round passes cleanly.
