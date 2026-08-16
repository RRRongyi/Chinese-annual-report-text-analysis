---
name: chinese-annual-report-text-analysis
description: Batch Chinese annual-report and MD&A dictionary text analysis. Use for TXT, CSV, XLSX, or XLS inputs when importing stopwords, a jieba word-protection dictionary, and a target dictionary, then calculating target word counts, sentence counts, log1p values, ratios, and Excel panel outputs.
---

# Chinese Annual Report Text Analysis

Use `scripts/analyze_annual_reports.py` for reproducible Chinese annual-report dictionary analysis.

## Inputs

Ask only for missing paths: an annual-report folder or Excel/CSV file; a target dictionary (required); optional stopwords; optional word-protection dictionary; and optional output path.

Supported text files are `.txt`, `.csv`, `.xlsx`, and `.xls`. Folder mode scans TXT files and extracts the first four-digit year from each filename. Spreadsheet mode requires a text column named `text`, `content`, `正文`, or `文本`; company and year columns are optional.

## Workflow

Clean text, split sentences on the original text, load the word-protection dictionary into jieba, tokenize with jieba, remove stopwords and invalid tokens, match target terms, calculate word and sentence metrics, and export Excel. The protection dictionary is used only to prevent incorrect segmentation; the target dictionary is used only for matching and counting.

## Metric definitions

- `total_words`: valid tokens after stopword removal.
- `target_words`: total target-term occurrences, counting repeats.
- `log_target_words`: `log(1 + target_words)`.
- `target_word_ratio`: `target_words / total_words`.
- `total_sentences`: non-empty sentences from original text.
- `target_sentences`: sentences containing at least one target term; multiple terms in one sentence count once.
- `log_target_sentences`: `log(1 + target_sentences)`.
- `target_sentence_ratio`: `target_sentences / total_sentences`.

Record `status` and `error_message` for failures. Do not change denominator or log definitions without documenting the requested alternative.

## Command template

```powershell
python scripts/analyze_annual_reports.py `
  --input "annual-report-folder-or-file" `
  --target-dict "target-dictionary.txt" `
  --stopwords "stopwords.txt" `
  --protect-dict "word-protection-dictionary.txt" `
  --output "text_analysis_results.xlsx"
```
