#!/usr/bin/env python3
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

SOCKET_PATH = "/tmp/mpvsocket"
OUTPUT_BASE_DIR = Path("/Users/getmanov/Лабораторный_полигон/01_projects/Tennis_Brain/Raw_Clips")

class MpvIPCClient:
    def __init__(self, socket_path: str = SOCKET_PATH):
        self.socket_path = socket_path

    def send_command(self, command: list) -> dict:
        if not os.path.exists(self.socket_path):
            raise FileNotFoundError(f"Сокет mpv не найден: {self.socket_path}")

        payload = json.dumps({"command": command}) + "\n"
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.connect(self.socket_path)
            client.sendall(payload.encode("utf-8"))
            response = client.recv(4096).decode("utf-8")
            return json.loads(response.splitlines()[0])

    def get_time_pos(self) -> float:
        res = self.send_command(["get_property", "time-pos"])
        return float(res.get("data", 0.0))

    def get_source_path(self) -> str:
        res = self.send_command(["get_property", "path"])
        return str(res.get("data", ""))

def execute_cmd(cmd: list):
    process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if process.returncode != 0:
        raise RuntimeError(f"Ошибка выполнения: {' '.join(cmd)}\n{process.stderr}")

def process_clip(source_path: str, t_in: float, t_out: float, tags: list, clip_id: str):
    session_dir = OUTPUT_BASE_DIR / time.strftime("%Y-%m-%d_Session")
    clip_dir = session_dir / clip_id
    frames_dir = clip_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    video_out = clip_dir / f"{clip_id}.mp4"
    audio_out = clip_dir / f"{clip_id}.wav"
    meta_out = clip_dir / f"{clip_id}_meta.json"

    duration = max(0.1, t_out - t_in)
    print(f"[*] Нарезка фрагмента: {clip_id} ({t_in:.3f}с -> {t_out:.3f}с, длительность: {duration:.3f}с)")

    cmd_video = [
        "ffmpeg", "-y",
        "-ss", str(t_in),
        "-i", source_path,
        "-t", str(duration),
        "-c:v", "libx264",
        "-crf", "19",
        "-preset", "fast",
        "-c:a", "aac",
        "-avoid_negative_ts", "make_zero",
        str(video_out)
    ]
    execute_cmd(cmd_video)

    cmd_audio = [
        "ffmpeg", "-y",
        "-ss", str(t_in),
        "-i", source_path,
        "-t", str(duration),
        "-vn",
        "-ar", "16000",
        "-ac", "1",
        "-c:a", "pcm_s16le",
        str(audio_out)
    ]
    execute_cmd(cmd_audio)

    fps_sample = max(1.0, 5.0 / duration)
    cmd_frames = [
        "ffmpeg", "-y",
        "-i", str(video_out),
        "-vf", f"fps={fps_sample:.2f}",
        "-q:v", "2",
        str(frames_dir / f"{clip_id}_c%02d.jpg")
    ]
    execute_cmd(cmd_frames)

    metadata = {
        "clip_id": clip_id,
        "source_video": str(source_path),
        "boundaries": {
            "t_in": round(t_in, 3),
            "t_out": round(t_out, 3),
            "duration_sec": round(duration, 3)
        },
        "tags": tags,
        "coach_audio_transcript": "",
        "status": "READY_FOR_EXTRACTION",
        "artifacts": {
            "video": str(video_out),
            "audio": str(audio_out),
            "transcript": None,
            "frames_dir": str(frames_dir)
        }
    }

    with open(meta_out, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"[✓] Успешно! Файлы сохранены в:\n    {clip_dir}")

def main():
    if len(sys.argv) < 2:
        print("Команды: mark_in | mark_out | commit [теги]")
        sys.exit(1)

    state_file = Path("/tmp/slicer_transit_state.json")
    client = MpvIPCClient()
    action = sys.argv[1].lower()

    state = {"t_in": None, "t_out": None, "tags": []}
    if state_file.exists():
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                state = json.load(f)
        except Exception:
            pass

    if action == "mark_in":
        t_in = client.get_time_pos()
        state["t_in"] = t_in
        print(f"[IN] Метка начала зафиксирована: {t_in:.3f}с")

    elif action == "mark_out":
        t_out = client.get_time_pos()
        state["t_out"] = t_out
        print(f"[OUT] Метка конца зафиксирована: {t_out:.3f}с")

    elif action == "commit":
        if state.get("t_in") is None or state.get("t_out") is None:
            print("[!] Ошибка: Не заданы обе метки. Сначала вызовите mark_in и mark_out.")
            sys.exit(1)

        t_in = state["t_in"]
        t_out = state["t_out"]
        if t_out <= t_in:
            print(f"[!] Ошибка: t_out ({t_out:.3f}) <= t_in ({t_in:.3f}). Конец должен быть позже начала.")
            sys.exit(1)

        source_path = client.get_source_path()
        tags = sys.argv[2:] if len(sys.argv) > 2 else ["forehand", "rally"]
        clip_id = f"clip_{time.strftime('%Y%m%d_%H%M%S')}"

        process_clip(source_path, t_in, t_out, tags, clip_id)
        state = {"t_in": None, "t_out": None, "tags": []}

    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
