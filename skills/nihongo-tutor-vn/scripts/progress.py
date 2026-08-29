#!/usr/bin/env python3
"""Quản lý file tiến độ progress.json của nihongo-tutor-vn.

Chỉ dùng thư viện chuẩn Python 3. Mọi thao tác ghi đều ghi vào file tạm rồi
đổi tên, nên không bao giờ để lại file hỏng nếu bị ngắt giữa chừng.

Đường dẫn file: ~/.nihongo-tutor/progress.json, ghi đè bằng biến môi trường
NIHONGO_PROGRESS.

Ví dụ:
  progress.py init --name "Hùng" --romaji true --goals "nói chuyện với đồng nghiệp"
  progress.py due --mode chuan
  progress.py review --jp 確認 --result correct
  progress.py add --jp 確認 --reading かくにん --vi "xác nhận" --han-viet "XÁC NHẬN"
  progress.py session-end --mode chuẩn --score 4/5 --notes "..."
  progress.py report
  progress.py validate
"""

import argparse
import datetime as dt
import json
import os
import random
import sys
import tempfile

# Bảo đảm in được tiếng Nhật/tiếng Việt trên console Windows.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

LEITNER = {1: 1, 2: 2, 3: 4, 4: 8, 5: 16}
LIMIT = {"nhanh": 5, "chuan": 8, "sau": 8}
MODE_ALIASES = {
    "nhanh": "nhanh", "chuẩn": "chuan", "chuan": "chuan", "sâu": "sau",
    "sau": "sau", "ôn": "on", "on": "on", "dạy lại": "day-lai",
    "day-lai": "day-lai",
}
STAGES = ("kana", "foundation", "n5", "n4")
STAGE_VI = {"kana": "Kana", "foundation": "Nền tảng",
            "n5": "N5", "n4": "N4 và công sở"}
SESSION_MILESTONES = (5, 10, 25, 50, 100)
VOCAB_MILESTONES = (25, 50, 100, 200)
KANJI_MILESTONES = (10, 25, 50)
COMPRESS_THRESHOLD = 40   # số bản ghi sessions tối đa trước khi nén
COMPRESS_KEEP = 30        # giữ lại chừng này buổi gần nhất
TONG_HOP_EVERY = 7        # gợi ý ôn tổng hợp mỗi chừng này buổi
GENTLE_FLOOR = 3          # ôn tổng hợp: sai ở hộp 4–5 chỉ tụt về hộp này

# (tên collection, tên trường khóa, nhãn tiếng Việt)
COLLECTIONS = (
    ("vocabulary", "jp", "từ vựng"),
    ("kanji", "char", "kanji"),
    ("grammar", "pattern", "ngữ pháp"),
)


# ---------------------------------------------------------------- tiện ích

class ProgressError(Exception):
    pass


def progress_path():
    env = os.environ.get("NIHONGO_PROGRESS")
    if env:
        return os.path.expanduser(env)
    return os.path.join(os.path.expanduser("~"), ".nihongo-tutor", "progress.json")


def load(path):
    if not os.path.exists(path):
        raise ProgressError(
            f"Không tìm thấy file tiến độ: {path}\n"
            "Chạy `progress.py init` để tạo, hoặc đặt NIHONGO_PROGRESS.")
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ProgressError(f"File tiến độ không phải JSON hợp lệ: {e}")


def save(path, data):
    """Ghi atomic: file tạm cùng thư mục → os.replace."""
    d = os.path.dirname(path) or "."
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".progress-", suffix=".tmp", dir=d)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def today(args):
    if getattr(args, "date", None):
        try:
            dt.date.fromisoformat(args.date)
        except ValueError:
            raise ProgressError(f"--date phải có dạng YYYY-MM-DD, nhận: {args.date}")
        return args.date
    return dt.date.today().isoformat()


def parse_bool(s):
    v = str(s).strip().lower()
    if v in ("true", "1", "yes", "có", "co", "bật", "bat"):
        return True
    if v in ("false", "0", "no", "không", "khong", "tắt", "tat"):
        return False
    raise argparse.ArgumentTypeError(f"cần true/false, nhận: {s}")


def norm_mode(m):
    key = (m or "").strip().lower()
    if key not in MODE_ALIASES:
        raise ProgressError(
            f"Chế độ không hợp lệ: {m!r}. Dùng nhanh | chuẩn | sâu | ôn | dạy lại.")
    return MODE_ALIASES[key]


def current_session(data):
    """Số thứ tự của buổi ĐANG diễn ra."""
    return data["profile"]["session_count"] + 1


def out(obj):
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def find_item(data, key):
    """Tìm mục theo khóa trong cả ba collection. Trả (collection, item)."""
    for coll, field, _ in COLLECTIONS:
        for item in data.get(coll, []):
            if item.get(field) == key:
                return coll, item
    return None, None


def item_key(coll, item):
    for c, field, _ in COLLECTIONS:
        if c == coll:
            return item.get(field)
    return None


def item_view(coll, item):
    """Bản rút gọn để in ra cho gia sư dùng."""
    v = {"type": coll, "key": item_key(coll, item), "box": item.get("box")}
    for f in ("reading", "vi", "han_viet", "on", "kun", "topic", "source",
              "taught"):
        if f in item and item[f] not in (None, ""):
            v[f] = item[f]
    return v


def empty_progress(name, romaji, goals, tts, started):
    return {
        "profile": {
            "name": name,
            "started": started,
            "stage": "kana",
            "session_count": 0,
            "last_session_date": started,
            "sessions_last_7_days": 0,
            "romaji": romaji,
            "tts": tts,
            "goals": goals,
            "context": "IT generalist tại công ty Nhật, khu công nghiệp, từ 09/2026",
            "milestones": [],
        },
        "kana": {"hiragana_learned": [], "katakana_learned": []},
        "vocabulary": [],
        "kanji": [],
        "grammar": [],
        "sessions": [],
        "notes": "",
    }


# ---------------------------------------------------------------- lệnh con

def cmd_init(args):
    path = progress_path()
    if os.path.exists(path) and not args.force:
        raise ProgressError(
            f"File đã tồn tại: {path}. Thêm --force nếu thật sự muốn tạo lại "
            "(sẽ mất toàn bộ tiến độ cũ).")
    data = empty_progress(args.name, args.romaji, args.goals, args.tts, today(args))
    save(path, data)
    print(f"Đã tạo file tiến độ: {path}")


def due_items(data, limit=None):
    cur = current_session(data)
    items = []
    for coll, field, _ in COLLECTIONS:
        for item in data.get(coll, []):
            box = int(item.get("box", 1))
            last = item.get("last_reviewed", item.get("introduced", 0))
            gap = cur - int(last)
            if gap >= LEITNER.get(box, 1):
                v = item_view(coll, item)
                v["overdue_by"] = gap - LEITNER.get(box, 1)
                items.append(v)
    # hộp thấp trước; cùng hộp thì quá hạn lâu trước
    items.sort(key=lambda x: (x["box"], -x["overdue_by"]))
    total = len(items)
    if limit is not None:
        items = items[:limit]
    return cur, total, items


def cmd_due(args):
    data = load(progress_path())
    limit = None if args.all else LIMIT[norm_mode(args.mode)]
    cur, total, items = due_items(data, limit)
    out({
        "session": cur,
        "total_due": total,
        "shown": len(items),
        "remaining": total - len(items),
        "suggest_tong_hop": cur % TONG_HOP_EVERY == 0,
        "items": items,
    })


def cmd_sample(args):
    """Bốc ngẫu nhiên n mục từ mọi hộp, xen kẽ loại; lọc theo topic/type."""
    data = load(progress_path())
    types = set(args.type or [])
    want_kana = not types or types & {"kana", "hiragana", "katakana"}
    groups = {}
    for coll, field, _ in COLLECTIONS:
        if types and coll not in types:
            continue
        for item in data.get(coll, []):
            if int(item.get("box", 1)) < args.min_box:
                continue
            if args.topic and (item.get("topic") or "").lower() != args.topic.lower():
                continue
            groups.setdefault(coll, []).append(item_view(coll, item))
    if want_kana and not args.topic and args.min_box <= 1:
        for kind in ("hiragana", "katakana"):
            if types and not types & {"kana", kind}:
                continue
            for ch in data.get("kana", {}).get(f"{kind}_learned", []):
                groups.setdefault("kana", []).append(
                    {"type": "kana", "kind": kind, "key": ch, "box": None})
    rng = random.Random(args.seed)
    for g in groups.values():
        rng.shuffle(g)
    # xen kẽ: lấy vòng tròn mỗi loại một mục cho tới đủ n
    order = sorted(groups)
    rng.shuffle(order)
    picked = []
    while len(picked) < args.n and any(groups.values()):
        for t in order:
            if groups.get(t):
                picked.append(groups[t].pop())
                if len(picked) >= args.n:
                    break
    out({
        "session": current_session(data),
        "requested": args.n,
        "available": len(picked) + sum(len(g) for g in groups.values()),
        "filters": {"min_box": args.min_box, "topic": args.topic,
                    "type": sorted(types) or None},
        "items": picked,
    })


def cmd_review(args):
    path = progress_path()
    data = load(path)
    coll, item = find_item(data, args.jp)
    if item is None:
        raise ProgressError(f"Không tìm thấy mục: {args.jp!r}")
    old = int(item.get("box", 1))
    if args.result == "correct":
        new = min(old + 1, 5)
    elif args.result == "hesitant":
        new = old
    elif args.rule == "gentle" and old >= 4:
        new = GENTLE_FLOOR   # ôn tổng hợp: một lần quên không phạt về 1
    else:  # wrong
        new = 1
    item["box"] = new
    item["last_reviewed"] = current_session(data)
    save(path, data)
    out({"type": coll, "key": args.jp, "result": args.result, "rule": args.rule,
         "box_before": old, "box_after": new,
         "last_reviewed": item["last_reviewed"]})


def _add(args, coll, key_field, item):
    path = progress_path()
    data = load(path)
    existing_coll, existing = find_item(data, item[key_field])
    if existing is not None:
        raise ProgressError(
            f"Mục {item[key_field]!r} đã tồn tại trong {existing_coll} "
            f"(hộp {existing.get('box')}). Không thêm lại.")
    cur = current_session(data)
    item.update({"introduced": cur, "last_reviewed": cur, "box": 1})
    data.setdefault(coll, []).append(item)
    save(path, data)
    out({"added": coll, "item": item})


def cmd_add(args):
    _add(args, "vocabulary", "jp", {
        "jp": args.jp, "reading": args.reading, "vi": args.vi,
        "han_viet": args.han_viet, "topic": args.topic, "source": args.source,
    })


def cmd_add_kanji(args):
    _add(args, "kanji", "char", {
        "char": args.char, "han_viet": args.han_viet, "on": args.on,
        "kun": args.kun, "vi": args.vi,
    })


def cmd_add_grammar(args):
    _add(args, "grammar", "pattern", {"pattern": args.pattern, "vi": args.vi})


def cmd_add_kana(args):
    path = progress_path()
    data = load(path)
    field = f"{args.type}_learned"
    lst = data.setdefault("kana", {}).setdefault(field, [])
    added = []
    for ch in args.chars.replace(" ", "").replace("、", "").replace(",", ""):
        if ch not in lst:
            lst.append(ch)
            added.append(ch)
    save(path, data)
    out({"type": args.type, "added": added, "total": len(lst)})


def cmd_set(args):
    path = progress_path()
    data = load(path)
    key, raw = args.key, args.value
    if key not in data["profile"]:
        raise ProgressError(
            f"profile không có trường {key!r}. Có: {', '.join(data['profile'])}")
    if key == "stage":
        if raw not in STAGES:
            raise ProgressError(f"stage phải là một trong: {', '.join(STAGES)}")
        val = raw
    elif isinstance(data["profile"][key], bool):
        val = parse_bool(raw)
    elif isinstance(data["profile"][key], int):
        val = int(raw)
    else:
        val = raw
    data["profile"][key] = val
    save(path, data)
    out({"profile": {key: val}})


def cmd_notes(args):
    path = progress_path()
    data = load(path)
    data["notes"] = args.text
    save(path, data)
    print("Đã cập nhật ghi chú của gia sư.")


def _sessions_last_7_days(sessions, today_s):
    t = dt.date.fromisoformat(today_s)
    n = 0
    for s in sessions:
        if s.get("summary"):
            continue
        try:
            d = dt.date.fromisoformat(s["date"])
        except (KeyError, ValueError):
            continue
        if 0 <= (t - d).days < 7:
            n += 1
    return n


def _check_milestones(data):
    p = data["profile"]
    got = set(p.setdefault("milestones", []))
    new = []

    def hit(name, label):
        if name not in got:
            got.add(name)
            new.append(label)

    sc = p["session_count"]
    for m in SESSION_MILESTONES:
        if sc >= m:
            hit(f"sessions_{m}", f"{m} buổi học")
    if len(data["kana"].get("hiragana_learned", [])) >= 46:
        hit("hiragana_46", "thuộc đủ 46 hiragana")
    if len(data["kana"].get("katakana_learned", [])) >= 46:
        hit("katakana_46", "thuộc đủ 46 katakana")
    nv = len(data.get("vocabulary", []))
    for m in VOCAB_MILESTONES:
        if nv >= m:
            hit(f"vocab_{m}", f"{m} từ vựng")
    nk = len(data.get("kanji", []))
    for m in KANJI_MILESTONES:
        if nk >= m:
            hit(f"kanji_{m}", f"{m} kanji")
    p["milestones"] = sorted(got)
    return new


def _compress_sessions(sessions, session_count):
    """Nếu vượt 40 bản ghi: gộp các buổi cũ hơn 30 buổi thành một mục tóm tắt."""
    if len(sessions) <= COMPRESS_THRESHOLD:
        return sessions, False
    cutoff = session_count - COMPRESS_KEEP  # n <= cutoff thì bị gộp
    old = [s for s in sessions if s.get("summary") or s.get("n", 0) <= cutoff]
    keep = [s for s in sessions if not (s.get("summary") or s.get("n", 0) <= cutoff)]
    if not old:
        return sessions, False
    prev = next((s for s in old if s.get("summary")), None)
    real = [s for s in old if not s.get("summary")]
    count = (prev["count"] if prev else 0) + len(real)
    n_from = prev["n_from"] if prev else min(s["n"] for s in real)
    n_to = max([s["n"] for s in real] + ([prev["n_to"]] if prev else []))
    modes = dict(prev.get("modes", {})) if prev else {}
    for s in real:
        modes[s.get("mode", "?")] = modes.get(s.get("mode", "?"), 0) + 1
    finds = list(prev.get("workplace_finds", [])) if prev else []
    for s in real:
        for w in s.get("workplace_finds", []) or []:
            if w not in finds:
                finds.append(w)
    date_from = prev["date_from"] if prev else min(s.get("date", "") for s in real)
    date_to = max([s.get("date", "") for s in real] + ([prev["date_to"]] if prev else []))
    summary = {
        "summary": True,
        "n_from": n_from, "n_to": n_to, "count": count,
        "date_from": date_from, "date_to": date_to,
        "modes": modes,
        "workplace_finds": finds,
        "notes": f"Tóm tắt {count} buổi (buổi {n_from}–{n_to}). "
                 "Chi tiết từng buổi đã được gộp để file không phình.",
    }
    return [summary] + keep, True


def cmd_session_end(args):
    path = progress_path()
    data = load(path)
    p = data["profile"]
    date = today(args)
    mode_key = norm_mode(args.mode)
    mode_label = {"nhanh": "nhanh", "chuan": "chuẩn", "sau": "sâu",
                  "on": "ôn", "day-lai": "dạy lại"}[mode_key]
    p["session_count"] += 1
    n = p["session_count"]
    record = {
        "n": n, "date": date, "mode": mode_label,
        "new_items": args.new_items or [],
        "reviewed": args.reviewed or [],
        "workplace_finds": args.workplace_finds or [],
        "score": args.score or "",
        "notes": args.notes or "",
    }
    if args.topic:
        record["topic"] = args.topic
    data.setdefault("sessions", []).append(record)
    p["last_session_date"] = date
    p["sessions_last_7_days"] = _sessions_last_7_days(data["sessions"], date)
    new_ms = _check_milestones(data)
    data["sessions"], compressed = _compress_sessions(data["sessions"], n)
    save(path, data)
    out({
        "session": n, "date": date, "mode": mode_label,
        "sessions_last_7_days": p["sessions_last_7_days"],
        "new_milestones": new_ms,
        "sessions_compressed": compressed,
        "sessions_records": len(data["sessions"]),
    })


def cmd_report(args):
    data = load(progress_path())
    p = data["profile"]
    vocab = data.get("vocabulary", [])
    real_sessions = [s for s in data.get("sessions", []) if not s.get("summary")]
    last3 = real_sessions[-3:]
    scores = ", ".join(f"buổi {s['n']}: {s.get('score') or '—'}" for s in last3) or "—"
    workplace = sum(1 for v in vocab if v.get("source") == "workplace")
    strong = sum(1 for v in vocab if int(v.get("box", 1)) >= 4)
    building = sum(1 for v in vocab if int(v.get("box", 1)) <= 2)
    _, total_due, _ = due_items(data)
    last_notes = last3[-1].get("notes", "") if last3 else ""
    bar = "━" * 35
    print(bar)
    print(f"Tiến độ tiếng Nhật của {p.get('name') or '(chưa đặt tên)'}")
    print(bar)
    print()
    print("📊 TỔNG QUAN")
    print(f"  Giai đoạn: {STAGE_VI.get(p.get('stage'), p.get('stage'))}")
    print(f"  Số buổi đã học: {p.get('session_count', 0)}")
    print(f"  Nhịp độ: {p.get('sessions_last_7_days', 0)} buổi trong 7 ngày qua")
    print(f"  Buổi gần nhất: {p.get('last_session_date', '—')}")
    print()
    print("✍️ CHỮ VIẾT")
    k = data.get("kana", {})
    print(f"  Hiragana: {len(k.get('hiragana_learned', []))}/46"
          f"    Katakana: {len(k.get('katakana_learned', []))}/46")
    print()
    print("📝 TỪ VỰNG")
    print(f"  Tổng: {len(vocab)} từ   (trong đó {workplace} từ thu được ở công ty)")
    print(f"  Hộp 4–5 (nhớ chắc): {strong}")
    print(f"  Hộp 1–2 (đang xây): {building}")
    print()
    print(f"🈶 KANJI: {len(data.get('kanji', []))} chữ")
    print(f"📐 NGỮ PHÁP: {len(data.get('grammar', []))} điểm")
    print(f"⏳ ĐẾN HẠN ÔN: {total_due} mục")
    print()
    print("📈 GẦN ĐÂY")
    print(f"  Điểm 3 buổi gần nhất: {scores}")
    print(f"  Ghi chú buổi gần nhất: {last_notes or '—'}")
    print(f"  Ghi chú gia sư: {data.get('notes') or '—'}")
    print(f"  Làm tốt: [gia sư điền từ ghi chú trên]")
    print(f"  Cần chú ý: [gia sư điền từ ghi chú trên]")
    print()
    print("🎯 BUỔI TỚI: [gia sư điền theo roadmap.md và giai đoạn hiện tại]")
    print(bar)


# ---------------------------------------------------------------- validate

def validate(data):
    errs = []

    def need(obj, key, typ, where):
        if key not in obj:
            errs.append(f"{where}: thiếu trường '{key}'")
            return False
        if typ is not None and not isinstance(obj[key], typ):
            errs.append(f"{where}.{key}: kiểu {type(obj[key]).__name__}, "
                        f"cần {typ.__name__ if not isinstance(typ, tuple) else '/'.join(t.__name__ for t in typ)}")
            return False
        return True

    if not isinstance(data, dict):
        return ["Gốc file phải là một object JSON"]
    for key, typ in (("profile", dict), ("kana", dict), ("vocabulary", list),
                     ("kanji", list), ("grammar", list), ("sessions", list),
                     ("notes", str)):
        need(data, key, typ, "root")
    if errs:
        return errs

    p = data["profile"]
    for key, typ in (("name", str), ("started", str), ("stage", str),
                     ("session_count", int), ("last_session_date", str),
                     ("sessions_last_7_days", int), ("romaji", bool),
                     ("goals", str), ("milestones", list)):
        need(p, key, typ, "profile")
    if "tts" in p and not isinstance(p["tts"], bool):
        errs.append("profile.tts phải là true/false")
    if p.get("stage") not in STAGES:
        errs.append(f"profile.stage = {p.get('stage')!r}, cần một trong {STAGES}")
    for f in ("started", "last_session_date"):
        try:
            dt.date.fromisoformat(str(p.get(f, "")))
        except ValueError:
            errs.append(f"profile.{f} không phải ngày YYYY-MM-DD: {p.get(f)!r}")

    for f in ("hiragana_learned", "katakana_learned"):
        if need(data["kana"], f, list, "kana"):
            lst = data["kana"][f]
            if len(set(lst)) != len(lst):
                errs.append(f"kana.{f} có chữ lặp")

    sc = p.get("session_count", 0)
    required = {
        "vocabulary": ("jp", "reading", "vi"),
        "kanji": ("char", "han_viet", "vi"),
        "grammar": ("pattern", "vi"),
    }
    for coll, field, _ in COLLECTIONS:
        seen = set()
        for i, item in enumerate(data[coll]):
            where = f"{coll}[{i}]"
            if not isinstance(item, dict):
                errs.append(f"{where}: không phải object")
                continue
            for r in required[coll]:
                if not item.get(r):
                    errs.append(f"{where}: thiếu '{r}'")
            k = item.get(field)
            if k in seen:
                errs.append(f"{where}: khóa {k!r} bị trùng")
            seen.add(k)
            box = item.get("box")
            if not isinstance(box, int) or not 1 <= box <= 5:
                errs.append(f"{where} ({k}): box = {box!r}, cần số nguyên 1–5")
            for f in ("introduced", "last_reviewed"):
                v = item.get(f)
                if v is None and f == "last_reviewed":
                    continue  # chấp nhận thiếu, coi như = introduced
                if not isinstance(v, int) or v < 0:
                    errs.append(f"{where} ({k}): {f} = {v!r}, cần số nguyên ≥ 0")
                elif isinstance(sc, int) and v > sc + 1:
                    errs.append(f"{where} ({k}): {f} = {v} lớn hơn buổi hiện tại {sc + 1}")

    ns = [s.get("n") for s in data["sessions"] if not s.get("summary")]
    for i, s in enumerate(data["sessions"]):
        where = f"sessions[{i}]"
        if s.get("summary"):
            for f in ("n_from", "n_to", "count"):
                if not isinstance(s.get(f), int):
                    errs.append(f"{where} (tóm tắt): thiếu/sai '{f}'")
            continue
        if not isinstance(s.get("n"), int):
            errs.append(f"{where}: 'n' phải là số nguyên")
        try:
            dt.date.fromisoformat(str(s.get("date", "")))
        except ValueError:
            errs.append(f"{where}: date không hợp lệ: {s.get('date')!r}")
    if ns and len(set(ns)) != len(ns):
        errs.append("sessions: có số buổi 'n' bị trùng")
    if ns and isinstance(sc, int) and max(ns) > sc:
        errs.append(f"sessions: buổi lớn nhất {max(ns)} > session_count {sc}")
    if len(data["sessions"]) > COMPRESS_THRESHOLD + 1:
        errs.append(f"sessions: {len(data['sessions'])} bản ghi, chưa được nén "
                    f"(ngưỡng {COMPRESS_THRESHOLD})")
    return errs


def cmd_validate(args):
    path = progress_path()
    data = load(path)
    errs = validate(data)
    if errs:
        print(f"File {path} có {len(errs)} lỗi:")
        for e in errs:
            print(f"  - {e}")
        sys.exit(1)
    print(f"OK: {path} hợp lệ "
          f"({len(data['vocabulary'])} từ, {len(data['kanji'])} kanji, "
          f"{len(data['grammar'])} ngữ pháp, {data['profile']['session_count']} buổi).")


# ---------------------------------------------------------------- main

def build_parser():
    ap = argparse.ArgumentParser(
        description="Quản lý tiến độ học tiếng Nhật (nihongo-tutor-vn).")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("init", help="tạo file tiến độ mới")
    s.add_argument("--name", required=True)
    s.add_argument("--romaji", type=parse_bool, required=True)
    s.add_argument("--goals", default="")
    s.add_argument("--tts", type=parse_bool, default=False,
                   help="bật phát âm bằng speak.py")
    s.add_argument("--date", help="ngày bắt đầu (mặc định hôm nay)")
    s.add_argument("--force", action="store_true", help="ghi đè file đã có")
    s.set_defaults(fn=cmd_init)

    s = sub.add_parser("due", help="liệt kê mục đến hạn ôn")
    s.add_argument("--mode", default="chuan", help="nhanh | chuẩn | sâu")
    s.add_argument("--all", action="store_true",
                   help="toàn bộ hàng đợi, không giới hạn số mục")
    s.set_defaults(fn=cmd_due)

    s = sub.add_parser("sample", help="bốc ngẫu nhiên mục từ mọi hộp (ôn tổng hợp / theo chủ đề)")
    s.add_argument("--n", type=int, default=12, help="số mục (mặc định 12)")
    s.add_argument("--min-box", dest="min_box", type=int, default=1)
    s.add_argument("--topic", default=None, help="lọc theo topic, ví dụ 'công sở'")
    s.add_argument("--type", nargs="*", default=None,
                   help="vocabulary kanji grammar kana hiragana katakana")
    s.add_argument("--seed", type=int, default=None, help="cố định ngẫu nhiên (kiểm thử)")
    s.set_defaults(fn=cmd_sample)

    s = sub.add_parser("review", help="ghi kết quả ôn một mục")
    s.add_argument("--jp", required=True, help="từ / kanji / mẫu ngữ pháp")
    s.add_argument("--result", required=True,
                   choices=["correct", "hesitant", "wrong"])
    s.add_argument("--rule", default="standard", choices=["standard", "gentle"],
                   help="gentle = ôn tổng hợp: sai ở hộp 4–5 tụt về hộp 3")
    s.set_defaults(fn=cmd_review)

    s = sub.add_parser("add", help="thêm từ vựng mới (hộp 1)")
    s.add_argument("--jp", required=True)
    s.add_argument("--reading", required=True)
    s.add_argument("--vi", required=True)
    s.add_argument("--han-viet", dest="han_viet", default=None)
    s.add_argument("--topic", default=None)
    s.add_argument("--source", default="lesson",
                   help="lesson | workplace | lookup | n5")
    s.set_defaults(fn=cmd_add)

    s = sub.add_parser("add-kanji", help="thêm kanji mới (hộp 1)")
    s.add_argument("--char", required=True)
    s.add_argument("--han-viet", dest="han_viet", required=True)
    s.add_argument("--on", default="")
    s.add_argument("--kun", default="")
    s.add_argument("--vi", required=True)
    s.set_defaults(fn=cmd_add_kanji)

    s = sub.add_parser("add-grammar", help="thêm điểm ngữ pháp mới (hộp 1)")
    s.add_argument("--pattern", required=True)
    s.add_argument("--vi", required=True)
    s.set_defaults(fn=cmd_add_grammar)

    s = sub.add_parser("add-kana", help="ghi nhận kana đã học")
    s.add_argument("--type", required=True, choices=["hiragana", "katakana"])
    s.add_argument("--chars", required=True, help="ví dụ: あいうえお")
    s.set_defaults(fn=cmd_add_kana)

    s = sub.add_parser("set", help="đổi một trường trong profile (stage, tts, romaji...)")
    s.add_argument("--key", required=True)
    s.add_argument("--value", required=True)
    s.set_defaults(fn=cmd_set)

    s = sub.add_parser("notes", help="ghi đè ghi chú của gia sư")
    s.add_argument("--text", required=True)
    s.set_defaults(fn=cmd_notes)

    s = sub.add_parser("session-end", help="kết thúc buổi, ghi bản ghi sessions")
    s.add_argument("--mode", required=True, help="nhanh | chuẩn | sâu | ôn | dạy lại")
    s.add_argument("--score", default="")
    s.add_argument("--notes", default="")
    s.add_argument("--topic", default=None, help="chủ đề (chế độ dạy lại)")
    s.add_argument("--new-items", dest="new_items", nargs="*")
    s.add_argument("--reviewed", nargs="*")
    s.add_argument("--workplace-finds", dest="workplace_finds", nargs="*")
    s.add_argument("--date", help="ghi đè ngày (chỉ để kiểm thử)")
    s.set_defaults(fn=cmd_session_end)

    s = sub.add_parser("report", help="in báo cáo tiến độ")
    s.set_defaults(fn=cmd_report)

    s = sub.add_parser("validate", help="kiểm tra file hợp lệ")
    s.set_defaults(fn=cmd_validate)
    return ap


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        args.fn(args)
    except ProgressError as e:
        print(f"Lỗi: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
