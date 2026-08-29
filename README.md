# nihongo-tutor-vn

Gia sư tiếng Nhật cho **người Việt** học từ con số 0, thiết kế riêng cho dân IT
làm việc trong môi trường công ty Nhật.

Chạy được trên **Claude Code** và **Gemini CLI** từ cùng một thư mục.

---

## Có gì khác so với các skill dạy tiếng Nhật khác

**Dạy kanji qua âm Hán-Việt.** 確認 → "xác nhận" → かくにん. Người Việt đã biết
nghĩa từ nhỏ nhờ từ Hán-Việt, chỉ còn phải học cách đọc — công việc giảm một
nửa so với người học nói tiếng Anh. Skill còn dạy quy luật đoán âm On từ âm
Hán-Việt, nên bạn có thể *đoán* cách đọc chữ mới chứ không chỉ tra từ điển.

**Katakana song song hiragana ngay từ buổi đầu.** Thuật ngữ IT tiếng Nhật gần
như toàn từ mượn tiếng Anh viết bằng katakana: データ, システム, サーバー,
バグ. Biết tiếng Anh cộng với đọc được katakana là mở khóa hàng trăm từ chuyên
ngành ngay lập tức.

**Ba chế độ buổi học: 10 / 25 / 50 phút.** Ngày bận vẫn học được, và buổi 10
phút vẫn được tính đầy đủ vào tiến độ. Biết rằng luôn có lối thoát ngắn chính
là thứ giữ người học không bỏ cuộc.

**Không dùng streak theo ngày liên tiếp.** Với lịch làm việc thất thường,
streak chỉ tạo cảm giác thất bại rồi bỏ hẳn. Thay bằng nhịp độ theo tuần, và
skill không trách móc khi bạn nghỉ lâu.

**Ôn tập giãn cách Leitner 5 hộp.** Trả lời sai thì về hộp 1 và gặp lại ngay
buổi sau. Khoảng cách tính theo *số buổi học* chứ không theo ngày, phù hợp với
người học không đều.

**Thu hoạch từ nơi làm việc.** Mỗi buổi mở đầu bằng việc bạn mang về những
tiếng Nhật nghe hoặc nhìn thấy ở công ty hôm đó. Từ vựng có ngữ cảnh thật thì
nhớ lâu hơn hẳn từ vựng trong sách.

**Từ vựng hướng nhà máy, không hướng công ty phần mềm.** 現場, 品質, 不良,
朝礼, 改善, ヒヤリハット, 5S — thứ bạn thật sự gặp ở khu công nghiệp.

---

## Cấu trúc

```
nihongo-tutor-vn/
├── .claude-plugin/
│   ├── marketplace.json          # Để cài bằng /plugin trên Claude Code
│   └── plugin.json               # Metadata plugin
├── gemini-extension.json         # Manifest cho Gemini CLI
├── GEMINI.md                     # Context nạp vào Gemini CLI
├── commands/
│   ├── nihongo.toml              # /nihongo — buổi học thường (Gemini CLI)
│   ├── on.toml                   # /on — ôn bài, không học mới
│   └── day-lai.toml              # /day-lai — bạn làm thầy, AI làm học viên
├── skills/
│   └── nihongo-tutor-vn/         # Nội dung dùng chung cho cả hai công cụ
│       ├── SKILL.md              # Hướng dẫn chính (giữ dưới 500 dòng)
│       ├── resources.json        # Tài nguyên học, có nguồn tiếng Việt
│       ├── scripts/
│       │   ├── progress.py       # Toàn bộ thao tác với progress.json
│       │   ├── speak.py          # Phát âm tiếng Nhật (TTS)
│       │   └── test_progress.py  # Kiểm thử progress.py trên file tạm
│       └── references/
│           ├── roadmap.md            # Lộ trình 4 giai đoạn
│           ├── kanji-hanviet.md      # Dạy kanji qua âm Hán-Việt
│           ├── workplace-japanese.md # Tiếng Nhật công sở, nhà máy, IT
│           ├── vocab-n5.json         # 509 từ N5 có Hán-Việt, topic, priority
│           ├── review-mode.md        # Chế độ ôn bài độc lập
│           ├── teach-back.md         # Chế độ dạy lại
│           └── progress-format.md    # Cấu trúc progress.json, bảng lệnh
├── LICENSE
└── README.md
```

Thư mục `skills/` là phần lõi và dùng chung. Cả Claude Code lẫn Gemini CLI đều
đọc định dạng `skills/<tên>/SKILL.md`, nên không cần duy trì hai bản nội dung.
Chỉ các file manifest ở ngoài là khác nhau.

**Quan trọng:** giữ nguyên cấu trúc thư mục. `SKILL.md` trỏ tới các file trong
`references/` bằng đường dẫn tương đối. Nếu gộp hết vào một thư mục phẳng thì
phần lộ trình và bảng Hán-Việt sẽ mất tác dụng.

---

## Cài đặt cho Claude Code

### Cách 1 — cài trực tiếp, không cần GitHub

```bash
mkdir -p ~/.claude/skills/
cp -r nihongo-tutor-vn/skills/nihongo-tutor-vn ~/.claude/skills/
```

Claude Code tự quét thư mục này và nhận skill, không cần khởi động lại.

### Cách 2 — cài từ GitHub bằng lệnh plugin

Sau khi đã push repo lên GitHub ở chế độ **public** (Claude Code lấy marketplace
trực tiếp từ GitHub nên repo private sẽ không dùng được):

```
/plugin marketplace add TÊN_GITHUB_CỦA_BẠN/nihongo-tutor-vn
/plugin install nihongo-tutor-vn@nihongo-skills
/reload-plugins
```

Nếu lệnh `/plugin` không được nhận, hãy cập nhật Claude Code lên bản mới hơn.

### Cách dùng

Nói tự nhiên, không cần lệnh đặc biệt:

```
học tiếng Nhật
hôm nay tôi chỉ có 10 phút thôi
tiến độ tới đâu rồi
hôm nay sếp nói "かくにん" là gì vậy?
ôn bài thôi, không học mới
để tôi dạy lại cho bạn
```

---

## Cài đặt cho Gemini CLI

### Cách 1 — cài từ GitHub

```bash
gemini extensions install https://github.com/TÊN_GITHUB_CỦA_BẠN/nihongo-tutor-vn
```

### Cách 2 — cài từ thư mục trên máy

```bash
gemini extensions install ./nihongo-tutor-vn
```

### Cách 3 — chép tay

```bash
mkdir -p ~/.gemini/extensions/
cp -r nihongo-tutor-vn ~/.gemini/extensions/
```

Gemini CLI chỉ nạp extension khi khởi động, nên cần **thoát và mở lại** sau khi
cài. Kiểm tra bằng `gemini extensions list`.

Lưu ý: khi cài bằng `gemini extensions install`, Gemini tạo một bản sao riêng.
Nếu sau này bạn sửa nội dung skill, phải chạy `gemini extensions update` để cập
nhật bản sao đó.

### Cách dùng

```
/nihongo
/nihongo hôm nay chỉ có 10 phút
/on kanji
/day-lai は và が
```

Hoặc nói tự nhiên như với Claude Code — `GEMINI.md` đã hướng dẫn model tự kích
hoạt skill khi bạn nhắc tới việc học tiếng Nhật.

---

## Quy trình sử dụng

### Buổi đầu tiên (~15 phút)

Chạy Claude Code hoặc Gemini CLI ở bất kỳ thư mục nào, gõ "học tiếng Nhật"
(hoặc `/nihongo` với Gemini CLI). Skill tìm `~/.nihongo-tutor/progress.json`,
không thấy nên biết đây là lần đầu.

Nó hỏi bốn câu ngắn: tên gọi, mỗi lần học được bao lâu và mấy lần một tuần, có
muốn hiển thị romaji không, và mục tiêu của bạn. **Không có bài kiểm tra trình
độ** — người bắt đầu từ 0 thì kiểm tra là vô nghĩa và chỉ gây nản.

Trả lời xong, nó tạo file tiến độ rồi dạy luôn trong cùng buổi đó: 5 chữ
hiragana あいうえお và 5 katakana アイウエオ tương ứng. Đây là chủ ý — bạn phải
rời buổi đầu tiên với cảm giác đã học được thứ gì thật, không phải chỉ ngồi trả
lời câu hỏi thiết lập.

### Các buổi sau

Vẫn gõ "học tiếng Nhật". Skill đọc tiến độ, biết bạn đang ở đâu, rồi chạy theo
trình tự:

1. **Thu hoạch từ nơi làm việc** — hôm nay ở công ty có nghe hay thấy tiếng
   Nhật nào lạ không? Một từ sếp hay nói, một dòng trên bảng thông báo, kể cả
   chỉ nhớ mang máng cách phát âm cũng đưa vào được, skill sẽ đoán giúp. Không
   có gì thì bỏ qua.
2. **Chọn chế độ** — hôm nay bạn có bao nhiêu thời gian? Trả lời thật. "10 phút
   thôi" là câu trả lời hợp lệ và vẫn tính đủ một buổi.
3. **Ôn tập giãn cách** — vài mục đến hạn, đổi kiểu hỏi liên tục.
4. **Nội dung mới** — kana, từ vựng, kanji, hoặc ngữ pháp tùy giai đoạn.
5. **Hội thoại và luyện nghe** (bỏ qua ở chế độ 10 phút).
6. **Bài tập và lưu tiến độ**.

### Các chế độ

Skill nhìn câu đầu tiên của bạn để quyết định làm gì. Không khớp gì thì mở
buổi học thường.

| Chế độ | Câu kích hoạt | Làm gì |
|---|---|---|
| **Buổi học thường — Nhanh** (~10 phút) | `học tiếng Nhật`, `hôm nay chỉ có 10 phút` | Ôn Leitner (≤5 mục) + 3 mục mới. Bỏ hội thoại, bài tập. |
| **Buổi học thường — Chuẩn** (~25 phút) | `học tiếng Nhật` rồi trả lời "25 phút" (mặc định) | Ôn (≤8 mục) + 5 mục mới + 1 ngữ pháp + hội thoại + 5 câu bài tập. |
| **Buổi học thường — Sâu** (~50 phút) | `hôm nay có 50 phút` | Như Chuẩn + shadowing (phát âm nếu bật TTS) + 10 câu + một mảng từ công sở. |
| **Tra cứu nhanh** | `かくにん là gì?`, `sếp nói "yoroshiku" là sao?`, `安全 đọc thế nào?` | Trả lời gọn: nghĩa, cách đọc, Hán-Việt, một ví dụ, ngữ cảnh công ty. Hỏi có thêm vào ôn tập không. **Không** mở buổi học. |
| **Ôn bài — đến hạn** | `ôn bài`, `chỉ ôn thôi`, `hôm nay không học mới` | Toàn bộ hàng đợi Leitner, không giới hạn. Dùng sau kỳ nghỉ dài. |
| **Ôn bài — tổng hợp** | `ôn tổng hợp` (skill tự đề xuất mỗi 7 buổi) | 10–15 mục ngẫu nhiên từ mọi hộp kể cả hộp 5, xen kẽ kana/từ/kanji/ngữ pháp. Sai ở hộp 4–5 chỉ tụt về 3. |
| **Ôn bài — theo chủ đề** | `ôn từ công sở`, `ôn kanji`, `ôn katakana` | Lọc theo topic hoặc loại. |
| **Dạy lại** | `để tôi dạy lại`, `tôi giảng cho bạn`, `dạy lại`, `feynman`, `cho tôi làm thầy` | Bạn làm thầy, AI làm đồng nghiệp mới chưa biết tiếng Nhật: hỏi, đòi ví dụ, cố ý sai một lỗi. Không sửa bạn lúc đang giảng — nhận xét sau. Giảng đúng thì lên hộp. |
| **Báo cáo tiến độ** | `tiến độ tới đâu rồi`, `thống kê` | Bảng tổng kết, không có streak. |

Trong buổi học, gõ `gợi ý` bất cứ lúc nào giữa hội thoại để xin trợ giúp (skill
cho một mẫu câu, không cho luôn đáp án).

Buổi ôn và buổi dạy lại **vẫn đếm là một buổi** — khoảng cách Leitner tính
theo số buổi nên chúng phải đếm.

### Mấy câu đáng thuộc

| Gõ gì | Kết quả |
|---|---|
| `học tiếng Nhật` | Bắt đầu buổi học |
| `hôm nay chỉ có 10 phút` | Chạy chế độ Nhanh |
| `tiến độ tới đâu rồi` | Hiện bảng tổng kết |
| `gợi ý` | Xin trợ giúp giữa hội thoại (không cho luôn đáp án) |
| `hôm nay sếp nói かくにん là gì vậy?` | Tra cứu nhanh, không mở buổi học |
| `ôn bài` / `chỉ ôn thôi` | Ôn đến hạn, không học mới |
| `ôn từ công sở` / `ôn kanji` / `ôn katakana` | Ôn theo chủ đề hoặc loại |
| `để tôi dạy lại` / `cho tôi làm thầy` | Bạn giảng, AI làm học viên |

### Dùng chung tiến độ giữa hai công cụ

Cả Claude Code và Gemini CLI đều đọc ghi cùng file
`~/.nihongo-tutor/progress.json`. Học bằng Claude Code hôm nay, mai mở Gemini
CLI học tiếp, tiến độ vẫn liền mạch. Bạn không bị khóa vào một công cụ nào.

Đổi lại, file đó là **toàn bộ trí nhớ của gia sư** — mất nó là mất sạch. Nên
thỉnh thoảng sao lưu sang chỗ khác, hoặc đẩy vào một repo private riêng. Đừng
đẩy vào repo skill public; `.gitignore` đã chặn sẵn vì lý do đó.

### Nhịp học khuyến nghị

Bốn đến năm buổi một tuần, phần lớn dùng chế độ 10 phút, thỉnh thoảng một buổi
dài vào cuối tuần. Đều đặn ăn đứt cường độ, nhất là khi không có deadline nào
ép bạn.

### Hai việc nằm ngoài skill nhưng quan trọng không kém

**Cài Mazii trên điện thoại ngay hôm nay.** Từ điển Nhật-Việt, tra kanji ra
luôn âm Hán-Việt, nhận diện chữ bằng camera. Bạn sẽ cần nó mỗi khi gặp chữ lạ
trên bảng thông báo ở công ty.

**Nghe 5 phút mỗi ngày trên đường đi làm, kể cả khi chưa hiểu gì.** Skill có
thể phát âm từng từ nếu bạn bật TTS (xem mục *Bật phát âm*), soạn bản
shadowing, giao đúng đoạn cần nghe và kiểm tra lại ở buổi sau — nhưng giọng
người thật trong hội thoại phải đến từ nguồn ngoài. Nghe hiểu là kỹ năng chậm
nhất, và cách duy nhất là tiếp xúc âm thanh hằng ngày từ sớm.

---

## Bật phát âm (TTS)

Skill có thể đọc to từ mới và bản shadowing bằng giọng Nhật qua
`skills/nihongo-tutor-vn/scripts/speak.py`. Script tự chọn công cụ đầu tiên
chạy được theo thứ tự: **edge-tts** (giọng `ja-JP-NanamiNeural`) → **gTTS** →
`say -v Kyoko` (macOS) → Windows SAPI (chỉ khi máy có giọng tiếng Nhật). Phát
bằng `afplay` / `mpv` / `ffplay` / PowerShell tùy hệ điều hành.

```bash
python -m pip install edge-tts     # khuyến nghị; cần mạng khi phát
python skills/nihongo-tutor-vn/scripts/speak.py --check
python skills/nihongo-tutor-vn/scripts/speak.py "お疲れ様です"
python skills/nihongo-tutor-vn/scripts/speak.py "確認" --save kakunin.mp3
```

Ở buổi thiết lập, skill hỏi bạn có muốn bật phát âm không và lưu vào
`profile.tts`. Đổi sau bằng `progress.py set --key tts --value true|false`.
Khi tắt, hoặc script không chạy được, skill bỏ qua yên lặng — không lặp lại
thông báo lỗi ở mỗi từ.

**Kết quả kiểm tra thực tế trên máy phát triển** (Windows 11, Python 3.14):
`pip install edge-tts` cài được (bản 7.2.8) và phát được ngay qua PowerShell
(`System.Windows.Media.MediaPlayer`), mất khoảng 5–6 giây mỗi lần vì phải tổng
hợp qua mạng. gTTS chưa thử vì edge-tts đã đủ. Windows SAPI **không** dùng được
trên máy này vì chỉ có giọng en-US (David, Zira) — muốn dùng phải cài gói
giọng tiếng Nhật trong *Settings → Time & language → Speech*. `mpv`/`ffplay`
không có nhưng không cần.

---

## Scripts

Hai script trong `skills/nihongo-tutor-vn/scripts/`, Python 3, chỉ dùng thư
viện chuẩn (trừ TTS, xem mục trên). Skill gọi chúng thay vì tự tính toán —
với vài trăm từ vựng, để model tự đếm khoảng cách Leitner là chắc chắn sai.

**`progress.py`** — mọi thao tác với `~/.nihongo-tutor/progress.json` (ghi đè
đường dẫn bằng biến môi trường `NIHONGO_PROGRESS`). Ghi atomic qua file tạm,
nên ngắt giữa chừng không để lại file hỏng.

```bash
S=skills/nihongo-tutor-vn/scripts
python $S/progress.py init --name "Hùng" --romaji true --tts true --goals "..."
python $S/progress.py due --mode chuan            # hàng đợi ôn (thêm --all để bỏ giới hạn)
python $S/progress.py review --jp 確認 --result correct   # hesitant | wrong; --rule gentle
python $S/progress.py sample --n 12 --topic "công sở"     # ôn tổng hợp / theo chủ đề
python $S/progress.py mark-taught --jp 確認 --result good # chế độ dạy lại
python $S/progress.py session-end --mode chuẩn --score 4/5 --notes "..."
python $S/progress.py report
python $S/progress.py validate
python $S/test_progress.py                        # chạy 39 kiểm thử trên file tạm
```

Bảng lệnh đầy đủ: `skills/nihongo-tutor-vn/references/progress-format.md`.

**`speak.py`** — phát âm, xem mục *Bật phát âm*.

Trên Windows, nếu output tiếng Nhật bị lỗi mã hóa khi đi qua pipe, đặt
`PYTHONUTF8=1`.

---

## Nhật ký nâng cấp

Sáu mục làm ngày 2026-08-29, mỗi mục một commit.

**1. Tra cứu nhanh.** README hứa "hỏi từ bất kỳ lúc nào" nhưng SKILL.md không
có nhánh xử lý, nên "かくにん là gì" sẽ kích hoạt nguyên một buổi học. Thêm
nhánh vào Bước 0: trả lời gọn (nghĩa, cách đọc, Hán-Việt, ví dụ, ngữ cảnh công
ty), hỏi có thêm vào ôn tập không (`source: "lookup"`), không mở buổi học.

**2. Tính toán ôn tập bằng code.** Trước đây model phải tự so `session −
last_reviewed` với khoảng cách từng hộp trên toàn bộ danh sách — với vài trăm
mục sẽ bỏ sót, và ghi tay JSON có thể làm hỏng file. Viết `progress.py` (init,
due, review, add, add-kanji, add-grammar, add-kana, set, notes, session-end,
report, validate), ghi atomic; SKILL.md gọi script ở Bước 0/1/2/4/7 và Báo
cáo, giữ đoạn dự phòng thủ công. Định dạng file chuyển sang
`references/progress-format.md` để SKILL.md gọn.

**3. Phát âm (TTS).** Skill thuần văn bản dù máy phát được. Viết `speak.py`
(edge-tts → gTTS → say → SAPI, phát bằng afplay/mpv/ffplay/PowerShell); Bước 1
hỏi bật phát âm (`profile.tts`), Bước 5 phát sau mỗi từ mới, Bước 6 phát bản
shadowing; lỗi thì im lặng. Đã thử thật: edge-tts chạy được trên Windows.

**4. Danh sách từ N5 chuẩn.** Model tự nghĩ từ mới mỗi buổi nên lệch tần suất
và lạc khỏi N5. Thêm `references/vocab-n5.json` (509 từ, có `han_viet`,
`topic`, `priority`, nhóm công sở lấy từ `workplace-japanese.md`); Bước 5 chọn
từ đó, bỏ từ đã có, priority thấp trước, xoay vòng topic. Từ thu hoạch ở công
ty vẫn được chèn ngoài danh sách.

**5. Ôn bài độc lập.** Ôn chỉ tồn tại bên trong buổi học đầy đủ. Thêm chế độ
riêng với ba kiểu (đến hạn `due --all`, tổng hợp `sample` + quy tắc hộp nhẹ
`--rule gentle`, theo chủ đề `--topic/--type`), xoay vòng năm dạng câu hỏi
kể cả nghe qua TTS, gợi ý tổng hợp mỗi 7 buổi. Chi tiết ở
`references/review-mode.md`; `/on` cho Gemini CLI.

**6. Dạy lại.** Tính năng mới: người dùng giảng, AI đóng vai đồng nghiệp mới
chưa biết tiếng Nhật — hỏi chạm chỗ khó, đòi ví dụ, cố ý mắc một lỗi điển hình
của người Việt, tuyệt đối không sửa lúc đang giảng; sau đó quay lại vai gia sư
nhận xét. `mark-taught` cập nhật hộp (`taught: true`). Chi tiết ở
`references/teach-back.md`; `/day-lai` cho Gemini CLI.

---

## Dùng trên giao diện chat web hoặc app

Tải `skills/nihongo-tutor-vn/SKILL.md` lên đầu cuộc trò chuyện, kèm các file
trong `references/` nếu cần.

Hạn chế: môi trường chat không có hệ thống file bền vững, nên tiến độ **không
tự lưu**. Cuối mỗi buổi hãy xin file `progress.json` để tải về, rồi tải lên lại
ở buổi sau. Skill đã được viết để xử lý tình huống này.

---

## Tiến độ học tập

Lưu ở `~/.nihongo-tutor/progress.json`, định dạng JSON để sau này có thể đọc
bằng chương trình nếu bạn muốn tự viết app học tiếng Nhật. Mọi thao tác ghi đi
qua `scripts/progress.py`; cấu trúc đầy đủ ở
`skills/nihongo-tutor-vn/references/progress-format.md`.

File `.gitignore` đã loại `progress.json` ra khỏi repo — đây là dữ liệu học tập
cá nhân, không nên đẩy lên GitHub.

---

## Push lên GitHub

Thay `TÊN_CỦA_BẠN` trong `LICENSE`, `.claude-plugin/marketplace.json` và
`.claude-plugin/plugin.json` trước khi đẩy lên.

```bash
cd nihongo-tutor-vn
git init
git add .
git commit -m "Gia sư tiếng Nhật cho người Việt"
git branch -M main
git remote add origin https://github.com/TÊN_GITHUB_CỦA_BẠN/nihongo-tutor-vn.git
git push -u origin main
```

---

## Ghi công

Kiến trúc tham khảo ý tưởng từ [13rianK/japanese-tutor](https://github.com/13rianK/japanese-tutor)
— cấu trúc buổi học, file lưu tiến độ, và ý tưởng ôn tập giãn cách. Toàn bộ nội
dung trong repo này được viết mới, và có một số thay đổi thiết kế đáng kể:
sửa lỗi logic ôn tập giãn cách (bản gốc không phạt câu trả lời sai), bỏ streak
theo ngày, thêm phương pháp Hán-Việt, và hướng nội dung sang môi trường nhà máy.

## Giấy phép

MIT
