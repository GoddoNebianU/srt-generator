"""SRT subtitle generator using FunASR SenseVoiceSmall + DeepSeek AI splitting.

Usage:
    python main.py <video_path> [language] [output.srt]

    language: auto (default), zh, en, ja, ko, etc.
"""

import os
import sys

from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess

from audio import extract_audio
from splitter import split_sentences_ai
from srt import write_srt, write_fallback_srt


def generate_srt(
    res: list[dict],
    output_path: str,
) -> str:
    words = res[0].get("words", [])
    timestamps = res[0].get("timestamp", [])

    if not words or not timestamps:
        print(f"  No word-level data (words={len(words)}, timestamps={len(timestamps)}), using fallback")
        clean_text = rich_transcription_postprocess(res[0]["text"])
        return write_fallback_srt(clean_text, output_path)

    min_len = min(len(words), len(timestamps))
    words = words[:min_len]
    timestamps = timestamps[:min_len]
    print(f"  {min_len} words with timestamps, splitting with DeepSeek AI...")
    segments = split_sentences_ai(words, timestamps)

    return write_srt(segments, output_path)


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
