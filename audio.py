"""Audio extraction utilities using ffmpeg."""

import os
import subprocess


def extract_audio(
    video_path: str,
    output_path: str = "temp_audio.wav",
    sample_rate: int = 16000,
) -> str:
    """Extract audio from video file as mono WAV.

    Args:
        video_path: Path to the input video file.
        output_path: Path for the output WAV file.
        sample_rate: Target sample rate in Hz.

    Returns:
        Path to the extracted audio file.

    Raises:
        FileNotFoundError: If the video file does not exist.
        subprocess.CalledProcessError: If ffmpeg fails.
    """
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
