# Bundled runtime

Python 3.9+ standard library only. These helpers normalize files and maintain state; **they do not select meaningful goals, reason, verify claims, or call a model**. The host agent performs that work using the skill.

Resolve `scripts/second_look.py` relative to this installed skill, not the user's current directory. Run `--help` for all options. Put `--store /absolute/private/path` before the command. Default: `SECOND_LOOK_DATA_DIR` or `~/.local/share/second-look`. Never place private data inside the source repository or installed skill; the helper refuses both. On a sandboxed host select an allowed private working directory outside the repository. The database contains normalized transcript text and is private, not encrypted.

## File workflow

At the start of a repeated run, call `status` to find pending run IDs, existing goal IDs/source mappings, and feedback. Resume pending work or use those IDs when checking eligibility; do not invent a new goal ID to bypass repeat suppression.

```text
python3 <skill>/scripts/second_look.py capabilities --local
python3 <skill>/scripts/second_look.py --store <private-dir> import <selected-file> [more-files]
python3 <skill>/scripts/second_look.py --store <private-dir> run
python3 <skill>/scripts/second_look.py --store <private-dir> candidates --limit 100
python3 <skill>/scripts/second_look.py --store <private-dir> read <key>
```

Imports are atomic per file; one failed file produces a nonzero exit with explicit errors, without rolling back successful files. Read that result. No directory recursion or network fetching. Files over 100 MiB require explicit `--max-mb`; changing files are deferred.

Candidates are previews of the imported corpus, interleaving two recent records with one old record. This is a coverage strategy, not semantic ranking. `--query` is a literal case-insensitive substring filter, not semantic search. Use several relevant terms or agent reading for synonyms. `--include-inspected` allows a fresh screening when model/context changed; `--include-excluded` only for an explicitly requested excluded source.

After actually screening source records use `inspected <keys...>`; this advances discovery but does **not** mark their goals solved. A selected goal can use multiple source keys. Assign a stable scoped ID such as `workshop/45-minute-session`, retaining it in the run checkpoint. Then:

```text
... eligible --goal workshop/45-minute-session --keys <key> --model <observed-model>
```

Omit `--model` if unknown. `--context` describes explicitly changed circumstances; keep it stable across equivalent runs. `--retry` is for a specific user-requested retry, not default broad discovery. A new goal ID in the same conversation remains eligible.

After delivering/saving the result:

```text
... record --goal workshop/45-minute-session --keys <key> \
  --outcome supported_improvement --summary 'Corrected duration, preserving practice.' \
  --evidence '<actual-source-locator>' --artifact '<actual-delivered-result-locator>'
```

Outcome values: `supported_improvement`, `direction_to_test`, `retain_original`. The helper requires evidence/result locators but cannot verify their truth. Do not substitute invented strings. Preserve the same model/context as the eligibility check. Use the CLI via structured process arguments or proper shell quoting; transcript text is never shell code.

## Feedback and resumption

```text
... feedback --scope goal --target workshop/45-minute-session --value closed
... feedback --scope goal --target workshop/45-minute-session --value include
... run --id <run-id> --checkpoint '{"selected_goals":["workshop/45-minute-session"],"next_step":"verify"}'
... run --id <run-id>
... run --id <run-id> --finish
```

Scopes are `goal` and `source` (source target is a conversation key). Values: `exclude`, `closed`, `include`, `accepted`, `dismissed`. These record only explicit user feedback. Goal feedback requires the agent to resolve the user's topic to stable IDs; the helper does not perform semantic topic matching. Persist labels/mappings in the checkpoint and consult them on future runs.

Pending runs can be inspected after interruption. Resume from saved progress and check source fingerprints before reusing work. Completed runs are immutable; start a new one. Finishing a run does not mark any goal reviewed—only `record` does that. Persist native source discovery cursors in checkpoints if supported.

## Portable state

```text
... export-ledger --output <new-private-ledger.json>
... restore-ledger <private-ledger.json>
```

The exported ledger omits raw transcript text but may contain sensitive summaries, locators, and feedback. It is still private. Restore into an empty ledger, after importing the same sources if available. Source fingerprints prevent inspected status being applied to changed records. A restored ledger alone does not restore transcripts; re-import them to continue reasoning. Unknown/future schema versions are rejected. Repeated export never overwrites an existing file.

## Normalized native corpus v1

Optional JSON envelope: `{"kind":"second-look-corpus","schema_version":1,"conversations":[...]}`.

Each conversation has string `source`, stable `id`, `branch`, `title`, `locator`, and `completeness`; nullable `created_at`, `updated_at`, `project`; list `warnings`; nonempty `messages`.

Each message has unique string `id`, `role` (`user`, `assistant`, `system`, `developer`, `tool`, `unknown`), string `text`, nullable `timestamp`, actual string `locator`, and list `warnings`. Completeness: `complete`, `text_only`, `partial`, `summary_only`, `unknown`. Do not mark `complete` merely because the tool returned successfully. Keys/fingerprints are recomputed by the helper.

Identity uses source + native conversation ID + branch. A native ID must identify the same project/account scope consistently; adapter code must namespace it when IDs are only locally unique. Changed content updates the same record. A file import replaces the branch set for each included native conversation; use a full per-conversation snapshot when importing normalized native records, not one branch from a larger snapshot. Review fingerprints remain as history and make new material eligible.

## Data deletion

To remove private history, close the helper and delete the chosen private directory using the host's normal file controls. No automatic deletion or public sharing is performed. Without a persistence tool, use the portable ledger described in `delivery.md` and state the limitation.
