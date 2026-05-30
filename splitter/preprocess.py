"""ASR word merging and text construction.

Handles contraction merging (don+'+t → don't) and builds a reliable
mapping between character positions in the final text and the original
ASR word indices (for timestamp lookup).
"""

import re


def merge_words(raw_words: list[str]) -> list[tuple[str, list[int]]]:
    """Merge contraction tokens and associate with original indices.

    Returns list of (merged_word, [original_indices]).
    E.g. [("don't", [5,6,7]), ("go", [8])]
    """
    result: list[tuple[str, list[int]]] = []
    i = 0
    while i < len(raw_words):
        word = raw_words[i]
        indices = [i]
        # Look ahead for apostrophe + suffix pattern: word + ' + s/t/re/ve/ll/d/m
        if (i + 2 < len(raw_words)
                and raw_words[i + 1] in ("'", "'")
                and raw_words[i + 2] in ("s", "t", "re", "ve", "ll", "d", "m")):
            word = word + "'" + raw_words[i + 2]
            indices = [i, i + 1, i + 2]
            i += 3
        else:
            i += 1
        result.append((word, indices))
    return result


def build_text(
    merged: list[tuple[str, list[int]]],
) -> tuple[str, list[tuple[int, int]]]:
    """Build natural text from merged words.

    Returns (text, word_positions) where word_positions is a list of
    (start_char, end_char) for each merged word in the text.
    """
    parts: list[str] = []
    word_positions: list[tuple[int, int]] = []
    offset = 0

    for word, _ in merged:
        if parts:
            parts.append(" ")
            offset += 1
        parts.append(word)
        word_positions.append((offset, offset + len(word)))
        offset += len(word)

    text = "".join(parts)
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text, word_positions


def sentence_to_word_indices(
    sentence: str,
    full_text: str,
    word_positions: list[tuple[int, int]],
    merged: list[tuple[str, list[int]]],
    consumed_up_to: int,
) -> tuple[list[int], int] | None:
    pos = full_text.find(sentence, word_positions[consumed_up_to][0] if consumed_up_to < len(word_positions) else len(full_text))
    if pos != -1:
        indices = _char_range_to_indices(pos, pos + len(sentence), word_positions, merged)
        if indices and min(indices) >= _min_original_index(merged, consumed_up_to):
            end_word = _char_to_merged_index(pos + len(sentence), word_positions)
            return indices, max(consumed_up_to, end_word)

    return _word_align(sentence, merged, consumed_up_to)


def _min_original_index(merged: list[tuple[str, list[int]]], consumed_up_to: int) -> int:
    if consumed_up_to >= len(merged):
        return 999999
    return min(merged[consumed_up_to][1])


def _char_range_to_indices(
    start_char: int, end_char: int,
    word_positions: list[tuple[int, int]],
    merged: list[tuple[str, list[int]]],
) -> list[int]:
    result: list[int] = []
    for i, (ws, we) in enumerate(word_positions):
        if ws < end_char and we > start_char:
            result.extend(merged[i][1])
    return sorted(set(result))


def _char_to_merged_index(char_pos: int, word_positions: list[tuple[int, int]]) -> int:
    for i, (ws, we) in enumerate(word_positions):
        if ws <= char_pos <= we:
            return i + 1
    for i, (ws, _) in enumerate(word_positions):
        if ws > char_pos:
            return i
    return len(word_positions)


def _normalize_words(text: str) -> list[str]:
    return re.sub(r"[^\w\s]", "", text.lower()).split()


def _word_align(
    sentence: str,
    merged: list[tuple[str, list[int]]],
    consumed_up_to: int,
) -> tuple[list[int], int] | None:
    target = _normalize_words(sentence)
    if not target:
        return None

    n_merged = len(merged)
    best_end = 0
    best_count = 0
    best_start = consumed_up_to

    for start in range(consumed_up_to, min(consumed_up_to + 30, n_merged)):
        matched = 0
        ti = 0
        end = start
        for mi in range(start, min(start + 50, n_merged)):
            w = re.sub(r"[^\w]", "", merged[mi][0].lower())
            if ti < len(target) and w == target[ti]:
                matched += 1
                ti += 1
            end = mi + 1
            if ti >= len(target):
                break

        if matched > best_count and matched >= len(target) * 0.6:
            best_count = matched
            best_start = start
            best_end = end
            if matched >= len(target) * 0.85:
                break

    if best_count == 0:
        return None

    indices: list[int] = []
    for k in range(best_start, best_end):
        indices.extend(merged[k][1])
    return sorted(set(indices)), best_end
