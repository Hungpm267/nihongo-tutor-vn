# Chế độ ôn bài độc lập

Đọc khi người dùng nói "ôn bài", "chỉ ôn thôi", "ôn lại", "hôm nay không học
mới", "ôn từ công sở", "ôn kanji", "ôn katakana". Trong chế độ này:

- **KHÔNG dạy nội dung mới.** Người dùng chọn ôn là chọn không nạp thêm.
- **KHÔNG có bước thu hoạch bắt buộc.** Nếu họ tự kể một từ nghe ở công ty thì
  vẫn nhận, giải nghĩa và `add --source workplace`, rồi quay lại ôn.
- Buổi ôn **vẫn là một buổi**: kết thúc bằng `session-end --mode ôn`, vì khoảng
  cách Leitner tính theo số buổi nên buổi ôn cũng phải đếm.

## Ba kiểu ôn

Hỏi người dùng muốn kiểu nào, hoặc tự chọn theo ngữ cảnh: nghỉ lâu và
`remaining` lớn → (a); `suggest_tong_hop: true` trong output `due` → đề xuất
(b); nhắc tới một chủ đề/loại → (c).

### a) Ôn đến hạn — dọn tồn đọng

```
python scripts/progress.py due --mode chuan --all
python scripts/progress.py review --jp "<mục>" --result correct|hesitant|wrong
```

Toàn bộ hàng đợi Leitner, không giới hạn 5/8 mục. Dùng sau kỳ nghỉ dài. Nếu
hàng đợi quá dài (trên ~25 mục) thì báo trước con số, ôn theo từng nhóm 10 và
hỏi sau mỗi nhóm có muốn tiếp không — không ép ôn hết trong một lần. Quy tắc
hộp chuẩn: sai → hộp 1.

### b) Ôn tổng hợp — kiểm tra thứ "nhớ chắc" có còn chắc không

```
python scripts/progress.py sample --n 12
python scripts/progress.py review --jp "<mục>" --result ... --rule gentle
```

Bốc ngẫu nhiên 10–15 mục từ **mọi hộp kể cả hộp 5**, script đã trộn xen kẽ
kana, từ vựng, kanji, ngữ pháp (không theo lô). Với mục `type: "kana"` chỉ hỏi
cách đọc, không gọi `review` (kana không có hộp).

**Quy tắc hộp riêng**: dùng `--rule gentle` — sai ở hộp 4–5 tụt về hộp 3, không
về hộp 1 như ôn thường, để một lần quên không xóa sạch tiến độ. Hộp 1–3 sai
vẫn về 1.

Skill tự đề xuất kiểu này mỗi 7 buổi: lệnh `due` trả `suggest_tong_hop: true`
khi số buổi đang diễn ra chia hết cho 7. Đề xuất một câu, người dùng từ chối
thì thôi.

### c) Ôn theo chủ đề hoặc loại

```
python scripts/progress.py sample --n 10 --topic "công sở"
python scripts/progress.py sample --n 10 --type kanji
python scripts/progress.py sample --n 10 --type katakana
python scripts/progress.py sample --n 10 --type vocabulary grammar --min-box 2
```

`--topic` khớp trường `topic` của từ vựng (không phân biệt hoa thường).
`--type` nhận `vocabulary`, `kanji`, `grammar`, `kana`, `hiragana`,
`katakana`, có thể nhiều giá trị. Quy tắc hộp chuẩn (`--rule standard`).

## Dạng câu hỏi — xen kẽ, không lặp hai lần liên tiếp

Xoay vòng năm dạng, mục kế tiếp phải khác dạng mục vừa hỏi:

1. **Nghĩa** — đưa tiếng Nhật, hỏi nghĩa tiếng Việt.
2. **Cách đọc** — đưa kanji/từ, hỏi đọc thế nào (kèm hỏi âm Hán-Việt nếu là
   từ Hán tự — đây là lúc củng cố mối nối Hán-Việt).
3. **Đặt câu** — yêu cầu một câu ngắn dùng từ/mẫu đó, ưu tiên bối cảnh công ty.
4. **Dịch ngược** — đưa tiếng Việt, hỏi tiếng Nhật.
5. **Nghe** — chỉ khi `profile.tts` bật: chạy
   `python scripts/speak.py "<từ>" --quiet` KHÔNG hiện chữ, hỏi nghe được từ
   gì. Nếu speak.py lỗi thì bỏ dạng này cho hết buổi, không báo lỗi lặp lại.

Với ngữ pháp, dạng 1 = "mẫu này dùng khi nào", dạng 3 và 4 như trên, bỏ dạng 2.

## Chấm và kết buổi

- Ghi kết quả từng mục **ngay sau khi hỏi** bằng `review`, không dồn.
- Sai thì giải thích ngắn tại chỗ, đưa lại câu ví dụ, rồi đi tiếp. Đây là ôn,
  không phải kỳ thi; giữ nhịp nhanh.
- Kết thúc:

```
python scripts/progress.py session-end --mode ôn --score "9/12" --notes "kiểu: tổng hợp; yếu: ..." --reviewed ...
```

Ghi vào `--notes` kiểu ôn đã dùng và những mục sai để buổi học thường sau ưu
tiên. Kết buổi bằng một điều làm tốt, một điều cần chú ý, một câu khích lệ —
ngắn.
