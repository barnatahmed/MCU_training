"""
Simple UART Serial Terminal  —  for beginners
-----------------------------------------------
Install:  pip install pyserial
Run:      python uart_beginner.py

No threads, no complexity.
Uses tkinter (built into Python) + pyserial.
"""

import tkinter as tk
import serial
import serial.tools.list_ports

# ── The serial port object (None when not connected) ──────────────────────────
port = None


# ── STEP 1: Find available COM ports ─────────────────────────────────────────
def refresh_ports():
    """Fill the port dropdown with all available COM ports."""
    ports = [p.device for p in serial.tools.list_ports.comports()]
    port_menu["menu"].delete(0, "end")          # clear old list
    for p in ports:
        port_menu["menu"].add_command(label=p, command=tk._setit(port_var, p))
    if ports:
        port_var.set(ports[0])                  # select first port by default
    else:
        port_var.set("No ports found")


# ── STEP 2: Connect / disconnect ──────────────────────────────────────────────
def connect():
    """Open the serial port with the chosen settings."""
    global port
    try:
        port = serial.Serial(
            port     = port_var.get(),          # e.g. "COM3" or "/dev/ttyUSB0"
            baudrate = int(baud_var.get()),      # bits per second
            timeout  = 0                        # non-blocking read (returns immediately)
        )
        log(f"Connected to {port_var.get()} @ {baud_var.get()} baud", color="orange")
        btn_connect.config(state="disabled")
        btn_disconnect.config(state="normal")
        # Start the polling loop to receive data
        root.after(100, poll)
    except Exception as e:
        log(f"Error: {e}", color="red")


def disconnect():
    """Close the serial port."""
    global port
    if port:
        port.close()
        port = None
    log("Disconnected.", color="orange")
    btn_connect.config(state="normal")
    btn_disconnect.config(state="disabled")


# ── STEP 3: Send data ─────────────────────────────────────────────────────────
def send():
    """Read the input field and send its text over UART."""
    if port is None:
        log("Not connected!", color="red")
        return
    text = entry.get()                          # what the user typed
    if not text:
        return
    port.write((text + "\r\n").encode())        # encode string → bytes, then send
    log(f"TX  {text}", color="#4da6ff")         # show in terminal (blue)
    entry.delete(0, tk.END)                     # clear the input field


# ── STEP 4: Receive data (polling, called every 100 ms) ───────────────────────
def poll():
    """Check if any bytes arrived and print them."""
    if port and port.is_open:
        try:
            n = port.in_waiting                 # how many bytes are waiting?
            if n > 0:
                data = port.read(n)             # read those bytes
                text = data.decode("utf-8", errors="replace").strip()
                if text:
                    log(f"RX  {text}", color="#4dbb6d")   # green
        except Exception as e:
            log(f"Read error: {e}", color="red")
        root.after(100, poll)                   # schedule next check in 100 ms


# ── STEP 5: Print a line to the terminal ─────────────────────────────────────
def log(message, color="white"):
    """Append a coloured message to the terminal box."""
    terminal.config(state="normal")
    terminal.insert(tk.END, message + "\n", color)
    terminal.tag_config(color, foreground=color)
    terminal.see(tk.END)                        # auto-scroll to bottom
    terminal.config(state="disabled")


# ── Build the GUI ─────────────────────────────────────────────────────────────
root = tk.Tk()
root.title("UART Terminal — Beginner")
root.configure(bg="#0d1117")
root.resizable(True, True)

DARK  = "#0d1117"
PANEL = "#161b22"
BORD  = "#30363d"
FG    = "#c9d1d9"
FONT  = ("Consolas", 11)

# ── Row 1: Port + Baud + Buttons ─────────────────────────────────────────────
frame_top = tk.Frame(root, bg=DARK, pady=8, padx=10)
frame_top.pack(fill="x")

tk.Label(frame_top, text="Port:", bg=DARK, fg=FG, font=FONT).pack(side="left")
port_var = tk.StringVar()
port_menu = tk.OptionMenu(frame_top, port_var, "")
port_menu.config(bg=PANEL, fg=FG, font=FONT, highlightthickness=0, width=14)
port_menu.pack(side="left", padx=(4, 12))

tk.Label(frame_top, text="Baud:", bg=DARK, fg=FG, font=FONT).pack(side="left")
baud_var = tk.StringVar(value="115200")
baud_menu = tk.OptionMenu(frame_top, baud_var, "9600", "19200", "38400", "57600", "115200", "230400")
baud_menu.config(bg=PANEL, fg=FG, font=FONT, highlightthickness=0, width=8)
baud_menu.pack(side="left", padx=(4, 12))

btn_refresh = tk.Button(frame_top, text="⟳ Refresh", command=refresh_ports,
                        bg=PANEL, fg=FG, font=FONT, relief="flat", padx=8)
btn_refresh.pack(side="left", padx=4)

btn_connect = tk.Button(frame_top, text="Connect", command=connect,
                        bg="#1a7f37", fg="white", font=FONT, relief="flat", padx=8)
btn_connect.pack(side="left", padx=4)

btn_disconnect = tk.Button(frame_top, text="Disconnect", command=disconnect,
                           bg="#6e1a1a", fg="white", font=FONT, relief="flat", padx=8, state="disabled")
btn_disconnect.pack(side="left", padx=4)

# ── Row 2: Terminal display ───────────────────────────────────────────────────
frame_mid = tk.Frame(root, bg=DARK, padx=10)
frame_mid.pack(fill="both", expand=True)

tk.Label(frame_mid, text="Terminal", bg=DARK, fg="#8b949e", font=("Consolas", 9)).pack(anchor="w")

terminal = tk.Text(frame_mid, bg="#010409", fg=FG, font=FONT,
                   state="disabled", wrap="word", height=18,
                   insertbackground=FG, relief="flat", padx=8, pady=6)
terminal.pack(fill="both", expand=True)

scrollbar = tk.Scrollbar(frame_mid, command=terminal.yview)
terminal.config(yscrollcommand=scrollbar.set)

btn_clear = tk.Button(frame_mid, text="Clear terminal", command=lambda: [
    terminal.config(state="normal"), terminal.delete("1.0", tk.END), terminal.config(state="disabled")
], bg=PANEL, fg="#8b949e", font=("Consolas", 9), relief="flat")
btn_clear.pack(anchor="e", pady=(4, 0))

# ── Row 3: Send input ─────────────────────────────────────────────────────────
frame_bot = tk.Frame(root, bg=DARK, padx=10, pady=10)
frame_bot.pack(fill="x")

tk.Label(frame_bot, text="Send:", bg=DARK, fg=FG, font=FONT).pack(side="left")

entry = tk.Entry(frame_bot, bg=PANEL, fg=FG, font=FONT,
                 insertbackground=FG, relief="flat", highlightthickness=1,
                 highlightbackground=BORD, highlightcolor="#58a6ff")
entry.pack(side="left", fill="x", expand=True, padx=(6, 8), ipady=4)
entry.bind("<Return>", lambda e: send())       # press Enter to send

btn_send = tk.Button(frame_bot, text="Send ▶", command=send,
                     bg="#1f4e8c", fg="white", font=FONT, relief="flat", padx=12)
btn_send.pack(side="left")

# ── Start ─────────────────────────────────────────────────────────────────────
refresh_ports()
log("Welcome! Choose a port and click Connect.", color="orange")
log("Blue = data you sent   Green = data received", color="#8b949e")

root.geometry("600x480")
root.mainloop()