# Changelog

## 0.3.0 — 2026-09-12 (preview)

Model-change re-review becomes operational:

- Add `detect-model`: compare an observed model identifier against the review
  ledger and list non-excluded reviewed goals worth re-checking. Detection still
  requires an identifier supplied inside the conversation; the helper observes
  nothing by itself.
- Fix duplicate suppression: a review recorded with an unknown model no longer
  permanently blocks re-review. Suppression now requires a definite same-model
  match (`reviewed_with_unknown_model` is reported instead of a silent block).
  Existing ledgers adopt the new semantics automatically; no migration needed.
- Add `important` feedback for explicitly valued goals/sources; candidates
  surface them first. Goal feedback on an unused ID now warns and suggests
  similar existing IDs instead of failing silently.
- Harden JSONL format detection: a stray shared field name can no longer
  misroute a foreign log; matching rows must dominate.
- Find LICENSE both at the repository root and beside a standalone skill zip.
- Add SECURITY.md with a private advisory channel, CODE_OF_CONDUCT.md,
  a pull request template, and Dependabot for GitHub Actions.

These changes make the model-upgrade scenario usable in-conversation. Scheduled
or automatic triggering remains intentionally out of scope; real-user efficacy
is still unverified.

## 0.2.1 — 2026-09-05 (preview)

- Put a source-backed before/after result before the installation details.
- Add a self-contained, no-install chat example and a clearer bilingual first-use path.
- Keep public source and distribution packages focused on users and contributors.
- Retire the superseded v0.2.0 downloads; use v0.2.1 packages for new installs.

## 0.2.0 — 2026-09-05 (preview)

- Add an explicit first-use path with six synthetic conversations and a helper that extracts them without opening private history.
- Publish three complete generated deliverables and a transparent strong-prompt comparison.
- Add opt-in minimized sharing guidance; ordinary reviews contain no promotion or automatic posting.
- Add explicit upgrades with recoverable backups outside the active skills directory and rollback on a failed final move.
- Simplify bilingual onboarding, document installation boundaries, add feedback forms.
- Include the demo in standard and plugin packages; keep private runtime records and holdout cases out.

These are usability and distribution improvements. Real-user efficacy, full native-history workflows and a marketplace listing remain unverified.

## 0.1.0 — 2026-09-05 (prototype)

Initial portable skill, standard-library history normalization and private ledger, synthetic format tests, 24 behavioral cases, installation and reproducible packaging.
