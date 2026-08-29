# Định dạng progress.json và bảng lệnh progress.py

Đọc khi cần sửa file tiến độ bằng tay (không chạy được script) hoặc khi
`validate` báo lỗi cấu trúc. Bình thường không cần nạp file này.

## Bảng lệnh `scripts/progress.py`

Đường dẫn file mặc định `~/.nihongo-tutor/progress.json`; ghi đè bằng biến môi
trường `NIHONGO_PROGRESS`. Mọi lệnh ghi đều ghi vào file tạm rồi đổi tên
(atomic), nên ngắt giữa chừng không để lại file hỏng. Lệnh lỗi trả mã thoát 2
và in `Lỗi: ...` ra stderr.

| Lệnh | Việc |
|---|---|
| `init --name --romaji true\|false [--goals] [--tts true\|false]` | Tạo file mới. Từ chối nếu đã có, trừ khi `--force`. |
| `validate` | Kiểm tra cấu trúc, báo từng lỗi cụ thể. Mã thoát 1 nếu lỗi. |
| `due --mode nhanh\|chuan\|sau [--all]` | Hàng đợi Leitner đến hạn (JSON). Giới hạn 5/8 mục; `--all` bỏ giới hạn. Hộp thấp trước. Trả thêm `suggest_tong_hop: true` khi buổi đang diễn ra chia hết cho 7. |
| `review --jp "<mục>" --result correct\|hesitant\|wrong [--rule standard\|gentle]` | Cập nhật hộp (+1 / giữ / về 1) và `last_reviewed` = buổi đang diễn ra. `gentle` (ôn tổng hợp): sai ở hộp 4–5 chỉ tụt về 3. Tìm trong cả từ vựng, kanji, ngữ pháp. |
| `sample --n <số> [--min-box <n>] [--topic "..."] [--type vocabulary kanji grammar kana hiragana katakana]` | Bốc ngẫu nhiên từ mọi hộp, xen kẽ loại (mục kana có `box: null`). Dùng cho ôn tổng hợp / theo chủ đề. |
| `add --jp --reading --vi [--han-viet] [--topic] [--source]` | Thêm từ vựng, hộp 1. Từ chối nếu trùng. `source`: lesson (mặc định), workplace, lookup, n5. |
| `add-kanji --char --han-viet [--on] [--kun] --vi` | Thêm kanji, hộp 1. |
| `add-grammar --pattern --vi` | Thêm điểm ngữ pháp, hộp 1. |
| `add-kana --type hiragana\|katakana --chars "あいうえお"` | Ghi nhận kana đã học (bỏ qua chữ đã có). |
| `set --key <trường> --value <giá trị>` | Đổi một trường trong `profile` (stage, tts, romaji, goals...). |
| `notes --text "..."` | Ghi đè ghi chú của gia sư (`notes` ở gốc file). |
| `session-end --mode <chế độ> [--score] [--notes] [--topic] [--new-items ...] [--reviewed ...] [--workplace-finds ...]` | Thêm bản ghi `sessions`, tăng `session_count`, ghi ngày hệ thống, tính nhịp 7 ngày, kiểm tra mốc, nén khi >40 bản ghi. In `new_milestones`. |
| `report` | In khung báo cáo tiến độ (xem mẫu dưới). |

Chế độ hợp lệ cho `--mode`: `nhanh`, `chuẩn`/`chuan`, `sâu`/`sau`, `ôn`/`on`,
`dạy lại`/`day-lai`.

Trên Windows, nếu output tiếng Nhật bị lỗi mã hóa khi đi qua ống lệnh, đặt
`PYTHONUTF8=1`.

## Quy tắc tính toán

- **Buổi đang diễn ra** = `session_count + 1`. `review` và `add` ghi số này
  vào `last_reviewed`/`introduced`; `session-end` mới tăng `session_count`.
- **Đến hạn** khi `(session_count + 1) − last_reviewed ≥ khoảng cách hộp`:
  hộp 1 → 1 buổi, 2 → 2, 3 → 4, 4 → 8, 5 → 16. Thiếu `last_reviewed` thì dùng
  `introduced`.
- **Nhịp 7 ngày** = số bản ghi `sessions` có `date` trong 7 ngày gần nhất tính
  từ ngày buổi vừa kết thúc.
- **Mốc thành tích** (ghi vào `profile.milestones`, mỗi mốc chỉ báo một lần):
  `sessions_5/10/25/50/100`, `hiragana_46`, `katakana_46`,
  `vocab_25/50/100/200`, `kanji_10/25/50`.
- **Nén sessions**: khi vượt 40 bản ghi, các buổi có `n ≤ session_count − 30`
  được gộp vào một bản ghi `{"summary": true, ...}` đứng đầu danh sách (gộp
  tiếp vào bản tóm tắt cũ nếu đã có), giữ 30 buổi gần nhất chi tiết.

## Cấu trúc file

```json
{
  "profile": {
    "name": "",
    "started": "YYYY-MM-DD",
    "stage": "kana",
    "session_count": 0,
    "last_session_date": "YYYY-MM-DD",
    "sessions_last_7_days": 0,
    "romaji": true,
    "tts": false,
    "goals": "",
    "context": "IT generalist tại công ty Nhật, khu công nghiệp, từ 09/2026",
    "milestones": []
  },
  "kana": {
    "hiragana_learned": [],
    "katakana_learned": []
  },
  "vocabulary": [
    {
      "jp": "確認",
      "reading": "かくにん",
      "vi": "xác nhận",
      "han_viet": "XÁC NHẬN",
      "topic": "công sở",
      "source": "workplace",
      "introduced": 3,
      "last_reviewed": 5,
      "box": 2
    }
  ],
  "kanji": [
    {
      "char": "人",
      "han_viet": "NHÂN",
      "on": "ジン・ニン",
      "kun": "ひと",
      "vi": "người",
      "introduced": 4,
      "last_reviewed": 4,
      "box": 1
    }
  ],
  "grammar": [
    { "pattern": "〜です", "vi": "thể lịch sự", "introduced": 2, "last_reviewed": 2, "box": 3 }
  ],
  "sessions": [
    {
      "summary": true,
      "n_from": 1, "n_to": 11, "count": 11,
      "date_from": "YYYY-MM-DD", "date_to": "YYYY-MM-DD",
      "modes": { "nhanh": 8, "chuẩn": 3 },
      "workplace_finds": [],
      "notes": "Tóm tắt 11 buổi (buổi 1–11)."
    },
    {
      "n": 12,
      "date": "YYYY-MM-DD",
      "mode": "chuẩn",
      "new_items": [],
      "reviewed": [],
      "workplace_finds": [],
      "score": "4/5",
      "notes": ""
    }
  ],
  "notes": "Ghi chú của gia sư: điểm mạnh, lỗi lặp lại, kế hoạch buổi sau."
}
```

Trường `stage` nhận một trong: `kana`, `foundation`, `n5`, `n4`. `source`
của từ vựng: `lesson`, `workplace`, `lookup`, `n5`. Mục đã được người dùng
giảng lại đúng (chế độ dạy lại) có thêm `"taught": true`.

## Mẫu báo cáo tiến độ

`report` in đúng khung này, ba dòng trong ngoặc vuông do gia sư điền:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Tiến độ tiếng Nhật của [tên]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 TỔNG QUAN
  Giai đoạn: [giai đoạn hiện tại]
  Số buổi đã học: [N]
  Nhịp độ: [N] buổi trong 7 ngày qua
  Buổi gần nhất: [ngày]

✍️ CHỮ VIẾT
  Hiragana: [N]/46    Katakana: [N]/46

📝 TỪ VỰNG
  Tổng: [N] từ   (trong đó [N] từ thu được ở công ty)
  Hộp 4–5 (nhớ chắc): [N]
  Hộp 1–2 (đang xây): [N]

🈶 KANJI: [N] chữ
📐 NGỮ PHÁP: [N] điểm
⏳ ĐẾN HẠN ÔN: [N] mục

📈 GẦN ĐÂY
  Điểm 3 buổi gần nhất: [...]
  Làm tốt: [gia sư điền]
  Cần chú ý: [gia sư điền]

🎯 BUỔI TỚI: [gia sư điền theo roadmap]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Không hiển thị streak theo ngày liên tiếp.
