#!/usr/bin/env python3
"""Kiểm thử progress.py trên một file tạm. Chạy: python test_progress.py

Không đụng tới ~/.nihongo-tutor/progress.json thật — đặt NIHONGO_PROGRESS trỏ
tới thư mục tạm của riêng nó.
"""

import datetime as dt
import json
import os
import subprocess
import sys
import tempfile

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "progress.py")
TMP = tempfile.mkdtemp(prefix="nihongo-test-")
PATH = os.path.join(TMP, "progress.json")
ENV = dict(os.environ, NIHONGO_PROGRESS=PATH, PYTHONUTF8="1")
PASSED = 0


def run(*args, ok=True):
    r = subprocess.run([sys.executable, SCRIPT, *args], capture_output=True,
                       text=True, encoding="utf-8", env=ENV)
    if ok:
        assert r.returncode == 0, (args, r.stdout, r.stderr)
    return r


def J(*args):
    return json.loads(run(*args).stdout)


def data():
    with open(PATH, encoding="utf-8") as f:
        return json.load(f)


def edit(fn):
    d = data()
    fn(d)
    with open(PATH, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False)


def check(label, cond, info=None):
    global PASSED
    assert cond, f"{label}: {info}"
    PASSED += 1
    print(f"  ok  {label}")


def day(i):
    return (dt.date(2026, 9, 1) + dt.timedelta(days=i - 1)).isoformat()


print("== init / add / validate")
run("init", "--name", "Hùng", "--romaji", "true", "--goals", "test", "--date", day(1))
check("init tạo file", os.path.exists(PATH))
check("init từ chối ghi đè", run("init", "--name", "x", "--romaji", "false", ok=False).returncode == 2)
run("add", "--jp", "確認", "--reading", "かくにん", "--vi", "xác nhận",
    "--han-viet", "XÁC NHẬN", "--topic", "công sở", "--source", "workplace")
run("add", "--jp", "たべる", "--reading", "たべる", "--vi", "ăn")
run("add", "--jp", "データ", "--reading", "データ", "--vi", "dữ liệu", "--topic", "IT")
run("add-kanji", "--char", "人", "--han-viet", "NHÂN", "--on", "ジン・ニン", "--kun", "ひと", "--vi", "người")
run("add-grammar", "--pattern", "〜です", "--vi", "thể lịch sự")
run("add-kana", "--type", "hiragana", "--chars", "あいうえお")
run("add-kana", "--type", "katakana", "--chars", "アイ")
check("add từ chối trùng", run("add", "--jp", "確認", "--reading", "x", "--vi", "y", ok=False).returncode == 2)
run("validate")

print("== Leitner")
check("buổi 1: chưa có gì đến hạn", J("due", "--mode", "chuan")["total_due"] == 0)
run("session-end", "--mode", "nhanh", "--score", "3/3", "--date", day(1), "--new-items", "確認", "たべる")
d = J("due", "--mode", "nhanh")
check("buổi 2: 5 mục hộp 1 đến hạn", d["total_due"] == 5 and d["shown"] == 5, d)
r = J("review", "--jp", "確認", "--result", "correct")
check("correct: hộp 1→2, last_reviewed=2", r["box_after"] == 2 and r["last_reviewed"] == 2, r)
check("hesitant: giữ hộp", J("review", "--jp", "たべる", "--result", "hesitant")["box_after"] == 1)
for k in ("データ", "人", "〜です"):
    run("review", "--jp", k, "--result", "correct")
run("session-end", "--mode", "chuẩn", "--date", day(2))
ks = [i["key"] for i in J("due", "--mode", "chuan")["items"]]
check("buổi 3: chỉ hộp 1 đến hạn (hộp 2 chờ 2 buổi)", ks == ["たべる"], ks)
run("review", "--jp", "たべる", "--result", "correct")
run("session-end", "--mode", "chuẩn", "--date", day(3))
ks = sorted(i["key"] for i in J("due", "--mode", "chuan")["items"])
check("buổi 4: hộp 2 đến hạn sau 2 buổi", ks == sorted(["確認", "データ", "人", "〜です"]), ks)
check("correct: hộp 2→3", J("review", "--jp", "確認", "--result", "correct")["box_after"] == 3)
check("wrong: về hộp 1", J("review", "--jp", "データ", "--result", "wrong")["box_after"] == 1)
run("session-end", "--mode", "chuẩn", "--date", day(4))
ks = [i["key"] for i in J("due", "--mode", "chuan")["items"]]
check("buổi 5: từ sai gặp lại ngay, hộp 3 chờ 4 buổi", "データ" in ks and "確認" not in ks, ks)
check("hộp 5 không vượt 5", (edit(lambda d: d["vocabulary"][0].__setitem__("box", 5)) or
                              J("review", "--jp", "確認", "--result", "correct")["box_after"] == 5))

print("== ôn tổng hợp / theo chủ đề")
edit(lambda d: d["vocabulary"][0].__setitem__("box", 5))
check("gentle: hộp 5 sai → 3", J("review", "--jp", "確認", "--result", "wrong", "--rule", "gentle")["box_after"] == 3)
check("gentle: hộp 1 sai → 1", J("review", "--jp", "データ", "--result", "wrong", "--rule", "gentle")["box_after"] == 1)
for k in "a1 a2 a3 a4 a5".split():
    run("add", "--jp", k, "--reading", "a", "--vi", "a", "--topic", "IT")
run("session-end", "--mode", "nhanh", "--date", day(5))
d = J("due", "--mode", "nhanh")
check("due nhanh giới hạn 5, báo remaining", d["shown"] == 5 and d["remaining"] == d["total_due"] - 5, d)
d = J("due", "--mode", "nhanh", "--all")
check("due --all bỏ giới hạn", d["shown"] == d["total_due"] and d["remaining"] == 0, d)
d = J("sample", "--n", "8", "--seed", "1")
ts = [i["type"] for i in d["items"]]
check("sample xen kẽ loại, không lặp liên tiếp", len(set(ts)) >= 3 and all(ts[i] != ts[i + 1] for i in range(len(ts) - 1)), ts)
check("sample --topic", all(i["topic"] == "công sở" for i in J("sample", "--n", "5", "--topic", "công sở")["items"]))
ks = sorted(i["key"] for i in J("sample", "--n", "5", "--type", "katakana")["items"])
check("sample --type katakana", ks == ["ア", "イ"], ks)
ts = sorted(i["type"] for i in J("sample", "--n", "5", "--type", "kanji", "grammar")["items"])
check("sample --type nhiều loại", ts == ["grammar", "kanji"], ts)
check("sample --min-box", all((i["box"] or 0) >= 2 for i in J("sample", "--n", "5", "--min-box", "2")["items"]))
run("session-end", "--mode", "ôn", "--score", "3/4", "--date", day(6))
check("session-end mode ôn vẫn đếm", data()["profile"]["session_count"] == 6 and data()["sessions"][-1]["mode"] == "ôn")
check("gợi ý tổng hợp ở buổi 7", J("due", "--mode", "chuan")["suggest_tong_hop"] is True)

print("== dạy lại")
r = J("mark-taught", "--jp", "たべる", "--result", "good")
check("mark-taught good: +1 hộp, taught", r["box_after"] == r["box_before"] + 1 and r["taught"] is True, r)
check("mark-taught partial: giữ", J("mark-taught", "--jp", "たべる", "--result", "partial")["box_after"] == r["box_after"])
r = J("mark-taught", "--jp", "たべる", "--result", "wrong")
check("mark-taught wrong: hộp 1, taught=false", r["box_after"] == 1 and r["taught"] is False, r)
check("mark-taught mục lạ → lỗi", run("mark-taught", "--jp", "zzz", "--result", "good", ok=False).returncode == 2)
check("teachable trả candidates", "candidates" in J("teachable", "--min-box", "1"))
run("session-end", "--mode", "dạy lại", "--topic", "たべる", "--notes", "ok", "--date", day(7))
check("session-end mode dạy lại + topic", data()["sessions"][-1].get("topic") == "たべる")

print("== mốc thành tích, nhịp 7 ngày, nén sessions")
milestones = {}
compressed_at = None
for i in range(8, 50):
    o = json.loads(run("session-end", "--mode", "nhanh", "--score", "2/3", "--date", day(i),
                       "--workplace-finds", f"w{i}").stdout)
    for m in o["new_milestones"]:
        milestones[m] = i
    if o["sessions_compressed"] and compressed_at is None:
        compressed_at = (i, o["sessions_records"])
check("mốc 10/25 buổi báo đúng lúc", milestones.get("10 buổi học") == 10 and milestones.get("25 buổi học") == 25, milestones)
check("nén ở buổi 41 còn 31 bản ghi", compressed_at == (41, 31), compressed_at)
d = data()
s = d["sessions"]
real = [x for x in s if not x.get("summary")]
check("bản tóm tắt đứng đầu, gộp buổi 1–11", s[0].get("summary") and s[0]["n_from"] == 1 and s[0]["n_to"] == 11 and s[0]["count"] == 11, s[0])
check("giữ chi tiết từ buổi 12", real[0]["n"] == 12 and real[-1]["n"] == 49)
check("tóm tắt giữ workplace_finds", "w10" in s[0]["workplace_finds"])
check("nhịp 7 ngày = 7", d["profile"]["sessions_last_7_days"] == 7)
run("validate")
run("report")

print("== validate bắt lỗi")
edit(lambda d: d["vocabulary"][0].__setitem__("box", 9))
r = run("validate", ok=False)
check("validate phát hiện box sai", r.returncode == 1 and "box = 9" in r.stdout, r.stdout)
edit(lambda d: d["vocabulary"][0].__setitem__("box", 2))
check("set stage sai → lỗi", run("set", "--key", "stage", "--value", "xyz", ok=False).returncode == 2)
run("set", "--key", "tts", "--value", "true")
check("set tts", data()["profile"]["tts"] is True)
run("validate")

print(f"\nTẤT CẢ {PASSED} KIỂM THỬ ĐẠT. File tạm: {PATH}")
