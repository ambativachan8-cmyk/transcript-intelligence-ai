"""Chart generation for notebook and deck assets."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


PALETTE = {
    "navy": "#172033",
    "blue": "#2D6CDF",
    "teal": "#20A39E",
    "coral": "#F25F5C",
    "amber": "#F5B841",
    "gray": "#7A869A",
    "light": "#F5F7FA",
}


def _style_ax(ax):
    ax.set_facecolor("white")
    ax.grid(axis="y", color="#E6EAF0", linewidth=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#CCD3DD")
    ax.spines["bottom"].set_color("#CCD3DD")
    ax.tick_params(colors="#364152", labelsize=9)


def save_call_type_chart(df: pd.DataFrame, out: Path) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    counts = df["call_type"].value_counts().reindex(["support", "external", "internal"]).dropna()
    fig, ax = plt.subplots(figsize=(7.2, 4.2), dpi=180)
    counts.plot(kind="bar", ax=ax, color=[PALETTE["coral"], PALETTE["blue"], PALETTE["teal"]])
    _style_ax(ax)
    ax.set_title("Transcript Volume by Call Type", loc="left", fontsize=13, weight="bold", color=PALETTE["navy"])
    ax.set_xlabel("")
    ax.set_ylabel("Transcripts")
    ax.bar_label(ax.containers[0], padding=3, fontsize=9)
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def save_sentiment_distribution(df: pd.DataFrame, out: Path) -> Path:
    pivot = pd.crosstab(df["call_type"], df["sentiment_label"]).reindex(columns=["negative", "neutral", "positive"], fill_value=0)
    colors = [PALETTE["coral"], PALETTE["gray"], PALETTE["teal"]]
    fig, ax = plt.subplots(figsize=(7.8, 4.4), dpi=180)
    pivot.plot(kind="bar", stacked=True, ax=ax, color=colors)
    _style_ax(ax)
    ax.set_title("Sentiment Distribution by Call Type", loc="left", fontsize=13, weight="bold", color=PALETTE["navy"])
    ax.set_xlabel("")
    ax.set_ylabel("Transcripts")
    ax.legend(frameon=False, ncols=3, loc="upper right")
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def save_avg_sentiment(df: pd.DataFrame, out: Path) -> Path:
    avg = df.groupby("call_type")["sentiment_score"].mean().sort_values()
    colors = [PALETTE["coral"] if v < 0 else PALETTE["teal"] for v in avg]
    fig, ax = plt.subplots(figsize=(7.2, 4.2), dpi=180)
    avg.plot(kind="barh", ax=ax, color=colors)
    _style_ax(ax)
    ax.axvline(0, color="#222", linewidth=1)
    ax.set_title("Average Sentiment by Call Type", loc="left", fontsize=13, weight="bold", color=PALETTE["navy"])
    ax.set_xlabel("Sentiment score (-1 to +1)")
    ax.set_ylabel("")
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def save_theme_counts(topic_summary: pd.DataFrame, out: Path) -> Path:
    data = topic_summary.sort_values("transcript_count", ascending=True)
    fig, ax = plt.subplots(figsize=(8.2, 5.0), dpi=180)
    ax.barh(data["theme"], data["transcript_count"], color=PALETTE["blue"])
    _style_ax(ax)
    ax.set_title("Themes Identified", loc="left", fontsize=13, weight="bold", color=PALETTE["navy"])
    ax.set_xlabel("Transcripts")
    ax.set_ylabel("")
    for i, v in enumerate(data["transcript_count"]):
        ax.text(v + 0.2, i, str(v), va="center", fontsize=8, color=PALETTE["navy"])
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def save_sentiment_by_theme(df: pd.DataFrame, out: Path) -> Path:
    data = df.groupby("theme")["sentiment_score"].mean().sort_values()
    colors = [PALETTE["coral"] if v < 0 else PALETTE["teal"] for v in data]
    fig, ax = plt.subplots(figsize=(8.4, 5.0), dpi=180)
    data.plot(kind="barh", ax=ax, color=colors)
    _style_ax(ax)
    ax.axvline(0, color="#222", linewidth=1)
    ax.set_title("Average Sentiment by Theme", loc="left", fontsize=13, weight="bold", color=PALETTE["navy"])
    ax.set_xlabel("Sentiment score (-1 to +1)")
    ax.set_ylabel("")
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def save_heatmap(df: pd.DataFrame, out: Path) -> Path:
    pivot = df.pivot_table(index="theme", columns="call_type", values="sentiment_score", aggfunc="mean")
    fig, ax = plt.subplots(figsize=(7.8, 5.2), dpi=180)
    im = ax.imshow(pivot.fillna(0), cmap="RdYlGn", vmin=-0.7, vmax=0.7)
    ax.set_xticks(range(len(pivot.columns)), pivot.columns)
    ax.set_yticks(range(len(pivot.index)), pivot.index)
    ax.set_title("Sentiment Heatmap: Theme x Call Type", loc="left", fontsize=13, weight="bold", color=PALETTE["navy"])
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            val = pivot.iloc[i, j]
            label = "" if pd.isna(val) else f"{val:.2f}"
            ax.text(j, i, label, ha="center", va="center", fontsize=8, color="#172033")
    fig.colorbar(im, ax=ax, fraction=0.035, pad=0.02)
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def generate_charts(df: pd.DataFrame, topic_summary: pd.DataFrame, charts_dir: Path) -> dict[str, Path]:
    charts_dir.mkdir(parents=True, exist_ok=True)
    charts = {
        "call_type_breakdown": save_call_type_chart(df, charts_dir / "call_type_breakdown.png"),
        "sentiment_distribution": save_sentiment_distribution(df, charts_dir / "sentiment_distribution_by_call_type.png"),
        "avg_sentiment": save_avg_sentiment(df, charts_dir / "average_sentiment_by_call_type.png"),
        "theme_counts": save_theme_counts(topic_summary, charts_dir / "theme_counts.png"),
        "sentiment_by_theme": save_sentiment_by_theme(df, charts_dir / "sentiment_by_theme.png"),
        "theme_calltype_heatmap": save_heatmap(df, charts_dir / "theme_calltype_sentiment_heatmap.png"),
    }
    return charts
