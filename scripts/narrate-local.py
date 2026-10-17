"""Narration for any project using the shared voice preference. Offline only."""
import argparse
import json
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
os.environ['HF_HOME']=str(ROOT/'tools/hf-cache')
os.environ['HF_HUB_OFFLINE']='1'
os.environ['HF_HUB_DISABLE_TELEMETRY']='1'
os.environ['ZEROTTS_VOICES_HOME']=str(ROOT/'tools/zerotts-voices')
sys.stdout.reconfigure(encoding='utf-8')

def local(value):
    path=(ROOT/value).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError('Path leaves workspace')
    return path

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--text-file')
    parser.add_argument('--output')
    parser.add_argument('--inspect',action='store_true')
    args=parser.parse_args()
    config=json.loads((ROOT/'config/voice-defaults.json').read_text(encoding='utf-8'))
    model=local(config['modelDirectory'])
    if config['engine']!='zerotts' or not config['offlineOnly']:
        raise ValueError('Unsupported shared voice configuration')
    if not model.is_dir():
        raise FileNotFoundError('Local voice model unavailable; no online fallback')
    if args.inspect:
        print(json.dumps({'engine':config['engine'],'preset':config['preset'],'requestedAccent':config['requestedAccent'],'presetAccent':config['presetAccent'],'modelPresent':True,'offlineOnly':True}))
        return
    if not sys.flags.utf8_mode:
        raise RuntimeError('Run Python with -X utf8 on Windows')
    if not args.text_file or not args.output:
        parser.error('--text-file and --output are required for synthesis')
    source,target=local(args.text_file),local(args.output)
    if target.suffix.lower()!='.wav' or not target.is_relative_to(ROOT/'assets/audio'):
        raise ValueError('New narration WAV must be under assets/audio/<project-id>/')
    metadata=target.with_suffix('.voice.json')
    if target.exists() or metadata.exists():
        raise FileExistsError('Narration or metadata already exists')
    text=source.read_text(encoding='utf-8-sig').strip()
    if not text:
        raise ValueError('Empty narration')
    import numpy as np
    import soundfile as sf
    from zerotts import ZeroTTS
    from zerotts.chunking import chunk_text,clean_segment_punctuation,normalize_punctuation
    chunks=[clean_segment_punctuation(s) for s in chunk_text(normalize_punctuation(text),max_chunk_sec=config['maxChunkSeconds'])]
    tts=ZeroTTS.from_pretrained(str(model),intra_op_num_threads=config['threads'])
    audio=[]
    for index,chunk in enumerate(chunks):
        np.random.seed(config['seed']+index)
        wav=np.asarray(tts.synthesize(chunk,voice=config['preset'],max_frames=400),dtype=np.float32).reshape(-1)
        if not len(wav) or not np.isfinite(wav).all():
            raise ValueError('Invalid synthesized audio')
        if index:
            audio.append(np.zeros(round(config['chunkGapSeconds']*tts.sample_rate),dtype=np.float32))
        audio.append(wav)
    wav=np.concatenate(audio)
    gain=min(1,config['peakCeiling']/max(float(np.max(np.abs(wav))),0.000001))
    wav*=gain
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('xb') as raw:
        sf.write(raw,wav,tts.sample_rate,format='WAV',subtype='PCM_16')
    record={'voiceConfig':config,'textSource':str(source.relative_to(ROOT)),'output':str(target.relative_to(ROOT)),'durationSeconds':len(wav)/tts.sample_rate,'sampleRate':tts.sample_rate,'gain':gain,'chunks':chunks}
    with metadata.open('x',encoding='utf-8') as raw:
        json.dump(record,raw,ensure_ascii=False,indent=2)
    print(json.dumps({'output':str(target.relative_to(ROOT)),'durationSeconds':record['durationSeconds'],'preset':config['preset']}))

if __name__=='__main__':
    main()
