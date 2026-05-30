"""AI-powered subtitle sentence splitting.

Pipeline: merge contractions → build natural text → single DeepSeek call
→ match sentences back to original word indices → timestamps.
"""

import asyncio

from splitter.client import split_text, close_client
from splitter.preprocess import merge_words, build_text, sentence_to_word_indices


async def _split_async(
    words: list[str],
    timestamps: list[list[int]],
) -> list[tuple[str, int, int]]:
    # Filter special tokens
    clean = [(w, ts) for w, ts in zip(words, timestamps)
             if not w.startswith("<|") and not w.startswith("|>")]
    if not clean:
        return []

    raw_words = [w for w, _ in clean]
    raw_ts = [ts for _, ts in clean]

    # Merge contractions, tracking original word indices
    merged = merge_words(raw_words)
    text, word_positions = build_text(merged)

    print(f"  {len(raw_words)} words → {len(text)} chars, "
          f"calling DeepSeek...")

    # Single request — text is short enough for one call
    sentences = await split_text(text)
    await close_client()

    print(f"  DeepSeek returned {len(sentences)} segments")

    # Match each sentence to word indices → timestamps
    result: list[tuple[str, int, int]] = []
    consumed = 0
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        match = sentence_to_word_indices(
            sentence, text, word_positions, merged, consumed
        )
        if match is None:
            continue
        indices, consumed = match
        start_ms = raw_ts[indices[0]][0]
        end_ms = raw_ts[indices[-1]][1]
        result.append((sentence, start_ms, end_ms))

    return result


def split_sentences_ai(
    words: list[str],
    timestamps: list[list[int]],
) -> list[tuple[str, int, int]]:
    """Split ASR words into subtitle segments via DeepSeek AI."""
    return asyncio.run(_split_async(words, timestamps))
