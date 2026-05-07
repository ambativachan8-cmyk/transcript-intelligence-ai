"""Hybrid topic discovery and business theme labeling."""

from __future__ import annotations

from collections import Counter

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer


THEME_RULES = {
    "Product bugs and technical reliability": [
        "outage",
        "bug",
        "latency",
        "failure",
        "pipeline",
        "backup",
        "performance",
        "downtime",
        "monitoring",
        "agent",
    ],
    "Renewal, pricing, and account risk": [
        "renewal",
        "pricing",
        "contract",
        "billing",
        "overage",
        "competitive",
        "competitor",
        "sla",
        "budget",
    ],
    "Compliance and audit readiness": [
        "soc",
        "iso",
        "hipaa",
        "audit",
        "compliance",
        "framework",
        "evidence",
        "controls",
    ],
    "Feature requests and product feedback": [
        "feature",
        "request",
        "dashboard",
        "integration",
        "api",
        "automation",
        "workflow",
        "roadmap",
    ],
    "Onboarding, adoption, and enablement": [
        "onboarding",
        "adoption",
        "training",
        "documentation",
        "rollout",
        "implementation",
        "enablement",
    ],
    "Internal engineering planning": [
        "standup",
        "sprint",
        "planning",
        "architecture",
        "launch",
        "refactor",
        "roadmap",
        "engineering",
    ],
    "Escalations and customer communication": [
        "escalation",
        "customer communication",
        "support ticket",
        "postmortem",
        "incident",
        "status update",
        "priority",
    ],
}

THEME_DESCRIPTIONS = {
    "Product bugs and technical reliability": "Reliability, outage, latency, backup, and technical defect discussions that create support burden and adoption risk.",
    "Renewal, pricing, and account risk": "Commercial conversations where contract value, renewal confidence, pricing, competitors, or SLA exposure affect revenue.",
    "Compliance and audit readiness": "Audit, evidence collection, control mapping, and regulated-customer use cases around Comply and security posture.",
    "Feature requests and product feedback": "Customer asks for missing capabilities, integrations, dashboarding, automation, or roadmap improvements.",
    "Onboarding, adoption, and enablement": "Implementation friction, training needs, documentation gaps, rollout readiness, and user adoption blockers.",
    "Internal engineering planning": "Internal team coordination around roadmap, launch readiness, technical remediation, and engineering execution.",
    "Escalations and customer communication": "Urgent cross-functional response, executive communication, incident handling, and ticket/customer escalation themes.",
}

KEYWORD_NOISE = {
    "aegis",
    "aegiscloud",
    "customer",
    "customers",
    "team",
    "teams",
    "support",
    "internal",
    "external",
    "post",
    "mortem",
    "post mortem",
    "good",
    "work",
    "works",
    "working",
    "your",
    "their",
    "there",
    "what",
    "want",
    "need",
    "like",
    "case",
    "request",
    "requests",
    "call",
    "meeting",
    "review",
    "summit",
    "trust",
    "summit trust",
    "detect",
    "comply",
    "comply v2",
}


def clean_keyword(keyword: str) -> str | None:
    keyword = " ".join(str(keyword).lower().replace("&", "and").split())
    replacements = {
        "soc": "soc 2",
        "api": "api",
        "sla": "sla",
        "mfa": "mfa",
        "hipaa": "hipaa",
    }
    keyword = replacements.get(keyword, keyword)
    if not keyword or keyword in KEYWORD_NOISE or len(keyword) < 3:
        return None
    if any(part in KEYWORD_NOISE for part in keyword.split()) and len(keyword.split()) == 1:
        return None
    return keyword


def _theme_score(text: str, keywords: list[str]) -> int:
    text_l = str(text).lower()
    return sum(text_l.count(k.lower()) for k in keywords)


def assign_business_theme(row: pd.Series) -> str:
    text = " ".join(
        [
            str(row.get("title", "")),
            str(row.get("summary", "")),
            " ".join(row.get("provided_topics", []) or []),
            str(row.get("clean_text", ""))[:2500],
        ]
    )
    scores = {theme: _theme_score(text, words) for theme, words in THEME_RULES.items()}
    best, score = max(scores.items(), key=lambda kv: kv[1])
    if score > 0:
        return best
    return "General customer and operating intelligence"


def fit_tfidf_clusters(df: pd.DataFrame, n_clusters: int = 7) -> pd.DataFrame:
    df = df.copy()
    docs = (
        df["title"].fillna("")
        + " "
        + df["summary"].fillna("")
        + " "
        + df["provided_topics"].map(lambda x: " ".join(x) if isinstance(x, list) else "")
    )
    n_clusters = min(n_clusters, max(2, len(df) // 8))
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=2, max_features=600)
    matrix = vectorizer.fit_transform(docs)
    model = KMeans(n_clusters=n_clusters, random_state=42, n_init="auto")
    df["tfidf_cluster"] = model.fit_predict(matrix)
    terms = vectorizer.get_feature_names_out()
    cluster_keywords = {}
    centers = model.cluster_centers_
    for cluster_id, center in enumerate(centers):
        top_idx = center.argsort()[-10:][::-1]
        cluster_keywords[int(cluster_id)] = [terms[i] for i in top_idx]
    df["cluster_keywords"] = df["tfidf_cluster"].map(cluster_keywords)
    return df


def apply_topics(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = fit_tfidf_clusters(df)
    df["theme"] = df.apply(assign_business_theme, axis=1)
    df["theme_description"] = df["theme"].map(THEME_DESCRIPTIONS).fillna(
        "Useful but lower-frequency transcript pattern worth monitoring as the corpus grows."
    )
    summary_rows = []
    for theme, g in df.groupby("theme", dropna=False):
        call_dist = g["call_type"].value_counts().to_dict()
        keywords = Counter()
        theme_text = " ".join(
            (
                g["title"].fillna("")
                + " "
                + g["summary"].fillna("")
                + " "
                + g["provided_topics"].map(lambda x: " ".join(x) if isinstance(x, list) else "")
            ).tolist()
        ).lower()
        for term in THEME_RULES.get(theme, []):
            cleaned = clean_keyword(term)
            if cleaned and term.lower() in theme_text:
                keywords.update([cleaned] * 3)
        for topics in g["provided_topics"]:
            if isinstance(topics, list):
                for topic in topics:
                    cleaned = clean_keyword(topic)
                    if cleaned:
                        keywords.update([cleaned])
        for terms in g["cluster_keywords"]:
            if isinstance(terms, list):
                for term in terms[:8]:
                    cleaned = clean_keyword(term)
                    if cleaned:
                        keywords.update([cleaned])
        examples = []
        for _, row in g.sort_values("sentiment_score").head(3).iterrows():
            excerpt = str(row["summary"] or row["clean_text"])[:240].replace("\n", " ")
            examples.append(f"{row['transcript_id']}: {excerpt}")
        summary_rows.append(
            {
                "theme": theme,
                "description": g["theme_description"].iloc[0],
                "transcript_count": len(g),
                "dominant_call_type": g["call_type"].value_counts().idxmax(),
                "call_type_distribution": call_dist,
                "avg_sentiment_score": round(float(g["sentiment_score"].mean()), 3),
                "representative_keywords": ", ".join(k for k, _ in keywords.most_common(12)),
                "example_transcripts": " | ".join(examples),
                "business_importance": business_importance(theme),
            }
        )
    topic_summary = pd.DataFrame(summary_rows).sort_values(["transcript_count", "theme"], ascending=[False, True])
    return df, topic_summary


def business_importance(theme: str) -> str:
    return {
        "Product bugs and technical reliability": "Turns repeated defects into prioritizable engineering work and reduces support drag.",
        "Renewal, pricing, and account risk": "Highlights revenue risk before the renewal motion becomes reactive.",
        "Compliance and audit readiness": "Connects product value to regulated buyer urgency and audit deadlines.",
        "Feature requests and product feedback": "Converts customer language into roadmap evidence for PMs.",
        "Onboarding, adoption, and enablement": "Shows where customers need enablement before low adoption becomes churn.",
        "Internal engineering planning": "Reveals whether engineering execution is aligned with customer-facing pain.",
        "Escalations and customer communication": "Creates an early warning system for incidents and executive-sensitive accounts.",
    }.get(theme, "Adds searchable structure to long-form transcripts.")
