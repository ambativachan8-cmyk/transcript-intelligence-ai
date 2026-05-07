# Transcript Intelligence

This project is a take-home prototype for a B2B Enterprise SaaS product called **Transcript Intelligence**. It turns raw call transcripts into product, support, account, and engineering insights.

## Objective

Build an end-to-end pipeline that ingests transcript folders, normalizes the data, categorizes transcripts by business theme, scores sentiment, extracts additional insights, and packages the findings for a 30-minute leadership presentation.

## Key Findings

- Processed **100 transcripts**: 50 support, 35 external/customer, and 15 internal calls.
- Identified **6 major themes**. The largest theme was **Product bugs and technical reliability** with **44 transcripts**.
- Support calls carried the clearest risk signal: **19 of 50 support transcripts** were negative, concentrated around technical reliability, outage, SLA, and escalation language.
- External calls were more positive overall, but renewal/pricing conversations still surfaced trust, outage, and competitive risk signals.
- Additional insight layers identify escalation risk, feature requests, churn/renewal risk, stakeholder-specific views, and product-engineering alignment gaps.

## Folder Structure

```text
transcript-intelligence/
  README.md
  requirements.txt
  run_pipeline.py
  build_submission_assets.py
  data/
    raw/dataset/
    processed/
  notebooks/
    01_transcript_intelligence_analysis.ipynb
  src/
    load_data.py
    preprocess.py
    topic_modeling.py
    sentiment.py
    insights.py
    visualization.py
  outputs/
    processed_transcripts.csv
    topic_summary.csv
    sentiment_summary.csv
    additional_insights.csv
    charts/
    slide_assets/
  deck/
    Transcript_Intelligence_Presentation.pptx
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

The default input path is `data/raw/dataset`, copied from the provided assignment folder. You can also pass a different raw folder:

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

- `outputs/processed_transcripts.csv`: normalized transcript-level dataset.
- `outputs/topic_summary.csv`: theme names, counts, call type distribution, keywords, examples, and business importance.
- `outputs/sentiment_summary.csv`: sentiment by call type with interpretation.
- `outputs/additional_insights.csv`: combined additional insight output.
- `outputs/charts/*.png`: reusable chart assets for deck and demo.
- `deck/Transcript_Intelligence_Presentation.pptx`: 20-slide leadership presentation.
- `notebooks/01_transcript_intelligence_analysis.ipynb`: readable analysis notebook.

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
