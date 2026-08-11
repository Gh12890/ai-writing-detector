# Humanizer Robustness Test (Quillbot, Standard mode)

Held-out AI files: sample07.txt, sample12.txt (n=2 — not statistically powered, illustrative only)
Consent: both authors confirmed consent for AI research use of their documents.

## Results
sample07: 2 flags -> 1 flag (lost superficial_ing_analysis, em_dash_density survived)
sample12: 2 flags -> 2 flags (both rules survived: em_dash_density, superficial_ing_analysis)

## Interpretation
Inconsistent, low-n result. em_dash_density (a low-level punctuation habit) survived
paraphrasing in both cases. superficial_ing_analysis (a phrasing-level pattern) survived
once, was erased once. No claim of general humanizer robustness or fragility is
supported by this data -- it motivates a larger-n test, not a conclusion.

## Dry-run note
Initial 139-word test excerpt was too short to produce meaningful flag counts (1 flag
each side) and was discarded as a methodology-validation step only, not a data point.