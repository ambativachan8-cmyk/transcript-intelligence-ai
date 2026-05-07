"""Text cleaning, metadata enrichment, and call-type inference."""

from __future__ import annotations

import re
from collections import Counter
from typing import Iterable

import pandas as pd


SUPPORT_PATTERNS = [
    r"\bsupport case\b",
    r"\bticket\b",
    r"\bcase #",
    r"\bissue\b",
    r"\bnot working\b",
    r"\berror\b",
    r"\bbug\b",
    r"\bescalat",
]
INTERNAL_PATTERNS = [
    r"\binternal\b",
    r"\bstandup\b",
    r"\bsprint\b",
    r"\broadmap\b",
    r"\bplanning\b",
    r"\blaunch readiness\b",
    r"\bpostmortem\b",
    r"\barchitecture\b",
]
EXTERNAL_PATTERNS = [
    r"\brenewal\b",
    r"\bq[1-4]\b",
    r"\bcontract\b",
    r"\badoption\b",
    r"\baccount\b",
    r"\bbusiness review\b",
    r"\bcompetitive\b",
]

KEYWORD_GROUPS = {
    "issue_keywords": [
        "bug",
        "outage",
        "error",
        "failure",
        "latency",
        "slow",
        "broken",
        "ticket",
        "sla",
        "downtime",
        "missing",
    ],
    "action_keywords": [
        "follow up",
        "send",
        "prepare",
        "review",
        "schedule",
        "deploy",
        "investigate",
        "document",
        "escalate",
        "owner",
    ],
    "decision_keywords": [
        "decided",
        "agreed",
        "approved",
        "aligned",
        "commit",
        "priority",
        "timeline",
        "roadmap",
        "defer",
    ],
}


def clean_text(text: str) -> str:
    text = str(text or "")
    text = re.sub(r"\[[0-9.]+s\]\s*", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _contains_any(text: str, patterns: Iterable[str]) -> bool:
    return any(re.search(pattern, text, flags=re.I) for pattern in patterns)


def infer_call_type(row: pd.Series) -> str:
    title_text = f"{row.get('title', '')} {row.get('summary', '')} {' '.join(row.get('provided_topics', []) or [])}".lower()
    external_domains = row.get("external_domains", [])
    has_customer = bool(external_domains)
    if _contains_any(title_text, SUPPORT_PATTERNS):
        return "support"
    if not has_customer:
        return "internal"
    if _contains_any(title_text, EXTERNAL_PATTERNS):
        return "external"
    if _contains_any(title_text, INTERNAL_PATTERNS) and not has_customer:
        return "internal"
    return "external" if has_customer else "internal"


def count_keywords(text: str, keywords: list[str]) -> int:
    text_l = str(text).lower()
    return sum(len(re.findall(rf"\b{re.escape(keyword)}\b", text_l)) for keyword in keywords)


def top_terms(text: str, n: int = 10) -> list[str]:
    stop = {
        "the",
        "and",
        "that",
        "for",
        "you",
        "this",
        "with",
        "have",
        "are",
        "was",
        "but",
        "not",
        "from",
        "our",
        "can",
        "will",
        "just",
        "need",
        "about",
        "they",
        "we",
        "aegis",
        "yeah",
        "okay",
        "what",
        "want",
        "right",
        "really",
        "actually",
        "think",
        "there",
        "been",
        "now",
        "like",
        "one",
        "let",
        "we're",
        "you're",
        "they're",
        "would",
        "could",
        "should",
        "going",
        "got",
        "get",
        "also",
        "thanks",
        "thank",
        "sure",
        "yes",
        "no",
    }
    words = re.findall(r"[A-Za-z][A-Za-z\-]{2,}", str(text).lower())
    counts = Counter(w for w in words if w not in stop)
    return [w for w, _ in counts.most_common(n)]


def enrich_transcripts(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["clean_text"] = df["transcript_text"].map(clean_text)
    df["word_count"] = df["clean_text"].str.split().map(len)
    df["char_count"] = df["clean_text"].str.len()
    df["call_type"] = df.apply(infer_call_type, axis=1)
    df["customer_internal_indicator"] = df["external_domains"].map(lambda domains: "customer-facing" if domains else "internal-only")
    df["customer_or_account"] = df["customer_domain"].str.replace(r"\.com$|\.io$|\.ai$", "", regex=True).str.replace("-", " ").str.title()
    for col, keywords in KEYWORD_GROUPS.items():
        df[col] = df["clean_text"].map(lambda text: count_keywords(text, keywords))
    df["top_terms"] = df["clean_text"].map(lambda text: top_terms(text, 12))
    df["action_item_count"] = df["action_items"].map(lambda x: len(x) if isinstance(x, list) else 0)
    df["key_moment_count"] = df["key_moments"].map(lambda x: len(x) if isinstance(x, list) else 0)
    return df
