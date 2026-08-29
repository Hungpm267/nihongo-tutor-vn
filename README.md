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
│   └── nihongo.toml              # Lệnh /nihongo cho Gemini CLI
├── skills/
│   └── nihongo-tutor-vn/         # Nội dung dùng chung cho cả hai công cụ
│       ├── SKILL.md              # Hướng dẫn chính
│       ├── resources.json        # Tài nguyên học, có nguồn tiếng Việt
│       └── references/
│           ├── roadmap.md
│           ├── kanji-hanviet.md
│           └── workplace-japanese.md
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
```

Hoặc nói tự nhiên như với Claude Code — `GEMINI.md` đã hướng dẫn model tự kích
hoạt skill khi bạn nhắc tới việc học tiếng Nhật.

---

## Quy trình sử dụng

Buổi đầu tiên khác các buổi sau, nên tách riêng.

### Buổi đầu tiên (~15 phút)

Mở terminal, chạy Claude Code hoặc Gemini CLI ở bất kỳ thư mục nào, gõ "học
tiếng Nhật" (hoặc `/nihongo` với Gemini CLI). Skill tìm
`~/.nihongo-tutor/progress.json`, không thấy nên biết đây là lần đầu.

Nó hỏi bốn câu ngắn: tên gọi, mỗi lần học được bao lâu và mấy lần một tuần, có
muốn hiển thị romaji không, và mục tiêu của bạn. **Không có bài kiểm tra trình
độ** — nếu bạn bắt đầu từ 0 thì kiểm tra là vô nghĩa và chỉ gây nản.

Trả lời xong, nó tạo file tiến độ rồi dạy luôn trong cùng buổi đó: 5 chữ
hiragana あいうえお và 5 katakana アイウエオ tương ứng. Đây là chủ ý — bạn phải
rời buổi đầu tiên với cảm giác đã học được thứ gì thật, không phải chỉ ngồi
trả lời câu hỏi thiết lập.

### Các buổi sau

Vẫn gõ "học tiếng Nhật". Skill đọc tiến độ, biết bạn đang ở đâu, rồi chạy theo
trình tự:

1. **Thu hoạch** — hỏi hôm nay ở công ty bạn có nghe hay thấy tiếng Nhật nào lạ
   không. Một từ sếp hay nói, một dòng trên bảng thông báo, kể cả chỉ nhớ mang
   máng cách phát âm cũng đưa vào được, skill sẽ đoán giúp. Không có gì thì bỏ
   qua, không sao cả.
2. **Chọn chế độ** — hôm nay bạn có bao nhiêu thời gian. Trả lời thật. "10 phút
   thôi" là câu trả lời hợp lệ và vẫn tính đủ một buổi.
3. **Ôn tập giãn cách** — vài từ đến hạn, dạng câu hỏi thay đổi liên tục.
4. **Nội dung mới** — kana, từ vựng, kanji, hoặc ngữ pháp tùy giai đoạn.
5. **Hội thoại** — bỏ qua ở chế độ 10 phút.
6. **Bài tập và lưu tiến độ.**

### Mấy câu đáng thuộc

| Gõ | Kết quả |
|---|---|
| `học tiếng Nhật` | Bắt đầu buổi học |
| `hôm nay tôi chỉ có 10 phút` | Chạy chế độ ngắn |
| `tiến độ tới đâu rồi` | Bảng tổng kết |
| `gợi ý` | Xin trợ giúp giữa lúc hội thoại |
| `sếp nói かくにん là gì vậy?` | Hỏi lẻ, không cần đang trong buổi học |

### Dùng chung tiến độ giữa hai công cụ

Cả Claude Code và Gemini CLI đều đọc ghi cùng file
`~/.nihongo-tutor/progress.json`. Học bằng Claude Code hôm nay, mai mở Gemini
CLI học tiếp, tiến độ vẫn liền mạch. Bạn không bị khóa vào một công cụ nào.

Đổi lại, file đó là toàn bộ trí nhớ của gia sư — mất nó là mất sạch. Nên
thỉnh thoảng sao lưu, hoặc đẩy vào một repo **private** riêng. Đừng đẩy vào
repo skill public; `.gitignore` đã chặn sẵn vì lý do này.

### Nhịp học khuyến nghị

Bốn đến năm buổi một tuần, phần lớn dùng chế độ 10 phút, thỉnh thoảng một buổi
dài vào cuối tuần. Đều đặn ăn đứt cường độ, nhất là khi không có deadline nào
ép bạn cả.

Hai việc nằm ngoài skill nhưng quan trọng không kém:

- **Cài Mazii trên điện thoại** để tra chữ lạ ngay tại công ty. Nó hiện luôn âm
  Hán-Việt của kanji, đúng thứ skill này dựa vào.
- **Nghe 5 phút mỗi ngày** trên đường đi làm, kể cả khi chưa hiểu gì. Skill
  không phát được âm thanh, phần nghe phải đến từ nguồn ngoài.

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

### Mấy câu đáng thuộc

| Gõ gì | Kết quả |
|---|---|
| `học tiếng Nhật` | Bắt đầu buổi học |
| `hôm nay chỉ có 10 phút` | Chạy chế độ Nhanh |
| `tiến độ tới đâu rồi` | Hiện bảng tổng kết |
| `gợi ý` | Xin trợ giúp giữa hội thoại (không cho luôn đáp án) |
| `hôm nay sếp nói かくにん là gì vậy?` | Hỏi từ bất kỳ lúc nào, không cần đang học |

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

**Nghe 5 phút mỗi ngày trên đường đi làm, kể cả khi chưa hiểu gì.** Skill không
phát được âm thanh — nó soạn bản shadowing, giao đúng đoạn cần nghe và kiểm tra
lại ở buổi sau, nhưng phần nghe thật phải đến từ nguồn ngoài. Nghe hiểu là kỹ
năng chậm nhất, và cách duy nhất là tiếp xúc âm thanh hằng ngày từ sớm.

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
bằng chương trình nếu bạn muốn tự viết app học tiếng Nhật. Xem cấu trúc đầy đủ
ở cuối `skills/nihongo-tutor-vn/SKILL.md`.

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