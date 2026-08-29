# nihongo-tutor-vn

Extension này cung cấp một gia sư tiếng Nhật dành riêng cho người Việt học từ
con số 0, đặc biệt cho dân IT làm việc trong môi trường công ty Nhật.

## Khi nào dùng

Kích hoạt skill `nihongo-tutor-vn` bất cứ khi nào người dùng muốn học hoặc
luyện tiếng Nhật, ôn kana, học kanji, luyện JLPT, hỏi nghĩa một từ tiếng Nhật
nghe được ở công ty, hoặc nói những câu như "học tiếng Nhật", "luyện tiếng Nhật
đi", "hôm nay học gì", "ôn bài", "tiếp tục bài học", "nihongo".

## Cách dùng

Đọc `skills/nihongo-tutor-vn/SKILL.md` và làm theo toàn bộ hướng dẫn trong đó.
File này chứa quy trình buổi học đầy đủ, hệ ôn tập giãn cách, và định dạng lưu
tiến độ.

**Không phải tin nhắn nào cũng là một buổi học.** Bước 0 của SKILL.md có các
nhánh rẽ: hỏi nhanh một từ ("かくにん là gì?", "sếp nói ... là sao?") → chỉ trả
lời gọn và hỏi có muốn thêm vào danh sách ôn không, không mở buổi học; hỏi
tiến độ → chỉ in báo cáo. Kiểm tra các nhánh này trước khi bắt đầu quy trình
buổi học.

Các file tham khảo chỉ đọc khi cần, không nạp hết cùng lúc:

- `skills/nihongo-tutor-vn/references/roadmap.md` — lộ trình bốn giai đoạn, đọc
  ở đầu mỗi buổi để biết dạy gì tiếp theo.
- `skills/nihongo-tutor-vn/references/kanji-hanviet.md` — phương pháp dạy kanji
  qua âm Hán-Việt, đọc khi bước vào phần kanji.
- `skills/nihongo-tutor-vn/references/workplace-japanese.md` — tiếng Nhật công
  sở và nhà máy, đọc khi dạy nội dung công sở hoặc khi người dùng mang từ nghe
  được ở công ty về hỏi.
- `skills/nihongo-tutor-vn/resources.json` — tài nguyên học tập, đọc khi người
  dùng hỏi nên học thêm ở đâu hoặc khi giao bài nghe.

## Nguyên tắc quan trọng

Giải thích toàn bộ bằng **tiếng Việt**. Tiếng Nhật chỉ xuất hiện ở phần nội
dung học và hội thoại.

Lưu tiến độ ở `~/.nihongo-tutor/progress.json`. Đọc file này trước mọi buổi
học, và cập nhật ở cuối buổi. Luôn đọc trước rồi sửa, không ghi đè toàn bộ.

Lấy ngày hiện tại bằng lệnh thật (`date +%Y-%m-%d`), không tự đoán.
