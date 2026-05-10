# AI真人剧 Pacing Guide

## Default Shot Timing

Use these as starting points, then adjust for script intent:

| Shot type | Typical duration | Use for |
|---|---:|---|
| Establishing or location reset | 1-3s | Place, time, relationship geography |
| Two-shot | 3-6s | Conflict setup, power relation, shared action |
| Medium close-up | 3-5s | Dialogue line, listening, tension |
| Close-up | 2-4s | Reaction, realization, lie, decision |
| Insert | 1-2.5s | Phone, document, weapon, ring, message |
| Continuous action | 5-10s | Entering, crossing room, handing object |
| Suspense hold | 4-8s | Waiting, hesitation, reveal buildup |

## Lens Defaults

Use a consistent lens vocabulary when generating Seedance shot prompts:

- `24mm广角`: street geography, crowds, establishing shots, spatial resets.
- `35mm定焦`: walking shots, two-person movement, medium spatial relation.
- `50mm定焦`: dialogue, medium close-ups, ordinary reactions.
- `85mm定焦`: emotional close-ups, sweet smiles, shame, anger, tension.
- `100mm微距`: props, mechanisms, paper notes, jewelry, waist detail, hands.

Every shot in a Seedance prompt should include focal length or lens type. If exact lens choice is uncertain, choose from this default set based on shot intent.

## Shot Size Logic

Choose shot size by story function, not decoration. The default logic is: wide shots explain space, medium shots manage blocking, close shots carry performance, inserts prove plot facts.

Use `全景` or `远景` when:

- Starting a new location or resetting geography.
- Showing who surrounds whom, crowd pressure, entrance/exit, or distance.
- A physical action changes multiple people's positions.
- The audience may otherwise lose track of where characters stand.
- In short-drama openings, keep the establishing wide shot brief, usually 1-2 seconds, then cut into faces.

Use `中景` when:

- Showing body movement, handoff, approach, retreat, or two-person relation.
- A character crosses in front of another or changes screen side.
- Dialogue depends on visible posture, distance, or power relation.

Use `中近景` when:

- Dialogue and reaction both matter.
- The frame needs face, upper body, and hand prop at the same time.
- A character is listening, hesitating, testing, or hiding intent.
- The scene is a verbal confrontation with stable positions; this is the default coverage size.

Use `近景` or `特写` when:

- The beat is an emotional turn: shame, threat, realization, lie, sweet smile, anger, fear.
- A joke lands through expression or timing.
- The audience must read eyes, mouth, breathing, hand tension, or micro-reaction.
- A main character's rebuttal, reveal, or power shift needs a held performance moment.

Use `大特写` or `插入特写` when:

- A prop is evidence: paper note, sign, phone, letter, document, weapon, ring, medicine, blood mark, missing object.
- A mechanism changes state: latch opens, spring releases, powder sprays, small copper piece turns.
- The shot must prove a cause or prevent audience confusion.

After a close-up chain, return to `中景` or `全景` when:

- Characters move.
- A prop changes owner.
- A crowd reaction changes the social pressure.
- The next beat depends on distance or screen direction.

For public conflict scenes, use reaction coverage deliberately:

- Cut to the listener when a line wounds, exposes, or pressures them.
- Cut to a third-party reaction when social judgment matters.
- Return to the speaker when they retake control.
- Keep the principal character visually dominant during their reversal; do not overcut away from the decisive expression.

Avoid:

- Starting a complex scene with only close-ups.
- Using inserts that do not change plot understanding.
- Cutting from one close-up to another when the audience needs to know where people are.
- Letting the camera get so close that Seedance loses hands, props, or body orientation needed for continuity.

## Shot Count Targets

For AI真人短剧:

- 15-second segment: usually 2-5 shots, or 1 continuous performance shot.
- 30-second scene: usually 6-10 shots.
- 60-second scene: usually 12-20 shots.
- Dialogue-heavy 60-second scene: fewer shots if performances need continuity.
- Action-heavy 60-second scene: more shots, but include wider geography resets.

For the user's prior examples, a practical default is 3-4 shots per 15-second Seedance segment, with most shots lasting 3-5 seconds.

For pure dialogue confrontation with stable blocking, a 15-second segment can contain 4-6 shots. For mechanism action, prop transfer, crowd movement, or spatial changes, keep the safer 3-4 shot target.

## Rhythm Patterns

Conflict dialogue:

1. Two-shot establishes distance and power.
2. Medium close-up on speaker.
3. Reaction close-up.
4. Insert or hand movement if plot-relevant.
5. Return to two-shot when positions change.

Reveal:

1. Setup close-up or insert.
2. Hold on discovery.
3. Reaction close-up.
4. Wider shot showing changed relationship.

Confrontation:

1. Wide or two-shot establishes face-off.
2. Alternating close-ups intensify.
3. Insert of decisive prop/action.
4. Final held close-up or exit frame.

Reference AI真人短剧 dialogue rhythm:

1. Use a 1-2 second establishing shot only to identify place, public pressure, and who is present.
2. Move quickly into medium close-ups and close-ups for faces, eye lines, posture, and social pressure.
3. Use two-shots or medium shots when distance, power relation, crowd pressure, or approach/retreat changes.
4. Hold the protagonist's key rebuttal or reversal in close-up for 4-6 seconds when the expression and pause matter.
5. Cut tight listener reactions after verbal hits, then return to the speaker or a third-party reaction.
6. Keep platform-style dialogue subtitles out of Seedance prompts; spoken lines stay audio only.

## AI Reliability Notes

- Keep each shot's physical action simple.
- Avoid crowd scenes unless the script requires them.
- Limit hand-specific actions unless the prop is central and anchored.
- Avoid rapid changes in wardrobe, hair, lighting, or location within one segment.
- Make emotional changes visible through posture, gaze, distance, and timing.
