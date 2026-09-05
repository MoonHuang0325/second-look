# Three completed Second Look results

## Atlas: a working local word-and-phrase search draft

**Supported improvement.** The standalone [Atlas prototype](atlas_search.py) builds a local SQLite FTS5 index from an explicitly selected folder of UTF-8 `.txt` files. Queries return relative paths and matching text without rereading the source folder. It uses Python 3.9+ standard-library modules, checks FTS5 availability, and has no external-service calls or paid dependencies.

Example usage, after substituting your explicitly selected paths:

```sh
python3 atlas_search.py index '/your/selected/txt-folder' '/your/separate/atlas.sqlite'
python3 atlas_search.py query '/your/separate/atlas.sqlite' 'client feedback'
python3 atlas_search.py query '/your/separate/atlas.sqlite' 'feedback' --limit 10
```

The index must live outside the source folder. Indexing rebuilds it; an unsuccessful rebuild preserves the previous index. The prototype rejects an existing unrelated file instead of overwriting it. It skips all symlinked files and directories, including ones pointing outside the selected folder. Notes are opened only for reading. Keep the folder stable while indexing; the prototype does not defend against concurrent malicious path replacement.

“Exact phrase” here means adjacent SQLite word tokens, case-insensitive under its `unicode61` tokenizer. It is not byte-for-byte punctuation matching or semantic search. A query containing `OR` is treated as phrase text rather than a search operator. Results are JSON with `path` and `matching_text`, suitable for a plain terminal. The index contains a local copy of indexed text, so it should be stored with the same privacy care as the notes. Updated or deleted notes require another indexing run.

**Why revisit:** D2 made a hosted embedding service a prerequisite, stopping the project at D3. D1 already prohibited external note uploads and paid APIs. E1 then clarified that remembered words and phrases are the first requirement and explicitly allowed a command-line prototype. Those requirements permit a local full-text solution; semantic search is unnecessary for this first version.

**Observed verification:** Two executed test methods cover phrase precision, unrelated and nonadjacent-text exclusion, relative paths, highlighted matching text, word queries, omitted symlinks, source-byte and modification-time preservation, successful querying while the source folder is absent, safe failed rebuilds, stale-entry removal on rebuild, unrelated-index-file preservation, and an explicit missing-FTS5 error. The actual environment successfully created and queried FTS5. A separate command-line smoke check is recorded in [verification summary](../README.md).

**Limits:** The supplied 12,000-note/150 MB collection was not available. Small invented fixtures establish tested correctness only, not speed, memory use or production readiness at that scale. No private notes were accessed. Sources: **D1–D3, E1–E2**.

## Lantern: an eight-interview pilot within the current budget

**Supported improvement.** Begin with the six eligible volunteers and request the two free partner introductions. Treat all eight as recruitment prospects until booked, and report only interviews actually completed. The old agency expense is no longer a blocking dependency.

Offer **100 yuan for each completed interview**, including volunteers. Eight completions cost **800 yuan**, leaving **400 yuan unallocated** within the 1,200-yuan cap. The partner charges zero. Use existing meeting tools and manual notes; this plan commits no agency or software spending.

Each person has two hours per week for three weeks: **six hours each, twelve person-hours total**. Work separately on interviews. Use the same guide and note template so their evidence can be compared.

| Week | Each person's allocation | Total across both people |
|---|---|---|
| 1 | 40 min invitations, scheduling and introductions; 30 min one interview; 15 min its notes; 35 min shared guide preparation and pilot debrief | 4 person-hours; 2 interviews |
| 2 | 90 min three interviews; 30 min immediate notes, 10 min each | 4 person-hours; 6 interviews |
| 3 | 30 min evidence coding; 45 min joint synthesis; 15 min incentive administration and completion count; 30 min scheduling/no-show buffer | 4 person-hours |

The week-three buffer combines to one person-hour, but each person has only 30 minutes of it: do not assume it automatically accommodates a replacement interview plus notes. If bookings slip, explicitly reallocate available time and accept a smaller completed sample; do not silently add hours. Week two is full, so schedule it during week one. If note quality needs more time, reduce the number of interviews rather than drop synthesis or exceed the capacity limit.

**Invitation draft**

> We are speaking with freelance designers about how they handle client feedback in their current work. Would you be available for a 30-minute conversation about a recent project? We offer 100 yuan after completing the interview, including to volunteers. You do not need to prepare a presentation or share confidential client material. We will take manual notes. Recording is optional, requires your separate consent, and is not a condition of participating.

**30-minute interview guide**

- **0–3 min:** Explain the purpose, timing and incentive. Obtain participation consent. Default to manual notes; ask separately before any recording. Ask them to avoid client-identifying or confidential material.
- **3–8 min:** “Tell me about your most recent paid design project that involved client feedback. What was the work, and when did this happen?”
- **8–17 min:** “Walk me through the feedback from when it arrived to your next revision. Which channels did it use? How did you decide what to act on? Was anything missed or contradictory?” Ask for the sequence, including examples where feedback went smoothly.
- **17–23 min:** “What happened as a result? Did this change revision time, payment, deadlines or later work? What makes you connect that consequence to the feedback?” Distinguish observed loss of paid work from frustration or speculation.
- **23–28 min:** “What did you do to manage it? What time or cost did that take? What worked, and what remained difficult?”
- **28–30 min:** Check the factual summary, invite corrections, and explain the incentive process. Ask separately whether follow-up contact about a possible manual-service trial would be welcome. Do not pitch an app.

**Note template:** participant code; completion status; incident recency; work context; channels; event sequence; observed consequence and supporting detail; existing workaround and cost; counterexample; participant correction; follow-up permission. Keep direct quotes distinct from interviewer interpretation. Mark unknowns rather than filling them in.

**Decision sheet:** List the actual completion count, recurring mechanisms, contrasting cases, current workarounds and missing evidence. A proposed planning rule—not a finding—is to consider a narrowly scoped manual trial if at least two independent recent incidents reveal a similar actionable problem, consequences are concrete, and at least two people explicitly agree to discuss a trial. Otherwise, defer it or refine the question. Meeting that rule does not validate market demand.

If the evidence supports it, draft a manual service around the observed problem—for example, a designer-provided feedback summary organized into one revision checklist for one live project. Confirm consent, permitted material, scope and operator capacity before any trial. Agree on an observable trial measure such as reconciliation time or missed feedback items. No research results or trial participants are assumed here.

**Why revisit:** A2 recommended waiting for a 6,000-yuan agency contract and asking whether people would use an app. A3 rejected unapproved spending and app-pitch interviews. B1 supplies a free recruitment route; B2 supplies budget, staffing and consent constraints; B3 makes the decision a possible manual-service experiment. The plan fits those later constraints and produces incident evidence. Bookings and the usefulness of the resulting evidence remain unverified. Sources: **A1–A3, B1–B3**. The unrelated festival in **C1** is closed and was excluded; its deposit and attendance were not imported into this project.

## Cedar: a submission-ready main-body draft

**Supported improvement.** The following is the actual application main body; a standalone copy is in [cedar-application.txt](cedar-application.txt).

### Need
Cedar aims to help adults who are new to the neighborhood feel welcome and connect through shared reading. No participants are enrolled yet. We hope to bring together 12 adults for accessible discussion and companionship.

### Activity
We propose four free weekly sessions, each lasting 60 minutes, in a room offered free by the library. A facilitator will select a short passage and guide discussion. A volunteer can read the passage aloud, giving participants a shared starting point.

### Access
Participants will not need to buy a book or speak publicly. We will use legally available library copies and allow people to listen without contributing aloud. Before confirming arrangements, we will check accessible room details with the library and communicate the confirmed information to participants.

### Evaluation
We will track attendance and invite optional anonymous feedback about welcome, participation and the sessions. We will summarize attendance and feedback to improve future sessions, without claiming that four meetings caused changes in loneliness or produced clinical benefits.

**Why revisit:** F2 introduced a business model, customer count, grant amount and unsupported outcomes. F3 explicitly rejected those inventions and asked for the actual text. This replacement uses the four required headings and the stated activity and access commitments. It distinguishes aims from observed outcomes and includes no requested grant amount. Sources: **F1–F3**.

**Verification and remaining work:** The standalone main body was checked for the exact headings and the 250-word maximum; the observed word count is recorded in [verification summary](../README.md). Accessible-room details still need the library's confirmation. Complete the separate budget field once costs are confirmed. Neither this draft nor the supplied history establishes confirmed costs, enrollment or outcomes.

## Coverage

Read all six supplied synthetic conversations, dated April 12–September 1, 2026, using September 5, 2026 as the exercise date. Screened four distinct goals, selected three, and excluded the explicitly completed festival. These are supplied text messages, not a real account search; no attachments exist in the pack. No personal history, real notes, live projects or external research were accessed. The recorded improvements come from later facts and corrected reasoning, not a measured model comparison. Search-scale performance, actual interview bookings and research findings, and Cedar's room and budget details remain unverified. A private local review ledger records saved results with model ID unknown and no inferred acceptance.
