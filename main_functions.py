import os, time, threading, subprocess
import console_control as console

def is_float(string: str):
    try:
        float(string)
        return True
    except (ValueError, TypeError):
        return False

def find_mp4_files(search_path: str):
    found_files = []
    
    console.write("- - - -  SEARCHING FOR .MP4 VIDEOS  - - - -")
    for root, dirs, files in os.walk(search_path):
        if len(files) == 0:
            continue
        
        for file in files:
            console.write(f"FOUND: {len(found_files)}")
            
            name, extension = os.path.splitext(file)
            if extension == ".mp4" and os.path.basename(root) != "compressed":
                found_files.append(os.path.join(root, file))
            
            console.clean_upper_line()
    
    time.sleep(1)
    console.clean_upper_line()
    return found_files

def run_command(cmd: list[str]) -> tuple[int, str, str]:
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return p.returncode, p.stdout, p.stderr

def get_mp4_duration(path: str) -> str:
    cmd = [
        "./bin/ffprobe.exe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        path
    ]
    rc, out, err = run_command(cmd)
    if rc != 0:
        raise RuntimeError(f"ffprobe failed (rc={rc}): {err.strip()}")
    try:
        return hhmmss(float(out.strip()))
    except ValueError:
        raise RuntimeError(f"Could not parse duration from ffprobe output: {out!r}")

def cut_number(number: float, quantity: int):
    factor = 10 ** quantity
    return int(number * factor) / factor

def hhmmss(seconds: float) -> str:
    if seconds < 0:
        seconds = 0
    s = int(seconds)
    hh = s // 3600
    mm = (s % 3600) // 60
    ss = s % 60
    return f"{hh:02d}:{mm:02d}:{ss:02d}"

def compress_async(
    input_path: str,
    output_path: str,
    crf: float,
    preset: str,
    encoder: str,
    stats_period_seconds: float = 0.5,
) -> tuple[threading.Thread, dict]:
    state = {"process": None, "finished": False, "error": None, "seconds_processed": 0}

    def worker():
        try:
            cmd = [
                "./bin/ffmpeg.exe",
                "-hide_banner",
                "-loglevel", "error",
                "-nostdin",
                "-stats_period", str(stats_period_seconds),
                "-progress", "pipe:1",
                "-i", os.path.abspath(input_path),

                "-c:v", encoder,
                "-preset", preset,
                "-crf", str(crf),
                "-pix_fmt", "yuv420p",

                "-c:a", "aac",
                "-b:a", "160k",

                "-movflags", "+faststart",
                os.path.abspath(output_path),
            ]
            
            if encoder == "hevc_nvenc":
                cmd.append("-hwaccel")
                cmd.append("cuda")

            p = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,  # para que NO ensucie la consola
                text=True,
                bufsize=1,
                universal_newlines=True,
            )
            state["process"] = p

            for line in p.stdout:
                line = line.strip()
                if not line or "=" not in line:
                    continue

                key, value = line.split("=", 1)

                if key == "out_time_ms":
                    try:
                        seconds_processed = float(value) / 1_000_000.0
                    except ValueError:
                        continue
                    
                    state["seconds_processed"] = seconds_processed

                elif key == "progress" and value == "end":
                    break

            p.wait()
            state["finished"] = True

            if p.returncode != 0:
                state["error"] = f"ffmpeg failed with return code {p.returncode}"
        except Exception as e:
            state["error"] = str(e)
            state["finished"] = True

    t = threading.Thread(target=worker, daemon=True)
    t.start()
    return t, state