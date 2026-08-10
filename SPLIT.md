# Held-Out Test Split

Created: 2026-08-10
Method: random.seed(42), random.sample(files, 2) per class

## Train/Dev (used for rule tuning, threshold decisions, all prior FINDINGS.md numbers)
Human: sample02.txt, sample03.txt, sample04.txt, sample05.txt
AI: sample08.txt, sample09.txt, sample10.txt, sample11.txt, sample13.txt

## Held-Out Test (corpus/held_out_test/)
Human: sample01.txt, sample06.txt
AI: sample07.txt, sample12.txt

## Rules
- Held-out test files are not read, opened, or analyzed until a final evaluation run.
- No rule threshold, exclusion filter, or scoring change may be made in response to a held-out test result. If that happens, the split is void and must be redone with a new seed.
- sample05 (the Layer 2 outlier document responsible for ~80% of the apparent Layer 2 human/AI gap, see LAYER2_FINDINGS.md) fell into train/dev, not test — by chance, not selection. The held-out test set has not been checked against this known problem case. Any clean-looking held-out result should be read with that gap in mind.
- All numbers in FINDINGS.md and LAYER2_FINDINGS.md predate this split and were computed without a held-out set. They stand as prior exploratory findings, not validated results, until re-verified against held_out_test.