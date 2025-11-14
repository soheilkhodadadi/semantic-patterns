1. Review and understand current segmentation

src/core/sentence_filter.py provides segment_sentences(text) and filter_ai_sentences(sentences, keywords). It uses spaCy (if available) or a regex to split text at sentence boundaries. The splitting heuristics are fairly simple: sentences are separated at ., ?, or ! followed by whitespace and a capital letter
pubmed.ncbi.nlm.nih.gov
.

The top‑level script src/scripts/filter_ai_sentences.py reads text from each filing, calls segment_sentences, then calls filter_ai_sentences to keep only AI‑related sentences.

2. Identify the failure modes

Page‑number interruptions: In filings, page numbers and boilerplate like “Table of Contents” appear in the middle of sentences. The current segmentation sees these lines as separate “sentences” because they end with no punctuation and sometimes contain digits only.

Bullet or list items: Companies often list risk factors or initiatives in bullet‑like runs, each item starting with a lowercase letter and ending with a semicolon, with the final item ending with a period. These fragments are conceptually one long sentence but are treated as separate lines.

3. Add a post‑processing function to merge fragments

Introduce a function, e.g. merge_sentence_fragments, that operates on the list returned by segment_sentences before passing it to filter_ai_sentences. The function would:

Iterate through the list of segmented sentences and build a new list.

Skip any lines that are just a page number (e.g. “22”) or match phrases like “Table of Contents”.

Detect incomplete sentences: if a sentence does not end with a period, question mark, or exclamation mark or ends with a semicolon, treat it as an incomplete fragment.

Check the next sentence: if it begins with a lowercase letter (or is a continuation like “our ability”) and the current one is incomplete, join them by removing any trailing semicolons from the current fragment, stripping page numbers and “Table of Contents” from the next fragment, and concatenating with a space.

Continue joining until you encounter a fragment that ends with proper sentence‑ending punctuation.

After merging, ensure the combined sentence starts with a capital letter (capitalize it if necessary) and ends with a period if it’s missing.

Append the merged sentence to the output list.

This simple loop handles both page‑number interruptions and bullet lists. It does not require changing the underlying spaCy or regex segmentation and preserves all other features of the current pipeline.

4. Integrate the merging into the pipeline

In filter_ai_sentences.py (the top‑level script), after calling segment_sentences(text), call merge_sentence_fragments(sentences) to obtain cleaned sentences.

Pass these cleaned sentences into filter_ai_sentences(cleaned, keywords) to identify AI‑related sentences.

Leave the rest of the pipeline (directory scanning, file skipping, command‑line options) untouched.

5. Testing and iteration

Before merging into production, test the new function on several problematic filings (like the example you provided). Confirm that sentences split by page numbers and lists are now merged correctly.

Compare the number of AI sentences before and after merging to ensure a sensible increase without introducing noisy data.

Once satisfied, re‑run the extraction on a subset of filings for smoke testing, then apply it to the full 500‑firm sample.