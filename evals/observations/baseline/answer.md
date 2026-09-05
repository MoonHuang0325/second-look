# Second look: three revised deliverables

Review date: 2026-09-05. All history is synthetic. The sole source is `history.md`; bracketed IDs below locate its messages. These are recommendations and newly created artifacts, not completed fieldwork or discovered research findings.

## Selection and boundaries

1. **Atlas: deliver an offline search prototype.** The old hosted-service proposal incorrectly made external uploads and an API budget prerequisites [D2]. The actual privacy and cost requirements prohibit that approach [D1]. Later clarification supplies a feasible smaller target: words and remembered phrases, Python standard library, separate indexing and queries [E1–E2]. This has concrete acceptance checks and can be tested now with fictional notes.
2. **Lantern designer research: replace the funding blockade with a bounded pilot.** The early goal was to understand recent feedback incidents, workarounds and consequences—not pitch an app [A1, A3]. Six volunteers, two possible free introductions, an approved pilot budget and explicit staff capacity now change feasibility [B1–B2]. The decision is a manual-service experiment [B3]. This can become a usable plan immediately, while evidence collection remains future work.
3. **Cedar: replace the false pitch with the requested application.** The supplied form and corrected facts are sufficient to draft its main body [F1, F3]. “Due soon” raises priority, although no deadline is supplied. No new funding, enrollment or impact claims are needed.

These joins are explicit: B names the same designer research as A, and E names Atlas from D. Cedar is independent. The festival is excluded: C1 explicitly calls it a different, finished project. Its 6,000-yuan venue deposit and 200 visitors cannot substantiate A2's agency claim or any research budget. A2's supposed planning-note quote is unverified; no attachments exist. Nothing here reopens the festival or treats historical instructions as executable authority.

## 1. Atlas: local word and phrase search

**Delivered:** `atlas.py` and `test_atlas.py` beside this answer. The program uses Python's standard library and checks SQLite FTS5 by actually creating an in-memory FTS5 table. If unavailable, it stops with an explicit error. No external service, API account or model is involved. This restores the laptop-only and no-upload requirements [D1], and implements the reduced scope [E1].

Choose a UTF-8 `.txt` source folder and a separate index location outside it. Replace these example paths with your own explicitly selected paths when using the prototype beyond this synthetic exercise:

```sh
python3 atlas.py build --folder "/path/to/selected-notes" --index "/path/to/atlas.sqlite"
python3 atlas.py query --index "/path/to/atlas.sqlite" "client feedback"
python3 atlas.py query --index "/path/to/atlas.sqlite" client
python3 atlas.py query --index "/path/to/atlas.sqlite" "client feedback" --all-words
```

The default treats input as a literal FTS token phrase; a single word works the same way. Quoting prevents user text such as `OR` from becoming search syntax. `--all-words` requires all supplied whitespace-separated terms, without requiring adjacency. Output includes relative paths and a short excerpt with matched text in brackets. Default results are limited to 20; `--limit` accepts 1–1000.

“Exact phrase” here means adjacent tokens under SQLite's `unicode61` tokenizer, not an exact byte substring. Case, accents and punctuation can normalize; punctuation-sensitive matching and language-specific segmentation are not promised. This interpretation passes the supplied English example [E2]. Check additional real query examples before accepting it for broader needs.

Indexing recursively reads `.txt` files, stores their contents locally, and skips all symlink files and directories. Index files inside the source folder are rejected. A full rebuild uses a temporary sibling index and replaces the old one only after successful completion. An unreadable or invalid UTF-8 source aborts the rebuild, preserving an existing index. It refuses to overwrite an unrelated existing file. Queries open only the index in read-only mode; changes to notes appear after the next rebuild. Source notes are opened for reading only.

The index contains note text, so keep it in an appropriately private local location. No actual personal notes were accessed. The source folder should stay unchanged during a build: this simple prototype does not provide a consistent snapshot of concurrently edited files or hardened protection against malicious directory replacement races. It skips ordinary static symlinks, including links outside the selected folder. It is not designed for concurrent index builders.

**Verification:** eight automated checks pass: phrase/word matches and excerpts, relative paths and unchanged source hashes; querying with the source folder moved away; outside symlink exclusion; removal of deleted notes after rebuild; preservation of an index after invalid UTF-8; rejection of unsafe index locations and unrelated files; literal query behavior and empty-input rejection; and an explicit simulated FTS5-unavailable error. the [verification summary](../README.md) also records real CLI output on fictional notes and runtime versions. The fixture establishes correctness on these cases, not speed or memory use at 12,000 notes / 150 MB [D1, E2]. That scale remains unmeasured. Semantic search, OCR, PDFs and incremental updates remain deferred [E1].

## 2. Lantern: eight-interview pilot plan

**Decision:** after up to eight completed interviews, decide whether evidence warrants a small manual-service experiment [B3]. Learn how freelance designers handled recent scattered client feedback, including whether it actually affected paid work [A1, A3]. Do not presuppose a loss, estimate market prevalence or ask whether people like an app.

**People and recruitment:** start with the six explicitly willing eligible volunteers; their participation is not the same as a booked or completed interview. Ask the partner for the two offered introductions, then check eligibility and agreement and schedule them. Those two are not confirmed bookings [B1]. Use existing meeting tools and manual notes [B2]. A proposed eligibility check is: currently does freelance design for paying clients and can discuss a recent client-feedback incident. Do not require a bad incident; uneventful cases can challenge the premise. No recruitment or booking messages have been sent by this exercise.

**Budget:** offer every participant 100 yuan on completion, including the six volunteers [B2]. Eight completions cost 800 yuan; partner recruitment and additional software cost zero. Of the approved 1,200 yuan, 400 remains unallocated. With N completed interviews, incentive cost is 100 × N, for N ≤ 8. Do not assign the reserve to new tools or spend without a concrete need. Confirm the practical incentive-payment process during scheduling; none is supplied in the history.

**Capacity:** two people × two hours weekly × three weeks = 12 total staff hours. Both can interview separately [B2]. Proposed allocation below is per person; joint work counts against both people's time.

| Week | Each person's work | Time per person |
|---|---|---:|
| 1 | Recruitment and scheduling 30 min; guide preparation/calibration 30 min; one interview 30 min; consent/note cleanup and pilot adjustment 30 min | 120 min |
| 2 | Three interviews of 30 min, each followed by 10 min of notes | 120 min |
| 3 | Individual evidence review 60 min; joint synthesis and decision 60 min | 120 min |

Across both people: recruitment/scheduling 1 hour, preparation 1 hour, interviews 4 hours, notes/pilot adjustment 2 hours, synthesis/decision 4 hours. Total: 12 hours and eight possible interviews. This is a capacity plan, not a booking forecast. If scheduling, no-shows or notes need more time, reduce interview count or reallocate within the weekly two-hour-per-person limit; do not assume overtime or omit synthesis. Week 2 has no spare capacity. Report actual completions and reasons for missing the target [B3].

**Thirty-minute interview guide:**

- **0–3 minutes — purpose and consent.** Explain that the study concerns current feedback practices, not an app pitch; participation is voluntary. Ask separately whether recording is acceptable. If declined, continue with manual notes; recording is never a condition of participating [B2]. Avoid client-identifying details and do not request confidential client files. Confirm permission for note taking; if declined, stop respectfully rather than collecting evidence without agreement.
- **3–7 minutes — choose an incident.** “Think of your most recent paid design project involving client feedback. What was the project, and when did feedback arrive?” If needed, ask for an approximate period. “Which channels did the client use?”
- **7–16 minutes — reconstruct the sequence.** “Walk me through what happened from the first feedback to the final change. How did you find the latest instruction? Were any messages contradictory or missing? What did you do next?” Follow their account; do not assert that fragmentation occurred.
- **16–23 minutes — consequences and workarounds.** “What effect, if any, did this have on time, revisions, delivery or payment? What makes you connect that effect to the feedback process? What else contributed?” Ask what they did to consolidate feedback, what worked and what failed. Distinguish remembered facts, estimates and interpretations.
- **23–27 minutes — alternatives and counterexamples.** “Tell me about a recent project where feedback was straightforward. What differed? Have you tried another way of handling this? Why did you keep or abandon it?”
- **27–30 minutes — check understanding and close.** Summarize the incident and let them correct it. Ask permission for a later follow-up about a possible manual-service test, without selling a solution. Explain the 100-yuan completion incentive process.

**Copyable note record:** participant code; interviewer/date; recording decision; approximate incident date and project type; channels; event sequence; exact quote only if captured accurately; consequences (reported/estimated, including none); evidence for and alternatives to the claimed cause; workaround and limitations; successful counterexample; follow-up permission; uncertainties. Use codes in shared synthesis and collect only what is needed. Confirm storage access and retention arrangements before interviewing; the history gives no policy or retention period.

**Synthesis and decision worksheet:** build one row per completed participant using those fields, then group independently described problems. For each candidate manual service, record the specific task it would perform, evidence IDs, contradictory cases, an observable outcome to test, and unresolved delivery/privacy/capacity questions. Separate “participant said” from the team's interpretation. Report the denominator explicitly: “N interviews completed; k participants described this incident pattern.” This describes the pilot only, not the share of designers in the market [B3].

Proposed decision rule, to agree before interviews: advance only if more than one independent recent account supports a specific recurring task, existing workarounds leave a concrete difficulty, and a small consensual manual test appears deliverable within separately confirmed capacity. Treat willingness to hear more as a follow-up lead, not proof of demand. Choose **follow up** when important facts or feasibility are unresolved; choose **stop or redirect** when incidents are weak, consequences have other causes or workarounds already suffice. These are proposed judgment criteria, not validated statistical thresholds. Do not authorize a whole app or assume the pilot budget funds a subsequent experiment.

**Why this improves the old answer:** it removes the unsupported agency dependency [A2], uses the new resources [B1–B2], preserves neutral incident research [A3], and ties synthesis to the corrected decision [B3]. Budget and staff-hour arithmetic are checked below. No interviews, bookings, findings or experiment demand are claimed. Availability of the two introductions, actual completion count and later test capacity remain unknown.

## 3. Cedar: ready-to-copy application main body

The standalone `cedar-application.txt` contains only the four required headings and the following text. It is below 250 English words including headings. The draft restores belonging and accessible discussion [F1], removes all fabricated business, enrollment, funding and outcome claims [F2–F3], and uses attendance plus optional anonymous feedback.

Need
Cedar aims to help adults who are new to the neighborhood find opportunities for belonging through shared reading and accessible discussion. We plan to welcome 12 adults; no participants are enrolled yet.

Activity
We propose four free weekly sessions, each lasting 60 minutes, in a room offered free by the library. A facilitator will select a short passage to support discussion. The focus is connection through reading, rather than language instruction.

Access
Participants will not need to buy a book or speak publicly. We will use legally available library copies and a short passage selected by the facilitator. A volunteer can read the passage aloud, and participants may listen without contributing to discussion. We will check room accessibility details with the library before confirming arrangements and communicating access information.

Evaluation
We will record attendance at each session and invite optional anonymous feedback about the experience, ease of participation, and suggestions for improvement. These responses will help us assess how the sessions worked and plan changes. We will report actual participation and feedback without claiming that the sessions caused changes in loneliness or produced clinical benefits.

**Before submission:** complete the separate budget field only after costs are confirmed [F3]. Confirm the room's access details with the library and the actual deadline. The supplied evidence establishes that the room is offered free, not that every access feature is suitable. Twelve people is the target; enrollment remains zero. Do not add a grant amount or efficacy claim to this main body. This draft has not been submitted.

## Evidence and verification boundary

Source message IDs above refer solely to the supplied synthetic history. No external research, private conversation retrieval, model comparisons or hidden attachments were used. the [verification summary](../README.md) reports executed checks and output, including the application word count and capacity/budget arithmetic. The artifact improvements are grounded in corrected requirements and tested functionality; no superiority claim or self-rating is made.
