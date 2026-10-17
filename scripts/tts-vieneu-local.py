"""Local VieNeu preset synthesis; online access is only for model setup."""
import argparse
import json
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
os.environ["HF_HOME"] = str(ROOT / "tools/hf-cache")
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["HF_HUB_DISABLE_XET"] = "1"
os.environ["NUMBA_CACHE_DIR"] = str(ROOT / "temp/numba-cache")
os.environ["MPLCONFIGDIR"] = str(ROOT / "temp/matplotlib-cache")
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")


def local(value):
    path = (ROOT / value).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError("Path must stay in workspace")
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", required=True)
    parser.add_argument("--prepare-models", action="store_true")
    args = parser.parse_args()
    if not args.prepare_models:
        os.environ["HF_HUB_OFFLINE"] = "1"
    import numpy as np
    import soundfile as sf
    from vieneu import Vieneu
    plan = json.loads(local(args.plan).read_text(encoding="utf-8"))
    for item in plan["items"]:
        if local(item["output"]).exists():
            raise FileExistsError(item["output"])
    print("Loading local VieNeu v3 Turbo CPU/fp32...", flush=True)
    tts = Vieneu(mode="v3turbo", backend="onnx", device="cpu", precision="fp32", threads=4)
    # After setup, prevent any further Hub requests during actual synthesis.
    import huggingface_hub.constants
    huggingface_hub.constants.HF_HUB_OFFLINE = True
    result = []
    try:
        for index, item in enumerate(plan["items"]):
            np.random.seed(item.get("seed", 24017 + index))
            started = time.time()
            print(f"Synthesizing {index+1}/{len(plan['items'])}: {item['voice']}", flush=True)
            audio = np.asarray(tts.infer(item["text"], voice=item["voice"], temperature=item.get("temperature", 0.8), max_new_frames=item.get("max_new_frames", 220), max_chars=item.get("max_chars", 256)), dtype=np.float32)
            if not audio.size or not np.isfinite(audio).all():
                raise ValueError("Invalid synthesis")
            output = local(item["output"])
            output.parent.mkdir(parents=True, exist_ok=True)
            with output.open("xb") as target:
                sf.write(target, audio, 48000, format="WAV", subtype="PCM_16")
            entry = {"output": item["output"], "voice": item["voice"], "seconds": len(audio)/48000, "elapsed": time.time()-started}
            result.append(entry)
            print(json.dumps(entry, ensure_ascii=False), flush=True)
    finally:
        tts.close()
    report = local(plan["report"])
    with report.open("x", encoding="utf-8") as target:
        json.dump(result, target, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
