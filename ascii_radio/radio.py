import curses, subprocess, time, random, os, json, socket, pkgutil

# Load stations from file
data = pkgutil.get_data("ascii_radio", "stations.txt").decode("utf-8")
stations = []
for line in data.splitlines():
    if "|" in line:
        name, url = line.split("|", 1)
        stations.append((name.strip(), url.strip()))

station_index = 0
mpv_process = None
ipc_socket_path = "/tmp/mpv_radio_socket"
volume = 50  # Initial volume (0-100)

def send_ipc_command(command):
    if not os.path.exists(ipc_socket_path):
        return
    try:
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(ipc_socket_path)
        client.send((json.dumps(command) + "\n").encode())
        client.close()
    except Exception:
        pass

def set_volume(vol):
    global volume
    volume = max(0, min(100, vol))  # Clamp 0–100
    send_ipc_command({"command": ["set_property", "volume", volume]})

def play_station(idx):
    stop_station()
    name, url = stations[idx]
    if os.path.exists(ipc_socket_path):
        os.remove(ipc_socket_path)
    return subprocess.Popen([
        "mpv", "--no-video", "--quiet", url,
        f"--volume={volume}",
        f"--input-ipc-server={ipc_socket_path}"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def stop_station():
    global mpv_process
    if mpv_process:
        mpv_process.terminate()
        try:
            mpv_process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            mpv_process.kill()
        mpv_process = None

def draw_ui(stdscr, sel, playing):
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    title = "🎵 ascii‑radio (India edition)"
    stdscr.addstr(1, (width - len(title)) // 2, title, curses.A_BOLD)

    controls = "[↑↓] station  [←→] volume  [space] play/pause  [q] quit"
    stdscr.addstr(2, (width - len(controls)) // 2, controls)

    for i, (name, _) in enumerate(stations):
        marker = "▶" if (i == sel and playing) else "⏸" if (i == sel and not playing) else " "
        line = f" {marker} {name}"
        style = curses.A_BOLD | curses.A_REVERSE if i == sel else curses.A_NORMAL
        stdscr.addstr(4 + i, 4, line[:width - 8], style)

    vol_str = f"🔊 Volume: {volume}%"
    stdscr.addstr(5 + len(stations), (width - len(vol_str)) // 2, vol_str, curses.A_DIM)

    # ── Footer with GitHub link ──
    github_username = "tookstanmay"
    github_url = f"https://github.com/{github_username}"
    text = f"made with ❤️  by {github_username}"

    # Calculate position for centered footer
    x = (width - len(text)) // 2
    y = height - 2

    try:
        stdscr.addstr(y, x, f"made with ❤️  by ", curses.A_DIM)
        stdscr.addstr(y, x + len("made with ❤️  by "), github_username,
                      curses.A_UNDERLINE | curses.color_pair(2))
    except curses.error:
        pass

    stdscr.refresh()


def fake_waveform_bar(stdscr):
    width = curses.COLS - 4
    wave_chars = ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']
    waveform = ''.join(random.choice(wave_chars) for _ in range(width - 2))
    stdscr.addstr(7 + len(stations), 2, waveform, curses.color_pair(2))
    stdscr.refresh()
    time.sleep(0.035)

def main(stdscr):
    global station_index, mpv_process, volume

    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(80)

    curses.start_color()
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    playing = True
    mpv_process = play_station(station_index)
    tick = 0

    while True:
        draw_ui(stdscr, station_index, playing)
        if playing:
            fake_waveform_bar(stdscr)
        else:
            stdscr.addstr(7 + len(stations), 2, "[⏸ PAUSED]".center(curses.COLS - 4), curses.A_DIM)
            stdscr.refresh()

        tick += 1

        try:
            key = stdscr.getch()
        except:
            key = -1

        if key == -1:
            continue
        elif key in [ord('q'), ord('Q')]:
            stop_station()
            break
        elif key in [curses.KEY_DOWN]:
            station_index = (station_index + 1) % len(stations)
            mpv_process = play_station(station_index)
            playing = True
        elif key in [curses.KEY_UP]:
            station_index = (station_index - 1) % len(stations)
            mpv_process = play_station(station_index)
            playing = True
        elif key == ord(' '):
            if playing:
                stop_station()
            else:
                mpv_process = play_station(station_index)
            playing = not playing
        elif key == curses.KEY_RIGHT:
            set_volume(volume + 5)
        elif key == curses.KEY_LEFT:
            set_volume(volume - 5)

        time.sleep(0.05)

