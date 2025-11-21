Stage 0 – Segmentation and Filtering

This plan is for the Codex agent working in the semantic‑patterns repository. The aim of Stage 0 is to fix sentence segmentation and filtering so that the AI‑related sentence extraction is robust on the full set of filings. We also want to make the pipeline configurable so it can read the entire dataset from an external folder but still run quickly on a small sample during testing. Structural refactoring of the repository will come later—Stage 0 focuses on functionality.

1 Context

Existing code:

src/core/sentence_filter.py defines segment_sentences(text) and filter_ai_sentences(sentences, keywords). It uses spaCy (if available) or a regex to split text at sentence boundaries.

src/scripts/filter_ai_sentences.py is the top‑level script. It reads filings, calls segment_sentences, then calls filter_ai_sentences to keep only AI‑related sentences.

There is currently no handling of page numbers or bullet‑style lists, so sentences are sometimes broken at page numbers and semicolons.

Scaling: we want to run the pipeline over all available filings (e.g. 2024 back to 2000) located in an external directory. However, during development and debugging we need to limit the number of filings processed so the script runs quickly.

2 Objectives

Improve segmentation by adding a post‑processing function to merge fragments split by page numbers or list separators.

Integrate the new function into the existing pipeline without changing the overall structure.

Parameterise input path and sample size so the script can process the full dataset or a limited number of filings for testing.

Test the updated pipeline on a small subset of filings before running it on the full dataset.

3 Tasks for Codex

Follow these steps in order. Create a new branch for Stage 0 (e.g. feature/stage0-segmentation). Do not perform unrelated refactoring.

3.1 Add merge_sentence_fragments in src/core/sentence_filter.py

Implement a function merge_sentence_fragments(sentences: list[str]) -> list[str] that takes the list of segmented sentences and returns a new list where fragments are merged. The logic should:

Skip page numbers or boilerplate lines such as lines consisting solely of digits (e.g. "22") or phrases like "Table of Contents". Do not include these lines in the output.

Identify incomplete fragments: a fragment is considered incomplete if it does not end with a period, question mark, or exclamation mark, or if it ends with a semicolon.

Detect continuation: look ahead to the next fragment. If it begins with a lowercase letter or looks like a continuation (e.g. "our ability"), treat it as the continuation of the current fragment.

Merge fragments: when an incomplete fragment and its continuation are detected, remove trailing semicolons from the current fragment, strip page numbers and boilerplate from the next fragment, concatenate them with a single space, and repeat this process until a fragment ending with proper punctuation is formed.

Capitalization: after merging, capitalise the resulting sentence if needed and ensure it ends with a period.

Append the merged sentence to the output list and continue processing the rest of the list.

Add this function below the existing functions in src/core/sentence_filter.py with an appropriate docstring describing its purpose and parameters.

3.2 Integrate merging into src/scripts/filter_ai_sentences.py

Modify the script so that after calling segment_sentences(text), it calls merge_sentence_fragments(sentences) and stores the result. Then pass this cleaned list into filter_ai_sentences(cleaned_sentences, keywords) instead of the original segmented list. Leave the rest of the pipeline intact (directory scanning, file writing, etc.).

3.3 Parameterise input path and limit

Allow the top‑level script to accept two new options:

--input-dir: the path to the directory containing yearly subdirectories of filings. Use this path instead of any hard‑coded subsample folder.

--limit (optional): an integer specifying how many filings to process per run. When provided, process only the first N filings (ordered as the script currently orders them). If not provided, process all filings found in --input-dir.

Update the script’s argument parser accordingly. Use the default argument values so that existing usage (e.g. running the script without these flags) behaves as before but points to the full dataset.

3.4 Testing instructions

Before running on the full dataset, run the script with a small limit to verify that the merging logic works and that AI‑related sentence counts look sensible. For example:

python src/scripts/filter_ai_sentences.py --input-dir /path/to/full/dataset --limit 3


Review the output files to ensure sentences spanning page breaks or lists are merged correctly. Once satisfied, run the script without --limit to process the entire dataset.

3.5 Report back

After implementing the above changes and running the limited test, provide a summary of:

The number and names of files modified.

Any issues encountered while merging fragments.

The test run results (number of AI sentences extracted before and after merging for the sample filings).

Do not proceed to other stages until Stage 0 changes are merged and confirmed.

4 Notes

This plan does not require moving modules between folders. All modifications are localised to the existing core and scripts directories.

Structural refactoring (e.g. reorganising packages) can be deferred to later stages after this functionality is validated on the full dataset.