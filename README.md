# SRT Generator

Video subtitle generator powered by [FunASR SenseVoiceSmall](https://github.com/FunAudioLLM/SenseVoice) and [DeepSeek](https://deepseek.com). Feed it a video file, get a timestamped SRT subtitle file.

**[中文文档](README.zh-CN.md)**

## Features

- All common video formats (mp4, mkv, avi, mov, etc.)
- Auto-detect across 52 languages, or specify manually
- Built-in VAD (Voice Activity Detection) for long videos
- Word-level timestamps + DeepSeek AI sentence segmentation

## How It Works

```
Video → ffmpeg audio extraction → SenseVoiceSmall ASR (word-level timestamps)
      → DeepSeek AI segmentation → timestamp matching → SRT file
```

1. **Audio extraction** — ffmpeg converts video to 16 kHz mono WAV
2. **Speech recognition** — SenseVoiceSmall produces word-level transcript + timestamps
3. **Smart segmentation** — DeepSeek splits text into subtitle segments by semantics and length (8–20 words each)
4. **Timestamp matching** — segments are mapped back to original word-level timestamps, producing the final SRT

## Prerequisites

- Python >= 3.14
- [uv](https://docs.astral.sh/uv/) (package manager)
- ffmpeg (audio extraction)
- NVIDIA GPU + CUDA (model inference)

## Installation

```bash
git clone <repo-url>
cd srt-generator
uv sync
```

The SenseVoiceSmall model (~900 MB) is downloaded automatically from ModelScope on first run.

## Configuration

Create a `.env` file in the project root:

```
DEEPSEEK_API_KEY=your_api_key_here
```

The DeepSeek API key is required for AI-powered sentence segmentation. Get one at [DeepSeek Platform](https://platform.deepseek.com/).

## Usage

```bash
# Basic (auto-detect language)
uv run python main.py video.mp4

# Specify language
uv run python main.py video.mp4 en

# Specify output path
uv run python main.py video.mp4 auto output.srt
```

**Arguments**: `python main.py <video_path> [language] [output.srt]`

| Argument | Default | Description |
|---|---|---|
| `video_path` | — | Path to input video |
| `language` | `auto` | Language code: `auto`, `zh`, `en`, `ja`, `ko`, etc. |
| `output.srt` | Same name as video with `.srt` | Output subtitle path |

## Project Structure

```
srt-generator/
├── main.py              # Entry point: extract audio → ASR → segment → write SRT
├── audio.py             # ffmpeg audio extraction
├── srt.py               # SRT formatting and file writing
├── splitter/
│   ├── __init__.py      # Pipeline: merge contractions → build text → AI split → match timestamps
│   ├── preprocess.py    # ASR word merging (contraction handling) and char-position mapping
│   ├── prompt.py        # DeepSeek segmentation system prompt
│   └── client.py        # DeepSeek API client
├── pyproject.toml
└── .env                 # API key (not tracked in git)
```

## Dependencies

| Dependency | Purpose |
|---|---|
| funasr | Speech recognition framework (Alibaba DAMO Academy) |
| torch | Model inference backend |
| torchaudio | Audio processing |
| openai | DeepSeek API client (OpenAI-compatible SDK) |
| python-dotenv | Environment variable loading |
| ffmpeg (system) | Video-to-audio extraction |

## License

[GPL-3.0](LICENSE)
