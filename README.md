# AI Videos

Workspace tạo video bằng **Remotion, React và TypeScript**, điều khiển qua chat với Codex. Bạn cung cấp ảnh và mục tiêu; Codex đề xuất kịch bản, dựng video, làm ảnh bìa và viết bài đăng.

Không có trang upload hay backend riêng. Remotion Studio dùng để xem composition. Đây là quy trình có Codex điều phối, chưa phải chương trình tự tạo video hoàn chỉnh bằng một lệnh.

## Cài đặt

Cần Git, Node.js và npm. Máy phát triển hiện dùng Node.js 24. Âm thanh tùy chọn dùng Python 3.11; môi trường Python và model không được đưa lên GitHub.

Clone repository bằng URL của bạn, mở terminal trong thư mục dự án rồi chạy:

```powershell
npm ci
npm run typecheck
npm run studio
```

Nếu Windows chặn `npm.ps1`, dùng `npm.cmd` thay cho `npm`.

`npm ci` tự tạo các thư mục và cấu hình local còn thiếu, không tải model AI. Nếu cài với tùy chọn bỏ qua install scripts, chạy `npm run setup` sau đó. Bản clone mới chỉ có `BootstrapComposition`; video và tài nguyên trên máy tác giả không nằm trong repository.

## Tạo video qua Codex

Mở workspace trong Codex. Quy tắc chi tiết nằm trong [AGENTS.md](AGENTS.md).

1. Yêu cầu **“Tạo dự án Giới thiệu khóa học Excel”**. Codex tạo thư mục theo ID riêng.
2. Chép ảnh, video nguồn, âm thanh hoặc logo vào thư mục tương ứng. Logo dùng chung nằm trong `assets/logos/logo-chung/`.
3. Codex hỏi **mục tiêu và nền tảng/vị trí đăng** nếu bạn chưa nêu. Người xem mặc định là học viên, người đi làm và sinh viên.
4. Codex xem tài nguyên, nghiên cứu nguồn được phép và gửi **ý tưởng, kịch bản để bạn duyệt**.
5. Sau khi duyệt, Codex tạo lời đọc local, chuẩn bị nhạc có quyền sử dụng và dựng video theo nền tảng.
6. Xuất, kiểm tra video; tạo ảnh bìa; viết bài đăng đầy đủ, có icon, liên hệ, hashtag và ghi công cần thiết.
7. Giao đường dẫn sản phẩm. Không tự đăng lên tài khoản mạng xã hội.
8. Sau khi bản mới kiểm tra thành công, dọn bản cũ và dữ liệu phát sinh riêng của chúng. **Giữ mọi bài post, tài nguyên nguồn, logo và công cụ dùng chung.**

Ví dụ yêu cầu:

> Làm video từ ảnh tôi đã thêm. Mục tiêu tuyển sinh, đăng Facebook Reels và YouTube Shorts. Gửi ý tưởng và kịch bản trước, dựng sau khi tôi duyệt.

## Cấu trúc thư mục

```text
assets/
  images/<project-id>/       Ảnh nguồn
  videos/<project-id>/       Video nguồn
  audio/<project-id>/        Nhạc, lời đọc, bản mix
  logos/<project-id>/        Logo riêng
  logos/logo-chung/          Logo dùng chung
config/
  projects.example.json     Ví dụ đăng ký composition
  projects.local.json       Video trên máy (không commit)
  voice-defaults.example.json
  voice-defaults.json        Cấu hình giọng local (không commit)
jobs/
  job.schema.json           Cấu trúc job
  <project-id>-<video>.json  Job local (không commit)
src/
  compositions/             Composition dùng chung
  projects/                 Composition từng dự án (không commit)
  generated/                Registry tự sinh (không commit)
scripts/                    Công cụ thiết lập, âm thanh và kiểm tra
output/
  videos/<project-id>/      Video xuất
  previews/<project-id>/    Khung hình kiểm tra
  covers/<project-id>/      Ảnh bìa
  posts/<project-id>/       Bài Facebook, mô tả YouTube…
temp/<job-id>/              Tệp trung gian
tools/                      Python environment, model, cache local
```

ID dùng chữ thường không dấu, chữ số và dấu gạch nối. Các dự án độc lập không trộn tài nguyên. Tệp đầu vào không bị chỉnh sửa khi dựng.

## Đăng ký video trong Studio

Codex thực hiện bước này khi dựng. Nếu thao tác thủ công, tạo job theo schema, đặt component ở `src/projects/`, thêm vào `config/projects.local.json`:

```json
{
  "projects": [
    {
      "id": "MyCourseIntro",
      "component": "src/projects/MyCourseIntro.tsx",
      "exportName": "MyCourseIntro",
      "job": "jobs/my-course-intro-v1.json"
    }
  ]
}
```

Component export đúng tên; job có `format.width`, `height`, `fps`, `durationInFrames`. Chạy `npm run setup` để sinh registry. Lệnh studio và typecheck tự chạy setup trước. Nếu dùng script Remotion API trực tiếp, chạy setup sau khi thay danh sách video.

Composition local có thể nhập job local. Mã dùng chung không nhập trực tiếp job bị Git bỏ qua, để bản clone mới vẫn chạy được.

## Giọng đọc và nhạc local

Cấu hình mẫu dùng **Mai Chi / ZeroTTS 0.1.5**. Định hướng là nữ, tự nhiên, vui vẻ, miền Nam; vùng miền của preset chưa được tài liệu xác nhận. Cần nghe mẫu để đánh giá; ASR không thay thế việc nghe.

Clone repository không bao gồm môi trường Python hay model. Thiết lập tùy chọn:

```powershell
py -3.11 -m venv tools/zerotts-env
tools/zerotts-env/Scripts/python.exe -m pip install -r requirements-audio.txt
```

Tải model là bước có mạng, tách khỏi tổng hợp giọng. Nếu đã có model trong workspace, bỏ qua bước tải. Ví dụ tải đúng revision đang dùng:

```powershell
tools/zerotts-env/Scripts/python.exe -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='zeroweight-ai/ZeroTTS', revision='c2bfbd67dc648cac455077333f7cf5c18a2e3bb4', local_dir='tools/models/zerotts')"
```

Đặt `modelDirectory` trong `config/voice-defaults.json` thành `tools/models/zerotts`. Xem [model ZeroTTS](https://huggingface.co/zeroweight-ai/ZeroTTS) và giữ giấy phép của model, codec, thư viện.

Tạo thư mục, tệp lời dẫn UTF-8 rồi chạy:

```powershell
tools/zerotts-env/Scripts/python.exe -X utf8 scripts/narrate-local.py --inspect
tools/zerotts-env/Scripts/python.exe -X utf8 scripts/narrate-local.py --text-file temp/my-job/narration.txt --output assets/audio/my-project/narration-v1.wav
```

Script từ chối ghi đè, chỉ đọc/ghi trong workspace và báo lỗi nếu thiếu model; không chuyển sang AI online.

`scripts/mix-local.py` trộn WAV bằng NumPy theo plan, có giảm nhạc dưới lời đọc. Chưa tích hợp tạo nhạc offline. Chỉ dùng nhạc có quyền sử dụng và giữ nguồn/ghi công. Piper, VieNeu và ASR là công cụ tùy chọn, không được cài bằng `requirements-audio.txt`. Tên môi trường trong tài liệu cũ có thể khác; dùng Python đã cài đúng thư viện tương ứng.

## Render và kiểm tra

Sau khi có component, job và registry:

```powershell
npm run setup
npx remotion render src/index.ts MyCourseIntro output/videos/my-project/intro-v1.mp4
```

Dùng tên đầu ra mới mỗi lần render; cấu hình hiện tại không cho ghi đè. Kiểm tra codec, kích thước, FPS, thời lượng, hình đầu–cuối, bố cục và âm thanh trước khi giao. FFmpeg/FFprobe có trong dependency `ffmpeg-static` và `ffprobe-static`.

## Phạm vi GitHub

Đưa lên Git: mã dùng chung, script, schema, cấu hình mẫu, lockfile và hướng dẫn.

`.gitignore` bỏ qua:

- Tài nguyên từng dự án, kể cả `gioi-thieu-khoa-hoc-...` và `logo-chung`.
- Job, composition và cấu hình local.
- Mọi video, ảnh bìa, preview, bài post, báo cáo và tệp tạm.
- `node_modules/`, `tools/`, model, cache và biến môi trường riêng.
- Script chỉ dành cho video Sao Việt trên máy tác giả.

**Bỏ qua Git không xóa dữ liệu trên máy.** Bài post vẫn được giữ khi dọn phiên bản, nhưng không đẩy lên GitHub. Sang máy khác, chuyển tài nguyên cần thiết bằng cách riêng và thiết lập model local.

Kiểm tra trước khi commit:

```powershell
git status --short
git diff --cached --stat
```

Nếu tệp đã được Git theo dõi từ trước, `.gitignore` không tự xóa nó khỏi lịch sử. Workspace này được khởi tạo Git mới sau khi thiết lập quy tắc bỏ qua.
