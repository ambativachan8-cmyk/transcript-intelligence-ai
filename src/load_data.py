"""Load and normalize the provided transcript JSON folder format."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


EXPECTED_FILES = {
    "meeting-info.json",
    "summary.json",
    "speakers.json",
    "speaker-meta.json",
    "events.json",
    "transcript.json",
}


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def discover_transcript_folders(raw_dir: Path) -> list[Path]:
    """Return transcript folders without assuming a flat or perfect structure."""
    raw_dir = Path(raw_dir)
    candidates = []
    for folder in raw_dir.rglob("*"):
        if folder.is_dir() and (folder / "transcript.json").exists():
            candidates.append(folder)
    return sorted(candidates)


def _domain(email: str) -> str | None:
    if isinstance(email, str) and "@" in email:
        return email.split("@", 1)[1].lower()
    return None


def _speaker_turns(transcript: list[dict[str, Any]]) -> str:
    lines = []
    for row in transcript:
        speaker = row.get("speaker_name") or row.get("speakerName") or "Unknown"
        sentence = row.get("sentence") or row.get("text") or ""
        time = row.get("time")
        if sentence:
            prefix = f"[{time:.1f}s] " if isinstance(time, (int, float)) else ""
            lines.append(f"{prefix}{speaker}: {sentence}")
    return "\n".join(lines)


def normalize_transcript_folder(folder: Path) -> dict[str, Any]:
    meeting = read_json(folder / "meeting-info.json", {})
    summary = read_json(folder / "summary.json", {})
    speakers_meta = read_json(folder / "speaker-meta.json", {})
    events = read_json(folder / "events.json", [])
    transcript_obj = read_json(folder / "transcript.json", {})
    transcript = transcript_obj.get("data", []) if isinstance(transcript_obj, dict) else []

    all_emails = meeting.get("allEmails") or meeting.get("invitees") or []
    domains = sorted({d for d in (_domain(e) for e in all_emails) if d})
    external_domains = [d for d in domains if d != "aegiscloud.com"]
    speakers = sorted(
        {
            row.get("speaker_name") or row.get("speakerName")
            for row in transcript
            if row.get("speaker_name") or row.get("speakerName")
        }
    )
    sentences = [str(row.get("sentence", "")).strip() for row in transcript if row.get("sentence")]
    transcript_text = " ".join(sentences)
    speaker_turns = _speaker_turns(transcript)
    average_confidence = [
        row.get("averageConfidence") for row in transcript if isinstance(row.get("averageConfidence"), (int, float))
    ]

    return {
        "transcript_id": meeting.get("meetingId") or summary.get("meetingId") or folder.name,
        "source_folder": f"data/raw/dataset/{folder.name}",
        "title": meeting.get("title", ""),
        "organizer_email": meeting.get("organizerEmail", ""),
        "host": meeting.get("host", ""),
        "start_time": meeting.get("startTime", ""),
        "end_time": meeting.get("endTime", ""),
        "duration_minutes": meeting.get("duration"),
        "email_domains": domains,
        "external_domains": external_domains,
        "customer_domain": external_domains[0] if external_domains else "",
        "all_emails": all_emails,
        "speaker_names": speakers,
        "speaker_count": len(speakers) or len(speakers_meta),
        "event_count": len(events) if isinstance(events, list) else 0,
        "sentence_count": len(transcript),
        "avg_transcript_confidence": sum(average_confidence) / len(average_confidence)
        if average_confidence
        else None,
        "summary": summary.get("summary", ""),
        "action_items": summary.get("actionItems", []),
        "provided_topics": summary.get("topics", []),
        "provided_sentiment": summary.get("overallSentiment", ""),
        "provided_sentiment_score": summary.get("sentimentScore"),
        "key_moments": summary.get("keyMoments", []),
        "transcript_text": transcript_text,
        "speaker_turns": speaker_turns,
    }


def load_transcripts(raw_dir: Path) -> pd.DataFrame:
    folders = discover_transcript_folders(Path(raw_dir))
    records = [normalize_transcript_folder(folder) for folder in folders]
    return pd.DataFrame(records)


def build_manifest(raw_dir: Path) -> pd.DataFrame:
    rows = []
    for folder in discover_transcript_folders(Path(raw_dir)):
        files = sorted(p.name for p in folder.glob("*") if p.is_file())
        rows.append(
            {
                "transcript_id": folder.name,
                "source_folder": f"data/raw/dataset/{folder.name}",
                "file_count": len(files),
                "files": "; ".join(files),
                "missing_expected_files": "; ".join(sorted(EXPECTED_FILES - set(files))),
            }
        )
    return pd.DataFrame(rows)
