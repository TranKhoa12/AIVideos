"""Mix a local WAV music bed and narration with explicit, smooth ducking."""
import argparse
import json
from pathlib import Path
import wave
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def local(value):
    path = (ROOT / value).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError("Path leaves workspace")
    return path


def read_audio(value, rate):
    with wave.open(str(local(value)), "rb") as source:
        if source.getsampwidth() != 2:
            raise ValueError("Expected signed 16-bit PCM")
        channels = source.getnchannels()
        source_rate = source.getframerate()
        data = np.frombuffer(source.readframes(source.getnframes()), dtype="<i2").astype(np.float32).reshape(-1, channels) / 32768
    if channels == 1:
        data = np.repeat(data, 2, axis=1)
    if source_rate != rate:
        count = round(len(data) * rate / source_rate)
        positions = np.arange(count) * source_rate / rate
        data = np.column_stack([np.interp(positions, np.arange(len(data)), data[:, c]) for c in range(2)]).astype(np.float32)
    return data


def level(data, target, ceiling):
    mask = np.max(np.abs(data), axis=1) > 0.005
    rms = float(np.sqrt(np.mean(data[mask] ** 2))) if mask.any() else 0
    if rms:
        gain = min(target / rms, ceiling / max(float(np.max(np.abs(data))), 0.000001))
        data = data * gain
    return data


def write_audio(value, rate, data):
    path = local(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as raw:
        with wave.open(raw, "wb") as target:
            target.setnchannels(2)
            target.setsampwidth(2)
            target.setframerate(rate)
            target.writeframes((np.clip(data, -1, 1) * 32767).astype("<i2").tobytes())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", required=True)
    args = parser.parse_args()
    plan = json.loads(local(args.plan).read_text(encoding="utf-8"))
    rate = 48000
    count = round(plan["duration"] * rate)
    clock = np.arange(count) / rate
    voice = np.zeros((count, 2), np.float32)
    envelope = np.ones(count, np.float32)
    for scene in plan["voices"]:
        data = level(read_audio(scene["audio"], rate), 0.14, 0.78)
        start = round(scene["start"] * rate)
        end = start + len(data)
        if end > count:
            raise ValueError("Voice exceeds timeline")
        voice[start:end] += data
        end_time = end / rate
        duck = np.interp(clock, [max(0, scene["start"] - 0.12), scene["start"], end_time, end_time + 0.3], [1, 0.45, 0.45, 1])
        envelope = np.minimum(envelope, duck)
    source = level(read_audio(plan["musicTrim"], rate), 0.12, 0.55)
    if len(source) < count - 1:
        raise ValueError("Music too short")
    music = np.zeros((count, 2), np.float32)
    music[:min(len(source), count)] = source[:count]
    fade = np.minimum(np.clip(clock / 0.12, 0, 1), np.clip((plan["duration"] - clock) / 1.2, 0, 1))
    music *= (envelope * fade)[:, None]
    mix = voice + music
    peak = float(np.max(np.abs(mix)))
    master_gain = min(1, 0.88 / max(peak, 0.000001))
    write_audio(plan["voiceStem"], rate, voice * master_gain)
    write_audio(plan["musicStem"], rate, music * master_gain)
    write_audio(plan["mix"], rate, mix * master_gain)
    print(json.dumps({"duration": count / rate, "peak": peak * master_gain, "masterGain": master_gain, "duckGain": 0.45}))


if __name__ == "__main__":
    main()
