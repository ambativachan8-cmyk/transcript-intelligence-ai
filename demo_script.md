# Demo Script: Transcript Intelligence

## 1. Introduction

Today I’m walking through Transcript Intelligence, a prototype that turns call transcripts into actionable product, support, account, and engineering insights. The goal is not just NLP output; it is a leadership-ready workflow that helps teams decide what to fix, who should act, and where customer risk is building.

## 2. Folder Structure

I’ll start in the `transcript-intelligence` project folder. The raw JSON transcript folders live in `data/raw/dataset`. The implementation is modular under `src`, with a single `run_pipeline.py` entrypoint. Outputs are written to `outputs`, charts are in `outputs/charts`, and the presentation is in `deck`.

## 3. Run the Pipeline

I’ll run:

```powershell
.\.venv\Scripts\python.exe run_pipeline.py
```

This loads the transcript folders, normalizes one row per transcript, infers call type, computes metadata, assigns themes, scores sentiment, extracts additional insights, and saves the artifacts.

## 4. Processed Transcript Output

Next I’ll open `outputs/processed_transcripts.csv`. The dataset has **100 normalized transcripts** with transcript ID, title, customer domain, call type, speaker count, word count, sentiment score, theme, keywords, and summary fields.

## 5. Topic Categories

Then I’ll show `outputs/topic_summary.csv`. The strongest theme is **Product bugs and technical reliability**, with **44 transcripts**. The theme summary includes call type distribution, representative keywords, example transcript IDs, and business importance.

## 6. Sentiment Analysis

I’ll show the sentiment charts. The key pattern is that support calls are the most negative, with **19 negative support transcripts**. That suggests product reliability and support friction are not just operational issues; they are adoption and renewal risks.

## 7. Additional Insights

I’ll show three insight layers:

- Escalation risk detection: flags urgent language, SLA concerns, outage references, and unresolved issues.
- Feature request mining: extracts repeated asks around dashboards, integrations, automation, reports, API, and workflow needs.
- Churn and renewal risk: combines sentiment, renewal language, pricing objections, competitor mentions, and unresolved support issues.

## 8. Recommendations

The practical recommendations are to prioritize the top negative reliability themes, operationalize escalation alerts, route feature requests into roadmap review, and create role-specific dashboards for support, product, account, and engineering leaders.

## 9. Production Vision

In production, this becomes a searchable transcript intelligence layer with batch ingestion first, then real-time risk alerts. It can integrate with CRM, support systems, and product planning tools so that transcript insights move directly into team workflows.
