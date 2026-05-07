"""Local sentiment scoring that runs without paid APIs."""

from __future__ import annotations

import re

import pandas as pd


POSITIVE_TERMS = {
    "good",
    "great",
    "excellent",
    "positive",
    "helpful",
    "happy",
    "confident",
    "solid",
    "clear",
    "resolved",
    "appreciate",
    "opportunity",
    "expand",
    "expansion",
    "interested",
    "success",
    "improved",
    "ready",
    "aligned",
}
NEGATIVE_TERMS = {
    "bad",
    "broken",
    "concern",
    "concerns",
    "issue",
    "problem",
    "failure",
    "outage",
    "downtime",
    "risk",
    "breach",
    "frustrated",
    "angry",
    "unhappy",
    "slow",
    "missed",
    "delayed",
    "churn",
    "cancel",
    "competitor",
    "escalation",
}


def lexical_score(text: str) -> tuple[float, list[str]]:
    words = re.findall(r"[a-z][a-z\-]+", str(text).lower())
    if not words:
        return 0.0, []
    positive = [w for w in words if w in POSITIVE_TERMS]
    negative = [w for w in words if w in NEGATIVE_TERMS]
    raw = (len(positive) - len(negative)) / max(8, len(positive) + len(negative))
    score = max(-1.0, min(1.0, raw))
    phrases = list(dict.fromkeys(positive[:4] + negative[:4]))
    return score, phrases


def normalize_provided_score(score: float | int | None) -> float | None:
    if score is None:
        return None
    try:
        return max(-1.0, min(1.0, (float(score) - 3.0) / 2.0))
    except (TypeError, ValueError):
        return None


def sentiment_label(score: float) -> str:
    if score <= -0.25:
        return "negative"
    if score >= 0.25:
        return "positive"
    return "neutral"


def score_sentiment(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    lexical = df["clean_text"].map(lexical_score)
    df["lexical_sentiment_score"] = lexical.map(lambda x: x[0])
    df["sentiment_key_phrases"] = lexical.map(lambda x: x[1])
    df["provided_sentiment_norm"] = df["provided_sentiment_score"].map(normalize_provided_score)
    # The source data includes summary-level sentiment; blend it with a transparent local lexical score.
    df["sentiment_score"] = df.apply(
        lambda r: 0.7 * r["provided_sentiment_norm"] + 0.3 * r["lexical_sentiment_score"]
        if pd.notna(r["provided_sentiment_norm"])
        else r["lexical_sentiment_score"],
        axis=1,
    )
    df["sentiment_label"] = df["sentiment_score"].map(sentiment_label)
    df["sentiment_strength"] = df["sentiment_score"].abs().round(3)
    return df
