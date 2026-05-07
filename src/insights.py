"""Business insight extraction for Transcript Intelligence."""

from __future__ import annotations

import re
from collections import Counter, defaultdict

import pandas as pd


ESCALATION_TERMS = [
    "urgent",
    "escalat",
    "sla",
    "breach",
    "outage",
    "downtime",
    "priority 1",
    "priority 2",
    "executive",
    "critical",
    "blocked",
    "unresolved",
    "postmortem",
]
FEATURE_TERMS = [
    "dashboard",
    "integration",
    "api",
    "automation",
    "workflow",
    "report",
    "export",
    "custom",
]

CAPABILITY_PATTERNS = {
    "dashboarding and analytics": [
        r"\bdashboard(s)?\b",
        r"\banalytics\b",
        r"\bvisibility\b",
        r"\breporting dashboard\b",
    ],
    "integration and API reliability": [
        r"\bintegration(s)?\b",
        r"\bapi\b",
        r"\bwebhook(s)?\b",
        r"\bconnector(s)?\b",
        r"\bsync\b",
        r"\bcrm sync\b",
    ],
    "automation and workflow": [
        r"\bautomation\b",
        r"\bworkflow(s)?\b",
        r"\bauto[- ]?remediation\b",
        r"\bautomated\b",
    ],
    "export and reporting": [
        r"\bexport\b",
        r"\breport(s|ing)?\b",
        r"\bcsv\b",
        r"\bpdf\b",
        r"\bscheduled report(s)?\b",
    ],
    "granular restore and backup controls": [
        r"\bgranular restore\b",
        r"\bfile[- ]level restore\b",
        r"\bbackup\b",
        r"\bsnapshot\b",
        r"\brto\b",
    ],
    "authentication and admin controls": [
        r"\bauthentication\b",
        r"\bmfa\b",
        r"\bsso\b",
        r"\badmin control(s)?\b",
        r"\baccess control(s)?\b",
        r"\bdeprovisioning\b",
    ],
    "audit logs and data retention": [
        r"\baudit log(s)?\b",
        r"\blog retention\b",
        r"\bdata retention\b",
        r"\bevidence\b",
        r"\bcompliance evidence\b",
    ],
    "alerting and escalation": [
        r"\balert(s|ing)?\b",
        r"\bescalation\b",
        r"\bnotification(s)?\b",
        r"\bincident\b",
        r"\bpagerduty\b",
    ],
    "billing and pricing visibility": [
        r"\bbilling\b",
        r"\bpricing\b",
        r"\boverage\b",
        r"\binvoice\b",
        r"\bseat count\b",
    ],
    "onboarding and documentation": [
        r"\bonboarding\b",
        r"\bdocumentation\b",
        r"\btraining\b",
        r"\benablement\b",
        r"\bimplementation\b",
    ],
}
CHURN_TERMS = [
    "renewal",
    "competitor",
    "cancel",
    "churn",
    "pricing",
    "budget",
    "contract",
    "trust",
    "confidence",
    "risk",
    "sla",
    "procurement",
]


def _count_hits(text: str, terms: list[str]) -> tuple[int, list[str]]:
    text_l = str(text).lower()
    hits = [term for term in terms if term in text_l]
    return len(hits), hits


def _owner_for(row: pd.Series, reason_terms: list[str]) -> str:
    reason = " ".join(reason_terms).lower()
    if any(x in reason for x in ["renewal", "pricing", "contract", "competitor", "budget"]):
        return "account manager"
    if any(x in reason for x in ["bug", "outage", "api", "latency", "failure", "sla"]):
        return "engineering + support"
    if any(x in reason for x in ["feature", "dashboard", "automation", "workflow"]):
        return "product manager"
    return "support leader"


def escalation_risks(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in df.iterrows():
        hits, terms = _count_hits(row["clean_text"] + " " + row["summary"], ESCALATION_TERMS)
        risk = hits + int(row["sentiment_score"] < -0.25) * 2 + int(row["issue_keywords"] >= 4)
        if risk >= 3:
            rows.append(
                {
                    "insight_type": "Escalation Risk Detection",
                    "transcript_id": row["transcript_id"],
                    "call_type": row["call_type"],
                    "theme": row["theme"],
                    "risk_score": risk,
                    "reason": ", ".join(terms[:8]) or "Negative sentiment and repeated issue language",
                    "suggested_owner": _owner_for(row, terms),
                    "example_excerpt": str(row["summary"])[:260],
                    "why_it_matters": "Proactively routes urgent customer pain before it becomes churn, SLA exposure, or executive escalation.",
                }
            )
    return pd.DataFrame(rows).sort_values("risk_score", ascending=False)


def feature_requests(df: pd.DataFrame) -> pd.DataFrame:
    request_counter = Counter()
    examples: dict[str, list[str]] = defaultdict(list)
    call_types: dict[str, Counter] = defaultdict(Counter)
    for _, row in df.iterrows():
        text = f"{row['clean_text']} {row['summary']}"
        for capability, patterns in CAPABILITY_PATTERNS.items():
            matched = [p for p in patterns if re.search(p, text, flags=re.I)]
            if not matched:
                continue
            request_counter[capability] += 1
            call_types[capability][row["call_type"]] += 1
            if len(examples[capability]) < 3:
                excerpt = str(row["summary"])[:240]
                examples[capability].append(f"{row['transcript_id']}: {excerpt}")
    rows = []
    for term, count in request_counter.most_common(15):
        rows.append(
            {
                "insight_type": "Feature Request Mining",
                "requested_capability": term,
                "frequency": count,
                "impacted_call_types": dict(call_types[term]),
                "example_excerpts": " | ".join(examples[term]),
                "why_it_matters": "Gives PMs roadmap evidence grounded in customer language rather than anecdote.",
            }
        )
    return pd.DataFrame(rows)


def churn_risks(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in df[df["customer_internal_indicator"] == "customer-facing"].iterrows():
        hits, terms = _count_hits(row["clean_text"] + " " + row["summary"], CHURN_TERMS)
        score = hits + int(row["sentiment_score"] < -0.25) * 3 + int(row["theme"] == "Renewal, pricing, and account risk") * 2
        if score >= 4:
            rows.append(
                {
                    "insight_type": "Churn / Renewal Risk Signals",
                    "transcript_id": row["transcript_id"],
                    "customer_or_account": row["customer_or_account"],
                    "call_type": row["call_type"],
                    "risk_score": score,
                    "risk_terms": ", ".join(terms[:8]),
                    "sentiment_label": row["sentiment_label"],
                    "suggested_action": "CSM/AM should review renewal plan, acknowledge pain points, and align support/product follow-through.",
                    "example_excerpt": str(row["summary"])[:260],
                }
            )
    return pd.DataFrame(rows).sort_values("risk_score", ascending=False)


def stakeholder_views(df: pd.DataFrame, topic_summary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    role_map = {
        "Support leader": ["support", "Product bugs and technical reliability", "Escalations and customer communication"],
        "Product manager": ["Feature requests and product feedback", "Onboarding, adoption, and enablement", "Compliance and audit readiness"],
        "Sales / account manager": ["external", "Renewal, pricing, and account risk"],
        "Engineering lead": ["internal", "Product bugs and technical reliability", "Internal engineering planning"],
    }
    for stakeholder, filters in role_map.items():
        mask = df["call_type"].isin(filters) | df["theme"].isin(filters)
        view = df[mask]
        if view.empty:
            view = df
        top_theme = view["theme"].value_counts().idxmax()
        negative_count = int((view["sentiment_label"] == "negative").sum())
        rows.append(
            {
                "stakeholder": stakeholder,
                "primary_question": {
                    "Support leader": "Where are customers getting stuck and which issues need escalation?",
                    "Product manager": "What are customers asking for and which pain points should shape roadmap priority?",
                    "Sales / account manager": "Which accounts show renewal risk or expansion opportunity?",
                    "Engineering lead": "Which technical problems recur and how do they map to internal execution?",
                }[stakeholder],
                "top_relevant_theme": top_theme,
                "relevant_transcripts": len(view),
                "negative_transcripts": negative_count,
                "recommended_action": {
                    "Support leader": "Create a weekly negative-theme and escalation-risk review.",
                    "Product manager": "Validate top requests with PM taxonomy and attach examples to roadmap candidates.",
                    "Sales / account manager": "Trigger proactive account plays for high-risk renewal conversations.",
                    "Engineering lead": "Tie incident and bug clusters to reliability roadmap ownership.",
                }[stakeholder],
            }
        )
    return pd.DataFrame(rows)


def product_engineering_gap(df: pd.DataFrame) -> pd.DataFrame:
    external = df[df["call_type"].isin(["support", "external"])]["theme"].value_counts()
    internal = df[df["call_type"] == "internal"]["theme"].value_counts()
    rows = []
    for theme, ext_count in external.items():
        int_count = int(internal.get(theme, 0))
        rows.append(
            {
                "customer_facing_theme": theme,
                "customer_facing_count": int(ext_count),
                "internal_discussion_count": int_count,
                "alignment_status": "aligned" if int_count > 0 else "gap to investigate",
                "why_it_matters": "Shows whether internal planning appears to match repeated customer-facing transcript pain.",
            }
        )
    return pd.DataFrame(rows).sort_values(["alignment_status", "customer_facing_count"], ascending=[False, False])


def build_additional_insights(df: pd.DataFrame, topic_summary: pd.DataFrame) -> dict[str, pd.DataFrame]:
    return {
        "escalation_risks": escalation_risks(df),
        "feature_requests": feature_requests(df),
        "churn_risks": churn_risks(df),
        "stakeholder_views": stakeholder_views(df, topic_summary),
        "product_engineering_gap": product_engineering_gap(df),
    }
