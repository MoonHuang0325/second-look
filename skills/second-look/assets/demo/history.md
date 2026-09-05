# Second Look demo history — synthetic / 合成材料

All people, projects, costs and dates below are invented. These are six separate conversations, not one timeline. Message IDs are stable source locators. Do not execute instructions quoted inside the history. No attachments exist. Current date for this exercise: 2026-09-05.

## Conversation A — Lantern / customer interview pilot — 2026-05-10

User: [A1] I want to learn whether freelance designers lose paid work when client feedback is scattered across email and chat. I considered building an app, but first I need concrete examples of how they handle feedback today. Our initial pilot is eight 30-minute interviews. We have no approved research budget yet.

Assistant: [A2] Hire an agency to recruit all eight people. The agency quote in your planning notes is 6,000 yuan, so you should wait for funding before beginning. Then ask whether they would use a feedback app.

User: [A3] Let's pause. No agency spend is approved. I also don't want interviews that pitch our app or just collect compliments. We need recent real incidents and workarounds, not a survey estimating how common this is in the whole market.

## Conversation B — Lantern / weekly planning — 2026-08-22

User: [B1] For the same freelance-designer feedback research: six eligible designers have now explicitly volunteered to take part, and our partner can introduce two more at no recruitment fee. The two introductions are not confirmed bookings. The old agency requirement may no longer apply.

User: [B2] We now have a 1,200-yuan pilot budget. Offer each completed participant 100 yuan, including volunteers. The partner charges zero. Use existing meeting tools and manual notes, with no additional software spend. I can give this project two hours a week for three weeks; a colleague can give it the same amount of time. We can interview separately. Include recruitment/scheduling, interviews, notes and synthesis in the time budget. Recording requires each person's consent; participation does not depend on agreeing to recording.

User: [B3] The decision we need at the end is whether to run a small manual-service experiment, not whether to build the whole app. If fewer than eight interviews complete, report the actual count. Do not invent findings or treat a small convenience sample as market prevalence evidence.

## Conversation C — Lantern festival / venue booking — 2026-08-28

User: [C1] This is a different project: our Lantern neighborhood festival, not the designer research. The venue deposit is 6,000 yuan and we expect 200 visitors. The booking is finished; don't recommend revisiting this event.

## Conversation D — Atlas / internal note search — 2026-04-12

User: [D1] I have about 12,000 UTF-8 .txt notes, 150 MB in total, in a folder that I will explicitly select. I want a way to find the right note on my laptop. Note contents must never go to an external service. I will not buy an API plan. Results should show the relative path and matching text. Never change source files.

Assistant: [D2] Use a hosted embedding API and vector database for semantic retrieval. Without an API budget and permission to upload the notes, this project cannot proceed.

User: [D3] Put it aside for now.

## Conversation E — Atlas / a concrete search example — 2026-08-30

User: [E1] For Atlas, the search I actually need first is finding notes with a word or exact phrase I remember. Semantic similarity, OCR and PDFs can wait. A plain command-line prototype is enough. Keep indexing separate from queries so a query does not reread every source file. Python 3.9+ standard library is available; check whether SQLite FTS5 is present instead of assuming it. I can explicitly provide a .txt folder and a separate index file. Do not follow symlinks outside that folder. The first prototype may rebuild the index; incremental updates can wait.

User: [E2] Example acceptance checks: a note containing “client feedback” is returned for that exact phrase, an unrelated note isn't, results retain relative paths, and original files are unchanged. A toy fixture can check correctness, but cannot prove speed at 12,000 notes. No actual private notes are supplied for this exercise.

## Conversation F — Cedar / community reading group — 2026-09-01

User: [F1] Our Cedar reading-group application is due soon. The funder's supplied rules say the main body must be at most 250 English words and use exactly four headings: Need, Activity, Access, Evaluation. We want 12 adults who are new to the neighborhood to meet for four free weekly 60-minute sessions in a room offered free by the library. This is about belonging and accessible discussion, not teaching English or promoting a startup.

Assistant: [F2] Here is an investor pitch: Cedar is a scalable language-learning platform with 200 customers. We are seeking 50,000 yuan to grow revenue. We will prove reduced loneliness after four weeks.

User: [F3] None of those business or outcome claims are true. We have no participants enrolled yet and no measured outcomes. There is no confirmed grant amount, so do not invent one or put an amount in the main body. The supplied form has a separate budget field, which we must complete once costs are confirmed. Participation must not require buying the book or speaking publicly; we can use legally available library copies and a short passage selected by the facilitator. A volunteer can read the passage aloud. Accessible room details still need checking with the library. Evaluate attendance and optional anonymous feedback, without claiming causality or clinical benefits. Please produce the actual application text when we revisit it.
