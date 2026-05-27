# Transcript Intelligence AI

**Portfolio:** [vachanambati.com](https://vachanambati.com)  
**AI Systems:** [vachanambati.com/ai-systems](https://vachanambati.com/ai-systems)  
**Role:** Python pipeline for transcript intelligence, business signal extraction, and leadership-ready summaries.

Transcript Intelligence AI turns messy call transcripts into product, support, sentiment, churn/risk, and leadership insights. It is part of my broader AI systems portfolio, alongside **AI News Intel**, an agentic RAG/document intelligence system that converts source material into evidence-backed answers and decision-ready summaries.

This public repository keeps the code and documentation visible while excluding raw transcript datasets, private records, credentials, and row-level generated outputs.

## Objective

Build an end-to-end pipeline that ingests transcript folders, normalizes the data, categorizes transcripts by business theme, scores sentiment, extracts additional insights, and packages the findings for a 30-minute leadership presentation.

## Why This Connects To My AI Systems Work

Transcript Intelligence follows the same practical pattern behind my broader document-intelligence work:

- ingest messy source material,
- normalize it into usable records,
- retrieve and classify the most important signals,
- generate structured insights for business users,
- keep outputs explainable and reviewable.

The same pattern can be applied to scanned reports, policy notes, trade documents, meeting transcripts, operational records, internal files, financial records, and intelligence dashboards.

## Example Analysis Scope

The original assignment run analyzed a transcript dataset and produced:

- support, external/customer, and internal call segmentation,
- business-theme classification,
- sentiment summaries,
- escalation and churn-risk signals,
- feature-request extraction,
- stakeholder views for product, support, engineering, and leadership.

Raw source transcripts and row-level outputs are intentionally not published in this repo.

## Folder Structure

```text
transcript-intelligence/
  README.md
  requirements.txt
  run_pipeline.py
  build_submission_assets.py
  data/raw/
    README.md
  notebooks/
    excluded from public repo
  src/
    load_data.py
    preprocess.py
    topic_modeling.py
    sentiment.py
    insights.py
    visualization.py
  outputs/
    generated locally; excluded from public repo
  deck/
    generated locally; excluded from public repo
  demo_script.md
```

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## How to Run

```powershell
.\.venv\Scripts\python.exe run_pipeline.py
.\.venv\Scripts\python.exe build_submission_assets.py
```

The default input path is `data/raw/dataset`. This public repository does not include the original raw transcript dataset. To run the pipeline, add your own authorized transcript export locally or pass a different raw folder:

```powershell
.\.venv\Scripts\python.exe run_pipeline.py --raw-dir "path\to\dataset"
```

## Methodology

- **Loading:** Recursively discovers transcript folders and reads `meeting-info.json`, `summary.json`, `transcript.json`, `speakers.json`, `speaker-meta.json`, and `events.json`.
- **Normalization:** Produces one row per transcript with meeting metadata, speaker count, transcript text, customer domain, provided topics, action items, key moments, and confidence metadata.
- **Call-type inference:** Uses title/content cues and email domains to infer support, external/customer, or internal calls when no explicit type is present.
- **Topic/theme categorization:** Uses a hybrid approach: TF-IDF clustering for discovery, provided topic metadata for signal, and business keyword rules for human-readable final themes.
- **Sentiment:** Blends the provided summary sentiment score with a transparent local lexical fallback. No paid API key is required.
- **Additional insights:** Detects escalation risk, feature requests, churn/renewal risk, stakeholder dashboard views, and customer-facing vs internal theme alignment.

## Outputs

Generated locally:

- `outputs/processed_transcripts.csv`: normalized transcript-level dataset.
- `outputs/topic_summary.csv`: theme names, counts, call type distribution, keywords, examples, and business importance.
- `outputs/sentiment_summary.csv`: sentiment by call type with interpretation.
- `outputs/additional_insights.csv`: combined additional insight output.
- `outputs/charts/*.png`: reusable chart assets for deck and demo.
- `deck/Transcript_Intelligence_Presentation.pptx`: leadership presentation.

These files are excluded from the public repo because they can contain source-derived details.

## Privacy And Safety

- No API keys, tokens, `.env` files, private datasets, credentials, or production infrastructure details are published.
- Raw transcripts and row-level output files are excluded from GitHub.
- Use only authorized, non-sensitive data when running the pipeline.
- If sensitive data was ever committed to a public branch, deleting the latest files is not enough; Git history cleanup and credential rotation may still be required.

## Limitations

- The taxonomy is intentionally practical, not final. In production, it should be validated with support, product, sales, and engineering stakeholders.
- Sentiment is context-sensitive; outage calls can include constructive language while still representing serious customer risk.
- The source data includes useful summary-level sentiment and topics; the pipeline uses them transparently but can run with local fallbacks.
- Customer/account names are inferred from email domains when explicit account fields are unavailable.

## Future Improvements

- Add optional LLM-assisted theme labeling and excerpt summarization behind an API-key flag.
- Store transcript embeddings for semantic search and similarity-based issue grouping.
- Add CRM/support integrations for account ownership and renewal date context.
- Implement alerting for high-risk escalation/churn transcripts.
- Add human feedback loops to tune taxonomy, sentiment thresholds, and routing ownership.

## More From My Portfolio

See the full AI systems portfolio at [vachanambati.com](https://vachanambati.com), including my AI News Intel case study and live portfolio experience.
