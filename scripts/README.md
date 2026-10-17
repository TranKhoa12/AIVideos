# Scripts

Dat cac cong cu tai su dung cho viec kiem tra tai nguyen, xu ly FFmpeg/FFprobe va render Remotion tai day.

- `tts-local.py`: tao loi doc tieng Viet offline bang Piper, tu choi ghi de.
- `narrate-local.py`: loi doc dung chung theo `config/voice-defaults.json`; engine ZeroTTS local, preset Mai Chi. Chay `tools/zerotts-env/Scripts/python.exe -X utf8 scripts/narrate-local.py --text-file temp/<job-id>/narration.txt --output assets/audio/<project-id>/narration-<unique-id>.wav`. Khong tu doi giong, khong ghi de, khong dung dich vu online. Vung mien preset chua duoc tai lieu xac nhan.
- `tts-vieneu-local.py`: tao giong doc tu preset VieNeu-TTS v3 Turbo offline; xem `vieneu-local.md` cho giong nu mien Nam.
- `local-audio.md`: huong dan, vi tri engine/model va thong tin giay phep.
- `mix-local.py`: tron nhac WAV va loi doc theo timeline, can RMS, ducking muot va headroom; chi doc/ghi trong workspace va tu choi ghi de.
- `setup-local.mjs`: tao thu muc/cau hinh local con thieu va sinh registry composition tu `config/projects.local.json`; khong tai model.
- Script render/kiem tra rieng tung video duoc giu local, khong dua len Git. Xem README goc de render bang Remotion CLI.

Chua co cong cu tao nhac offline hoac pipeline tu dong chung cho moi brief. Codex chon concept va trien khai composition theo tung job; khong dung mac dinh mot phong cach cho moi video.
