# Script-to-Storyboard Workflow

## Intake

Extract these facts before designing shots:

- Story goal of the scene or episode.
- Beat turns: new information, emotional shift, decision, reveal, interruption, physical action.
- Dialogue that must stay visible on screen.
- Characters, wardrobe, props, location, time of day, and mood.
- Physical layout: doors, windows, tables, beds, vehicles, counters, hallways, or other anchors.
- Required visual evidence: phone screen, document, blood mark, ring, money, medicine, message, photo.

If sample scripts are provided, infer:

- How dense the user's pacing is.
- Whether they prefer dialogue coverage or action-first coverage.
- Preferred shot sizes and transitions.
- Typical number of Seedance segments per scene.

## Design Order

1. Split the script into beats before shots.
2. Assign each beat a viewer question: "What must the audience understand now?"
3. Choose the simplest shot that makes the beat legible.
4. Add camera movement only when it clarifies a reveal, power shift, pursuit, or emotional pressure.
5. Create a shot list with duration estimates.
6. Group shots into Seedance segments under 15 seconds.
7. Write segment handoff anchors and generation prompts.
8. Run a continuity pass, a rhythm pass, then the content QA pass in `content-qa.md`.

## Shot Design Heuristics

- Use establishing shots sparingly in AI真人短剧; often 1-2 seconds is enough if the location is obvious.
- Let dialogue scenes breathe through shot-reverse-shot, two-shots, inserts, and reaction shots.
- In public verbal conflict, prioritize close facial coverage and reaction shots after a brief spatial reset.
- Use close-ups for emotional turns, lies, realizations, threats, and decisions.
- Use inserts for plot evidence, not decoration.
- Choose shot size by function: wide for space, medium for blocking, close for performance, insert for evidence.
- Avoid unmotivated fast cutting; AI-generated human continuity is more reliable when each shot has one clear intent.
- For complex physical movement, use a wider shot first, then closer coverage after positions are established.

## Continuity Pass

For every cut, verify:

- Who is on which side of frame.
- Which direction each person is looking.
- Whether a prop changes hands.
- Whether a character sits, stands, enters, exits, turns, or crosses the camera axis.
- Whether the next shot can plausibly follow from the previous last frame.

## Rhythm Pass

Check that the shot pattern fits the scene:

- Conflict dialogue: medium close-up / close-up rhythm with occasional two-shot reset.
- Suspense reveal: hold longer before the reveal, then cut to reaction.
- Chase or urgent action: shorter shots, but keep geography clear.
- Intimate confession: fewer cuts, stable camera, longer close-ups.
- Comedy or reversal: setup shot, timing hold, reaction cut.
