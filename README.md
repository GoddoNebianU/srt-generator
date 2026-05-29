# SRT Generator

基于 [FunASR](https://github.com/modelscope/FunASR) 和 [SenseVoiceSmall](https://github.com/FunAudioLLM/SenseVoice) 的视频字幕生成工具。输入视频文件，自动输出带时间戳的 SRT 字幕。

## 特性

- 支持所有常见视频格式（mp4, mkv, avi, mov 等）
- 52 种语言自动检测，也支持手动指定
- 内置 VAD（语音活动检测），自动处理长视频
- 词级时间戳，按标点和长度智能分句

## 环境要求

- Python >= 3.14
- [uv](https://docs.astral.sh/uv/)（包管理）
- ffmpeg（音频提取）
- NVIDIA GPU + CUDA（推理）

## 安装

```bash
git clone <repo-url>
cd srt-generator
uv sync
```

首次运行会自动从 ModelScope 下载模型（约 900MB）。

## 使用

```bash
# 基本用法（自动检测语言）
uv run python main.py video.mp4

# 指定语言
uv run python main.py video.mp4 en

# 指定输出路径
uv run python main.py video.mp4 auto output.srt
```

语言参数可选：`auto`（默认）、`zh`、`en`、`ja`、`ko` 等。

## 依赖

| 依赖 | 用途 |
|---|---|
| funasr | 语音识别框架 |
| torch | 模型推理 |
| torchaudio | 音频处理 |
| ffmpeg | 视频音频分离 |

## 致谢

- [FunASR](https://github.com/modelscope/FunASR) — 阿里达摩院语音识别框架
- [SenseVoice](https://github.com/FunAudioLLM/SenseVoice) — 通义实验室语音模型
