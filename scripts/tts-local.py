"""Offline Vietnamese narration. Run with tools/tts-env/Scripts/python.exe."""
import argparse
import json
from pathlib import Path
import wave

from piper import PiperVoice, SynthesisConfig

ROOT = Path(__file__).resolve().parents[1]


def workspace_path(value):
    path = (ROOT / value).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError("Path must stay inside workspace")
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text-file", required=True, help="Workspace-relative UTF-8 text")
    parser.add_argument("--output", required=True, help="New workspace-relative WAV")
    parser.add_argument("--length-scale", type=float, default=1.0, help="Speech duration multiplier (positive)")
    args = parser.parse_args()
    if not 0.5 <= args.length_scale <= 2:
        raise ValueError("Length scale must be between 0.5 and 2")
    source = workspace_path(args.text_file)
    target = workspace_path(args.output)
    if target.suffix.lower() != ".wav":
        raise ValueError("Output must be WAV")
    text = source.read_text(encoding="utf-8-sig").strip()
    if not text:
        raise ValueError("Narration is empty")
    model = ROOT / "tools/voices/vi-vais1000/vi_VN-vais1000-medium.onnx"
    voice = PiperVoice.load(str(model), use_cuda=False)
    target.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation protects all existing outputs, including concurrent runs.
    with target.open("xb") as raw:
        with wave.open(raw, "wb") as wav:
            voice.synthesize_wav(text, wav, SynthesisConfig(length_scale=args.length_scale))
    with wave.open(str(target), "rb") as wav:
        frames = wav.getnframes()
        if frames <= 0:
            raise ValueError("Synthesis produced no samples")
        print(json.dumps({"output": str(target.relative_to(ROOT)),
                          "sampleRate": wav.getframerate(),
                          "channels": wav.getnchannels(),
                          "durationSeconds": frames / wav.getframerate()}, ensure_ascii=True))


if __name__ == "__main__":
    main()
