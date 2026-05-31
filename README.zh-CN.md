# SRT Generator

**[English](README.md)**

基于 [FunASR SenseVoiceSmall](https://github.com/FunAudioLLM/SenseVoice) 和 [DeepSeek](https://deepseek.com) 的视频字幕生成工具。输入视频文件，自动输出带时间戳的 SRT 字幕。

## 特性

- 支持所有常见视频格式（mp4、mkv、avi、mov 等）
- 52 种语言自动检测，也支持手动指定
- 内置 VAD（语音活动检测），自动处理长视频
- 词级时间戳 + DeepSeek AI 智能分句

## 工作流程

```
视频 → ffmpeg 提取音频 → SenseVoiceSmall 语音识别（词级时间戳）
     → DeepSeek AI 分句 → 匹配时间戳 → SRT 文件
```

1. **音频提取**：ffmpeg 将视频转为 16kHz 单声道 WAV
2. **语音识别**：SenseVoiceSmall 生成词级转录 + 时间戳
3. **智能分句**：DeepSeek 按语义和长度（8-20 词/段）将文本切分为字幕段
4. **时间戳匹配**：将分句结果映射回原始词级时间戳，生成 SRT

## 环境要求

- Python >= 3.14
- [uv](https://docs.astral.sh/uv/)（包管理）
- ffmpeg（音频提取）
- NVIDIA GPU + CUDA（模型推理）

## 安装

```bash
git clone <repo-url>
cd srt-generator
uv sync
```

首次运行会自动从 ModelScope 下载 SenseVoiceSmall 模型（约 900MB）。

## 配置

在项目根目录创建 `.env` 文件：

```
DEEPSEEK_API_KEY=your_api_key_here
```

DeepSeek API Key 用于智能分句。获取方式：[DeepSeek 开放平台](https://platform.deepseek.com/)

## 使用

```bash
# 基本用法（自动检测语言）
uv run python main.py video.mp4

# 指定语言
uv run python main.py video.mp4 en

# 指定输出路径
uv run python main.py video.mp4 auto output.srt
```

**参数**：`python main.py <video_path> [language] [output.srt]`

| 参数 | 默认值 | 说明 |
|---|---|---|
| `video_path` | — | 输入视频文件路径 |
| `language` | `auto` | 语言代码：`auto`、`zh`、`en`、`ja`、`ko` 等 |
| `output.srt` | 与视频同名 `.srt` | 输出字幕文件路径 |

## 项目结构

```
srt-generator/
├── main.py              # 入口：音频提取 → ASR → 分句 → 写 SRT
├── audio.py             # ffmpeg 音频提取
├── srt.py               # SRT 格式化与文件写入
├── splitter/
│   ├── __init__.py      # 分句管线：合并缩写 → 构建文本 → AI 分句 → 时间戳匹配
│   ├── preprocess.py    # ASR 词合并（缩写处理）与字符位置映射
│   ├── prompt.py        # DeepSeek 分句 system prompt
│   └── client.py        # DeepSeek API 客户端
├── pyproject.toml
└── .env                 # API Key（不入库）
```

## 依赖

| 依赖 | 用途 |
|---|---|
| funasr | 阿里达摩院语音识别框架 |
| torch | 模型推理后端 |
| torchaudio | 音频处理 |
| openai | DeepSeek API 调用（兼容 OpenAI SDK） |
| python-dotenv | 环境变量加载 |
| ffmpeg（系统） | 视频音频分离 |

## License

[GPL-3.0](LICENSE)
