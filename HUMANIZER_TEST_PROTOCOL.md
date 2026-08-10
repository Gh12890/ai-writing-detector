# Humanizer Test Protocol

## Text Selection Rule
When selecting text from a sample file to run through a humanizer:
- Exclude any metadata header (author name, location, coordinates, date stamps, etc.) that isn't part of the actual prose.
- Start from the first line of actual written content (the main note/essay/message body).
- Apply this exclusion consistently to every file tested under this protocol — human or AI, held-out or dry run.
- If a file has no such header, note "no header present" rather than skipping the note entirely, so it's clear the rule was checked, not forgotten.