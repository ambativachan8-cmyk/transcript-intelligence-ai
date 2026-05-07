"""Run the Transcript Intelligence pipeline end-to-end."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from src.insights import build_additional_insights
from src.load_data import build_manifest, load_transcripts
from src.preprocess import enrich_transcripts
from src.sentiment import score_sentiment
from src.topic_modeling import apply_topics
from src.visualization import generate_charts


ROOT = Path(__file__).resolve().parent
RAW_DIR = ROOT / "data" / "raw" / "dataset"
OUTPUTS = ROOT / "outputs"
PROCESSED = ROOT / "data" / "processed"


def rel_path(path: Path) -> str:
    """Return a project-relative path for portable outputs."""
    try:
        return str(Path(path).resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(Path(path)).replace("\\", "/")


def json_ready(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in df.columns:
        if df[col].map(lambda x: isinstance(x, (list, dict))).any():
            df[col] = df[col].map(lambda x: json.dumps(x, ensure_ascii=False) if isinstance(x, (list, dict)) else x)
    return df


def build_sentiment_summary(df: pd.DataFrame) -> pd.DataFrame:
    by_call = df.groupby("call_type").agg(
        transcripts=("transcript_id", "count"),
        avg_sentiment_score=("sentiment_score", "mean"),
        negative_transcripts=("sentiment_label", lambda s: int((s == "negative").sum())),
        neutral_transcripts=("sentiment_label", lambda s: int((s == "neutral").sum())),
        positive_transcripts=("sentiment_label", lambda s: int((s == "positive").sum())),
        avg_word_count=("word_count", "mean"),
    )
    by_call["interpretation"] = by_call.index.map(
        {
            "support": "Support sentiment reflects immediate product friction and should feed issue triage.",
            "external": "External sentiment is a leading indicator for renewal confidence, adoption, and expansion potential.",
            "internal": "Internal sentiment shows team confidence and urgency around execution, incidents, and launch work.",
        }
    )
    return by_call.reset_index().round(3)


def run(raw_dir: Path = RAW_DIR, outputs_dir: Path = OUTPUTS) -> dict[str, Path]:
    outputs_dir.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    (outputs_dir / "charts").mkdir(parents=True, exist_ok=True)
    (outputs_dir / "slide_assets").mkdir(parents=True, exist_ok=True)

    manifest = build_manifest(raw_dir)
    df = load_transcripts(raw_dir)
    df = enrich_transcripts(df)
    df = score_sentiment(df)
    df, topic_summary = apply_topics(df)
    sentiment_summary = build_sentiment_summary(df)
    insights = build_additional_insights(df, topic_summary)
    charts = generate_charts(df, topic_summary, outputs_dir / "charts")

    processed_path = outputs_dir / "processed_transcripts.csv"
    topic_path = outputs_dir / "topic_summary.csv"
    sentiment_path = outputs_dir / "sentiment_summary.csv"
    manifest_path = outputs_dir / "transcript_manifest.csv"
    json_ready(df).to_csv(processed_path, index=False, encoding="utf-8")
    json_ready(df).to_csv(PROCESSED / "processed_transcripts.csv", index=False, encoding="utf-8")
    json_ready(topic_summary).to_csv(topic_path, index=False, encoding="utf-8")
    json_ready(sentiment_summary).to_csv(sentiment_path, index=False, encoding="utf-8")
    manifest.to_csv(manifest_path, index=False, encoding="utf-8")

    insight_frames = []
    for name, frame in insights.items():
        path = outputs_dir / f"{name}.csv"
        json_ready(frame).to_csv(path, index=False, encoding="utf-8")
        if not frame.empty:
            copy = frame.copy()
            copy.insert(0, "insight_table", name)
            insight_frames.append(copy)
    additional = pd.concat(insight_frames, ignore_index=True, sort=False) if insight_frames else pd.DataFrame()
    additional_path = outputs_dir / "additional_insights.csv"
    json_ready(additional).to_csv(additional_path, index=False, encoding="utf-8")

    metadata = {
        "raw_dir": rel_path(raw_dir),
        "transcripts": int(len(df)),
        "themes": int(topic_summary["theme"].nunique()),
        "call_type_counts": df["call_type"].value_counts().to_dict(),
        "sentiment_counts": df["sentiment_label"].value_counts().to_dict(),
        "chart_paths": {k: rel_path(v) for k, v in charts.items()},
    }
    metadata_path = outputs_dir / "run_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    return {
        "processed": processed_path,
        "topics": topic_path,
        "sentiment": sentiment_path,
        "manifest": manifest_path,
        "additional_insights": additional_path,
        "metadata": metadata_path,
        **charts,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Transcript Intelligence analysis.")
    parser.add_argument("--raw-dir", type=Path, default=RAW_DIR, help="Folder containing transcript JSON folders.")
    parser.add_argument("--outputs-dir", type=Path, default=OUTPUTS, help="Folder for generated outputs.")
    args = parser.parse_args()
    artifacts = run(args.raw_dir, args.outputs_dir)
    print("Generated artifacts:")
    for name, path in artifacts.items():
        print(f"- {name}: {path}")


if __name__ == "__main__":
    main()
