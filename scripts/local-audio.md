# Am thanh offline

Engine: Piper 1.8.0 (GPL-3.0), https://github.com/OHF-Voice/piper1-gpl

Model: vi_VN-vais1000-medium, 1 speaker, 22050 Hz.
Source: https://huggingface.co/rhasspy/piper-voices/tree/main/vi/vi_VN/vais1000/medium
Model card duoc luu cung model trong tools/voices/vi-vais1000/MODEL_CARD.
Model card ghi dataset VAIS-1000 theo CC BY 4.0:
https://ieee-dataport.org/documents/vais-1000-vietnamese-speech-synthesis-corpus
https://creativecommons.org/licenses/by/4.0/
Giu thong tin nguon, model va cac thay doi khi giao video co loi doc.

Python portable, moi truong TTS va model nam trong tools/ (khong commit Git).
Thu vien da cai trong tools/tts-env; khong can kich hoat virtualenv:

```powershell
tools/tts-env/Scripts/python.exe scripts/tts-local.py --text-file temp/<job-id>/narration.txt --output assets/audio/<project-id>/narration-<unique-id>.wav
```

Tep van ban UTF-8 va dau ra phai nam trong workspace. Script tu choi ghi de.
Tong hop dung CPU, khong tai model hay goi API khi chay. Day la giong doc,
khong phai cong cu tao nhac. Nhac van can tep local duoc phep su dung.
Kiem tra WAV bang FFprobe truoc khi dua vao video; nghe lai de danh gia phat am.

## Giong nu mien Nam

Da cai VieNeu-TTS v3 Turbo trong `tools/vieneu-env/` va cache model trong workspace.
Xem `scripts/vieneu-local.md` va `scripts/tts-vieneu-local.py` de dung preset Kim Thanh
hoac My Duyen. Da tao duoc audio 48 kHz khi tat Hub online; khong dung API AI.
Khong sua cao do cua Piper de gia lam giong nu hoac suy ra giong mien Nam.
