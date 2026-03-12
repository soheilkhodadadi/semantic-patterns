# Tranche 1 Calibration Slice v2.3

## Summary

- This was a prompt-only calibration rerun on the fixed rebuilt `slice40` text.
- No extraction or section-tagging changes were made in this pass.
- Overall agreement vs saved `v2.1` manual labels: `35/40`.
- `Actionable/Speculative` subset agreement: `8/12`.
- Result: the prompt-only pass did **not** improve the `Actionable/Speculative` boundary and does not meet the success gate for full-tranche regeneration.

## Known Mismatch Patterns

- `item_1_business`: manual `Actionable` vs assistive `Irrelevant` — Our Products and Suppliers We offer a comprehensive catalog of more than 200,000 technology products as measured by active SKU's from more than 2,500 original equipment manufacturers OEM , suppliers of traditional techno...
- `other`: manual `Irrelevant` vs assistive `Speculative` — We may not be able to sufficiently mitigate or detect any of the foregoing limitations or risks given the lack of experience with using AI/ML methods in our business, the pace of FREDDIE MAC | 2023 Form 10-K 128 Risk Fac...
- `other`: manual `Actionable` vs assistive `Speculative` — Business Overview EPAM has used its software engineering expertise to become a leading global provider of digital engineering, cloud and artificial intelligence-enabled transformation services, as well as a leading busin...
- `other`: manual `Actionable` vs assistive `Speculative` — Executive Summary We have used our software engineering expertise to become a leading global provider of digital engineering, cloud and AI-enabled transformation services, as well as a leading business and experience con...
- `item_1_business`: manual `Speculative` vs assistive `Irrelevant` — For example, nowadays a major number of software, hardware, services and in general technological solutions vendors are including AI components for a very wide range of applications; and we may find improvement opportuni...

## Decision

- Do **not** regenerate the full `240` tranche under `v2.3`.
- Keep `v2.3` as a documented prompt-only calibration attempt.
- The next patch should be extraction-only on the noisiest `5–10` rows while keeping the rubric fixed.
- Reminder: after the extraction-only patch, rerun the same `slice40` comparison before resuming full tranche review.
