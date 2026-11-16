import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import threading
import time
import socket
import psutil

BG = "#f3f6fb"
CARD = "#ffffff"
TEXT = "#182230"
MUTED = "#657386"
BLUE = "#2563eb"
GREEN = "#16834a"
AMBER = "#a16207"
RED = "#b42318"

class NetGuardAI:
    def __init__(self, root):
        self.root = root
        self.root.title("NetGuard AI")
        self.root.geometry("1050x700")
        self.root.minsize(860, 580)
        self.root.configure(bg=BG)
        self.running = False
        self.seen = set()
        self.events = []
        self.poll_seconds = 1.0
        self.build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.after(700, self.start_monitor)

    def build_ui(self):
        top = tk.Frame(self.root, bg=CARD, height=76, highlightbackground="#e2e8f0", highlightthickness=1)
        top.pack(fill="x")
        top.pack_propagate(False)
        left = tk.Frame(top, bg=CARD)
        left.pack(side="left", padx=24, pady=14)
        tk.Label(left, text="◈  NetGuard AI", bg=CARD, fg=TEXT,
                 font=("Segoe UI", 19, "bold")).pack(anchor="w")
        tk.Label(left, text="NETWORK ACTIVITY MONITOR", bg=CARD, fg=MUTED,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w")
        self.status = tk.Label(top, text="● STARTING", bg="#eaf7ef", fg=GREEN,
                               font=("Segoe UI", 9, "bold"), padx=13, pady=8)
        self.status.pack(side="right", padx=24, pady=20)

        content = tk.Frame(self.root, bg=BG)
        content.pack(fill="both", expand=True, padx=22, pady=20)

        summary = tk.Frame(content, bg=BG)
        summary.pack(fill="x", pady=(0, 16))
        self.total_value = self.stat_card(summary, "CONNECTION EVENTS", "0", 0)
        self.apps_value = self.stat_card(summary, "APPS SEEN", "0", 1)
        self.last_value = self.stat_card(summary, "LAST EVENT", "—", 2)

        toolbar = tk.Frame(content, bg=BG)
        toolbar.pack(fill="x", pady=(0, 10))
        tk.Label(toolbar, text="Recent network activity", bg=BG, fg=TEXT,
                 font=("Segoe UI", 14, "bold")).pack(side="left")
        self.pause_btn = tk.Button(toolbar, text="Pause monitoring", command=self.toggle_monitor,
                                   bg="#e8eefc", fg=BLUE, activebackground="#dbe6ff",
                                   relief="flat", padx=14, pady=8, font=("Segoe UI", 9, "bold"),
                                   cursor="hand2")
        self.pause_btn.pack(side="right")
        self.clear_btn = tk.Button(toolbar, text="Clear history", command=self.clear_history,
                                   bg=CARD, fg=MUTED, activebackground="#eef2f7",
                                   relief="flat", padx=14, pady=8, font=("Segoe UI", 9),
                                   cursor="hand2")
        self.clear_btn.pack(side="right", padx=8)

        table_card = tk.Frame(content, bg=CARD, highlightbackground="#e2e8f0", highlightthickness=1)
        table_card.pack(fill="both", expand=True)
        columns = ("time", "app", "pid", "remote", "status")
        self.table = ttk.Treeview(table_card, columns=columns, show="headings")
        headings = [("time","TIME",130), ("app","APPLICATION",230), ("pid","PID",80),
                    ("remote","REMOTE ADDRESS",280), ("status","STATE",120)]
        for col, title, width in headings:
            self.table.heading(col, text=title)
            self.table.column(col, width=width, anchor="w")
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=CARD, fieldbackground=CARD, foreground=TEXT,
                        rowheight=34, borderwidth=0, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", background="#f5f7fb", foreground=MUTED,
                        font=("Segoe UI", 8, "bold"), relief="flat")
        style.map("Treeview", background=[("selected", "#dbeafe")], foreground=[("selected", TEXT)])
        scrollbar = ttk.Scrollbar(table_card, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)
        self.table.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 8), pady=10)

        bottom = tk.Frame(content, bg=BG)
        bottom.pack(fill="x", pady=(12, 0))
        tk.Label(bottom, text="Checks active TCP/UDP endpoints every second. Some short-lived connections may not be observed.",
                 bg=BG, fg=MUTED, font=("Segoe UI", 8)).pack(anchor="w")
        tk.Label(bottom, text="Local monitoring only • No packet contents, passwords, or browsing content are collected",
                 bg=BG, fg=MUTED, font=("Segoe UI", 8)).pack(anchor="w", pady=(3, 0))

    def stat_card(self, parent, title, value, col):
        card = tk.Frame(parent, bg=CARD, highlightbackground="#e2e8f0", highlightthickness=1)
        card.grid(row=0, column=col, sticky="nsew", padx=(0 if col == 0 else 10, 0))
        parent.grid_columnconfigure(col, weight=1)
        tk.Label(card, text=title, bg=CARD, fg=MUTED, font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=16, pady=(13, 4))
        label = tk.Label(card, text=value, bg=CARD, fg=TEXT, font=("Segoe UI", 20, "bold"))
        label.pack(anchor="w", padx=16, pady=(0, 13))
        return label

    def start_monitor(self):
        if self.running:
            return
        self.running = True
        self.status.config(text="● MONITORING", bg="#eaf7ef", fg=GREEN)
        self.pause_btn.config(text="Pause monitoring")
        threading.Thread(target=self.monitor_loop, daemon=True).start()

    def toggle_monitor(self):
        if self.running:
            self.running = False
            self.status.config(text="● PAUSED", bg="#fff4e5", fg=AMBER)
            self.pause_btn.config(text="Resume monitoring")
        else:
            self.start_monitor()

    def monitor_loop(self):
        while self.running:
            try:
                conns = psutil.net_connections(kind="inet")
                current = set()
                for c in conns:
                    if not c.raddr or not c.laddr:
                        continue
                    if c.status not in ("ESTABLISHED", "SYN_SENT"):
                        continue
                    try:
                        remote_ip = c.raddr.ip
                        remote_port = c.raddr.port
                        local_ip = c.laddr.ip
                        local_port = c.laddr.port
                        if remote_ip in ("127.0.0.1", "::1") or remote_ip.startswith("169.254."):
                            continue
                        key = (c.pid, local_ip, local_port, remote_ip, remote_port)
                        current.add(key)
                        if key not in self.seen:
                            try:
                                proc = psutil.Process(c.pid) if c.pid else None
                                name = proc.name() if proc else "Unknown process"
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                name = "Unknown process (permission limited)"
                            event = {
                                "time": datetime.now().strftime("%H:%M:%S"),
                                "app": name,
                                "pid": str(c.pid or "—"),
                                "remote": f"{remote_ip}:{remote_port}",
                                "status": c.status
                            }
                            self.root.after(0, self.add_event, event)
                    except (AttributeError, OSError):
                        continue
                self.seen = current
            except psutil.AccessDenied:
                self.root.after(0, self.show_permission_hint)
            except Exception as exc:
                self.root.after(0, self.set_error, str(exc))
            time.sleep(self.poll_seconds)

    def add_event(self, event):
        self.events.insert(0, event)
        self.events = self.events[:1000]
        self.table.insert("", 0, values=(event["time"], event["app"], event["pid"], event["remote"], event["status"]))
        children = self.table.get_children()
        if len(children) > 1000:
            self.table.delete(children[-1])
        self.total_value.config(text=str(len(self.events)))
        self.apps_value.config(text=str(len(set(e["app"] for e in self.events))))
        self.last_value.config(text=event["time"])
        self.show_popup(event)

    def show_popup(self, event):
        popup = tk.Toplevel(self.root)
        popup.title("New network connection")
        popup.configure(bg=CARD)
        popup.resizable(False, False)
        popup.attributes("-topmost", True)
        frame = tk.Frame(popup, bg=CARD, padx=18, pady=16)
        frame.pack()
        tk.Label(frame, text="New connection detected", bg=CARD, fg=BLUE,
                 font=("Segoe UI", 12, "bold")).pack(anchor="w")
        tk.Label(frame, text=f'{event["app"]}  •  PID {event["pid"]}',
                 bg=CARD, fg=TEXT, font=("Segoe UI", 10)).pack(anchor="w", pady=(8, 3))
        tk.Label(frame, text=f'Remote: {event["remote"]}',
                 bg=CARD, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w")
        tk.Label(frame, text=event["time"], bg=CARD, fg=MUTED,
                 font=("Segoe UI", 8)).pack(anchor="w", pady=(3, 10))
        tk.Button(frame, text="OK", command=popup.destroy, bg=BLUE, fg="white",
                  activebackground="#1d4ed8", relief="flat", padx=20, pady=6,
                  font=("Segoe UI", 9, "bold")).pack(anchor="e")
        popup.update_idletasks()
        x = self.root.winfo_screenwidth() - popup.winfo_width() - 24
        y = self.root.winfo_screenheight() - popup.winfo_height() - 60
        popup.geometry(f"+{x}+{y}")
        popup.after(12000, lambda: popup.destroy() if popup.winfo_exists() else None)

    def show_permission_hint(self):
        self.status.config(text="● LIMITED PERMISSIONS", bg="#fff4e5", fg=AMBER)

    def set_error(self, msg):
        self.status.config(text="● MONITOR ERROR", bg="#fdecec", fg=RED)

    def clear_history(self):
        self.events.clear()
        for item in self.table.get_children():
            self.table.delete(item)
        self.total_value.config(text="0")
        self.apps_value.config(text="0")
        self.last_value.config(text="—")

    def close(self):
        self.running = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = NetGuardAI(root)
    root.mainloop()
