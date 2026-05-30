"""SRT subtitle formatting and file generation."""

import re


def format_srt_timestamp(ms: int) -> str:
    """Convert milliseconds to SRT timestamp format HH:MM:SS,mmm."""
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1_000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def clean_segment_text(text: str) -> str:
    """Clean up whitespace around punctuation in a subtitle segment."""
    text = re.sub(r"\s+([.,!?:;…])", r"\1", text)
    text = re.sub(r"([.,!?:;…])([A-Za-z])", r"\1 \2", text)
    text = re.sub(r"\s+' \s*", "'", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def write_srt(
    segments: list[tuple[str, int, int]],
    output_path: str,
) -> str:
    """Write segments to an SRT file.

    Args:
        segments: List of (text, start_ms, end_ms) tuples.
        output_path: Destination file path.

    Returns:
        The output_path.
    """
    with open(output_path, "w", encoding="utf-8") as f:
        for idx, (text, start_ms, end_ms) in enumerate(segments, 1):
            text = clean_segment_text(text)
            f.write(f"{idx}\n")
            f.write(f"{format_srt_timestamp(start_ms)} --> {format_srt_timestamp(end_ms)}\n")
            f.write(f"{text}\n\n")

    return output_path


def write_fallback_srt(text: str, output_path: str) -> str:
    """Write a single-segment SRT when word-level timestamps are unavailable."""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("1\n")
        f.write("00:00:00,000 --> 99:59:59,999\n")
        f.write(f"{text}\n")
    return output_path
