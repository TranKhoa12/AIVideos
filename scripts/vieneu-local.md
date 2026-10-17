# Giong nu mien Nam — VieNeu local

- SDK: vieneu 3.8.3, Apache-2.0, https://github.com/pnnbao97/VieNeu-TTS
- Model: pnnbao-ump/VieNeu-TTS-v3-Turbo, Apache-2.0.
- Codec: OpenMOSS-Team/MOSS-Audio-Tokenizer-Nano-ONNX.
- Phonemizer: sea-g2p. Cac model/codec duoc tai vao `tools/hf-cache/`.
- Engine: CPU ONNX Runtime fp32, 4 threads; khong can API AI, khong nhan ban giong nguoi dung.
- Preset Kim Thanh: SDK gan nhan nu, mien Nam, doc truyen. Mau thu them My Duyen de so sanh. Muc do vui ve/tu nhien can nguoi nghe danh gia, khong suy ra chi tu ten preset.
- `style` bi SDK bo qua tren v3 Turbo: khong hua dieu khien cam xuc bang tham so nay. Dung preset, kich ban, dau cau va nhip doc phu hop.

`tools/vieneu-env/Scripts/python.exe scripts/tts-vieneu-local.py --plan <workspace-relative-plan.json>`

Mac dinh offline; `--prepare-models` chi cho phep tai tai nguyen model khi khoi tao. Sau khoi tao script tat Hub online truoc khi tong hop. Plan gom `items` (text, voice, output) va `report`. Dau ra va report moi, khong ghi de.

Nguon:
https://huggingface.co/pnnbao-ump/VieNeu-TTS-v3-Turbo
https://huggingface.co/OpenMOSS-Team/MOSS-Audio-Tokenizer-Nano-ONNX
