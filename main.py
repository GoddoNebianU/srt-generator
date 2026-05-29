"""SRT subtitle generator using FunASR SenseVoiceSmall.

Usage:
    python main.py <video_path> [language] [output.srt]

    language: auto (default), zh, en, ja, ko, etc.
"""

import os
import re
import subprocess
import sys

from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess


def extract_audio(
    video_path: str,
    output_path: str = "temp_audio.wav",
    sample_rate: int = 16000,
) -> str:
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")

    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", str(sample_rate),
        "-ac", "1",
        "-y",
        output_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return output_path


def format_srt_timestamp(ms: int) -> str:
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1_000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def is_cjk_char(ch: str) -> bool:
    cp = ord(ch)
    return (
        0x4E00 <= cp <= 0x9FFF
        or 0x3400 <= cp <= 0x4DBF
        or 0x3000 <= cp <= 0x303F
        or 0x3040 <= cp <= 0x309F
        or 0x30A0 <= cp <= 0x30FF
        or 0xAC00 <= cp <= 0xD7AF
    )


def has_cjk(text: str) -> bool:
    return any(is_cjk_char(c) for c in text)


def clean_segment_text(text: str) -> str:
    text = re.sub(r"\s+([.,!?:;…])", r"\1", text)
    text = re.sub(r"([.,!?:;…])([A-Za-z])", r"\1 \2", text)
    text = re.sub(r"\s+' \s*", "'", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def join_words(words: list[str], lang_has_cjk: bool) -> str:
    if lang_has_cjk:
        return "".join(words)
    return " ".join(words)


def group_words_into_segments(
    words: list[str],
    timestamps: list[list[int]],
    max_chars: int = 42,
) -> list[tuple[str, int, int]]:
    punct_break = re.compile(r"[。！？!?]$")

    lang_has_cjk = has_cjk("".join(words))

    segments: list[tuple[str, int, int]] = []
    cur_words: list[str] = []
    cur_start: int | None = None
    cur_end: int = 0

    for word, (start, end) in zip(words, timestamps):
        if word.startswith("<|") or word.startswith("|>"):
            continue
        if cur_start is None:
            cur_start = start
        cur_words.append(word)
        cur_end = end

        joined = join_words(cur_words, lang_has_cjk)
        if len(joined) >= max_chars or punct_break.search(word):
            segments.append((joined, cur_start, cur_end))
            cur_words = []
            cur_start = None

    if cur_words:
        segments.append((join_words(cur_words, lang_has_cjk), cur_start or 0, cur_end))

    return segments


def generate_srt(
    res: list[dict],
    output_path: str,
    max_chars_per_segment: int = 30,
) -> str:
    words = res[0].get("words", [])
    timestamps = res[0].get("timestamp", [])

    if not words or not timestamps:
        clean_text = rich_transcription_postprocess(res[0]["text"])
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("1\n")
            f.write("00:00:00,000 --> 99:59:59,999\n")
            f.write(f"{clean_text}\n")
        return output_path

    min_len = min(len(words), len(timestamps))
    words = words[:min_len]
    timestamps = timestamps[:min_len]

    segments = group_words_into_segments(words, timestamps, max_chars_per_segment)

    with open(output_path, "w", encoding="utf-8") as f:
        for idx, (text, start_ms, end_ms) in enumerate(segments, 1):
            text = clean_segment_text(text)
            f.write(f"{idx}\n")
            f.write(f"{format_srt_timestamp(start_ms)} --> {format_srt_timestamp(end_ms)}\n")
            f.write(f"{text}\n\n")

    return output_path


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <video_path> [language] [output.srt]")
        sys.exit(1)

    video_path = sys.argv[1]
    language = sys.argv[2] if len(sys.argv) > 2 else "auto"
    srt_path = sys.argv[3] if len(sys.argv) > 3 else os.path.splitext(video_path)[0] + ".srt"

    print(f"Extracting audio from: {video_path}")
    audio_path = extract_audio(video_path)

    print("Loading SenseVoiceSmall model...")
    model = AutoModel(
        model="iic/SenseVoiceSmall",
        vad_model="fsmn-vad",
        vad_kwargs={"max_single_segment_time": 30000},
        device="cuda:0",
    )

    print(f"Transcribing (language={language})...")
    res = model.generate(
        input=audio_path,
        cache={},
        language=language,
        use_itn=True,
        batch_size_s=60,
        merge_vad=True,
        merge_length_s=15,
        output_timestamp=True,
    )

    generate_srt(res, srt_path)
    print(f"SRT saved: {srt_path}")

    if audio_path.startswith("temp_"):
        os.remove(audio_path)


if __name__ == "__main__":
    main()
