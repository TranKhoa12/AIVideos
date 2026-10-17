"""Offline speech content/timing audit; not a subjective naturalness judge."""
import argparse
from dataclasses import asdict
import difflib
import json
import os
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
os.environ['HF_HOME']=str(ROOT/'tools/hf-cache')
os.environ['HF_HUB_DISABLE_TELEMETRY']='1'
os.environ['HF_HUB_DISABLE_XET']='1'
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def local(value):
    path=(ROOT/value).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError('Outside workspace')
    return path

def normalized(value):
    return re.sub(r'[^\w\s]','',value.lower()).split()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan',required=True)
    parser.add_argument('--prepare-models',action='store_true')
    parser.add_argument('--model-dir',help='Workspace-relative predownloaded CTranslate2 model')
    args=parser.parse_args()
    if not args.prepare_models:
        os.environ['HF_HUB_OFFLINE']='1'
    from faster_whisper import WhisperModel
    plan=json.loads(local(args.plan).read_text(encoding='utf-8'))
    output=local(plan['report'])
    if output.exists():
        raise FileExistsError(output)
    print('Loading Whisper small CPU/int8 for local audit...',flush=True)
    model=WhisperModel(str(local(args.model_dir)) if args.model_dir else 'small',device='cpu',compute_type='int8',cpu_threads=4,download_root=str(ROOT/'tools/asr-models'),local_files_only=not args.prepare_models)
    report=[]
    for item in plan['items']:
        print('Auditing '+item['audio'],flush=True)
        segments,info=model.transcribe(str(local(item['audio'])),language='vi',beam_size=5,word_timestamps=True,condition_on_previous_text=False,vad_filter=True)
        records=[asdict(s) for s in segments]
        text=' '.join(s['text'].strip() for s in records)
        similarity=difflib.SequenceMatcher(None,normalized(item['expected']),normalized(text)).ratio()
        entry={'audio':item['audio'],'expected':item['expected'],'transcript':text,'tokenSimilarity':similarity,'segments':records,'languageProbability':info.language_probability,'limitation':'ASR can make errors; this does not score emotion or naturalness.'}
        report.append(entry)
        print(json.dumps({'transcript':text,'tokenSimilarity':similarity},ensure_ascii=False),flush=True)
    with output.open('x',encoding='utf-8') as target:
        json.dump(report,target,ensure_ascii=False,indent=2)

if __name__=='__main__':
    main()
