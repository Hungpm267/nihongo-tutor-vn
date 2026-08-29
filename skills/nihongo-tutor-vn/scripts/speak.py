#!/usr/bin/env python3
"""Phát âm một chuỗi tiếng Nhật ra loa (nihongo-tutor-vn).

Tự chọn công cụ đầu tiên chạy được theo thứ tự:
  1. edge-tts  (pip install edge-tts) — giọng ja-JP-NanamiNeural, cần mạng
  2. gTTS      (pip install gTTS)     — lang="ja", cần mạng
  3. say -v Kyoko                      — chỉ macOS
  4. Windows SAPI qua PowerShell       — chỉ khi máy có giọng tiếng Nhật
Phát bằng afplay / mpv / ffplay / PowerShell tùy hệ điều hành.

Ví dụ:
  speak.py "確認をお願いします"
  speak.py "お疲れ様です" --save otsukare.mp3
  speak.py --check            # chỉ báo công cụ nào dùng được, không phát

Không có công cụ nào → in hướng dẫn cài ngắn gọn, thoát mã 3, không crash.
Chạy với --quiet để im lặng hoàn toàn khi lỗi (dùng trong buổi học, tránh
lặp thông báo lỗi mỗi từ).
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
import tempfile

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

VOICE_EDGE = "ja-JP-NanamiNeural"
SYSTEM = platform.system()  # Windows / Darwin / Linux

INSTALL_HINT = """Chưa có công cụ phát âm nào. Cài một trong hai (cần mạng khi phát):
  python -m pip install edge-tts      # khuyến nghị, giọng tự nhiên
  python -m pip install gTTS          # thay thế
Trình phát: macOS có sẵn afplay; Windows có sẵn PowerShell; Linux cần mpv hoặc
ffplay (apt install mpv). Kiểm tra lại bằng:  python speak.py --check"""


# ----------------------------------------------------------------- tổng hợp

def synth_edge(text, out_path):
    import asyncio
    import edge_tts

    async def run():
        await edge_tts.Communicate(text, VOICE_EDGE).save(out_path)

    asyncio.run(run())


def synth_gtts(text, out_path):
    from gtts import gTTS
    gTTS(text=text, lang="ja").save(out_path)


def synth_say(text, out_path):
    # say chỉ xuất AIFF/ m4a; dùng --data-format để ra wav-ish? Đơn giản: aiff
    subprocess.run(["say", "-v", "Kyoko", "-o", out_path, text], check=True,
                   capture_output=True)


def synth_sapi(text, out_path):
    """Windows SAPI: chỉ dùng được khi có giọng ja-JP (Haruka/Ayumi/Ichiro)."""
    script = (
        "Add-Type -AssemblyName System.Speech;"
        "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer;"
        "$v = $s.GetInstalledVoices() | Where-Object { $_.VoiceInfo.Culture.Name -eq 'ja-JP' } | Select-Object -First 1;"
        "if (-not $v) { exit 9 };"
        "$s.SelectVoice($v.VoiceInfo.Name);"
        "$s.SetOutputToWaveFile($env:SPEAK_OUT);"
        "$s.Speak($env:SPEAK_TEXT); $s.Dispose()"
    )
    env = dict(os.environ, SPEAK_OUT=out_path, SPEAK_TEXT=text)
    r = subprocess.run(["powershell", "-NoProfile", "-Command", script],
                       env=env, capture_output=True)
    if r.returncode == 9:
        raise RuntimeError("Windows không có giọng tiếng Nhật (ja-JP)")
    r.check_returncode()


# (tên, hàm, đuôi file, hàm kiểm tra khả dụng)
def _has_module(name):
    try:
        __import__(name)
        return True
    except ImportError:
        return False


ENGINES = [
    ("edge-tts", synth_edge, ".mp3", lambda: _has_module("edge_tts")),
    ("gTTS", synth_gtts, ".mp3", lambda: _has_module("gtts")),
    ("say (macOS)", synth_say, ".aiff",
     lambda: SYSTEM == "Darwin" and shutil.which("say") is not None),
    ("Windows SAPI (cần giọng ja-JP cài sẵn)", synth_sapi, ".wav",
     lambda: SYSTEM == "Windows" and shutil.which("powershell") is not None),
]


# ----------------------------------------------------------------- phát

def play(path):
    """Phát file. Trả về tên trình phát, hoặc None nếu không có."""
    if SYSTEM == "Darwin" and shutil.which("afplay"):
        subprocess.run(["afplay", path], check=True)
        return "afplay"
    if shutil.which("mpv"):
        subprocess.run(["mpv", "--really-quiet", "--no-video", path], check=True)
        return "mpv"
    if shutil.which("ffplay"):
        subprocess.run(["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", path],
                       check=True)
        return "ffplay"
    if SYSTEM == "Windows" and shutil.which("powershell"):
        if path.lower().endswith(".wav"):
            script = ("(New-Object System.Media.SoundPlayer $env:SPEAK_FILE).PlaySync()")
        else:
            script = (
                "Add-Type -AssemblyName PresentationCore;"
                "$p = New-Object System.Windows.Media.MediaPlayer;"
                "$p.Open([Uri]$env:SPEAK_FILE);"
                "$deadline = (Get-Date).AddSeconds(5);"
                "while (-not $p.NaturalDuration.HasTimeSpan -and (Get-Date) -lt $deadline) { Start-Sleep -Milliseconds 50 };"
                "$p.Play();"
                "if ($p.NaturalDuration.HasTimeSpan) { Start-Sleep -Milliseconds ($p.NaturalDuration.TimeSpan.TotalMilliseconds + 300) } else { Start-Sleep -Seconds 3 };"
                "$p.Stop(); $p.Close()"
            )
        subprocess.run(["powershell", "-NoProfile", "-Command", script],
                       env=dict(os.environ, SPEAK_FILE=os.path.abspath(path)),
                       check=True, capture_output=True)
        return "powershell"
    return None


def player_name():
    if SYSTEM == "Darwin" and shutil.which("afplay"):
        return "afplay"
    for t in ("mpv", "ffplay"):
        if shutil.which(t):
            return t
    if SYSTEM == "Windows" and shutil.which("powershell"):
        return "powershell"
    return None


# ----------------------------------------------------------------- main

def synthesize(text, save_path=None, quiet=False):
    """Thử từng engine. Trả (tên engine, đường dẫn file) hoặc (None, None)."""
    errors = []
    for name, fn, ext, avail in ENGINES:
        if not avail():
            continue
        if save_path:
            out = save_path
        else:
            fd, out = tempfile.mkstemp(prefix="nihongo-", suffix=ext)
            os.close(fd)
        try:
            fn(text, out)
            if os.path.getsize(out) > 0:
                return name, out
            errors.append(f"{name}: file rỗng")
        except Exception as e:  # noqa: BLE001 — mọi lỗi đều thử engine kế
            errors.append(f"{name}: {type(e).__name__}: {str(e)[:120]}")
        if not save_path:
            try:
                os.unlink(out)
            except OSError:
                pass
    if errors and not quiet:
        print("Không tổng hợp được âm thanh:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
    return None, None


def cmd_check():
    print(f"Hệ điều hành: {SYSTEM}")
    for name, _, _, avail in ENGINES:
        print(f"  {'✓' if avail() else '✗'} {name}")
    p = player_name()
    print(f"Trình phát: {p or 'không có'}")
    name, path = synthesize("テスト", quiet=True)
    if name:
        print(f"Tổng hợp thử: OK bằng {name}")
        os.unlink(path)
        return 0
    print("Tổng hợp thử: THẤT BẠI")
    print(INSTALL_HINT)
    return 3


def main(argv=None):
    ap = argparse.ArgumentParser(description="Phát âm tiếng Nhật ra loa.")
    ap.add_argument("text", nargs="?", help="chuỗi tiếng Nhật cần đọc")
    ap.add_argument("--save", metavar="FILE",
                    help="lưu ra file .mp3/.wav thay vì file tạm")
    ap.add_argument("--no-play", action="store_true", help="chỉ tạo file, không phát")
    ap.add_argument("--quiet", action="store_true",
                    help="im lặng khi lỗi (mã thoát vẫn khác 0)")
    ap.add_argument("--check", action="store_true",
                    help="báo công cụ nào dùng được rồi thoát")
    args = ap.parse_args(argv)

    if args.check:
        sys.exit(cmd_check())
    if not args.text:
        ap.error("cần chuỗi tiếng Nhật, hoặc dùng --check")

    if args.save and not args.save.lower().endswith((".mp3", ".wav", ".aiff")):
        # gợi ý đuôi phù hợp với engine đầu tiên khả dụng
        args.save += ".mp3"

    name, path = synthesize(args.text, args.save, quiet=args.quiet)
    if not name:
        if not args.quiet:
            print(INSTALL_HINT, file=sys.stderr)
        sys.exit(3)

    rc = 0
    if not args.no_play:
        try:
            player = play(path)
        except subprocess.CalledProcessError as e:
            player = None
            if not args.quiet:
                print(f"Không phát được bằng trình phát: {e}", file=sys.stderr)
            rc = 4
        if player is None and rc == 0:
            if not args.quiet:
                print("Không có trình phát âm thanh (afplay/mpv/ffplay/powershell).",
                      file=sys.stderr)
            rc = 4

    if args.save:
        if not args.quiet:
            print(f"Đã lưu ({name}): {args.save}")
    else:
        try:
            os.unlink(path)
        except OSError:
            pass
    sys.exit(rc)


if __name__ == "__main__":
    main()
